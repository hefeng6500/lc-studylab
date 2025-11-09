# 第 3 阶段开发计划：LangGraph 自定义工作流

## 📋 阶段目标

在第 3 阶段，我们将基于 **LangChain v1.0.3** 和 **LangGraph** 构建一个完整的学习任务工作流系统，实现以下核心功能：

1. **有状态工作流（Stateful）**：维护完整的对话状态和任务进度
2. **检查点机制（Checkpointer）**：支持工作流的暂停、恢复和回滚
3. **人机交互（Human-in-the-Loop, HITL）**：在关键节点支持人工审核和干预
4. **流式输出（Streaming）**：实时输出工作流执行进度和结果

## 🎯 业务场景

实现一个智能学习助手工作流，流程如下：

```
用户提问 
  ↓
规划学习路径 (Planner Node)
  ↓
检索相关文档 (Retrieval Node)
  ↓
生成学习计划 (Plan Generation Node)
  ↓
生成练习题 (Quiz Generation Node)
  ↓
【人机交互】等待用户答题 (Human-in-the-Loop)
  ↓
自动评分 (Grading Node)
  ↓
生成反馈 (Feedback Node)
  ↓
【条件分支】根据分数决定是否重新出题或结束
```

## 🏗️ 技术架构

### 1. 核心技术栈

- **LangChain v1.0.3**：核心框架
- **LangGraph**：状态图工作流引擎
- **LangChain-OpenAI**：模型提供商
- **SQLite Checkpointer**：持久化检查点存储

### 2. 项目结构

```
backend/
  workflows/
    __init__.py
    study_flow_graph.py          # 主工作流图定义
    state.py                      # 状态模型定义
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
    test_workflow.py              # 工作流测试脚本
  
  data/
    checkpoints/                  # 检查点存储目录
      study_flow/                 # 学习工作流检查点
```

## 📝 详细实现计划

### 阶段 3.1：状态模型设计

**文件：** `backend/workflows/state.py`

**功能：** 定义工作流的全局状态结构

**状态字段：**
```python
class StudyFlowState(TypedDict):
    # 基础信息
    messages: Annotated[list, add_messages]  # 对话历史
    user_question: str                        # 用户问题
    
    # 规划阶段
    learning_plan: Optional[dict]             # 学习计划
    
    # 检索阶段
    retrieved_docs: Optional[list]            # 检索到的文档
    
    # 练习题阶段
    quiz: Optional[dict]                      # 生成的练习题
    user_answers: Optional[dict]              # 用户答案
    
    # 评分阶段
    score: Optional[int]                      # 得分
    feedback: Optional[str]                   # 反馈信息
    
    # 流程控制
    retry_count: int                          # 重试次数
    should_retry: bool                        # 是否需要重新出题
    
    # 元数据
    thread_id: str                            # 会话 ID
    checkpoint_id: Optional[str]              # 检查点 ID
```

### 阶段 3.2：节点实现

#### 节点 1：学习规划节点 (Planner Node)

**文件：** `backend/workflows/nodes/planner_node.py`

**功能：**
- 分析用户问题
- 生成学习路径和计划
- 使用结构化输出（Pydantic）

**输入：** `user_question`
**输出：** `learning_plan`

#### 节点 2：文档检索节点 (Retrieval Node)

**文件：** `backend/workflows/nodes/retrieval_node.py`

**功能：**
- 根据学习计划调用 RAG 系统
- 检索相关文档内容
- 整理和排序检索结果

**输入：** `learning_plan`
**输出：** `retrieved_docs`

#### 节点 3：练习题生成节点 (Quiz Generator Node)

**文件：** `backend/workflows/nodes/quiz_generator_node.py`

**功能：**
- 基于检索到的文档生成练习题
- 使用结构化输出生成题目、选项、答案
- 支持多种题型（选择题、填空题、简答题）

**输入：** `retrieved_docs`, `learning_plan`
**输出：** `quiz`

#### 节点 4：人机交互节点 (Human-in-the-Loop Node)

**功能：**
- 暂停工作流，等待用户提交答案
- 通过 API 接收用户输入
- 使用 LangGraph 的 `interrupt` 机制

**输入：** `quiz`
**输出：** `user_answers`

#### 节点 5：自动评分节点 (Grading Node)

**文件：** `backend/workflows/nodes/grading_node.py`

**功能：**
- 对比用户答案和标准答案
- 计算得分
- 生成详细的评分报告

**输入：** `quiz`, `user_answers`
**输出：** `score`, `feedback`

#### 节点 6：反馈生成节点 (Feedback Node)

**文件：** `backend/workflows/nodes/feedback_node.py`

**功能：**
- 根据得分生成个性化反馈
- 提供改进建议
- 决定是否需要重新出题

**输入：** `score`, `feedback`
**输出：** `should_retry`, 更新 `retry_count`

### 阶段 3.3：工作流图构建

**文件：** `backend/workflows/study_flow_graph.py`

**功能：** 使用 LangGraph 构建完整的状态图

**关键实现：**

1. **创建 StateGraph**
```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

workflow = StateGraph(StudyFlowState)
```

