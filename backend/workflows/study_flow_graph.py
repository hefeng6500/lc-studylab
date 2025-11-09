"""
学习工作流图 (Study Flow Graph)

本模块使用 LangGraph 构建完整的学习工作流，包括：
- 状态管理
- 检查点持久化
- 人机交互（Human-in-the-Loop）
- 条件路由
- 流式输出
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import StudyFlowState
from .nodes import (
    planner_node,
    retrieval_node,
    quiz_generator_node,
    grading_node,
    feedback_node
)
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


def should_continue(state: StudyFlowState) -> Literal["retry", "end"]:
    """
    条件路由函数：决定是否需要重新出题
    
    规则：
    - 如果 should_retry 为 True 且重试次数 < 3，则返回 "retry"
    - 否则返回 "end"
    
    Args:
        state: 当前工作流状态
        
    Returns:
        "retry" 或 "end"
    """
    should_retry = state.get("should_retry", False)
    retry_count = state.get("retry_count", 0)
    
    logger.info(f"[Conditional Edge] should_retry={should_retry}, retry_count={retry_count}")
    
    if should_retry and retry_count < 3:
        logger.info("[Conditional Edge] 决定重新出题")
        return "retry"
    else:
        logger.info("[Conditional Edge] 决定结束流程")
        return "end"


def create_study_flow_graph(checkpointer_path: str = None) -> StateGraph:
    """
    创建学习工作流图
    
    工作流结构：
    START
      ↓
    planner (规划节点)
      ↓
    retrieval (检索节点)
      ↓
    quiz_generator (生成练习题)
      ↓
    human_review (人机交互：等待用户答题) ← 这里会暂停
      ↓
    grading (评分节点)
      ↓
    feedback (反馈节点)
      ↓
    [条件分支]
      ├─ retry → quiz_generator (重新出题)
      └─ end → END
    
    Args:
        checkpointer_path: 检查点数据库路径，如果为 None 则使用默认路径
        
    Returns:
        编译后的工作流图
    """
    logger.info("[Study Flow Graph] 开始创建学习工作流图")
    
    # 创建状态图
    workflow = StateGraph(StudyFlowState)
    
    # ==================== 添加节点 ====================
    logger.info("[Study Flow Graph] 添加工作流节点...")
    
    # 1. 学习规划节点
    workflow.add_node("planner", planner_node)
    
    # 2. 文档检索节点
    workflow.add_node("retrieval", retrieval_node)
    
    # 3. 练习题生成节点
    workflow.add_node("quiz_generator", quiz_generator_node)
    
    # 4. 人机交互节点（实际上是一个空节点，用于标记暂停点）
    # 在这个节点之前，工作流会暂停，等待用户提交答案
    def human_review_node(state: StudyFlowState):
        """人机交互节点：等待用户提交答案"""
        logger.info("[Human Review Node] 等待用户提交答案...")
        return {
            "current_step": "waiting_for_answers",
            "updated_at": datetime.now().isoformat()
        }
    
    workflow.add_node("human_review", human_review_node)
    
    # 5. 评分节点
    workflow.add_node("grading", grading_node)
    
    # 6. 反馈节点
    workflow.add_node("feedback", feedback_node)
    
    # ==================== 添加边 ====================
    logger.info("[Study Flow Graph] 添加工作流边...")
    
    # 设置入口点
    workflow.set_entry_point("planner")
    
    # 普通边：定义节点之间的固定连接
    workflow.add_edge("planner", "retrieval")
    workflow.add_edge("retrieval", "quiz_generator")
    workflow.add_edge("quiz_generator", "human_review")  # 生成题目后进入人机交互
    workflow.add_edge("human_review", "grading")         # 用户提交答案后进行评分
    workflow.add_edge("grading", "feedback")             # 评分后生成反馈
    
    # 条件边：根据反馈决定是重新出题还是结束
    workflow.add_conditional_edges(
        "feedback",                    # 从 feedback 节点出发
        should_continue,               # 使用 should_continue 函数决定路由
        {
            "retry": "quiz_generator", # 如果需要重试，回到 quiz_generator
            "end": END                 # 否则结束流程
        }
    )
    
    # ==================== 配置检查点 ====================
    if checkpointer_path is None:
        # 使用默认路径
        checkpointer_path = os.path.join(
            settings.DATA_DIR,
            "checkpoints",
            "study_flow.db"
        )
    
    # 确保目录存在
    os.makedirs(os.path.dirname(checkpointer_path), exist_ok=True)
    
    logger.info(f"[Study Flow Graph] 配置检查点存储: {checkpointer_path}")
    
    # 创建内存检查点保存器
    # 注意：LangGraph 1.0.2 使用 MemorySaver，不支持持久化到文件
    # 如需持久化，请升级到支持 SqliteSaver 的更高版本
    checkpointer = MemorySaver()
    
    # ==================== 编译工作流 ====================
    logger.info("[Study Flow Graph] 编译工作流图...")
    
    # 编译工作流，配置检查点和中断点
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review"]  # 在 human_review 节点之前暂停
    )
    
    logger.info("[Study Flow Graph] 学习工作流图创建完成")
    logger.info("[Study Flow Graph] 中断点设置在: human_review (等待用户答题)")
    
    return app


# ==================== 全局工作流实例 ====================
# 创建一个全局的工作流实例，供 API 使用
study_flow_app = None


def get_study_flow_app():
    """
    获取学习工作流应用实例（单例模式）
    
    Returns:
        编译后的工作流应用
    """
    global study_flow_app
    
    if study_flow_app is None:
        logger.info("[Study Flow Graph] 初始化全局工作流实例")
        study_flow_app = create_study_flow_graph()
    
    return study_flow_app


# ==================== 工作流执行辅助函数 ====================

def start_study_flow(user_question: str, thread_id: str) -> dict:
    """
    启动新的学习工作流
    
    Args:
        user_question: 用户的学习问题
        thread_id: 线程 ID（用于标识会话）
        
    Returns:
        工作流执行结果
    """
    logger.info(f"[Study Flow] 启动新的学习工作流，thread_id={thread_id}")
    
    app = get_study_flow_app()
    
    # 初始化状态
    initial_state: StudyFlowState = {
        "messages": [],
        "user_question": user_question,
        "learning_plan": None,
        "retrieved_docs": None,
        "quiz": None,
        "user_answers": None,
        "score": None,
        "score_details": None,
        "feedback": None,
        "retry_count": 0,
        "should_retry": False,
        "current_step": "start",
        "thread_id": thread_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "error": None,
        "error_node": None
    }
    
    # 配置（包含 thread_id）
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # 执行工作流（会在 human_review 之前暂停）
    logger.info("[Study Flow] 开始执行工作流...")
    result = app.invoke(initial_state, config)
    
    logger.info(f"[Study Flow] 工作流暂停在: {result.get('current_step')}")
    
    return result


def submit_answers(thread_id: str, user_answers: dict) -> dict:
    """
    提交用户答案，继续执行工作流
    
    Args:
        thread_id: 线程 ID
        user_answers: 用户答案字典 {"q1": "A", "q2": "xxx", ...}
        
    Returns:
        工作流执行结果
    """
    logger.info(f"[Study Flow] 提交答案，thread_id={thread_id}")
    
    app = get_study_flow_app()
    
    # 配置
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # 获取当前状态
    current_state = app.get_state(config)
    logger.info(f"[Study Flow] 当前状态: {current_state.values.get('current_step')}")
    
    # 更新状态：添加用户答案
    app.update_state(
        config,
        {
            "user_answers": user_answers,
            "updated_at": datetime.now().isoformat()
        }
    )
    
    # 继续执行工作流（从 human_review 之后继续）
    logger.info("[Study Flow] 继续执行工作流...")
    result = app.invoke(None, config)
    
    logger.info(f"[Study Flow] 工作流执行完成，最终状态: {result.get('current_step')}")
    
    return result


def get_workflow_state(thread_id: str) -> dict:
    """
    获取工作流的当前状态
    
    Args:
        thread_id: 线程 ID
        
    Returns:
        当前状态字典
    """
    logger.info(f"[Study Flow] 获取工作流状态，thread_id={thread_id}")
    
    app = get_study_flow_app()
    
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    state = app.get_state(config)
    
    return state.values if state else None


def get_workflow_history(thread_id: str) -> list:
    """
    获取工作流的执行历史
    
    Args:
        thread_id: 线程 ID
        
    Returns:
        历史状态列表
    """
    logger.info(f"[Study Flow] 获取工作流历史，thread_id={thread_id}")
    
    app = get_study_flow_app()
    
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    history = []
    for state in app.get_state_history(config):
        history.append({
            "checkpoint_id": state.config["configurable"].get("checkpoint_id"),
            "step": state.values.get("current_step"),
            "timestamp": state.values.get("updated_at")
        })
    
    return history

