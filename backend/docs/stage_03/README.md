# 第 3 阶段：LangGraph 自定义工作流

## 📚 概述

第 3 阶段实现了基于 LangGraph 的智能学习工作流系统，这是一个完整的、有状态的、支持人机交互的学习助手。

### 核心特性

✅ **有状态工作流 (Stateful)**
- 使用 LangGraph 的 StateGraph 管理全局状态
- 状态在节点间自动传递和更新
- 支持复杂的数据结构和类型检查

✅ **检查点持久化 (Checkpointer)**
- 使用 SQLite 存储检查点
- 支持工作流的暂停和恢复
- 可以查看完整的执行历史

✅ **人机交互 (Human-in-the-Loop)**
- 在练习题生成后暂停，等待用户答题
- 支持异步提交答案
- 提交后自动继续执行评分和反馈

✅ **流式输出 (Streaming)**
- 支持 Server-Sent Events (SSE)
- 实时推送节点执行进度
- 可以监控 LLM 的 token 生成

✅ **智能重试机制**
- 得分低于 60 分自动重新出题
- 最多重试 3 次
- 每次重试生成不同的题目

## 🏗️ 架构设计

### 工作流图结构

```
START
  ↓
planner (学习规划)
  ↓
retrieval (文档检索)
  ↓
quiz_generator (生成练习题)
  ↓
human_review (人机交互：等待用户答题) ← 在此暂停
  ↓
grading (自动评分)
  ↓
feedback (生成反馈)
  ↓
[条件分支]
  ├─ retry → quiz_generator (重新出题)
  └─ end → END
```

### 目录结构

```
backend/
  workflows/
    __init__.py
    state.py                      # 状态模型定义
    study_flow_graph.py           # 工作流图构建
    nodes/
      __init__.py
      planner_node.py             # 学习规划节点
      retrieval_node.py           # 文档检索节点
      quiz_generator_node.py      # 练习题生成节点
      grading_node.py             # 自动评分节点
      feedback_node.py            # 反馈生成节点
  
  api/routers/
    workflow.py                   # 工作流 API 路由
  
  scripts/
    test_workflow.py              # 测试脚本
    test_workflow.sh              # 启动脚本
  
  data/checkpoints/
    study_flow.db                 # SQLite 检查点数据库
```

## 🚀 快速开始

### 1. 安装依赖

确保已安装 LangGraph：

```bash
cd backend
source venv/bin/activate
pip install langgraph
```

### 2. 启动 API 服务器

```bash
./start_server.sh
```

服务器将在 `http://localhost:8000` 启动。

### 3. 测试工作流

#### 方法 1: 使用 CLI 测试脚本

```bash
./scripts/test_workflow.sh
```

这将运行完整的测试套件，包括：
- 完整工作流测试
- 检查点恢复测试
- 重试机制测试

#### 方法 2: 使用 API

**步骤 1: 启动工作流**

```bash
curl -X POST http://localhost:8000/workflow/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_question": "我想学习 Python 的基础知识"
  }'
```

响应示例：

```json
{
  "thread_id": "study_abc123",
  "status": "waiting_for_answers",
  "current_step": "waiting_for_answers",
  "learning_plan": {
    "topic": "Python 基础知识",
    "objectives": ["理解变量和数据类型", "掌握控制流", "..."],
    "key_points": ["变量", "数据类型", "if语句", "循环", "..."],
    "difficulty": "beginner",
    "estimated_time": 60
  },
  "quiz": {
    "questions": [
      {
        "id": "q1",
        "type": "multiple_choice",
        "question": "Python 中哪个是正确的变量命名？",
        "options": ["A. 1variable", "B. variable_1", "C. variable-1", "D. variable 1"],
        "answer": "B",
        "explanation": "...",
        "points": 10
      }
    ],
    "total_points": 100,
    "time_limit": 30
  },
  "message": "学习计划和练习题已生成，请提交答案。"
}
```

**步骤 2: 提交答案**

```bash
curl -X POST http://localhost:8000/workflow/submit-answers \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "study_abc123",
    "answers": {
      "q1": "B",
      "q2": "变量",
      "q3": "Python 是一种..."
    }
  }'
```

响应示例：

```json
{
  "thread_id": "study_abc123",
  "status": "completed",
  "score": 85,
  "score_details": {
    "correct_count": 4,
    "total_count": 5,
    "question_scores": [...]
  },
  "feedback": "您的表现很好！...",
  "should_retry": false,
  "message": "恭喜通过测验！"
}
```

**步骤 3: 查询状态**

```bash
curl http://localhost:8000/workflow/status/study_abc123
```

**步骤 4: 查看历史**

```bash
curl http://localhost:8000/workflow/history/study_abc123
```

## 📖 API 文档

### POST /workflow/start

启动新的学习工作流。

**请求体：**
```json
{
  "user_question": "string",
  "thread_id": "string (optional)"
}
```

**响应：**
```json
{
  "thread_id": "string",
  "status": "waiting_for_answers",
  "current_step": "string",
  "learning_plan": {...},
  "quiz": {...},
  "message": "string"
}
```

### POST /workflow/submit-answers

提交用户答案，继续执行工作流。

**请求体：**
```json
{
  "thread_id": "string",
  "answers": {
    "question_id": "answer",
    ...
  }
}
```

**响应：**
```json
{
  "thread_id": "string",
  "status": "completed|retry|failed",
  "score": 85,
  "score_details": {...},
  "feedback": "string",
  "should_retry": false,
  "message": "string"
}
```

### GET /workflow/status/{thread_id}

