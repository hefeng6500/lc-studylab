# 第 2 阶段：RAG 知识库模块 - 使用指南

## 📋 概述

第 2 阶段实现了完整的 RAG（Retrieval-Augmented Generation）系统，支持：
- 📄 多格式文档加载（PDF、Markdown、TXT、HTML、JSON）
- ✂️ 智能文本分块
- 🔢 向量化和向量存储（FAISS）
- 🔍 多种检索策略
- 🤖 RAG Agent（基于检索的智能问答）
- 🌐 HTTP API 接口
- 💻 CLI 命令行工具

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

确保 `.env` 文件中配置了 OpenAI API Key：

```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. 创建第一个索引

使用 CLI 工具创建索引：

```bash
python scripts/rag_cli.py index create test_index data/documents/test --description "测试文档索引"
```

### 4. 查询索引

```bash
python scripts/rag_cli.py query test_index "什么是机器学习？"
python scripts/rag_cli.py query test_index "长江赋中写的最好的一句是什么？"
```

### 5. 交互模式

```bash
python scripts/rag_cli.py interactive test_index
```

## 📚 核心功能

### 1. 文档加载

支持的文档格式：
- PDF (.pdf)
- Markdown (.md, .mdx)
- 文本文件 (.txt)
- HTML (.html, .htm)
- JSON (.json)

**代码示例：**

```python
from rag import load_document, load_directory

# 加载单个文档
documents = load_document("document.pdf")

# 加载整个目录
documents = load_directory("data/documents/")

# 加载特定格式
documents = load_directory(
    "data/documents/",
    glob_pattern="**/*.md"
)
```

### 2. 文本分块

支持多种分块策略：
- `recursive`: 递归字符分块（推荐）
- `character`: 简单字符分块
- `markdown`: Markdown 专用分块
- `token`: 基于 Token 的分块

**代码示例：**

```python
from rag import split_documents

# 使用默认配置
chunks = split_documents(documents)

# 自定义参数
chunks = split_documents(
    documents,
    splitter_type="recursive",
    chunk_size=1000,
    chunk_overlap=200
)
```

### 3. 向量化和存储

使用 OpenAI Embeddings 和 FAISS 向量库：

```python
from rag import get_embeddings, create_vector_store, save_vector_store

# 创建 embeddings
embeddings = get_embeddings()

# 创建向量库
vector_store = create_vector_store(chunks, embeddings)

# 保存向量库
save_vector_store(vector_store, "data/indexes/my_index")
```

### 4. 检索

支持多种检索策略：

```python
from rag import load_vector_store, create_retriever

# 加载向量库
vector_store = load_vector_store("data/indexes/my_index", embeddings)

# 相似度检索
retriever = create_retriever(vector_store, search_type="similarity", k=4)

# MMR 检索（更多样化）
retriever = create_retriever(vector_store, search_type="mmr", k=4, fetch_k=20)

# 阈值过滤
retriever = create_retriever(
    vector_store,
    search_type="similarity_score_threshold",
    score_threshold=0.7
)

# 使用检索器
docs = retriever.invoke("什么是机器学习？")
```

### 5. RAG Agent

创建支持检索的智能问答 Agent：

```python
from rag import create_rag_agent, query_rag_agent

# 创建 RAG Agent
agent = create_rag_agent(retriever)

# 查询
result = query_rag_agent(agent, "什么是机器学习？")
print(result["answer"])
print(result["sources"])

# 流式查询
agent_streaming = create_rag_agent(retriever, streaming=True)
for chunk in agent_streaming.stream({"input": "解释深度学习"}):
    if "output" in chunk:
        print(chunk["output"], end="", flush=True)
```

### 6. 索引管理

使用 IndexManager 统一管理索引：

```python
from rag import IndexManager, get_embeddings, split_documents, load_directory

manager = IndexManager()

# 创建索引
documents = load_directory("data/documents/test")
chunks = split_documents(documents)
embeddings = get_embeddings()

