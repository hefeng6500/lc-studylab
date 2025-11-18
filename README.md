# LC-StudyLab

> 一个基于 LangChain v1.0.3 的完整智能体学习与实践平台，涵盖 Agent、RAG、LangGraph、DeepAgents 和 Guardrails 等核心能力。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v1.0.3-green.svg)](https://docs.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-v1.0.2-orange.svg)](https://docs.langchain.com/oss/python/langgraph/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

## 项目简介

LC-StudyLab 是一个以学习和研究为导向的 LangChain v1.0.3 全栈示例项目，系统性地集成了 LangChain 生态的核心能力。项目采用模块化设计，分为五个渐进式阶段，每个阶段对应 LangChain 文档中的关键特性，帮助开发者从基础到高级系统掌握智能体开发。

**核心定位**：

- 学习平台：系统学习 LangChain v1.0.3 的完整能力地图
- 实践模板：可直接用于构建生产级 AI 智能体系统
- 参考实现：展示最佳实践和设计模式

## 核心特性

### 阶段一：基础 Agent 与工具调用

- 基于 `create_agent` 的智能体封装
- 流式输出支持（Streaming）
- 工具调用系统（时间、计算器、网络搜索）
- FastAPI HTTP 接口
- CLI 交互式工具

### 阶段二：RAG 知识库系统

- 多格式文档加载（PDF、Markdown、TXT、HTML、JSON）
- 智能文本分块策略
- 向量索引构建与管理（FAISS）
- 多种检索策略（相似度、MMR、阈值过滤）
- RAG Agent 实现
- 完整的索引管理 API

### 阶段三：LangGraph 工作流

- 有状态工作流管理（StateGraph）
- 检查点持久化（SQLite）
- 人机交互（Human-in-the-Loop）
- 流式事件输出（SSE）
- 智能学习工作流（规划 → 检索 → 出题 → 评分 → 反馈）
- 自动重试机制

### 阶段四：DeepAgents 深度研究

- 多智能体协作系统
- 子智能体分工（WebResearcher、DocAnalyst、ReportWriter）
- 文件系统工具集成
- 研究计划自动生成
- 结构化研究报告输出

### 阶段五：Guardrails 安全机制

- 输入输出内容过滤
- Prompt Injection 检测
- 敏感信息检测与脱敏
- 结构化输出验证（Pydantic Schema）
- 人工审核机制
- 三级安全等级（SAFE/WARNING/UNSAFE）

## 技术栈

### 后端

- **语言**: Python 3.10+
- **核心框架**: LangChain 1.0.3, LangGraph 1.0.2
- **Web 框架**: FastAPI 0.121.0
- **向量数据库**: FAISS
- **数据验证**: Pydantic 2.12.4
- **日志**: Loguru
- **模型支持**: OpenAI, DeepSeek, Anthropic, Ollama 等

### 前端

- **框架**: Next.js 16.0.1
- **UI 库**: shadcn/ui + Tailwind CSS 4.x
- **AI SDK**: Vercel AI SDK v6 (beta)
- **组件库**: AI Elements
- **语言**: TypeScript 5.x

## 项目结构

```
lc-studylab/
├── backend/                    # Python 后端
│   ├── agents/                 # Agent 实现
│   │   └── base_agent.py       # 基础 Agent 封装
│   ├── api/                    # API 接口
│   │   ├── http_server.py      # FastAPI 应用
│   │   └── routers/            # 路由模块
│   │       ├── chat.py         # 聊天接口
│   │       ├── rag.py          # RAG 接口
│   │       ├── workflow.py     # 工作流接口
│   │       └── deep_research.py # 深度研究接口
│   ├── core/                   # 核心功能
│   │   ├── models.py           # 模型封装
│   │   ├── prompts.py          # 提示词模板
│   │   ├── tools/              # 工具集合
│   │   │   ├── web_search.py   # 网络搜索
│   │   │   ├── calculator.py   # 计算器
│   │   │   ├── time_tools.py   # 时间工具
│   │   │   └── filesystem.py   # 文件系统
│   │   └── guardrails/         # 安全机制
│   │       ├── content_filters.py
│   │       ├── input_validators.py
│   │       ├── output_validators.py
│   │       ├── schemas.py
│   │       └── middleware.py
│   ├── rag/                    # RAG 模块
│   │   ├── loaders.py          # 文档加载
│   │   ├── splitters.py        # 文本分块
│   │   ├── embeddings.py       # 向量化
│   │   ├── vector_stores.py    # 向量存储
│   │   ├── index_manager.py    # 索引管理
│   │   ├── retrievers.py       # 检索器
│   │   ├── rag_agent.py        # RAG Agent
│   │   └── safe_rag_agent.py   # 安全 RAG Agent
│   ├── workflows/             # LangGraph 工作流
│   │   ├── state.py            # 状态定义
│   │   ├── study_flow_graph.py # 学习工作流
│   │   ├── safe_study_flow.py  # 安全工作流
│   │   └── nodes/              # 工作流节点
│   ├── deep_research/          # DeepAgents
│   │   ├── deep_agent.py       # 深度研究智能体
│   │   ├── safe_deep_agent.py  # 安全深度研究智能体
│   │   └── subagents.py        # 子智能体
│   ├── config/                 # 配置管理
│   │   ├── settings.py         # 配置类
│   │   └── logging.py          # 日志配置
│   ├── scripts/                # 脚本工具
│   │   ├── demo_cli.py         # CLI 演示
│   │   ├── rag_cli.py          # RAG CLI
│   │   └── test_*.py            # 测试脚本
│   ├── docs/                   # 文档
│   │   └── stage_*/            # 各阶段文档
│   ├── data/                   # 数据目录
│   │   ├── documents/          # 文档库
│   │   ├── indexes/            # 向量索引
│   │   └── research/           # 研究数据
│   └── requirements.txt       # 依赖列表
│
└── frontend/                   # Next.js 前端
    ├── app/                    # App Router
    │   ├── chat/               # 聊天页面
    │   ├── rag/                # RAG 页面
    │   ├── workflows/          # 工作流页面
    │   ├── deep-research/      # 深度研究页面
    │   └── settings/           # 设置页面
    ├── components/             # 组件
    │   ├── ai-elements/        # AI Elements 组件
    │   ├── chat/               # 聊天组件
    │   ├── layout/             # 布局组件
    │   └── ui/                 # UI 组件
    ├── lib/                    # 工具库
    │   ├── api-client.ts       # API 客户端
    │   ├── session.ts          # 会话管理
    │   └── types.ts            # 类型定义
    └── docs/                   # 文档
        └── sprint_*/           # Sprint 文档
```

## 快速开始

### 方式一：Docker 一键部署（推荐）

使用 Docker Compose 可以一键启动前后端服务：

```bash
# 1. 克隆项目
git clone https://github.com/hefeng6500/lc-studylab.git
cd lc-studylab

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写 OPENAI_API_KEY 等配置

# 3. 一键启动
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

启动成功后访问：

- 前端应用: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

详细说明请查看 [Docker 部署指南](./DOCKER.md)

### 方式二：本地开发部署

#### 环境要求

- Python 3.10+
- Node.js 18+
- pnpm (推荐) 或 npm

#### 后端设置

1. **克隆项目**

```bash
git clone https://github.com/hefeng6500/lc-studylab.git
cd lc-studylab/backend
```

2. **创建虚拟环境**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

复制 `env.example` 到 `.env` 并填写配置：

```bash
cp env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI 配置
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# Tavily 搜索（可选）
TAVILY_API_KEY=your-tavily-key

# 日志级别
LOG_LEVEL=INFO
```

5. **启动服务**

```bash
# 方式一：使用脚本
bash start_server.sh

# 方式二：直接运行
python -m api.http_server

# 方式三：使用 uvicorn
uvicorn api.http_server:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 前端设置

1. **进入前端目录**

```bash
cd ../frontend
```

2. **安装依赖**

```bash
pnpm install
```

3. **配置环境变量**

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **启动开发服务器**

```bash
pnpm dev
```

访问前端应用：http://localhost:3000

## 使用示例

### 基础 Agent 调用

```python
from agents import create_base_agent

# 创建 Agent
agent = create_base_agent(prompt_mode="default", use_tools=True)

# 同步调用
response = agent.invoke("现在几点？帮我计算 123 + 456")
print(response)

# 流式调用
for chunk in agent.stream("讲一个关于编程的笑话"):
    print(chunk, end="", flush=True)
```

### RAG 知识库查询

```python
from rag import (
    load_directory,
    split_documents,
    get_embeddings,
    IndexManager,
    create_rag_agent,
    query_rag_agent,
)

# 1. 加载文档
documents = load_directory("data/documents/test")

# 2. 分块
chunks = split_documents(documents, chunk_size=1000, chunk_overlap=200)

# 3. 创建索引
manager = IndexManager()
embeddings = get_embeddings()
manager.create_index("my_docs", chunks, embeddings)

# 4. 创建 RAG Agent
vector_store = manager.load_index("my_docs", embeddings)
retriever = create_retriever(vector_store, k=4)
agent = create_rag_agent(retriever)

# 5. 查询
result = query_rag_agent(agent, "什么是机器学习？")
print(result["answer"])
print(result["sources"])
```

### API 调用示例

```bash
# 基础聊天
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下自己",
    "mode": "default",
    "use_tools": true
  }'

# 流式聊天
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "讲一个笑话"}'

# RAG 查询
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "test_docs",
    "query": "什么是机器学习？"
  }'

# 启动工作流
curl -X POST "http://localhost:8000/workflow/start" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "我想学习 Python 编程",
    "thread_id": "test-123"
  }'
```

## 部署方式

### Docker 部署（推荐）

使用 Docker Compose 一键部署，适合生产环境：

```bash
docker-compose up -d
```

详细说明请查看 [Docker 部署指南](./DOCKER.md)

### 本地开发部署

适合开发和调试，需要手动配置环境。

## 文档

### 后端文档

- [阶段一：基础 Agent](./backend/docs/stage_01/STAGE1_COMPLETION.md) - 基础 Agent 与工具调用
- [阶段二：RAG 系统](./backend/docs/stage_02/STAGE2_COMPLETION.md) - RAG 知识库模块
- [阶段三：LangGraph 工作流](./backend/docs/stage_03/STAGE3_COMPLETION.md) - 自定义工作流
- [阶段四：DeepAgents](./backend/docs/stage_04/STAGE4_COMPLETION.md) - 深度研究模式
- [阶段五：Guardrails](./backend/docs/stage_05/STAGE5_COMPLETION.md) - 安全与结构化输出

### 前端文档

- [Sprint 1 完成总结](./frontend/docs/sprint_01/SPRINT1_COMPLETION.md) - 前端基础框架
- [快速开始指南](./frontend/docs/sprint_01/QUICKSTART.md) - 前端开发指南

### 快速参考

- [后端 README](./backend/README.md) - 后端完整文档
- [前端 README](./frontend/README.md) - 前端完整文档

## 学习路线

本项目按照 LangChain v1.0.3 文档的核心能力，分为五个渐进式阶段：

1. **阶段一：基础 Agent** - 掌握 `create_agent`、工具调用、流式输出
2. **阶段二：RAG 系统** - 学习文档加载、向量化、检索增强生成
3. **阶段三：LangGraph** - 理解状态图、检查点、人机交互
4. **阶段四：DeepAgents** - 实践多智能体协作、子智能体分工
5. **阶段五：Guardrails** - 实现安全机制、结构化输出

每个阶段都有完整的文档、测试脚本和使用示例，可以独立学习或组合使用。

## 特性亮点

- **完全基于 LangChain v1.0.3**：严格使用最新版本，遵循官方最佳实践
- **模块化设计**：高内聚低耦合，易于扩展和维护
- **生产级质量**：完善的错误处理、日志记录、测试覆盖
- **详细文档**：每个模块都有完整的中文文档和代码注释
- **渐进式学习**：从基础到高级，循序渐进掌握核心能力
- **开箱即用**：提供 CLI 工具、API 接口和 Web 前端

## 开发状态

### 已完成

- [x] 阶段一：基础 Agent + Streaming + 工具
- [x] 阶段二：RAG 知识库模块
- [x] 阶段三：LangGraph 自定义工作流
- [x] 阶段四：DeepAgents 深度研究模式
- [x] 阶段五：Guardrails 安全与结构化输出
- [x] 前端基础框架（Sprint 1）

### 进行中

- [ ] 前端功能增强（Sprint 2+）
- [ ] 性能优化
- [ ] 更多测试用例

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - 优秀的 AI 应用开发框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 强大的工作流编排工具
- [Vercel AI SDK](https://github.com/vercel/ai) - 优秀的 AI SDK
- [shadcn/ui](https://github.com/shadcn-ui/ui) - 精美的 UI 组件库

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hefeng6500/lc-studylab&type=Date)](https://star-history.com/#hefeng6500/lc-studylab&Date)

---

**LC-StudyLab** - 让 LangChain 学习更简单，让智能体开发更高效。
