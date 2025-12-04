"""
Advanced Retrievers 模块

提供高级检索器实现，包括：
- Multi-Query Retriever：多查询检索器
- HyDE Retriever：假设文档检索器
- BM25 Retriever：关键词检索器
- Hybrid Retriever：混合检索器
- RRF Fusion：结果融合算法

同时重新导出基础检索器（从 rag/retrievers.py）

参考：
- https://docs.langchain.com/oss/python/langchain/retrieval
"""

# 重新导出基础检索器（从 rag/retrievers.py）
# 注意：由于 Python 的模块导入机制，rag/retrievers.py 会被 rag/retrievers/ 目录覆盖
# 所以我们需要通过 importlib 导入
import importlib.util
import sys
from pathlib import Path

# 动态导入 rag/retrievers.py
_retrievers_file = Path(__file__).parent.parent / "retrievers.py"
if _retrievers_file.exists():
    _spec = importlib.util.spec_from_file_location("rag.base_retrievers", _retrievers_file)
    _base_retrievers = importlib.util.module_from_spec(_spec)
    sys.modules["rag.base_retrievers"] = _base_retrievers
    _spec.loader.exec_module(_base_retrievers)
    
    # 重新导出基础检索器
    create_retriever = _base_retrievers.create_retriever
    create_retriever_tool = _base_retrievers.create_retriever_tool
else:
    # 如果文件不存在，提供占位符
    def create_retriever(*args, **kwargs):
        raise ImportError("rag/retrievers.py 文件不存在")
    
    def create_retriever_tool(*args, **kwargs):
        raise ImportError("rag/retrievers.py 文件不存在")

# Advanced Retrievers
from rag.retrievers.multi_query_retriever import create_multi_query_retriever, MultiQueryRetriever
from rag.retrievers.hyde_retriever import create_hyde_retriever, HyDERetriever
from rag.retrievers.bm25_retriever import (
    create_bm25_retriever,
    create_bm25_retriever_from_texts,
)
from rag.retrievers.hybrid_retriever import (
    create_hybrid_retriever,
    create_rrf_retriever,
    RRFFusionRetriever,
)
from rag.retrievers.rrf_fusion import (
    rrf_fusion,
    rrf_fusion_with_scores,
)

__all__ = [
    # 基础检索器（重新导出）
    "create_retriever",
    "create_retriever_tool",
    # Multi-Query Retriever
    "create_multi_query_retriever",
    "MultiQueryRetriever",
    # HyDE Retriever
    "create_hyde_retriever",
    "HyDERetriever",
    # BM25 Retriever
    "create_bm25_retriever",
    "create_bm25_retriever_from_texts",
    # Hybrid Retriever
    "create_hybrid_retriever",
    "create_rrf_retriever",
    "RRFFusionRetriever",
    # RRF Fusion
    "rrf_fusion",
    "rrf_fusion_with_scores",
]

