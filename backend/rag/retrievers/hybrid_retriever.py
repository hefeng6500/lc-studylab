"""
Hybrid Retriever 模块

实现混合检索器，组合 BM25 和 Vector 检索器，使用 RRF 或加权融合结果。

参考：
- https://python.langchain.com/docs/modules/data_connection/retrievers/ensemble
"""

from typing import List, Optional, Literal
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

from config import settings, get_logger
from rag.retrievers.rrf_fusion import rrf_fusion

logger = get_logger(__name__)

# 尝试导入 EnsembleRetriever
try:
    from langchain.retrievers import EnsembleRetriever
    ENSEMBLE_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.retrievers import EnsembleRetriever
        ENSEMBLE_AVAILABLE = True
    except ImportError:
        ENSEMBLE_AVAILABLE = False
        EnsembleRetriever = None


def create_hybrid_retriever(
    vector_retriever: BaseRetriever,
    bm25_retriever: BaseRetriever,
    fusion_method: Literal["ensemble", "rrf"] = "ensemble",
    weights: Optional[List[float]] = None,
    rrf_k: Optional[int] = None,
    top_k: int = 10,
) -> BaseRetriever:
    """
    创建混合检索器
    
    组合 BM25 和 Vector 检索器，使用 Ensemble 或 RRF 融合结果。
    
    Args:
        vector_retriever: 向量检索器
        bm25_retriever: BM25 检索器
        fusion_method: 融合方法
            - "ensemble": 使用 LangChain 的 EnsembleRetriever（加权融合）
            - "rrf": 使用 RRF 融合算法
        weights: 权重列表 [vector_weight, bm25_weight]，仅用于 ensemble 方法
        rrf_k: RRF 常数 k，仅用于 rrf 方法
        top_k: 返回的 Top-K 文档数量
    
    Returns:
        混合检索器实例
    
    Example:
        >>> from rag import create_retriever, create_bm25_retriever
        >>> from rag.retrievers import create_hybrid_retriever
        >>> 
        >>> # 创建两个检索器
        >>> vector_retriever = create_retriever(vector_store, k=5)
        >>> bm25_retriever = create_bm25_retriever(documents, k=5)
        >>> 
        >>> # 创建混合检索器（使用 Ensemble）
        >>> hybrid_retriever = create_hybrid_retriever(
        ...     vector_retriever=vector_retriever,
        ...     bm25_retriever=bm25_retriever,
        ...     fusion_method="ensemble",
        ...     weights=[0.6, 0.4]
        ... )
        >>> 
        >>> # 或使用 RRF
        >>> hybrid_retriever = create_hybrid_retriever(
        ...     vector_retriever=vector_retriever,
        ...     bm25_retriever=bm25_retriever,
        ...     fusion_method="rrf",
        ...     top_k=5
        ... )
    """
    logger.info(f"🔗 创建混合检索器: fusion_method={fusion_method}")
    
    if fusion_method == "ensemble":
        # 使用 LangChain 的 EnsembleRetriever（如果可用）
        if not ENSEMBLE_AVAILABLE:
            logger.warning("EnsembleRetriever 不可用，使用 RRF 融合")
            fusion_method = "rrf"
        else:
            weights = weights or [settings.vector_weight, settings.bm25_weight]
            
            # 归一化权重
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            logger.info(f"   权重: vector={weights[0]:.2f}, bm25={weights[1]:.2f}")
            
            try:
                hybrid_retriever = EnsembleRetriever(
                    retrievers=[vector_retriever, bm25_retriever],
                    weights=weights,
                )
                
                logger.info("✅ 混合检索器创建成功（Ensemble）")
                return hybrid_retriever
                
            except Exception as e:
                logger.error(f"❌ 创建混合检索器失败: {e}")
                logger.warning("回退到 RRF 融合")
                fusion_method = "rrf"
    
    elif fusion_method == "rrf":
        # 使用 RRF 融合
        return RRFFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            rrf_k=rrf_k,
            top_k=top_k,
        )
    
    else:
        raise ValueError(
            f"未知的融合方法: {fusion_method}。"
            f"支持的方法: ensemble, rrf"
        )


class RRFFusionRetriever(BaseRetriever):
    """
    RRF 融合检索器
    
    使用 RRF 算法融合多个检索器的结果。
    """
    
    def __init__(
        self,
        retrievers: List[BaseRetriever],
        rrf_k: Optional[int] = None,
        top_k: int = 10,
    ):
        """
        初始化 RRF 融合检索器
        
        Args:
            retrievers: 检索器列表
            rrf_k: RRF 常数 k
            top_k: 返回的 Top-K 文档数量
        """
        super().__init__()
        self.retrievers = retrievers
        self.rrf_k = rrf_k or settings.rrf_k
        self.top_k = top_k
    
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
        logger.info(f"🔍 RRF 融合检索: {query[:50]}...")
        
        try:
            # 1. 使用每个检索器进行检索
            retrieval_results = []
            for retriever in self.retrievers:
                docs = retriever.invoke(query, run_manager=run_manager, **kwargs)
                retrieval_results.append(docs)
            
            # 2. RRF 融合
            fused_docs = rrf_fusion(
                retrieval_results=retrieval_results,
                k=self.rrf_k,
                top_k=self.top_k,
            )
            
            logger.info(f"✅ RRF 融合检索完成: 找到 {len(fused_docs)} 个文档")
            return fused_docs
            
        except Exception as e:
            logger.error(f"❌ RRF 融合检索失败: {e}")
            # 如果失败，返回第一个检索器的结果
            if self.retrievers:
                return self.retrievers[0].invoke(
                    query,
                    run_manager=run_manager,
                    **kwargs,
                )
            return []
    
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


def create_rrf_retriever(
    retrievers: List[BaseRetriever],
    rrf_k: Optional[int] = None,
    top_k: int = 10,
) -> RRFFusionRetriever:
    """
    创建 RRF 融合检索器的便捷函数
    
    Args:
        retrievers: 检索器列表
        rrf_k: RRF 常数 k
        top_k: 返回的 Top-K 文档数量
    
    Returns:
        RRFFusionRetriever 实例
    """
    return RRFFusionRetriever(
        retrievers=retrievers,
        rrf_k=rrf_k,
        top_k=top_k,
    )

