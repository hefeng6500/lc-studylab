# LC-StudyLab Backend

## 🎯 项目概述

LC-StudyLab 是一个智能学习 & 研究助手系统，基于 **LangChain v1.0.3** 全家桶构建。

### 已完成阶段

#### ✅ 第 1 阶段：基础 Agent + Streaming + 工具
- 基于 LangChain 1.0.3 的 `create_agent` 实现
- 流式输出支持（Streaming）
- 工具调用（时间、计算器、网络搜索）
- FastAPI HTTP 接口
- CLI 交互式演示工具

#### ✅ 第 2 阶段：RAG 知识库模块
- 文档加载和分割
- 向量索引构建（FAISS）
- 文档检索系统
- RAG Agent 实现
- RAG API 接口

#### ✅ 第 3 阶段：LangGraph 自定义工作流
- 有状态工作流管理（StateGraph）
- 检查点持久化（SQLite）
- 人机交互（Human-in-the-Loop）
- 流式输出（SSE）
- 智能学习工作流（规划→检索→出题→评分→反馈）

### 进行中阶段

#### ⏳ 第 4 阶段：DeepAgents 深度研究（计划中）
#### ⏳ 第 5 阶段：Guardrails 安全（计划中）

## 🏗️ 技术栈

- **LangChain**: 1.0.3（宪法级别规定）
- **LangChain Core**: 1.0.3
- **LangChain OpenAI**: 1.0.2
- **LangChain Community**: 0.4.1
- **LangGraph**: 1.0.2
- **FastAPI**: 0.121.0
- **Python**: 3.9+

## 📦 安装

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `env.example` 到 `.env` 并填写配置：

```bash
cp env.example .env
```

## 🚀 快速开始

### 方式 1: CLI 交互式工具（推荐用于测试）

```bash
python scripts/demo_cli.py
```

CLI 支持的命令：
- `/help` - 显示帮助
- `/mode <模式>` - 切换模式（default/coding/research/concise/detailed）
- `/stream` - 切换流式/非流式输出
- `/tools` - 切换工具启用/禁用
- `/clear` - 清空对话历史
- `/info` - 显示当前配置
- `/quit` - 退出

快速测试示例：
```
👤 你: 现在几点？
👤 你: 计算 123 + 456
👤 你: 搜索 LangChain 1.0.3 新特性
```

### 方式 2: HTTP API 服务器

启动服务器：

```bash
python api/http_server.py
```

或使用 uvicorn：

```bash
uvicorn api.http_server:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API 接口

### 1. 非流式聊天

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下自己",
    "mode": "default",
    "use_tools": true
  }'
```

### 2. 流式聊天（SSE）

```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "讲一个关于编程的笑话",
    "mode": "default"
  }'
```

### 3. 获取可用模式

```bash
curl http://localhost:8000/chat/modes
```

### 4. 健康检查

```bash
curl http://localhost:8000/health
```

## 🔧 核心组件

### 1. 工具模块 (`core/tools/`)

- **time_tools.py**: 时间相关工具
  - `get_current_time()` - 获取当前时间
  - `get_current_date()` - 获取当前日期

- **calculator.py**: 计算器工具
  - `calculator(expression)` - 安全的数学表达式计算

- **web_search.py**: 网络搜索工具
  - `web_search(query)` - 使用 Tavily 搜索互联网
  - `web_search_simple(query)` - 快速搜索模式

### 2. Agent 模块 (`agents/`)

- **base_agent.py**: 基础 Agent 实现
  - `BaseAgent` - 封装 LangChain 1.0.3 的 create_agent
  - 支持同步/异步调用
  - 支持流式/非流式输出
  - 支持工具调用

### 3. API 模块 (`api/`)

- **http_server.py**: FastAPI 应用主入口
- **routers/chat.py**: 聊天接口路由
  - `POST /chat` - 非流式聊天
  - `POST /chat/stream` - 流式聊天（SSE）
  - `GET /chat/modes` - 获取可用模式

### 4. 配置模块 (`config/`)

- **settings.py**: 统一配置管理（Pydantic Settings）
- **logging.py**: 日志配置（Loguru）

## 🎨 Agent 模式

系统提供多种预设的 Agent 模式：

1. **default** - 默认学习助手
2. **coding** - 编程学习助手
3. **research** - 研究助手
4. **concise** - 简洁模式
5. **detailed** - 详细解释模式

## 🧪 测试示例

### 测试时间工具

```python
from agents import create_base_agent

agent = create_base_agent()
response = agent.invoke("现在几点？")
print(response)
```

### 测试计算器

```python
agent = create_base_agent()
response = agent.invoke("帮我计算 (123 + 456) * 2")
print(response)
```

### 测试流式输出

```python
agent = create_base_agent(streaming=True)
for chunk in agent.stream("讲一个笑话"):
    print(chunk, end="", flush=True)
```

### 测试网络搜索

```python
from core.tools import ALL_TOOLS

agent = create_base_agent(tools=ALL_TOOLS)
response = agent.invoke("搜索 LangChain 1.0.3 的新特性")
print(response)
```

## 📝 日志

日志文件位置：`logs/app.log`

日志级别可在 `.env` 中配置：
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔍 调试

启用详细日志：

```python
agent = create_base_agent(verbose=True)
```

或在 `.env` 中设置：
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📚 项目结构

```
backend/
├── agents/              # Agent 实现
│   ├── __init__.py
│   └── base_agent.py   # 基础 Agent
├── api/                # API 接口
│   ├── __init__.py
│   ├── http_server.py  # FastAPI 应用
│   └── routers/
│       ├── __init__.py
│       └── chat.py     # 聊天路由
├── config/             # 配置管理
│   ├── __init__.py
│   ├── settings.py     # 配置类
│   └── logging.py      # 日志配置
├── core/               # 核心功能
│   ├── __init__.py
│   ├── models.py       # 模型封装
│   ├── prompts.py      # 提示词模板
│   └── tools/          # 工具集合
│       ├── __init__.py
│       ├── calculator.py
│       ├── time_tools.py
│       └── web_search.py
├── scripts/            # 脚本工具
│   └── demo_cli.py     # CLI 演示工具
├── .env                # 环境变量配置
├── env.example         # 配置示例
├── requirements.txt    # 依赖列表
└── README.md          # 本文档
```

## 🎯 快速开始指南

### 第 1 阶段：基础聊天
详见 `docs/stage_01/` 目录

### 第 2 阶段：RAG 文档问答
详见 `docs/stage_02/` 目录

### 第 3 阶段：学习工作流
详见 `docs/stage_03/README.md` 完整使用指南

**快速测试工作流：**
```bash
# 启动 API 服务器
./start_server.sh

# 或运行测试脚本
./scripts/test_workflow.sh
```

## 🎯 下一步计划

前 3 个阶段已完成！接下来：

- **第 4 阶段**: DeepAgents 深度研究模式（计划中）
- **第 5 阶段**: Guardrails / 安全与结构化输出（计划中）

## 🤝 贡献

本项目遵循敏捷开发原则，欢迎提交 Issue 和 Pull Request。

## 📄 许可

MIT License

