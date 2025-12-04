# Stage 2: Re-ranking & Context Compression

## 📋 阶段目标

实现重排序和上下文压缩，提升检索精度：
- Cross-encoder Re-ranking（Cohere、bge-reranker）
- LLM-as-Reranker（使用 GPT-4o 进行重排序）
- Context Compression（上下文压缩）
- Document Compressor Pipeline（文档压缩管道）

## 🎯 核心功能

### 1. Re-ranking（重排序）

#### 1.1 Cross-encoder Reranker

**功能描述**：
使用 Cross-encoder 模型对检索结果进行重排序，提升检索精度。

**支持的 Reranker**：
- Cohere Rerank（推荐）
- bge-reranker（开源）
- LLM-as-Reranker（GPT-4o）

**实现方案**：
使用 LangChain 的 `ContextualCompressionRetriever` 和 `CohereRerank`。

**代码结构**：
```python
# rag/retrievers/reranker.py
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain_core.retrievers import BaseRetriever

def create_reranker_retriever(
    base_retriever: BaseRetriever,
    reranker_type: str = "cohere",
    top_n: int = 3,
    **kwargs,
) -> ContextualCompressionRetriever:
    """
    创建带重排序的检索器
    
    Args:
        base_retriever: 基础检索器
        reranker_type: Reranker 类型（cohere, bge, llm）
        top_n: 重排序后的 Top-N 文档
        **kwargs: 其他参数
    
    Returns:
        ContextualCompressionRetriever 实例
    """
    pass
```

**LangChain v1.0 API**：
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
```

#### 1.2 Cohere Reranker

**功能描述**：
使用 Cohere 的 Rerank API 进行重排序。

**代码结构**：
```python
# rag/retrievers/cohere_reranker.py
from langchain_cohere import CohereRerank

def create_cohere_reranker(
    model: str = "rerank-english-v3.0",
    top_n: int = 3,
) -> CohereRerank:
    """
    创建 Cohere Reranker
    
    Args:
        model: Cohere Rerank 模型
        top_n: Top-N 文档
    
    Returns:
        CohereRerank 实例
    """
    pass
```

#### 1.3 LLM-as-Reranker

**功能描述**：
使用 LLM（如 GPT-4o）对检索结果进行重排序。

**实现方案**：
1. 将查询和文档对输入 LLM
2. LLM 输出相关性分数
3. 根据分数排序

**代码结构**：
```python
# rag/retrievers/llm_reranker.py
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.documents import Document

class LLMReranker:
    """
    LLM-as-Reranker
    
    使用 LLM 对检索结果进行重排序
    """
    def __init__(
        self,
        llm: BaseChatModel,
        top_n: int = 3,
    ):
        pass
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
    ) -> List[Document]:
        """重排序文档"""
        pass
```

### 2. Context Compression（上下文压缩）

#### 2.1 LLMChainExtractor

**功能描述**：
使用 LLM 提取文档中与查询相关的片段。

**实现方案**：
使用 LangChain 的 `LLMChainExtractor`。

**代码结构**：
```python
# rag/retrievers/context_compression.py
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_core.retrievers import BaseRetriever

def create_llm_extractor_retriever(
    base_retriever: BaseRetriever,
    llm: BaseChatModel,
) -> ContextualCompressionRetriever:
    """
    创建 LLM 提取器检索器
    
    Args:
        base_retriever: 基础检索器
        llm: LLM 模型
    
    Returns:
        ContextualCompressionRetriever 实例
    """
    pass
```

**LangChain v1.0 API**：
```python
from langchain.retrievers.document_compressors import LLMChainExtractor
```

#### 2.2 EmbeddingsFilter

**功能描述**：
基于相似度过滤文档，只保留高相关度的文档。

**代码结构**：
```python
# rag/retrievers/context_compression.py
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain_core.embeddings import Embeddings

