"""
学习规划节点 (Planner Node)

本节点负责分析用户问题，生成个性化的学习计划。
"""

import logging
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage

from ..state import StudyFlowState, LearningPlan
from core.models import get_chat_model
from config.logging import get_logger

logger = get_logger(__name__)


class LearningPlanSchema(BaseModel):
    """学习计划的结构化输出模式"""
    topic: str = Field(description="学习主题")
    objectives: list[str] = Field(description="学习目标列表，至少3个")
    key_points: list[str] = Field(description="关键知识点列表，至少5个")
    difficulty: str = Field(description="难度级别：beginner, intermediate, advanced")
    estimated_time: int = Field(description="预计学习时间（分钟）")


def planner_node(state: StudyFlowState) -> Dict[str, Any]:
    """
    学习规划节点
    
    功能：
    1. 分析用户问题
    2. 生成结构化的学习计划
    3. 使用 LLM 的结构化输出功能
    
    Args:
        state: 当前工作流状态
        
    Returns:
        更新后的状态字典，包含 learning_plan
    """
    logger.info(f"[Planner Node] 开始生成学习计划，用户问题: {state['user_question']}")
    
    try:
        # 获取聊天模型，使用结构化输出
        model = get_chat_model()
        structured_model = model.with_structured_output(LearningPlanSchema)
        
        # 构建提示词
        system_prompt = """你是一位经验丰富的学习规划专家。
        
你的任务是根据用户的学习问题，制定一个详细的学习计划。

请分析问题的难度和范围，然后生成：
1. 学习主题：简洁明确的主题描述
2. 学习目标：至少3个具体、可衡量的学习目标
3. 关键知识点：至少5个需要掌握的核心知识点
4. 难度级别：beginner（入门）、intermediate（中级）或 advanced（高级）
5. 预计学习时间：合理估计完成学习所需的时间（分钟）

请确保计划具有针对性和可操作性。"""

        user_prompt = f"用户的学习问题：{state['user_question']}\n\n请为此问题制定学习计划。"
        
        # 调用模型生成学习计划
        logger.info("[Planner Node] 调用 LLM 生成学习计划...")
        plan_response = structured_model.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # 转换为字典格式
        learning_plan: LearningPlan = {
            "topic": plan_response.topic,
            "objectives": plan_response.objectives,
            "key_points": plan_response.key_points,
            "difficulty": plan_response.difficulty,
            "estimated_time": plan_response.estimated_time
        }
        
        logger.info(f"[Planner Node] 学习计划生成成功: {learning_plan['topic']}")
        logger.debug(f"[Planner Node] 学习计划详情: {learning_plan}")
        
        # 构建 AI 消息
        plan_summary = f"""已为您制定学习计划：

📚 **学习主题**: {learning_plan['topic']}

🎯 **学习目标**:
{chr(10).join(f"{i+1}. {obj}" for i, obj in enumerate(learning_plan['objectives']))}

💡 **关键知识点**:
{chr(10).join(f"• {point}" for point in learning_plan['key_points'])}

📊 **难度级别**: {learning_plan['difficulty']}
⏱️ **预计时间**: {learning_plan['estimated_time']} 分钟
"""
        
        # 更新状态
        return {
            "learning_plan": learning_plan,
            "messages": [AIMessage(content=plan_summary)],
            "current_step": "planner",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[Planner Node] 生成学习计划失败: {str(e)}", exc_info=True)
        return {
            "error": f"学习计划生成失败: {str(e)}",
            "error_node": "planner",
            "current_step": "planner_error",
            "updated_at": datetime.now().isoformat()
        }

