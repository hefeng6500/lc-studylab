"""
Multi-Query Retriever 模块

实现 Multi-Query Retriever，将单个查询扩展为多个不同表达的查询，
然后对每个查询进行检索，最后合并结果。

参考：
- https://python.langchain.com/docs/modules/data_connection/retrievers/multi_query
"""

from typing import Optional, List
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel

from config import settings, get_logger
from core.models import get_chat_model, get_model_string
from rag.query_enhancement import generate_multi_queries

logger = get_logger(__name__)


class MultiQueryRetriever(BaseRetriever):
    """
    Multi-Query Retriever
    
    将用户的单个查询扩展为多个不同表达的查询，然后对每个查询进行检索，最后合并结果。
    """
    
    def __init__(
        self,
        retriever: BaseRetriever,
        llm: Optional[BaseChatModel] = None,
        num_queries: int = 3,
        model: Optional[str] = None,
    ):
        """
        初始化 Multi-Query Retriever
        
        Args:
            retriever: 基础检索器
            llm: LLM 模型实例
            num_queries: 生成的查询数量
            model: 模型字符串
        """
        super().__init__()
        self.retriever = retriever
        self.base_retriever = retriever  # 保持向后兼容
        self.llm = llm
        self.num_queries = num_queries
        self.model = model
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None,
        **kwargs,
    ) -> List[Document]:
        """
        检索相关文档
        
        Args:
            query: 用户查询
            run_manager: 运行管理器
            **kwargs: 其他参数
        
        Returns:
            相关文档列表
        """
        logger.info(f"🔄 Multi-Query 检索: {query[:50]}...")
        
        try:
            # 1. 生成多个查询变体
            queries = generate_multi_queries(
                query=query,
                llm=self.llm,
                num_queries=self.num_queries,
                model=self.model,
            )
            
            logger.debug(f"   生成了 {len(queries)} 个查询变体")
            for i, q in enumerate(queries, 1):
                logger.debug(f"   [{i}] {q}")
            
            # 2. 对每个查询进行检索
            all_docs = []
            seen_docs = set()
            
            for q in queries:
                docs = self.base_retriever.invoke(
                    q,
                    run_manager=run_manager,
                    **kwargs,
                )
                
                # 去重（基于文档内容）
                for doc in docs:
                    doc_key = doc.page_content[:100] if doc.page_content else str(id(doc))
                    if doc_key not in seen_docs:
                        seen_docs.add(doc_key)
                        all_docs.append(doc)
            
            logger.info(f"✅ Multi-Query 检索完成: 找到 {len(all_docs)} 个文档")
            return all_docs
            
        except Exception as e:
            logger.error(f"❌ Multi-Query 检索失败: {e}")
            # 如果失败，回退到原始查询
            logger.warning("回退到原始查询检索")
            return self.base_retriever.invoke(
                query,
                run_manager=run_manager,
                **kwargs,
            )
    
    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None,
        **kwargs,
    ) -> List[Document]:
        """异步检索相关文档"""
        # 简化实现：同步调用
        return self._get_relevant_documents(query, run_manager=run_manager, **kwargs)


def create_multi_query_retriever(
    retriever: BaseRetriever,
    llm: Optional[BaseChatModel] = None,
    num_queries: Optional[int] = None,
    model: Optional[str] = None,
    **kwargs,
) -> MultiQueryRetriever:
    """
    创建 Multi-Query Retriever
    
    将用户的单个查询扩展为多个不同表达的查询，然后对每个查询进行检索，
    最后合并结果。这样可以：
    - 缓解 query-answer 语义鸿沟
    - 提升检索召回率
    - 覆盖更多相关文档
    
    Args:
        retriever: 基础检索器（向量检索器）
        llm: LLM 模型实例，用于生成查询变体。如果为 None 则使用配置中的模型
        num_queries: 生成的查询数量（默认 3）
        model: 模型字符串（如 "openai:gpt-4o"），如果 llm 为 None 则使用此参数
        **kwargs: 其他参数（保留用于未来扩展）
    
    Returns:
        MultiQueryRetriever 实例
    
    Example:
        >>> from rag import load_vector_store, get_embeddings, create_retriever
        >>> from rag.retrievers import create_multi_query_retriever
        >>> 
        >>> # 创建基础检索器
        >>> embeddings = get_embeddings()
        >>> vector_store = load_vector_store("data/indexes/my_docs", embeddings)
        >>> base_retriever = create_retriever(vector_store, k=4)
        >>> 
        >>> # 创建 Multi-Query Retriever
        >>> multi_query_retriever = create_multi_query_retriever(
        ...     retriever=base_retriever,
        ...     num_queries=3
        ... )
        >>> 
        >>> # 使用检索器
        >>> docs = multi_query_retriever.invoke("什么是机器学习？")
        >>> print(f"检索到 {len(docs)} 个文档")
    """
    num_queries = num_queries or settings.multi_query_num_queries
    
    logger.info(f"🔄 创建 Multi-Query Retriever: num_queries={num_queries}")
    
    # 获取 LLM
    if llm is None:
        model_str = model or get_model_string()
        llm = get_chat_model(model_str)
    
    try:
        multi_query_retriever = MultiQueryRetriever(
            retriever=retriever,
            llm=llm,
            num_queries=num_queries,
            model=model,
        )
        
        logger.info("✅ Multi-Query Retriever 创建成功")
        return multi_query_retriever
        
    except Exception as e:
        logger.error(f"❌ 创建 Multi-Query Retriever 失败: {e}")
        raise

