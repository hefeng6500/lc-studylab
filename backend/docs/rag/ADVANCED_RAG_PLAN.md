# Advanced RAG 实现计划

## 📋 项目概述

本项目旨在构建一个**企业级 Advanced RAG 系统**，基于 LangChain v1.0，适用于处理多种类型的通用文档，包括：

- **技术文档**：API 文档、技术规范、代码文档
- **知识库**：FAQ、知识库、Wiki
- **法律文档**：合同、法规、案例
- **医疗报告**：病历、诊断报告、医学文献
- **格式支持**：PDF（含扫描件）、图片（OCR）、Markdown、HTML、Word 等

## 🎯 核心目标

1. **高精度检索**：通过 Hybrid Retrieval + Re-ranking 提升检索准确率
2. **多模态支持**：支持文本、图片、表格的联合检索和理解
3. **智能上下文管理**：Context Compression、Parent Document、Multi-vector 等技术
4. **Agentic RAG**：让 LLM 主动检索、验证、推理
5. **生产级可用**：完善的错误处理、监控、评估体系

## 📚 技术栈

- **框架**：LangChain v1.0.3
- **向量库**：FAISS（本地）、Chroma（可选）、Pinecone（云端可选）
- **Embedding**：OpenAI text-embedding-3-large、多模态 CLIP
- **Reranking**：Cohere Rerank、bge-reranker、LLM-as-reranker
- **OCR**：Tesseract、PaddleOCR、Unstructured
- **PDF 处理**：PyMuPDF、pdfplumber、Unstructured
- **图像处理**：Pillow、OpenCV

---

## 🗺️ 分阶段实现计划

### Stage 1: 基础增强 - Query Enhancement & Hybrid Retrieval

**目标**：实现查询增强和混合检索，提升基础检索能力

**时间估算**：1-2 周

#### 1.1 Query Enhancement（查询增强）

**功能**：
- Multi-Query Retriever：将用户查询扩展为多个不同表达的查询
- HyDE（Hypothetical Document Embedding）：生成假设文档用于检索
- Query Rewriting：使用 LLM 重写查询，使其更专业、更准确

**实现文件**：
- `rag/query_enhancement.py`：查询增强模块
- `rag/retrievers/multi_query_retriever.py`：Multi-Query 检索器
- `rag/retrievers/hyde_retriever.py`：HyDE 检索器

**LangChain v1.0 API**：
```python
from langchain.retrievers import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
```

**验收标准**：
- [ ] Multi-Query Retriever 能够生成 3-5 个不同表达的查询
- [ ] HyDE 能够生成假设文档并用于检索
- [ ] 查询重写功能能够提升检索召回率 20%+

#### 1.2 Hybrid Retrieval（混合检索）

**功能**：
- BM25 关键词检索（使用 `rank_bm25` 或 `langchain-community`）
- Dense Vector Retrieval（现有）
- Sparse + Dense 混合检索
- RRF（Reciprocal Rank Fusion）结果融合

**实现文件**：
- `rag/retrievers/hybrid_retriever.py`：混合检索器
- `rag/retrievers/bm25_retriever.py`：BM25 检索器
- `rag/retrievers/rrf_fusion.py`：RRF 融合算法

**LangChain v1.0 API**：
```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
```

**验收标准**：
- [ ] BM25 检索器能够处理中文和英文
- [ ] Hybrid Retriever 能够融合 BM25 和 Vector 检索结果
- [ ] RRF 融合能够提升检索质量 15%+

---

### Stage 2: 高级检索 - Re-ranking & Context Compression

**目标**：实现重排序和上下文压缩，提升检索精度

**时间估算**：1-2 周

#### 2.1 Re-ranking（重排序）

**功能**：
- Cross-encoder Re-ranking（使用 Cohere、bge-reranker）
- LLM-as-Reranker（使用 GPT-4o 进行重排序）
- 可配置的 Top-K 重排序

