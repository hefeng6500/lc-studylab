#!/usr/bin/env python3
"""
Stage 1 Advanced RAG 测试脚本

测试 Query Enhancement 和 Hybrid Retrieval 功能。

使用方法：
    python scripts/test_stage1_advanced_rag.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import setup_logging, get_logger
from rag import (
    IndexManager,
    load_directory,
    split_documents,
    get_embeddings,
    create_retriever,
    # Advanced RAG
    rewrite_query,
    generate_multi_queries,
    generate_hypothetical_document,
    create_multi_query_retriever,
    create_hyde_retriever,
    create_bm25_retriever,
    create_hybrid_retriever,
    rrf_fusion,
)

# 初始化日志
setup_logging()
logger = get_logger(__name__)


def test_query_enhancement():
    """测试查询增强功能"""
    print("\n" + "="*60)
    print("测试 1: Query Enhancement")
    print("="*60)
    
    query = "什么是机器学习？"
    
    # 1. Query Rewriting
    print(f"\n1. Query Rewriting:")
    print(f"   原始查询: {query}")
    try:
        rewritten = rewrite_query(query)
        print(f"   重写后: {rewritten}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 2. Multi-Query Generation
    print(f"\n2. Multi-Query Generation:")
    print(f"   原始查询: {query}")
    try:
        multi_queries = generate_multi_queries(query, num_queries=3)
        print(f"   生成了 {len(multi_queries)} 个查询变体:")
        for i, q in enumerate(multi_queries, 1):
            print(f"   [{i}] {q}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 3. HyDE
    print(f"\n3. HyDE (Hypothetical Document Embedding):")
    print(f"   原始查询: {query}")
    try:
        hyde_doc = generate_hypothetical_document(query)
        print(f"   假设文档: {hyde_doc[:200]}...")
    except Exception as e:
        print(f"   ❌ 失败: {e}")


def test_retrievers(index_name: str = "test_index"):
    """测试高级检索器"""
    print("\n" + "="*60)
    print("测试 2: Advanced Retrievers")
    print("="*60)
    
    # 检查索引是否存在
    manager = IndexManager()
    if not manager.index_exists(index_name):
        print(f"\n⚠️  索引不存在: {index_name}")
        print("   请先创建索引: python scripts/rag_cli.py index create test_index data/documents/test")
        return
    
    # 加载索引
    print(f"\n📂 加载索引: {index_name}")
    embeddings = get_embeddings()
    vector_store = manager.load_index(index_name, embeddings)
    
    # 创建基础检索器
    base_retriever = create_retriever(vector_store, k=3)
    
    query = "什么是机器学习？"
    print(f"\n🔍 查询: {query}")
    
    # 1. Multi-Query Retriever
    print(f"\n1. Multi-Query Retriever:")
    try:
        multi_query_retriever = create_multi_query_retriever(
            retriever=base_retriever,
            num_queries=3
        )
        docs = multi_query_retriever.invoke(query)
        print(f"   ✅ 检索到 {len(docs)} 个文档")
        for i, doc in enumerate(docs[:2], 1):
            print(f"   [{i}] {doc.page_content[:100]}...")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 2. HyDE Retriever
    print(f"\n2. HyDE Retriever:")
    try:
        hyde_retriever = create_hyde_retriever(base_retriever)
        docs = hyde_retriever.invoke(query)
        print(f"   ✅ 检索到 {len(docs)} 个文档")
        for i, doc in enumerate(docs[:2], 1):
            print(f"   [{i}] {doc.page_content[:100]}...")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 3. BM25 Retriever（需要文档列表）
    print(f"\n3. BM25 Retriever:")
    try:
        # 需要从向量库获取文档列表
        # 这里简化处理，实际应用中需要保存原始文档列表
        print("   ⚠️  BM25 Retriever 需要文档列表，跳过测试")
        print("   提示: 在实际应用中，需要保存原始文档列表用于 BM25 索引")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 4. Hybrid Retriever
    print(f"\n4. Hybrid Retriever:")
    try:
        # 创建 BM25 检索器需要文档列表，这里简化处理
        print("   ⚠️  Hybrid Retriever 需要 BM25 检索器，跳过测试")
        print("   提示: 需要先创建 BM25 检索器")
    except Exception as e:
        print(f"   ❌ 失败: {e}")


def test_rrf_fusion():
    """测试 RRF 融合"""
    print("\n" + "="*60)
    print("测试 3: RRF Fusion")
    print("="*60)
    
    # 模拟两个检索结果
    from langchain_core.documents import Document
    
    doc1 = Document(page_content="机器学习是人工智能的一个分支")
    doc2 = Document(page_content="深度学习是机器学习的一个子领域")
    doc3 = Document(page_content="神经网络是深度学习的核心技术")
    doc4 = Document(page_content="机器学习算法包括监督学习和无监督学习")
    
    retrieval_results = [
        [doc1, doc2, doc3],  # 第一个检索结果
        [doc2, doc4, doc1],  # 第二个检索结果
    ]
    
    print(f"\n输入: {len(retrieval_results)} 个检索结果")
    for i, results in enumerate(retrieval_results, 1):
        print(f"   检索结果 {i}: {len(results)} 个文档")
    
    try:
        fused_results = rrf_fusion(
            retrieval_results=retrieval_results,
            top_k=5
        )
        print(f"\n✅ RRF 融合完成: 返回 {len(fused_results)} 个文档")
        for i, doc in enumerate(fused_results, 1):
            print(f"   [{i}] {doc.page_content[:80]}...")
    except Exception as e:
        print(f"   ❌ 失败: {e}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("Stage 1 Advanced RAG 测试")
    print("="*60)
    
    # 测试查询增强
    test_query_enhancement()
    
    # 测试检索器（需要索引）
    test_retrievers()
    
    # 测试 RRF 融合
    test_rrf_fusion()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

