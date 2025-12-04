# Advanced RAG 文档目录

## 📚 文档导航

### 总体规划
- **[ADVANCED_RAG_PLAN.md](./ADVANCED_RAG_PLAN.md)**：完整的 Advanced RAG 实现计划（6 个阶段）

### 分阶段详细计划
- **[STAGE_01_QUERY_ENHANCEMENT.md](./STAGE_01_QUERY_ENHANCEMENT.md)**：Stage 1 - Query Enhancement & Hybrid Retrieval
- **[STAGE_02_RERANKING_COMPRESSION.md](./STAGE_02_RERANKING_COMPRESSION.md)**：Stage 2 - Re-ranking & Context Compression
- **STAGE_03_MULTI_GRANULARITY.md**：Stage 3 - Parent Document & Multi-vector（待创建）
- **STAGE_04_MULTIMODAL.md**：Stage 4 - Image & PDF OCR（待创建）
- **STAGE_05_AGENTIC_RAG.md**：Stage 5 - Agentic RAG（待创建）
- **STAGE_06_EVALUATION.md**：Stage 6 - Evaluation & Monitoring（待创建）

### 技术调研
- **[1.md](./1.md)**：Advanced RAG 技术调研和理论分析

## 🚀 快速开始

### 1. 阅读总体规划
首先阅读 [ADVANCED_RAG_PLAN.md](./ADVANCED_RAG_PLAN.md)，了解整个项目的架构和 6 个阶段的规划。

### 2. 按阶段实施
按照优先级顺序，依次实施各个阶段：
1. **Stage 1**：基础增强（最高优先级）
2. **Stage 2**：高级检索（高优先级）
3. **Stage 3**：多粒度检索（中优先级）
4. **Stage 4**：多模态 RAG（中优先级）
5. **Stage 5**：Agentic RAG（中优先级）
6. **Stage 6**：评估与优化（持续进行）

### 3. 参考技术文档
在实施过程中，参考 [1.md](./1.md) 中的技术调研内容，了解 Advanced RAG 的理论基础。

## 📋 实施检查清单

### Stage 1 检查清单
- [ ] 阅读 [STAGE_01_QUERY_ENHANCEMENT.md](./STAGE_01_QUERY_ENHANCEMENT.md)
- [ ] 实现 Multi-Query Retriever
- [ ] 实现 HyDE Retriever
- [ ] 实现 BM25 Retriever
- [ ] 实现 Hybrid Retriever
- [ ] 实现 RRF Fusion
- [ ] 编写单元测试
- [ ] 编写文档和示例

### Stage 2 检查清单
- [ ] 阅读 [STAGE_02_RERANKING_COMPRESSION.md](./STAGE_02_RERANKING_COMPRESSION.md)
- [ ] 实现 Re-ranking 模块
- [ ] 实现 Context Compression
- [ ] 编写单元测试
- [ ] 编写文档和示例

## 🔧 技术栈

### 核心框架
- **LangChain v1.0.3**：核心框架
- **Python 3.9+**：开发语言

### 关键依赖
```bash
# 基础依赖
langchain>=1.0.3
langchain-community>=0.3.0
langchain-openai>=0.2.0

# Reranking
langchain-cohere>=0.2.0  # Cohere Reranker
sentence-transformers>=2.2.0  # bge-reranker

# OCR
pytesseract>=0.3.10
paddleocr>=2.7.0
unstructured>=0.10.0

# PDF 处理
pymupdf>=1.23.0
pdfplumber>=0.10.0

# 图像处理
Pillow>=10.0.0
opencv-python>=4.8.0

# BM25
rank-bm25>=0.2.2
```

## 📊 预期效果

### 检索质量提升
- **召回率（Recall）**：提升 30-50%
- **精确率（Precision）**：提升 20-40%
- **MRR（Mean Reciprocal Rank）**：提升 40-60%

### 生成质量提升
- **答案准确性**：提升 30-50%
- **事实一致性**：提升 40-60%
- **引用准确性**：提升 50%+

## 🎯 开发原则

1. **渐进式开发**：每个 Stage 完成后进行测试和评估
2. **向后兼容**：新功能不影响现有功能
3. **配置驱动**：所有功能都可通过配置启用/禁用
4. **文档完善**：每个模块都有详细的文档和示例
5. **测试覆盖**：单元测试 + 集成测试 + 端到端测试

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

## 🤝 贡献指南

1. 按照阶段计划实施功能
2. 编写单元测试（覆盖率 > 80%）
3. 更新文档和示例代码
4. 提交代码前运行测试和 lint

## 📝 更新日志

### 2025-01-06
- 创建 Advanced RAG 总体规划文档
- 创建 Stage 1 详细计划
- 创建 Stage 2 详细计划
- 创建 README 文档

---

**最后更新**：2025-01-06  
**版本**：v1.0.0  
**维护者**：LC-StudyLab Team