**实现文件**：
- `rag/retrievers/reranker.py`：重排序模块
- `rag/retrievers/cohere_reranker.py`：Cohere Reranker
- `rag/retrievers/llm_reranker.py`：LLM Reranker

**LangChain v1.0 API**：
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_cohere import CohereRerank
```

**验收标准**：
- [ ] Re-ranking 能够将检索错误率降低 30-60%
- [ ] 支持多种 Reranker（Cohere、bge、LLM）
- [ ] 可配置重排序的 Top-K 数量

#### 2.2 Context Compression（上下文压缩）

**功能**：
- LLMChainExtractor：使用 LLM 提取相关片段
- EmbeddingsFilter：基于相似度过滤
- DocumentCompressorPipeline：组合多个压缩器
- 去冗余、去噪声

**实现文件**：
- `rag/retrievers/context_compression.py`：上下文压缩模块
- `rag/retrievers/document_compressors.py`：文档压缩器集合

**LangChain v1.0 API**：
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    LLMChainExtractor,
    EmbeddingsFilter,
    DocumentCompressorPipeline,
)
```

**验收标准**：
- [ ] Context Compression 能够减少 50%+ 的无关内容
- [ ] 支持多种压缩策略组合
- [ ] 压缩后的上下文质量不下降

---

### Stage 3: 多粒度检索 - Parent Document & Multi-vector

**目标**：实现多粒度检索，支持 chunk 和 parent document 的层次检索

**时间估算**：1-2 周

#### 3.1 Parent Document Retriever（父文档检索器）

**功能**：
- 小 chunk 用于检索，返回完整的 parent document
- 支持多层次的文档结构（section → chapter → document）
- 保留文档的完整上下文

**实现文件**：
- `rag/retrievers/parent_document_retriever.py`：父文档检索器
- `rag/splitters/hierarchical_splitter.py`：层次化分块器

