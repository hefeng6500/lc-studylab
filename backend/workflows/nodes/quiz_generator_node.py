"""
练习题生成节点 (Quiz Generator Node)

本节点负责根据学习计划和检索文档生成练习题。
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from ..state import StudyFlowState, QuizQuestion
from core.models import get_chat_model
from config.logging import get_logger

logger = get_logger(__name__)


class QuizQuestionSchema(BaseModel):
    """单个练习题的结构化输出模式"""
    id: str = Field(description="题目唯一标识，如 q1, q2")
    type: str = Field(description="题型：multiple_choice（选择题）、fill_blank（填空题）、short_answer（简答题）")
    question: str = Field(description="题目内容")
    options: List[str] | None = Field(default=None, description="选择题的选项列表（A、B、C、D）")
    answer: str = Field(description="标准答案")
    explanation: str = Field(description="答案解析，解释为什么这是正确答案")
    points: int = Field(description="题目分值")


class QuizSchema(BaseModel):
    """完整练习题集的结构化输出模式"""
    questions: List[QuizQuestionSchema] = Field(description="题目列表，至少5题")
    total_points: int = Field(description="总分")
    time_limit: int = Field(description="建议答题时间（分钟）")


def quiz_generator_node(state: StudyFlowState) -> Dict[str, Any]:
    """
    练习题生成节点
    
    功能：
    1. 基于学习计划和检索文档生成练习题
    2. 生成多种题型（选择题、填空题、简答题）
    3. 使用结构化输出确保题目格式正确
    
    Args:
        state: 当前工作流状态
        
    Returns:
        更新后的状态字典，包含 quiz
    """
    logger.info("[Quiz Generator Node] 开始生成练习题")
    
    try:
        learning_plan = state.get("learning_plan")
        retrieved_docs = state.get("retrieved_docs", [])
        
        if not learning_plan:
            raise ValueError("学习计划不存在，无法生成练习题")
        
        # 获取聊天模型，使用结构化输出
        model = get_chat_model()
        structured_model = model.with_structured_output(QuizSchema)
        
        # 构建上下文：从检索文档中提取内容
        context_parts = []
        if retrieved_docs:
            logger.info(f"[Quiz Generator Node] 使用 {len(retrieved_docs)} 个检索文档作为参考")
            for i, doc in enumerate(retrieved_docs[:3], 1):  # 最多使用前3个文档
                context_parts.append(f"参考文档 {i}:\n{doc['content'][:500]}...")  # 每个文档最多500字符
        
        context = "\n\n".join(context_parts) if context_parts else "无参考文档，请基于通用知识出题。"
        
        # 构建提示词
        system_prompt = """你是一位专业的教育测评专家，擅长设计高质量的练习题。

你的任务是根据学习计划和参考资料，生成一套完整的练习题。

要求：
1. 题目数量：至少5题
2. 题型分布：
   - 选择题（multiple_choice）：3-4题，提供4个选项（A、B、C、D）
   - 填空题（fill_blank）：1-2题
   - 简答题（short_answer）：1题
3. 难度适配：根据学习计划的难度级别出题
4. 覆盖知识点：题目应覆盖学习计划中的关键知识点
5. 答案解析：每题都要提供详细的答案解析
6. 分值分配：
   - 选择题：每题10-15分
   - 填空题：每题15-20分
   - 简答题：每题20-30分
   - 总分控制在100分左右

请确保题目清晰、答案准确、解析详细。"""

        user_prompt = f"""学习计划：
主题：{learning_plan['topic']}
难度：{learning_plan['difficulty']}
关键知识点：
{chr(10).join(f"- {point}" for point in learning_plan['key_points'])}

参考资料：
{context}

请基于以上信息生成练习题。"""

        # 调用模型生成练习题
        logger.info("[Quiz Generator Node] 调用 LLM 生成练习题...")
        quiz_response = structured_model.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # 转换为字典格式
        questions = []
        for q in quiz_response.questions:
            question: QuizQuestion = {
                "id": q.id,
                "type": q.type,
                "question": q.question,
                "options": q.options,
                "answer": q.answer,
                "explanation": q.explanation,
                "points": q.points
            }
            questions.append(question)
        
        quiz = {
            "questions": questions,
            "total_points": quiz_response.total_points,
            "time_limit": quiz_response.time_limit
        }
        
        logger.info(f"[Quiz Generator Node] 成功生成 {len(questions)} 道练习题，总分 {quiz['total_points']} 分")
        
        # 构建题目展示
        quiz_display = f"\n\n📝 **练习题已生成**（共 {len(questions)} 题，总分 {quiz['total_points']} 分，建议用时 {quiz['time_limit']} 分钟）\n\n"
        
        for i, q in enumerate(questions, 1):
            quiz_display += f"**第 {i} 题** ({q['points']} 分)\n"
            quiz_display += f"{q['question']}\n"
            
            if q['type'] == 'multiple_choice' and q['options']:
                for opt in q['options']:
                    quiz_display += f"{opt}\n"
            
            quiz_display += "\n"
        
        quiz_display += "请提交您的答案以获得评分和反馈。"
        
        # 更新状态
        return {
            "quiz": quiz,
            "messages": [{"role": "assistant", "content": quiz_display}],
            "current_step": "quiz_generated",
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[Quiz Generator Node] 生成练习题失败: {str(e)}", exc_info=True)
        return {
            "error": f"练习题生成失败: {str(e)}",
            "error_node": "quiz_generator",
            "current_step": "quiz_error",
            "updated_at": datetime.now().isoformat()
        }