获取工作流的当前状态。

**响应：**
```json
{
  "thread_id": "string",
  "current_step": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "state": {...}
}
```

### GET /workflow/history/{thread_id}

获取工作流的执行历史。

**响应：**
```json
{
  "thread_id": "string",
  "history": [
    {
      "checkpoint_id": "string",
      "step": "string",
      "timestamp": "ISO8601"
    }
  ]
}
```

### GET /workflow/stream/{thread_id}

流式获取工作流执行进度（SSE）。

**响应：** Server-Sent Events 流

```
data: {"type": "node_start", "node": "planner"}
data: {"type": "token", "content": "正在"}
data: {"type": "token", "content": "生成"}
data: {"type": "node_end", "node": "planner"}
data: {"type": "complete"}
```

## 🔧 技术细节

### 状态管理

工作流状态使用 TypedDict 定义，包含以下字段：

```python
class StudyFlowState(TypedDict):
    # 基础信息
    messages: Annotated[List[BaseMessage], add_messages]
    user_question: str
    
    # 各阶段数据
    learning_plan: Optional[Dict]
    retrieved_docs: Optional[List]
    quiz: Optional[Dict]
    user_answers: Optional[Dict]
    score: Optional[int]
    score_details: Optional[Dict]
    feedback: Optional[str]
    
    # 流程控制
    retry_count: int
    should_retry: bool
    current_step: str
    
    # 元数据
    thread_id: str
    checkpoint_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    
    # 错误处理
    error: Optional[str]
    error_node: Optional[str]
```

### 检查点机制

使用 LangGraph 的 `SqliteSaver` 实现检查点持久化：

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)
```

### 人机交互实现

通过 `interrupt_before` 参数在指定节点前暂停：

```python
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]  # 在此节点前暂停
)
```

恢复执行：

```python
# 更新状态
app.update_state(config, {"user_answers": answers})

# 继续执行
result = app.invoke(None, config)
```

### 条件路由

使用条件边实现动态路由：

```python
def should_continue(state: StudyFlowState) -> Literal["retry", "end"]:
    if state["should_retry"] and state["retry_count"] < 3:
        return "retry"
    return "end"

workflow.add_conditional_edges(
    "feedback",
    should_continue,
    {
        "retry": "quiz_generator",
        "end": END
    }
)
```

### 结构化输出

使用 Pydantic 模型确保 LLM 输出格式正确：

```python
from pydantic import BaseModel, Field

class LearningPlanSchema(BaseModel):
    topic: str = Field(description="学习主题")
    objectives: list[str] = Field(description="学习目标")
    key_points: list[str] = Field(description="关键知识点")
    difficulty: str = Field(description="难度级别")
    estimated_time: int = Field(description="预计时间")

model = get_chat_model()
structured_model = model.with_structured_output(LearningPlanSchema)
```

## 🧪 测试

### 运行测试套件

```bash
./scripts/test_workflow.sh
```

测试包括：

1. **完整工作流测试**
   - 启动工作流
   - 生成学习计划和练习题
   - 提交答案
   - 自动评分和反馈

2. **检查点恢复测试**
   - 启动工作流并暂停
   - 模拟程序重启
   - 从检查点恢复状态

3. **重试机制测试**
   - 提交全错答案
   - 验证自动重新出题

### 手动测试

使用 Python 交互式环境：

```python
from workflows.study_flow_graph import start_study_flow, submit_answers

# 启动工作流
result = start_study_flow(
    user_question="学习 Python 基础",
    thread_id="test_123"
)

# 提交答案
result = submit_answers(
    thread_id="test_123",
    user_answers={"q1": "B", "q2": "变量"}
)
```

## 🐛 故障排查

### 问题 1: 检查点数据库锁定

**症状：** `database is locked` 错误

**解决：**
```bash
# 关闭所有使用数据库的进程
pkill -f test_workflow

# 删除数据库文件重新开始
rm data/checkpoints/study_flow.db
```

### 问题 2: 工作流卡住不继续

**症状：** 提交答案后工作流没有继续执行

**检查：**
```python
from workflows.study_flow_graph import get_workflow_state

state = get_workflow_state("your_thread_id")
print(state.get("current_step"))
print(state.get("error"))
```

### 问题 3: LLM 返回格式错误

**症状：** 结构化输出解析失败

**解决：** 检查 Pydantic 模型定义，确保与 LLM 输出匹配。可以临时移除结构化输出，查看原始响应：

```python
model = get_chat_model()
response = model.invoke([{"role": "user", "content": "..."}])
print(response.content)
```

## 📊 性能优化

### 1. 检查点存储优化

- 定期清理旧的检查点数据
- 考虑使用 PostgreSQL 替代 SQLite（生产环境）

### 2. 并发处理

- 每个 thread_id 独立，支持多用户并发
- 使用异步 API 提高吞吐量

### 3. 缓存策略

- 缓存常见问题的学习计划
- 缓存检索结果

## 🔜 下一步

完成第 3 阶段后，可以继续：

1. **第 4 阶段：DeepAgents 深度研究**
   - 实现复杂的研究工作流
   - 多智能体协作
   - 长期记忆

2. **第 5 阶段：Guardrails 安全**
   - 输入输出过滤
   - 内容安全检查
   - 结构化输出验证

## 📝 更新日志

### v1.0.0 (2025-01-09)

- ✅ 实现完整的学习工作流
- ✅ 支持检查点持久化
- ✅ 实现人机交互
- ✅ 支持流式输出
- ✅ 实现智能重试机制
- ✅ 提供完整的 API 和 CLI

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

