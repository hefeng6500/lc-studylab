# Stage 1: Query Enhancement & Hybrid Retrieval

## 📋 阶段目标

实现查询增强和混合检索，提升基础检索能力：
- Multi-Query Retriever：将用户查询扩展为多个不同表达的查询
- HyDE（Hypothetical Document Embedding）：生成假设文档用于检索
- Query Rewriting：使用 LLM 重写查询
- Hybrid Retrieval：BM25 + Vector 混合检索
- RRF（Reciprocal Rank Fusion）：结果融合

## 🎯 核心功能

### 1. Query Enhancement（查询增强）

#### 1.1 Multi-Query Retriever

**功能描述**：
将用户的单个查询扩展为多个不同表达的查询，然后对每个查询进行检索，最后合并结果。这样可以：
- 缓解 query-answer 语义鸿沟
- 提升检索召回率
- 覆盖更多相关文档

**实现方案**：
使用 LangChain v1.0 的 `MultiQueryRetriever`，它使用 LLM 生成多个查询变体。

**代码结构**：
```python
# rag/query_enhancement.py
from langchain.retrievers import MultiQueryRetriever
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models.chat_models import BaseChatModel

def create_multi_query_retriever(
    base_retriever: BaseRetriever,
    llm: BaseChatModel,
    num_queries: int = 3,
) -> MultiQueryRetriever:
    """
    创建 Multi-Query Retriever
    
    Args:
        base_retriever: 基础检索器
        llm: 用于生成查询变体的 LLM
        num_queries: 生成的查询数量（默认 3）
    
    Returns:
        MultiQueryRetriever 实例
    """
    pass
```

**LangChain v1.0 API**：
```python
from langchain.retrievers import MultiQueryRetriever
```

#### 1.2 HyDE（Hypothetical Document Embedding）

**功能描述**：
使用 LLM 生成一个假设的答案文档，然后对这个假设文档进行 embedding，用于检索。这样可以：
- 让检索更接近答案的语义空间
- 提升检索精度

**实现方案**：
1. 使用 LLM 根据查询生成假设答案
2. 对假设答案进行 embedding
3. 使用假设答案的 embedding 进行检索

**代码结构**：
```python
# rag/retrievers/hyde_retriever.py
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

class HyDERetriever(BaseRetriever):
    """
    HyDE Retriever
    
    生成假设文档并用于检索
    """
    def __init__(
        self,
        base_retriever: BaseRetriever,
        llm: BaseChatModel,
        embeddings: Embeddings,
        hyde_prompt: Optional[str] = None,
    ):
        pass
    
    def _generate_hypothetical_document(self, query: str) -> str:
        """生成假设文档"""
        pass
    
    def invoke(self, query: str, **kwargs) -> List[Document]:
        """执行检索"""
        pass
```

#### 1.3 Query Rewriting

**功能描述**：
使用 LLM 重写用户查询，使其更专业、更准确、更适合检索。

**实现方案**：
使用 LangChain 的 `Runnable` 和 `PromptTemplate` 实现查询重写。

**代码结构**：
```python
# rag/query_enhancement.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

def rewrite_query(
    query: str,
    llm: BaseChatModel,
    context: Optional[str] = None,
) -> str:
    """
    重写查询
    
    Args:
        query: 原始查询
        llm: LLM 模型
        context: 可选上下文（如对话历史）
    
    Returns:
        重写后的查询
    """
    pass
```

### 2. Hybrid Retrieval（混合检索）

#### 2.1 BM25 Retriever

**功能描述**：
实现基于关键词的 BM25 检索，用于补充向量检索的不足。

**实现方案**：
使用 `langchain-community` 的 `BM25Retriever` 或 `rank_bm25` 库。

**代码结构**：
```python
# rag/retrievers/bm25_retriever.py
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

def create_bm25_retriever(
    documents: List[Document],
    k: int = 4,
) -> BM25Retriever:
    """
    创建 BM25 检索器
    
    Args:
        documents: 文档列表
        k: 返回的文档数量
    
    Returns:
        BM25Retriever 实例
    """
    pass
```

**LangChain v1.0 API**：
```python
from langchain_community.retrievers import BM25Retriever
```

#### 2.2 Hybrid Retriever

**功能描述**：
组合 BM25 和 Vector 检索器，使用 RRF 融合结果。

**实现方案**：
使用 LangChain 的 `EnsembleRetriever` 或自定义实现。

**代码结构**：
```python
# rag/retrievers/hybrid_retriever.py
from langchain.retrievers import EnsembleRetriever
from langchain_core.retrievers import BaseRetriever

def create_hybrid_retriever(
    vector_retriever: BaseRetriever,
    bm25_retriever: BaseRetriever,
    weights: List[float] = [0.5, 0.5],
) -> EnsembleRetriever:
    """
    创建混合检索器
    
    Args:
        vector_retriever: 向量检索器
        bm25_retriever: BM25 检索器
        weights: 权重列表 [vector_weight, bm25_weight]
    
    Returns:
        EnsembleRetriever 实例
    """
    pass
```

