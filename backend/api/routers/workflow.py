"""
工作流 API 路由

提供学习工作流的 HTTP 接口，包括：
- 启动工作流
- 提交答案
- 查询状态
- 流式输出
"""

import logging
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from workflows.study_flow_graph import (
    start_study_flow,
    submit_answers,
    get_workflow_state,
    get_workflow_history,
    get_study_flow_app
)
from config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/workflow", tags=["workflow"])


# ==================== 请求/响应模型 ====================

class StartWorkflowRequest(BaseModel):
    """启动工作流请求"""
    user_question: str = Field(..., description="用户的学习问题", min_length=1)
    thread_id: Optional[str] = Field(None, description="可选的线程ID，不提供则自动生成")


class StartWorkflowResponse(BaseModel):
    """启动工作流响应"""
    thread_id: str = Field(..., description="线程ID，用于后续操作")
    status: str = Field(..., description="工作流状态")
    current_step: str = Field(..., description="当前执行步骤")
    learning_plan: Optional[Dict[str, Any]] = Field(None, description="学习计划")
    quiz: Optional[Dict[str, Any]] = Field(None, description="生成的练习题")
    message: str = Field(..., description="状态消息")


class SubmitAnswersRequest(BaseModel):
    """提交答案请求"""
    thread_id: str = Field(..., description="线程ID")
    answers: Dict[str, str] = Field(..., description="用户答案，格式: {question_id: answer}")


class SubmitAnswersResponse(BaseModel):
    """提交答案响应"""
    thread_id: str
    status: str
    score: Optional[int] = Field(None, description="得分（0-100）")
    score_details: Optional[Dict[str, Any]] = Field(None, description="详细评分")
    feedback: Optional[str] = Field(None, description="反馈信息")
    should_retry: bool = Field(False, description="是否需要重新出题")
    message: str


class WorkflowStatusResponse(BaseModel):
    """工作流状态响应"""
    thread_id: str
    current_step: str
    created_at: Optional[str]
    updated_at: Optional[str]
    state: Dict[str, Any]


# ==================== API 端点 ====================

@router.post("/start", response_model=StartWorkflowResponse)
async def start_workflow(request: StartWorkflowRequest):
    """
    启动新的学习工作流
    
    工作流会自动执行以下步骤：
    1. 分析用户问题，生成学习计划
    2. 检索相关文档
    3. 生成练习题
    4. 暂停，等待用户提交答案
    
    返回练习题后，需要调用 /submit-answers 提交答案继续流程。
    """
    try:
        # 生成或使用提供的 thread_id
        thread_id = request.thread_id or f"study_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"[API] 启动工作流，thread_id={thread_id}, question={request.user_question}")
        
        # 启动工作流
        result = start_study_flow(
            user_question=request.user_question,
            thread_id=thread_id
        )
        
        # 检查是否有错误
        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"工作流执行失败: {result['error']}"
            )
        
        # 构建响应
        response = StartWorkflowResponse(
            thread_id=thread_id,
            status="waiting_for_answers",
            current_step=result.get("current_step", "unknown"),
            learning_plan=result.get("learning_plan"),
            quiz=result.get("quiz"),
            message="学习计划和练习题已生成，请提交答案。"
        )
        
        logger.info(f"[API] 工作流启动成功，thread_id={thread_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"[API] 启动工作流失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-answers", response_model=SubmitAnswersResponse)
async def submit_user_answers(request: SubmitAnswersRequest):
    """
    提交用户答案，继续执行工作流
    
    工作流会自动执行以下步骤：
    1. 对用户答案进行评分
    2. 生成个性化反馈
    3. 根据得分决定是否重新出题
    
    如果 should_retry 为 True，会自动生成新的练习题，
    需要再次调用此接口提交答案。
    """
    try:
        thread_id = request.thread_id
        
        logger.info(f"[API] 提交答案，thread_id={thread_id}")
        
        # 提交答案并继续执行
        result = submit_answers(
            thread_id=thread_id,
            user_answers=request.answers
        )
        
        # 检查是否有错误
        if result.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"评分失败: {result['error']}"
            )
        
        # 构建响应
        should_retry = result.get("should_retry", False)
        
        if should_retry:
            status = "retry"
            message = "得分未达标，已重新生成练习题，请继续答题。"
        else:
            score = result.get("score", 0)
            if score >= 60:
                status = "completed"
                message = "恭喜通过测验！"
            else:
                status = "failed"
                message = "已达到最大重试次数，建议复习后再来挑战。"
        
        response = SubmitAnswersResponse(
            thread_id=thread_id,
            status=status,
            score=result.get("score"),
            score_details=result.get("score_details"),
            feedback=result.get("feedback"),
            should_retry=should_retry,
            message=message
        )
        
        logger.info(f"[API] 答案提交成功，thread_id={thread_id}, status={status}")
        
        return response
        
    except Exception as e:
        logger.error(f"[API] 提交答案失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{thread_id}", response_model=WorkflowStatusResponse)
