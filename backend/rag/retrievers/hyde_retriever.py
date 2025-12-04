"""
HyDE Retriever 模块

实现 HyDE (Hypothetical Document Embedding) Retriever。
使用 LLM 生成假设的答案文档，然后对这个假设文档进行 embedding，用于检索。

参考：
- https://arxiv.org/abs/2212.10496
"""

from typing import List, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from config import settings, get_logger
from core.models import get_chat_model, get_model_string
from rag.query_enhancement import generate_hypothetical_document
from rag.embeddings import get_embeddings as get_embeddings_model

logger = get_logger(__name__)


class HyDERetriever(BaseRetriever):
    """
    HyDE Retriever
    
    生成假设文档并用于检索的检索器。
    """
    
    def __init__(
        self,
        base_retriever: BaseRetriever,
        llm: Optional[BaseChatModel] = None,
        embeddings: Optional[Embeddings] = None,
        model: Optional[str] = None,
    ):
        """
        初始化 HyDE Retriever
        
        Args:
            base_retriever: 基础检索器（向量检索器）
            llm: LLM 模型实例，用于生成假设文档
            embeddings: Embedding 模型，用于对假设文档进行向量化
            model: 模型字符串
        """
        super().__init__()
        self.base_retriever = base_retriever
        self.llm = llm
        self.embeddings = embeddings
        self.model = model
        
        # 如果没有提供 LLM，使用配置中的模型
        if self.llm is None:
            model_str = model or get_model_string()
            self.llm = get_chat_model(model_str)
        
        # 如果没有提供 Embeddings，使用配置中的模型
        if self.embeddings is None:
            self.embeddings = get_embeddings_model()
    
    def _generate_hypothetical_document(self, query: str) -> str:
        """
        生成假设文档
        
        Args:
            query: 用户查询
        
        Returns:
            假设文档内容
        """
        return generate_hypothetical_document(
            query=query,
            llm=self.llm,
            model=self.model,
        )
    
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
        logger.info(f"🔍 HyDE 检索: {query[:50]}...")
        
        try:
            # 1. 生成假设文档
            hypothetical_doc = self._generate_hypothetical_document(query)
            logger.debug(f"   假设文档: {hypothetical_doc[:100]}...")
            
            # 2. 使用假设文档进行检索
            # 注意：这里我们使用假设文档的 embedding 进行检索
            # 由于 base_retriever 是基于向量检索的，我们需要将假设文档转换为查询向量
            # 但实际上，我们可以直接使用假设文档作为查询字符串
            # 因为向量检索器会自动对查询进行 embedding
            
            # 使用假设文档作为查询
            docs = self.base_retriever.invoke(
                hypothetical_doc,
                run_manager=run_manager,
                **kwargs,
            )
            
            logger.info(f"✅ HyDE 检索完成: 找到 {len(docs)} 个文档")
            return docs
            
        except Exception as e:
            logger.error(f"❌ HyDE 检索失败: {e}")
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


def create_hyde_retriever(
    base_retriever: BaseRetriever,
    llm: Optional[BaseChatModel] = None,
    embeddings: Optional[Embeddings] = None,
    model: Optional[str] = None,
) -> HyDERetriever:
    """
    创建 HyDE Retriever 的便捷函数
    
    Args:
        base_retriever: 基础检索器
        llm: LLM 模型实例
        embeddings: Embedding 模型
        model: 模型字符串
    
    Returns:
        HyDERetriever 实例
    
    Example:
        >>> from rag import load_vector_store, get_embeddings, create_retriever
        >>> from rag.retrievers import create_hyde_retriever
        >>> 
        >>> # 创建基础检索器
        >>> embeddings = get_embeddings()
        >>> vector_store = load_vector_store("data/indexes/my_docs", embeddings)
        >>> base_retriever = create_retriever(vector_store, k=4)
        >>> 
        >>> # 创建 HyDE Retriever
        >>> hyde_retriever = create_hyde_retriever(base_retriever)
        >>> 
        >>> # 使用检索器
        >>> docs = hyde_retriever.invoke("什么是机器学习？")
    """
    logger.info("📝 创建 HyDE Retriever")
    
    return HyDERetriever(
        base_retriever=base_retriever,
        llm=llm,
        embeddings=embeddings,
        model=model,
    )