def create_embeddings_filter_retriever(
    base_retriever: BaseRetriever,
    embeddings: Embeddings,
    similarity_threshold: float = 0.7,
) -> ContextualCompressionRetriever:
    """
    创建 Embeddings Filter 检索器
    
    Args:
        base_retriever: 基础检索器
        embeddings: Embedding 模型
        similarity_threshold: 相似度阈值
    
    Returns:
        ContextualCompressionRetriever 实例
    """
    pass
```

#### 2.3 DocumentCompressorPipeline

**功能描述**：
组合多个压缩器，形成压缩管道。

**代码结构**：
```python
# rag/retrievers/context_compression.py
from langchain.retrievers.document_compressors import DocumentCompressorPipeline

def create_compression_pipeline_retriever(
    base_retriever: BaseRetriever,
    compressors: List[BaseDocumentCompressor],
) -> ContextualCompressionRetriever:
    """
    创建压缩管道检索器
    
    Args:
        base_retriever: 基础检索器
        compressors: 压缩器列表
    
    Returns:
        ContextualCompressionRetriever 实例
    """
    pass
```

**LangChain v1.0 API**：
```python
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
```

## 📁 文件结构

```
backend/rag/
├── retrievers/
│   ├── reranker.py              # 重排序模块
│   ├── cohere_reranker.py       # Cohere Reranker
│   ├── llm_reranker.py          # LLM Reranker
│   ├── context_compression.py   # 上下文压缩
│   └── document_compressors.py  # 文档压缩器集合
```

## 🧪 测试用例

### 1. Re-ranking 测试
```python
def test_reranker():
    """测试重排序"""
    # 1. 创建基础检索器
    # 2. 创建 Reranker
    # 3. 执行查询
    # 4. 验证重排序结果
    # 5. 验证精度提升
    pass
```

### 2. Context Compression 测试
```python
def test_context_compression():
    """测试上下文压缩"""
    # 1. 创建基础检索器
    # 2. 创建压缩器
    # 3. 执行查询
    # 4. 验证压缩效果
    # 5. 验证质量保持
    pass
```

## 📊 性能指标

### 目标指标
- **检索错误率降低**：30-60%
- **精确率提升**：20-40%
- **上下文压缩率**：50%+（减少无关内容）
- **质量保持率**：> 95%（压缩后质量不下降）

### 评估方法
1. 使用标准数据集评估
2. 对比 Baseline（无重排序、无压缩）
3. 记录各项指标变化

## 🔧 配置项

在 `config/settings.py` 中添加：

```python
# Re-ranking 配置
reranking_enabled: bool = Field(
    default=True,
    description="是否启用重排序"
)

reranker_type: str = Field(
    default="cohere",
    description="Reranker 类型（cohere, bge, llm）"
)

reranker_top_n: int = Field(
    default=3,
    ge=1,
    le=20,
    description="重排序后的 Top-N 文档"
)

cohere_api_key: str = Field(
    default="",
    description="Cohere API Key（用于 Reranker）"
)

# Context Compression 配置
context_compression_enabled: bool = Field(
    default=True,
    description="是否启用上下文压缩"
)

compression_type: str = Field(
    default="llm_extractor",
    description="压缩类型（llm_extractor, embeddings_filter, pipeline）"
)

similarity_threshold: float = Field(
    default=0.7,
    ge=0.0,
    le=1.0,
    description="相似度阈值（用于 EmbeddingsFilter）"
)
```

## ✅ 验收标准

- [ ] Re-ranking 能够将检索错误率降低 30-60%
- [ ] 支持多种 Reranker（Cohere、bge、LLM）
- [ ] Context Compression 能够减少 50%+ 的无关内容
- [ ] 支持多种压缩策略组合
- [ ] 压缩后的上下文质量不下降（> 95%）
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

## 📚 参考资料

- [LangChain Contextual Compression](https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression)
- [Cohere Rerank](https://docs.cohere.com/docs/reranking)
- [bge-reranker](https://github.com/FlagOpen/FlagEmbedding)