async def get_status(thread_id: str):
    """
    获取工作流的当前状态
    
    可以查询工作流的执行进度、当前步骤等信息。
    """
    try:
        logger.info(f"[API] 查询工作流状态，thread_id={thread_id}")
        
        state = get_workflow_state(thread_id)
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail=f"未找到 thread_id={thread_id} 的工作流"
            )
        
        response = WorkflowStatusResponse(
            thread_id=thread_id,
            current_step=state.get("current_step", "unknown"),
            created_at=state.get("created_at"),
            updated_at=state.get("updated_at"),
            state=state
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] 查询状态失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{thread_id}")
async def get_history(thread_id: str):
    """
    获取工作流的执行历史
    
    返回工作流的所有检查点历史，可用于回溯和调试。
    """
    try:
        logger.info(f"[API] 查询工作流历史，thread_id={thread_id}")
        
        history = get_workflow_history(thread_id)
        
        return {
            "thread_id": thread_id,
            "history": history
        }
        
    except Exception as e:
        logger.error(f"[API] 查询历史失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{thread_id}")
async def stream_workflow(thread_id: str):
    """
    流式获取工作流执行进度（Server-Sent Events）
    
    实时推送工作流的执行事件，包括：
    - 节点开始/结束事件
    - LLM 生成的 token 流
    - 状态更新事件
    
    注意：此端点用于实时监控，需要在工作流执行前调用。
    """
    async def event_generator():
        """生成 SSE 事件流"""
        try:
            app = get_study_flow_app()
            
            # 获取当前状态
            config = {"configurable": {"thread_id": thread_id}}
            state = get_workflow_state(thread_id)
            
            if not state:
                yield f"data: {json.dumps({'type': 'error', 'message': '工作流不存在'})}\n\n"
                return
            
            # 发送初始状态
            yield f"data: {json.dumps({'type': 'start', 'state': state.get('current_step')})}\n\n"
            
            # 使用 astream_events 获取流式事件
            async for event in app.astream_events(None, config, version="v2"):
                event_type = event.get("event")
                event_name = event.get("name", "")
                
                # 节点开始事件
                if event_type == "on_chain_start":
                    yield f"data: {json.dumps({'type': 'node_start', 'node': event_name})}\n\n"
                
                # 节点结束事件
                elif event_type == "on_chain_end":
                    yield f"data: {json.dumps({'type': 'node_end', 'node': event_name})}\n\n"
                
                # LLM token 流
                elif event_type == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content"):
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
                
                # 工具调用事件
                elif event_type == "on_tool_start":
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': event_name})}\n\n"
                
                elif event_type == "on_tool_end":
                    yield f"data: {json.dumps({'type': 'tool_end', 'tool': event_name})}\n\n"
            
            # 发送完成事件
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            logger.error(f"[API] 流式输出失败: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.delete("/{thread_id}")
async def delete_workflow(thread_id: str):
    """
    删除工作流及其检查点数据
    
    注意：此操作不可恢复。
    """
    try:
        logger.info(f"[API] 删除工作流，thread_id={thread_id}")
        
        # TODO: 实现删除检查点的逻辑
        # 目前 LangGraph 的 SQLiteSaver 没有直接的删除接口
        # 可以考虑直接操作数据库或等待官方支持
        
        return {
            "thread_id": thread_id,
            "status": "deleted",
            "message": "工作流已删除（注意：检查点数据可能仍然存在）"
        }
        
    except Exception as e:
        logger.error(f"[API] 删除工作流失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

