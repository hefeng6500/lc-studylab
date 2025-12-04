"""
RRF Fusion 模块

实现 RRF (Reciprocal Rank Fusion) 算法，用于融合多个检索结果。

RRF 公式：
    RRF(d) = Σ(1 / (k + rank_i(d)))

其中：
- d 是文档
- rank_i(d) 是文档在第 i 个检索结果中的排名（从 1 开始）
- k 是常数（通常为 60）

参考：
- https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
"""

from typing import List, Dict, Optional
from langchain_core.documents import Document
from collections import defaultdict

from config import settings, get_logger

logger = get_logger(__name__)


def rrf_fusion(
    retrieval_results: List[List[Document]],
    k: Optional[int] = None,
    top_k: int = 10,
) -> List[Document]:
    """
    RRF 融合多个检索结果
    
    将多个检索结果按照 RRF 算法融合，返回排序后的文档列表。
    
    Args:
        retrieval_results: 多个检索结果列表，每个元素是一个文档列表
        k: RRF 常数（默认 60）
        top_k: 返回的 Top-K 文档数量
    
    Returns:
        融合后的文档列表（按 RRF 分数降序排列）
    
    Example:
        >>> from rag import create_retriever, create_bm25_retriever
        >>> from rag.retrievers import rrf_fusion
        >>> 
        >>> # 创建两个检索器
        >>> vector_retriever = create_retriever(vector_store, k=5)
        >>> bm25_retriever = create_bm25_retriever(documents, k=5)
        >>> 
        >>> # 执行检索
        >>> query = "什么是机器学习？"
        >>> vector_results = vector_retriever.invoke(query)
        >>> bm25_results = bm25_retriever.invoke(query)
        >>> 
        >>> # RRF 融合
        >>> fused_results = rrf_fusion(
        ...     [vector_results, bm25_results],
        ...     top_k=5
        ... )
    """
    k = k or settings.rrf_k
    
    logger.info(f"🔄 RRF 融合: {len(retrieval_results)} 个检索结果, k={k}, top_k={top_k}")
    
    if not retrieval_results:
        logger.warning("没有检索结果，返回空列表")
        return []
    
    # 使用文档的 page_content 和 metadata 作为唯一标识
    # 注意：这里假设相同内容的文档是同一个文档
    doc_scores: Dict[str, float] = defaultdict(float)
    doc_map: Dict[str, Document] = {}
    
    # 遍历每个检索结果
    for rank_list_idx, doc_list in enumerate(retrieval_results):
        if not doc_list:
            continue
        
        # 为每个文档计算 RRF 分数
        for rank, doc in enumerate(doc_list, start=1):
            # 使用 page_content 的前 100 个字符作为唯一标识
            # 实际应用中可以使用更可靠的唯一标识（如文档 ID）
            doc_key = doc.page_content[:100] if doc.page_content else str(id(doc))
            
            # 计算 RRF 分数
            rrf_score = 1.0 / (k + rank)
            doc_scores[doc_key] += rrf_score
            
            # 保存文档（如果还没有保存）
            if doc_key not in doc_map:
                doc_map[doc_key] = doc
    
    # 按 RRF 分数排序
    sorted_docs = sorted(
        doc_map.items(),
        key=lambda x: doc_scores[x[0]],
        reverse=True,
    )
    
    # 返回 Top-K
    result = [doc for _, doc in sorted_docs[:top_k]]
    
    logger.info(f"✅ RRF 融合完成: 返回 {len(result)} 个文档")
    
    # 记录前几个文档的分数
    if result:
        logger.debug("Top 3 文档的 RRF 分数:")
        for i, (doc_key, doc) in enumerate(sorted_docs[:3], 1):
            score = doc_scores[doc_key]
            logger.debug(f"   [{i}] Score: {score:.4f}, Content: {doc.page_content[:50]}...")
    
    return result


def rrf_fusion_with_scores(
    retrieval_results: List[List[Document]],
    k: Optional[int] = None,
    top_k: int = 10,
) -> List[tuple[Document, float]]:
    """
    RRF 融合多个检索结果，返回文档和分数
    
    Args:
        retrieval_results: 多个检索结果列表
        k: RRF 常数
        top_k: 返回的 Top-K 文档数量
    
    Returns:
        (Document, RRF_score) 元组列表
    """
    k = k or settings.rrf_k
    
    logger.info(f"🔄 RRF 融合（带分数）: {len(retrieval_results)} 个检索结果")
    
    if not retrieval_results:
        return []
    
    doc_scores: Dict[str, float] = defaultdict(float)
    doc_map: Dict[str, Document] = {}
    
    for doc_list in retrieval_results:
        if not doc_list:
            continue
        
        for rank, doc in enumerate(doc_list, start=1):
            doc_key = doc.page_content[:100] if doc.page_content else str(id(doc))
            rrf_score = 1.0 / (k + rank)
            doc_scores[doc_key] += rrf_score
            
            if doc_key not in doc_map:
                doc_map[doc_key] = doc
    
    sorted_docs = sorted(
        doc_map.items(),
        key=lambda x: doc_scores[x[0]],
        reverse=True,
    )
    
    result = [
        (doc_map[doc_key], doc_scores[doc_key])
        for doc_key, _ in sorted_docs[:top_k]
    ]
    
    logger.info(f"✅ RRF 融合完成: 返回 {len(result)} 个文档")
    
    return result



