/**
 * API 客户端 - 封装对 Python 后端的 HTTP 调用
 */

import { ChatRequest, ChatResponse, AgentMode } from './types';

// 后端 API 基础 URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * 通用请求函数
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * 聊天 API - 非流式
 */
export async function chat(chatRequest: ChatRequest): Promise<ChatResponse> {
  return request<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(chatRequest),
  });
}

/**
 * 聊天 API - 流式（返回 ReadableStream）
 */
export async function chatStream(chatRequest: ChatRequest): Promise<Response> {
  const url = `${API_BASE_URL}/chat`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ...chatRequest,
      stream: true,
    }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response;
}

/**
 * RAG 索引 API
 */
export async function buildRagIndex(params: {
  indexName: string;
  documentPath: string;
}): Promise<{ success: boolean; message: string }> {
  return request('/rag/index', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * RAG 查询 API
 */
export async function queryRag(params: {
  indexName: string;
  query: string;
  topK?: number;
}): Promise<ChatResponse> {
  return request('/rag/query', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Workflow API - 启动工作流
 */
export async function startWorkflow(params: {
  topic: string;
  threadId?: string;
}): Promise<{ threadId: string; status: string }> {
  return request('/workflow/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Workflow API - 获取工作流状态
 */
export async function getWorkflowStatus(threadId: string): Promise<{
  status: string;
  currentNode: string;
  history: any[];
}> {
  return request(`/workflow/status/${threadId}`, {
    method: 'GET',
  });
}

/**
 * Deep Research API - 启动研究
 */
export async function startResearch(params: {
  topic: string;
  sessionId?: string;
}): Promise<{ sessionId: string; status: string }> {
  return request('/deep-research/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Deep Research API - 获取研究状态
 */
export async function getResearchStatus(sessionId: string): Promise<{
  status: string;
  report?: string;
  progress: number;
}> {
  return request(`/deep-research/status/${sessionId}`, {
    method: 'GET',
  });
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<{ status: string; version: string }> {
  return request('/health', {
    method: 'GET',
  });
}