manager.create_index(
    name="my_docs",
    documents=chunks,
    embeddings=embeddings,
    description="我的文档集合"
)

# 列出所有索引
indexes = manager.list_indexes()

# 获取索引信息
info = manager.get_index_info("my_docs")

# 加载索引
vector_store = manager.load_index("my_docs", embeddings)

# 更新索引
new_docs = load_directory("data/documents/new")
new_chunks = split_documents(new_docs)
manager.update_index("my_docs", new_chunks, embeddings)

# 删除索引
manager.delete_index("my_docs")
```

### 5. 智能索引更新 ⭐

**推荐使用智能更新脚本，自动检测新文档并增量更新：**

```bash
# 1. 添加新文档到目录
cp new_document.md data/documents/test/

# 2. 运行智能更新（只处理新文档）
python scripts/update_index.py test_index data/documents/test

# 3. 查询验证
python scripts/rag_cli.py query test_index "新文档的内容"
```

**主要特性：**

✅ **自动检测新文档** - 只处理未索引的文档  
✅ **文件跟踪** - 自动记录已处理的文档  
✅ **增量更新** - 节省时间和 API 成本  
✅ **支持重建** - 需要时可以完全重建索引

**详细使用方法：**

```bash
# 增量更新（推荐）
python scripts/update_index.py test_index data/documents/test

# 强制重建整个索引
python scripts/update_index.py test_index data/documents/test --rebuild

# 查看帮助
python scripts/update_index.py --help
```

**工作流程：**

```bash
# 步骤 1: 添加新文档
echo "# 新主题\n这是新内容..." > data/documents/test/new_topic.md

# 步骤 2: 更新索引
python scripts/update_index.py test_index data/documents/test
# 输出: 📄 发现 1 个新文档: new_topic.md

# 步骤 3: 验证查询
python scripts/rag_cli.py query test_index "新主题"
```

**跟踪文件位置：**
```
data/indexes/test_index/tracked_files.json
```

**📖 完整文档：** [智能索引更新指南](INDEX_UPDATE_GUIDE.md)

## 🌐 HTTP API

### 启动服务器

```bash
python api/http_server.py
```

服务器启动后，访问 http://localhost:8000/docs 查看 API 文档。

### API 端点

#### 1. 创建索引

```bash
curl -X POST "http://localhost:8000/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_docs",
    "directory_path": "data/documents/test",
    "description": "测试文档索引",
    "chunk_size": 1000
  }'
```

#### 2. 列出索引

```bash
curl "http://localhost:8000/rag/index/list"
```

#### 3. 获取索引信息

```bash
curl "http://localhost:8000/rag/index/my_docs"
```

#### 4. RAG 查询

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_docs",
    "query": "什么是机器学习？",
    "k": 4
  }'
```

#### 5. 流式查询

```bash
curl -X POST "http://localhost:8000/rag/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_docs",
    "query": "什么是机器学习？"
  }'
```

#### 6. 纯检索

```bash
curl -X POST "http://localhost:8000/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "my_docs",
    "query": "机器学习",
    "k": 3
  }'
```

#### 7. 删除索引

```bash
curl -X DELETE "http://localhost:8000/rag/index/my_docs"
```

## 💻 CLI 工具

### 索引管理

```bash
# 创建索引
python scripts/rag_cli.py index create my_docs data/documents/test \
  --description "我的文档" \
  --chunk-size 1000 \
  --chunk-overlap 200

# 列出所有索引
python scripts/rag_cli.py index list

# 查看索引信息
python scripts/rag_cli.py index info my_docs

# 删除索引
python scripts/rag_cli.py index delete my_docs
```

### 查询

```bash
# RAG 查询
python scripts/rag_cli.py query my_docs "什么是机器学习？" --k 4 --show-sources

# 纯检索
python scripts/rag_cli.py search my_docs "机器学习" --k 3

# 交互模式
python scripts/rag_cli.py interactive my_docs
```

## ⚙️ 配置参数

在 `config/settings.py` 中配置 RAG 参数：