**LangChain v1.0 API**：
```python
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

**验收标准**：
- [ ] Parent Document Retriever 能够返回完整的父文档
- [ ] 支持多层次的文档结构
- [ ] 检索精度提升 10%+

#### 3.2 Multi-vector Retriever（多向量检索器）

**功能**：
- 为同一文档生成多个向量表示（摘要、问题、关键词等）
- 支持多种向量表示方式的融合检索
- 提升检索的多样性和准确性

**实现文件**：
- `rag/retrievers/multi_vector_retriever.py`：多向量检索器
- `rag/embeddings/multi_embedding.py`：多向量生成

**LangChain v1.0 API**：
```python
from langchain.retrievers import MultiVectorRetriever
from langchain_core.documents import Document
```

**验收标准**：
- [ ] Multi-vector Retriever 能够为文档生成多种向量表示
- [ ] 支持摘要、问题、关键词等多种表示方式
- [ ] 检索召回率提升 15%+

---

### Stage 4: 多模态 RAG - Image & PDF OCR

**目标**：支持图片和扫描 PDF 的 OCR，实现多模态检索

**时间估算**：2-3 周

#### 4.1 PDF OCR & 结构化提取

**功能**：
- PDF 文本提取（PyMuPDF、pdfplumber）
- 扫描 PDF OCR（Tesseract、PaddleOCR）
- 表格结构化提取（Unstructured、Camelot）
- 公式识别和保留
- 版式恢复（Layout Analysis）

**实现文件**：
- `rag/loaders/pdf_loader.py`：PDF 加载器增强
- `rag/loaders/pdf_ocr.py`：PDF OCR 模块
- `rag/loaders/table_extractor.py`：表格提取器
- `rag/loaders/layout_analyzer.py`：版式分析器

**依赖库**：
```bash
pip install pymupdf pdfplumber pytesseract paddleocr unstructured
```

**验收标准**：
- [ ] 能够处理扫描 PDF 并提取文本
- [ ] 能够提取和结构化表格
- [ ] 能够识别和保留公式
- [ ] 版式恢复准确率 > 90%

#### 4.2 Image OCR & 多模态 Embedding

**功能**：
- 图片 OCR（Tesseract、PaddleOCR、EasyOCR）
- 多模态 Embedding（CLIP、OpenAI CLIP）
- 图片 + 文本联合检索
- 图片描述生成（用于检索）

**实现文件**：
- `rag/loaders/image_loader.py`：图片加载器
- `rag/loaders/image_ocr.py`：图片 OCR 模块
- `rag/embeddings/multimodal_embeddings.py`：多模态 Embedding
- `rag/retrievers/multimodal_retriever.py`：多模态检索器

**LangChain v1.0 API**：
```python
from langchain_community.document_loaders import ImageCaptionLoader
from langchain_openai import OpenAIEmbeddings
```

**验收标准**：
- [ ] 能够对图片进行 OCR 并提取文本
- [ ] 多模态 Embedding 能够同时处理文本和图片
- [ ] 图片 + 文本联合检索准确率 > 85%

---

### Stage 5: Agentic RAG - 主动检索与推理

**目标**：实现 Agentic RAG，让 LLM 主动检索、验证、推理

**时间估算**：2-3 周

#### 5.1 Self-RAG（自我增强 RAG）

**功能**：
- LLM 自主决定何时检索
- 自主决定检索哪些内容
- 自主决定检索次数
- 自主验证检索结果的质量

**实现文件**：
- `rag/agents/self_rag.py`：Self-RAG Agent
- `rag/agents/retrieval_decision.py`：检索决策模块

**LangChain v1.0 API**：
```python
from langchain.agents import create_agent
from langchain_core.tools import Tool
```

**验收标准**：
- [ ] Self-RAG 能够自主决定检索时机
- [ ] 能够自主验证检索结果
- [ ] 检索效率提升 20%+

#### 5.2 Corrective RAG（纠正性 RAG）

**功能**：
- 生成后的事实验证
- 交叉验证多个检索片段
- 检查引用来源的一致性
- 自动纠正错误信息

**实现文件**：
- `rag/agents/corrective_rag.py`：Corrective RAG Agent
- `rag/agents/fact_checker.py`：事实检查器

**验收标准**：
- [ ] Corrective RAG 能够检测和纠正错误
- [ ] 事实准确率提升 30%+
- [ ] 支持多源交叉验证

#### 5.3 Agentic RAG with Tool Calling

**功能**：
- 多轮检索和验证循环
- 工具调用（SQL、API、文件系统）
- 任务分解和规划
- 结果合并和总结

**实现文件**：
- `rag/agents/agentic_rag.py`：Agentic RAG Agent
- `rag/agents/task_planner.py`：任务规划器

**LangChain v1.0 API**：
```python
from langchain.agents import create_agent
from langchain_core.tools import Tool
```

**验收标准**：
- [ ] Agentic RAG 能够执行多轮检索
- [ ] 能够调用外部工具
- [ ] 能够分解复杂任务
- [ ] 任务完成率 > 90%

---

### Stage 6: 评估与优化 - Evaluation & Monitoring

**目标**：建立完善的评估和监控体系

**时间估算**：1-2 周

#### 6.1 RAG 评估体系

**功能**：
- 检索质量评估（Recall、Precision、MRR、NDCG）
- 生成质量评估（Faithfulness、Answer Relevance、Context Precision）
- 端到端评估（Answer Correctness、Answer Similarity）
- 使用 LangSmith 进行追踪

**实现文件**：
- `rag/evaluation/retrieval_metrics.py`：检索指标
- `rag/evaluation/generation_metrics.py`：生成指标
- `rag/evaluation/end_to_end_metrics.py`：端到端指标

**LangChain v1.0 API**：
```python
from langchain.evaluation import (
    QAEvalChain,
    ContextQAEvalChain,
)
from langchain.smith import RunEvaluator
```

**验收标准**：
- [ ] 能够评估检索质量
- [ ] 能够评估生成质量
- [ ] 能够进行端到端评估
- [ ] 集成 LangSmith 追踪

#### 6.2 性能监控与优化

**功能**：
- 检索延迟监控
- Token 使用量监控
- 成本追踪
- A/B 测试框架
- 缓存优化

**实现文件**：
- `rag/monitoring/performance_monitor.py`：性能监控
- `rag/monitoring/cost_tracker.py`：成本追踪
- `rag/optimization/caching.py`：缓存优化

**验收标准**：
- [ ] 能够监控检索延迟
- [ ] 能够追踪 Token 使用和成本
- [ ] 缓存能够减少 50%+ 的重复计算
- [ ] 支持 A/B 测试

---

## 📁 项目结构

```
backend/rag/
├── __init__.py
├── loaders/                    # 文档加载器
│   ├── __init__.py
│   ├── pdf_loader.py          # PDF 加载器（增强）
│   ├── pdf_ocr.py             # PDF OCR
│   ├── image_loader.py        # 图片加载器
│   ├── image_ocr.py           # 图片 OCR
│   ├── table_extractor.py    # 表格提取
│   └── layout_analyzer.py     # 版式分析
├── splitters/                  # 文本分块器
│   ├── __init__.py
│   ├── hierarchical_splitter.py  # 层次化分块
│   └── semantic_splitter.py      # 语义分块（可选）
├── embeddings/                 # Embedding 模块
│   ├── __init__.py
│   ├── multimodal_embeddings.py  # 多模态 Embedding
│   └── multi_embedding.py        # 多向量生成
├── retrievers/                 # 检索器模块
│   ├── __init__.py
│   ├── hybrid_retriever.py      # 混合检索器
│   ├── bm25_retriever.py        # BM25 检索器
│   ├── multi_query_retriever.py # Multi-Query
│   ├── hyde_retriever.py        # HyDE
│   ├── reranker.py              # 重排序
│   ├── context_compression.py   # 上下文压缩
│   ├── parent_document_retriever.py  # 父文档检索
│   ├── multi_vector_retriever.py     # 多向量检索
│   ├── multimodal_retriever.py      # 多模态检索
│   └── rrf_fusion.py                # RRF 融合
├── agents/                      # Agent 模块
│   ├── __init__.py
│   ├── self_rag.py              # Self-RAG
│   ├── corrective_rag.py        # Corrective RAG
│   ├── agentic_rag.py           # Agentic RAG
│   ├── retrieval_decision.py   # 检索决策
│   ├── fact_checker.py          # 事实检查
│   └── task_planner.py          # 任务规划
├── evaluation/                  # 评估模块
│   ├── __init__.py
│   ├── retrieval_metrics.py    # 检索指标
│   ├── generation_metrics.py  # 生成指标
│   └── end_to_end_metrics.py   # 端到端指标
├── monitoring/                  # 监控模块
│   ├── __init__.py
│   ├── performance_monitor.py  # 性能监控
│   └── cost_tracker.py         # 成本追踪
├── optimization/                # 优化模块
│   ├── __init__.py
│   └── caching.py               # 缓存优化
└── query_enhancement.py         # 查询增强（Stage 1）
```

---

## 🔧 技术实现细节

### LangChain v1.0 关键 API

#### 1. Retrievers
```python
from langchain.retrievers import (
    MultiQueryRetriever,
    ContextualCompressionRetriever,
    ParentDocumentRetriever,
    MultiVectorRetriever,
    EnsembleRetriever,
)
from langchain_community.retrievers import BM25Retriever
```

#### 2. Document Compressors
```python
from langchain.retrievers.document_compressors import (
    LLMChainExtractor,
    EmbeddingsFilter,
    DocumentCompressorPipeline,
)
from langchain_cohere import CohereRerank
```

#### 3. Agents
```python
from langchain.agents import create_agent
from langchain_core.tools import Tool
```

#### 4. Evaluation
```python
from langchain.evaluation import (
    QAEvalChain,
    ContextQAEvalChain,
)
from langchain.smith import RunEvaluator
```

---

## 📊 预期效果

### 检索质量提升
- **召回率（Recall）**：提升 30-50%
- **精确率（Precision）**：提升 20-40%
- **MRR（Mean Reciprocal Rank）**：提升 40-60%

### 生成质量提升
- **答案准确性**：提升 30-50%
- **事实一致性**：提升 40-60%
- **引用准确性**：提升 50%+

### 性能指标
- **检索延迟**：< 500ms（本地向量库）
- **生成延迟**：< 3s（流式输出）
- **并发支持**：> 100 QPS

---

## 🚀 实施建议

### 优先级排序
1. **Stage 1**：基础增强（Query Enhancement + Hybrid Retrieval）- **最高优先级**
2. **Stage 2**：高级检索（Re-ranking + Context Compression）- **高优先级**
3. **Stage 3**：多粒度检索（Parent Document + Multi-vector）- **中优先级**
4. **Stage 4**：多模态 RAG（Image & PDF OCR）- **中优先级**
5. **Stage 5**：Agentic RAG - **中优先级**
6. **Stage 6**：评估与优化 - **持续进行**

### 开发原则
1. **渐进式开发**：每个 Stage 完成后进行测试和评估
2. **向后兼容**：新功能不影响现有功能
3. **配置驱动**：所有功能都可通过配置启用/禁用
4. **文档完善**：每个模块都有详细的文档和示例
5. **测试覆盖**：单元测试 + 集成测试 + 端到端测试

---

## 📝 后续计划

### 扩展方向
1. **GraphRAG**：知识图谱构建和推理路径检索
2. **Long-context RAG**：超长上下文处理
3. **Memory-Augmented RAG**：长期记忆和短期记忆
4. **Federated RAG**：多数据源联合检索
5. **Real-time RAG**：实时文档更新和增量索引

---

## 📚 参考资料

### LangChain v1.0 文档
- [Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [Evaluation](https://docs.langchain.com/oss/python/langchain/evaluation)

### Advanced RAG 技术
- [Multi-Query Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/multi_query)
- [Contextual Compression](https://python.langchain.com/docs/modules/data_connection/retrievers/contextual_compression)
- [Parent Document Retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/parent_document_retriever)
- [Self-RAG](https://arxiv.org/abs/2310.11511)

---

## ✅ 检查清单

### Stage 1 完成标准
- [ ] Multi-Query Retriever 实现并测试
- [ ] HyDE Retriever 实现并测试
- [ ] BM25 Retriever 实现并测试
- [ ] Hybrid Retriever 实现并测试
- [ ] RRF 融合算法实现并测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

### Stage 2 完成标准
- [ ] Re-ranking 模块实现并测试
- [ ] Context Compression 实现并测试
- [ ] 性能提升验证（检索错误率降低 30%+）
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

### Stage 3 完成标准
- [ ] Parent Document Retriever 实现并测试
- [ ] Multi-vector Retriever 实现并测试
- [ ] 层次化分块器实现并测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

### Stage 4 完成标准
- [ ] PDF OCR 功能实现并测试
- [ ] 图片 OCR 功能实现并测试
- [ ] 多模态 Embedding 实现并测试
- [ ] 多模态检索器实现并测试
- [ ] OCR 准确率 > 90%
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

### Stage 5 完成标准
- [ ] Self-RAG 实现并测试
- [ ] Corrective RAG 实现并测试
- [ ] Agentic RAG 实现并测试
- [ ] 任务规划器实现并测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

### Stage 6 完成标准
- [ ] 评估体系实现并测试
- [ ] 性能监控实现并测试
- [ ] 成本追踪实现并测试
- [ ] 缓存优化实现并测试
- [ ] 单元测试覆盖率 > 80%
- [ ] 文档和示例代码完成

---

**最后更新**：2025-01-06
**版本**：v1.0.0
**作者**：LC-StudyLab Team



