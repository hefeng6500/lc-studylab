"""
BM25 Retriever 模块

实现基于关键词的 BM25 检索器，用于补充向量检索的不足。

参考：
- https://python.langchain.com/docs/modules/data_connection/retrievers/bm25
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

try:
    from langchain_community.retrievers import BM25Retriever
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    BM25Retriever = None

from config import get_logger

logger = get_logger(__name__)


def create_bm25_retriever(
    documents: List[Document],
    k: int = 4,
    **kwargs,
) -> BaseRetriever:
    """
    创建 BM25 检索器
    
    BM25 是一种基于关键词的检索算法，能够补充向量检索的不足：
    - 精确匹配关键词
    - 处理长文本匹配
    - 不依赖语义理解
    
    Args:
        documents: 文档列表（用于构建 BM25 索引）
        k: 返回的文档数量（默认 4）
        **kwargs: 其他传递给 BM25Retriever 的参数
    
    Returns:
        BM25Retriever 实例
    
    Raises:
        ImportError: 如果 langchain_community 未安装
    
    Example:
        >>> from rag import load_directory, split_documents
        >>> from rag.retrievers import create_bm25_retriever
        >>> 
        >>> # 加载和分块文档
        >>> documents = load_directory("data/documents")
        >>> chunks = split_documents(documents)
        >>> 
        >>> # 创建 BM25 检索器
        >>> bm25_retriever = create_bm25_retriever(chunks, k=4)
        >>> 
        >>> # 使用检索器
        >>> docs = bm25_retriever.invoke("机器学习")
        >>> print(f"检索到 {len(docs)} 个文档")
    """
    if not BM25_AVAILABLE:
        raise ImportError(
            "BM25Retriever 需要 langchain_community。"
            "请运行: pip install langchain-community"
        )
    
    logger.info(f"🔍 创建 BM25 检索器: documents={len(documents)}, k={k}")
    
    try:
        # 创建 BM25 检索器
        bm25_retriever = BM25Retriever.from_documents(
            documents=documents,
            **kwargs,
        )
        
        # 设置 k 参数
        bm25_retriever.k = k
        
        logger.info("✅ BM25 检索器创建成功")
        return bm25_retriever
        
    except Exception as e:
        logger.error(f"❌ 创建 BM25 检索器失败: {e}")
        raise


def create_bm25_retriever_from_texts(
    texts: List[str],
    metadatas: Optional[List[dict]] = None,
    k: int = 4,
    **kwargs,
) -> BaseRetriever:
    """
    从文本列表创建 BM25 检索器
    
    Args:
        texts: 文本列表
        metadatas: 元数据列表（可选）
        k: 返回的文档数量
        **kwargs: 其他参数
    
    Returns:
        BM25Retriever 实例
    
    Example:
        >>> texts = ["文档1内容", "文档2内容", "文档3内容"]
        >>> bm25_retriever = create_bm25_retriever_from_texts(texts, k=2)
    """
    if not BM25_AVAILABLE:
        raise ImportError(
            "BM25Retriever 需要 langchain_community。"
            "请运行: pip install langchain-community"
        )
    
    logger.info(f"🔍 从文本创建 BM25 检索器: texts={len(texts)}, k={k}")
    
    try:
        # 创建 BM25 检索器
        bm25_retriever = BM25Retriever.from_texts(
            texts=texts,
            metadatas=metadatas,
            **kwargs,
        )
        
        # 设置 k 参数
        bm25_retriever.k = k
        
        logger.info("✅ BM25 检索器创建成功")
        return bm25_retriever
        
    except Exception as e:
        logger.error(f"❌ 创建 BM25 检索器失败: {e}")
        raise