2. **添加节点**
```python
workflow.add_node("planner", planner_node)
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("quiz_generator", quiz_generator_node)
workflow.add_node("grading", grading_node)
workflow.add_node("feedback", feedback_node)
```

3. **定义边和条件路由**
```python
# 普通边
workflow.add_edge("planner", "retrieval")
workflow.add_edge("retrieval", "quiz_generator")
workflow.add_edge("grading", "feedback")

# 条件边
workflow.add_conditional_edges(
    "feedback",
    should_continue,
    {
        "retry": "quiz_generator",  # 重新出题
        "end": END                   # 结束流程
    }
)
```

4. **配置检查点**
```python
# 使用 SQLite 作为检查点存储
checkpointer = SqliteSaver.from_conn_string("data/checkpoints/study_flow.db")
app = workflow.compile(checkpointer=checkpointer)
```

5. **实现人机交互（HITL）**
```python
# 在 quiz_generator 后添加中断点
workflow.add_node("human_review", lambda state: state)
workflow.add_edge("quiz_generator", "human_review")
workflow.add_edge("human_review", "grading")

# 在 human_review 节点设置中断
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]  # 在此节点前暂停
)
```

### 阶段 3.4：API 接口实现

**文件：** `backend/api/routers/workflow.py`

**端点设计：**

1. **POST /workflow/start** - 启动新的学习工作流
   - 输入：用户问题
   - 输出：thread_id, 初始状态

2. **GET /workflow/status/{thread_id}** - 查询工作流状态
   - 输出：当前状态、进度

3. **POST /workflow/submit-answers** - 提交答题答案
   - 输入：thread_id, 用户答案
   - 输出：评分结果、反馈

4. **POST /workflow/resume/{thread_id}** - 恢复暂停的工作流
   - 输出：继续执行结果

5. **GET /workflow/stream/{thread_id}** - 流式获取工作流执行进度
   - 输出：SSE 流式事件

### 阶段 3.5：流式输出实现

**功能：** 实时输出工作流执行进度

**实现方式：**
```python
async def stream_workflow(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    
    async for event in app.astream_events(initial_state, config, version="v2"):
        if event["event"] == "on_chain_start":
            yield f"data: {json.dumps({'type': 'node_start', 'node': event['name']})}\n\n"
        elif event["event"] == "on_chain_end":
            yield f"data: {json.dumps({'type': 'node_end', 'node': event['name']})}\n\n"
        elif event["event"] == "on_chat_model_stream":
            yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk']})}\n\n"
```

### 阶段 3.6：测试脚本

**文件：** `backend/scripts/test_workflow.py`

**测试场景：**
1. 完整流程测试
2. 检查点恢复测试
3. 人机交互测试
4. 流式输出测试
5. 错误处理测试

## 🔍 关键技术点

### 1. LangGraph State 管理

使用 `Annotated` 和 `add_messages` 实现消息历史的自动合并：

```python
from typing import Annotated
from langgraph.graph.message import add_messages

messages: Annotated[list, add_messages]
```

### 2. Checkpointer 持久化

使用 SQLite 实现检查点存储：

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
```

### 3. Human-in-the-Loop

使用 `interrupt_before` 或 `interrupt_after` 实现暂停：

```python
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)
```

恢复执行：

```python
# 更新状态后继续执行
app.invoke(None, config={"configurable": {"thread_id": thread_id}})
```

### 4. 条件路由

使用条件边实现动态路由：

```python
def should_continue(state: StudyFlowState) -> str:
    if state["should_retry"] and state["retry_count"] < 3:
        return "retry"
    return "end"

workflow.add_conditional_edges("feedback", should_continue)
```

### 5. 流式输出

使用 `astream_events` 实现细粒度的流式输出：

```python
async for event in app.astream_events(input, config, version="v2"):
    # 处理不同类型的事件
    pass
```

## 📚 参考文档

1. **LangGraph Quickstart**: https://docs.langchain.com/oss/python/langgraph/quickstart
2. **LangGraph Persistence**: https://docs.langchain.com/oss/python/langgraph/persistence
3. **LangGraph Streaming**: https://docs.langchain.com/oss/python/langgraph/streaming
4. **LangGraph Interrupts**: https://docs.langchain.com/oss/python/langgraph/interrupts
5. **LangGraph Memory**: https://docs.langchain.com/oss/python/langgraph/add-memory

## ✅ 验收标准

1. ✅ 能够启动完整的学习工作流
2. ✅ 支持检查点的保存和恢复
3. ✅ 实现人机交互暂停和继续
4. ✅ 支持流式输出工作流进度
5. ✅ 根据得分自动决定是否重新出题
6. ✅ 提供完整的 API 接口
7. ✅ 编写详细的测试用例
8. ✅ 提供完整的使用文档

## 📅 开发时间线

- **Day 1-2**: 状态模型设计 + 节点实现
- **Day 3-4**: 工作流图构建 + 检查点集成
- **Day 5**: API 接口实现
- **Day 6**: 流式输出 + 测试
- **Day 7**: 文档编写 + 优化

## 🚀 下一步

完成第 3 阶段后，将为第 4 阶段（DeepAgents 深度研究）打下坚实基础。