```python
# Embedding 配置
embedding_model = "text-embedding-3-small"  # 或 "text-embedding-3-large"
embedding_batch_size = 100

# 文本分块配置
chunk_size = 1000           # 分块大小（字符数）
chunk_overlap = 200         # 分块重叠大小

# 向量库配置
vector_store_type = "faiss"  # 向量库类型
vector_store_path = "data/indexes"  # 索引存储路径

# 检索配置
retriever_search_type = "similarity"  # similarity, mmr, similarity_score_threshold
retriever_k = 4                       # 返回文档数量
retriever_score_threshold = 0.5       # 相似度阈值
retriever_fetch_k = 20                # MMR 候选数量

# RAG Agent 配置
rag_agent_max_iterations = 10
rag_agent_return_source_documents = True
```

## 📊 最佳实践

### 1. 选择合适的分块大小

- **通用文档**: chunk_size=1000, overlap=200
- **代码文档**: chunk_size=1500, overlap=300
- **学术论文**: chunk_size=1200, overlap=250
- **对话记录**: chunk_size=500, overlap=50

### 2. 选择检索策略

- **相似度检索（similarity）**: 最快，适合大多数情况
- **MMR 检索（mmr）**: 结果更多样化，避免重复
- **阈值过滤（similarity_score_threshold）**: 只返回高质量结果

### 3. 优化检索参数

- `k`: 通常设置为 3-5
- `score_threshold`: 0.5-0.7 之间
- `fetch_k`: MMR 模式下设置为 k 的 3-5 倍

### 4. Embedding 模型选择

- **text-embedding-3-small**: 快速、便宜，适合开发测试
- **text-embedding-3-large**: 高质量，适合生产环境

### 5. 索引管理

- 定期更新索引以包含新文档
- 为不同类型的文档创建独立索引
- 使用描述性的索引名称

## 🔧 故障排除

### 问题 1: 找不到文档

**解决方案**:
- 检查文档路径是否正确
- 确保文档格式受支持
- 查看日志了解详细错误

### 问题 2: 索引创建失败

**解决方案**:
- 检查 OpenAI API Key 是否配置
- 确保有足够的磁盘空间
- 检查文档是否可读

### 问题 3: 查询结果不准确

**解决方案**:
- 调整 chunk_size 和 overlap
- 尝试不同的检索策略
- 增加 k 值获取更多上下文
- 使用更大的 embedding 模型

### 问题 4: 查询速度慢

**解决方案**:
- 减少 k 值
- 使用 FAISS 而不是 InMemory
- 考虑使用更小的 embedding 模型

## 📈 性能指标

基于测试文档（3 个文件，约 10,000 字）：

- **索引创建时间**: ~30 秒
- **查询响应时间**: ~2-3 秒
- **索引大小**: ~5 MB
- **内存占用**: ~200 MB

## 🎓 学习资源

### LangChain 文档

- [Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [Document Loaders](https://reference.langchain.com/python/langchain_core/document_loaders/)
- [Text Splitters](https://reference.langchain.com/python/langchain_text_splitters/)
- [Vector Stores](https://reference.langchain.com/python/langchain_core/vectorstores/)

### 相关概念

- RAG 原理和应用
- 向量数据库对比
- Embedding 模型选择
- 检索优化技巧

## 🐛 已知问题

1. PDF 加载可能在某些格式上失败 → 使用其他格式或手动转换
2. 大文件处理可能较慢 → 考虑分批处理
3. 某些特殊字符可能导致分块问题 → 预处理文本

## 🔜 下一步

完成第 2 阶段后，可以继续：

- **第 3 阶段**: LangGraph 自定义工作流
- **第 4 阶段**: DeepAgents 深度研究
- **第 5 阶段**: Guardrails 安全过滤

## 📞 获取帮助

遇到问题？
1. 查看日志文件 `logs/app.log`
2. 检查配置是否正确
3. 参考示例代码
4. 查阅 LangChain 官方文档