**LangChain v1.0 API**：
```python
from langchain.retrievers import EnsembleRetriever
```

#### 2.3 RRF Fusion（Reciprocal Rank Fusion）

**功能描述**：
实现 RRF 算法，融合多个检索结果。

**RRF 公式**：
```
RRF(d) = Σ(1 / (k + rank_i(d)))
```
其中：
- `d` 是文档
- `rank_i(d)` 是文档在第 i 个检索结果中的排名
- `k` 是常数（通常为 60）

**代码结构**：
```python
# rag/retrievers/rrf_fusion.py
from typing import List, Dict
from langchain_core.documents import Document

def rrf_fusion(
    retrieval_results: List[List[Document]],
    k: int = 60,
    top_k: int = 10,
) -> List[Document]:
    """
    RRF 融合多个检索结果
    
    Args:
        retrieval_results: 多个检索结果列表
        k: RRF 常数（默认 60）
        top_k: 返回的 Top-K 文档
    
    Returns:
        融合后的文档列表
    """
    pass
```

## 📁 文件结构

```
backend/rag/
├── query_enhancement.py          # 查询增强模块
├── retrievers/
│   ├── multi_query_retriever.py  # Multi-Query 检索器
│   ├── hyde_retriever.py         # HyDE 检索器
│   ├── bm25_retriever.py         # BM25 检索器
│   ├── hybrid_retriever.py       # 混合检索器
│   └── rrf_fusion.py             # RRF 融合算法
```

## 🧪 测试用例

### 1. Multi-Query Retriever 测试
```python
def test_multi_query_retriever():
    """测试 Multi-Query Retriever"""
    # 1. 创建基础检索器
    # 2. 创建 Multi-Query Retriever
    # 3. 执行查询
    # 4. 验证返回多个查询变体
    # 5. 验证检索结果合并
    pass
```

### 2. HyDE Retriever 测试
```python
def test_hyde_retriever():
    """测试 HyDE Retriever"""
    # 1. 创建 HyDE Retriever
    # 2. 执行查询
    # 3. 验证生成假设文档
    # 4. 验证检索结果
    pass
```

### 3. Hybrid Retriever 测试
```python
def test_hybrid_retriever():
    """测试混合检索器"""
    # 1. 创建 Vector 和 BM25 检索器
    # 2. 创建混合检索器
    # 3. 执行查询
    # 4. 验证结果融合
    pass
```

### 4. RRF Fusion 测试
```python
def test_rrf_fusion():
    """测试 RRF 融合"""
    # 1. 准备多个检索结果
    # 2. 执行 RRF 融合
    # 3. 验证排序正确性
    pass
```

## 📊 性能指标

### 目标指标
- **召回率提升**：20%+
- **精确率提升**：15%+
- **MRR 提升**：25%+

### 评估方法
1. 使用标准数据集（如 MS MARCO、Natural Questions）
2. 对比 Baseline（单一向量检索）
3. 记录各项指标变化

## 🔧 配置项

在 `config/settings.py` 中添加：

```python
# Query Enhancement 配置
query_enhancement_enabled: bool = Field(
    default=True,
    description="是否启用查询增强"
)

multi_query_num_queries: int = Field(
    default=3,
    ge=2,
    le=10,
    description="Multi-Query 生成的查询数量"
)

hyde_enabled: bool = Field(
    default=False,
    description="是否启用 HyDE"
)

# Hybrid Retrieval 配置
hybrid_retrieval_enabled: bool = Field(
    default=True,
    description="是否启用混合检索"
)

bm25_weight: float = Field(
    default=0.4,
    ge=0.0,
    le=1.0,
    description="BM25 检索权重"
)

vector_weight: float = Field(
    default=0.6,
    ge=0.0,
    le=1.0,
    description="向量检索权重"
)

rrf_k: int = Field(
    default=60,
    ge=1,
    description="RRF 常数 k"
)
```

## ✅ 验收标准

- [ ] Multi-Query Retriever 能够生成 3-5 个不同表达的查询
- [ ] HyDE Retriever 能够生成假设文档并用于检索
- [ ] Query Rewriting 能够提升查询质量
- [ ] BM25 Retriever 能够处理中文和英文
- [ ] Hybrid Retriever 能够融合 BM25 和 Vector 检索结果
- [ ] RRF 融合算法实现正确
- [ ] 召回率提升 20%+
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

## 📚 参考资料

- [LangChain Multi-Query Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/multi_query)
- [HyDE Paper](https://arxiv.org/abs/2212.10496)
- [RRF Algorithm](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [LangChain Ensemble Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/ensemble)

