/**
 * 前端类型定义 - 增强版
 * 支持所有 AI Elements 组件所需的数据结构
 */

import type { ToolUIPart } from "ai";

// 后端模式类型
export type AgentMode =
  | "basic-agent"
  | "rag"
  | "workflow"
  | "deep-research"
  | "guarded";

// 会话类型
export interface Session {
  id: string;
  title: string;
  mode: AgentMode;
  threadId?: string; // 后端 LangGraph/DeepAgents thread_id
  createdAt: number;
  updatedAt: number;
  messageCount: number;
}

// ===== 增强的消息类型 =====

// 消息版本（支持分支）
export interface MessageVersion {
  id: string;
  content: string;
  createdAt: Date;
}

// 推理过程
export interface Reasoning {
  content: string;
  duration: number; // 秒
}

// 工具调用（映射 AI SDK ToolUIPart）
export interface ToolCall {
  id: string;
  name: string;
  description?: string;
  type: string; // e.g., "tool-call-get_time"
  state: ToolUIPart["state"];
  parameters: Record<string, any>;
  result?: any;
  error?: string;
  requiresApproval?: boolean;
}

// RAG 来源
export interface Source {
  href: string;
  title: string;
  content?: string;
  similarity?: number;
  metadata?: Record<string, any>;
}

// 内联引用
export interface Citation {
  index: number;
  href?: string;
  title?: string;
  position: number; // 在文本中的位置
  text: string; // e.g., "[1]"
}

// 计划
export interface Plan {
  title: string;
  description: string;
  steps: PlanStep[];
  isStreaming?: boolean;
}

// 计划步骤
export interface PlanStep {
  id: string;
  title: string;
  description?: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  order?: number;
}

// 任务
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  files?: string[]; // 关联的文件
}

// 队列项目
export interface QueueItem {
  id: string;
  title: string;
  description?: string;
  status: "pending" | "completed";
  type?: "message" | "todo" | "file";
  parts?: any[]; // 如果是消息类型
}

// 思维链
export interface ChainOfThought {
  steps: ChainOfThoughtStep[];
}

export interface ChainOfThoughtStep {
  id: string;
  label: string;
  description?: string;
  status: "complete" | "active" | "pending";
  icon?: string;
  searchResults?: any[];
  image?: {
    url: string;
    caption?: string;
  };
}

// 上下文使用情况
export interface ContextUsage {
  usedTokens: number;
  maxTokens: number;
  usage: {
    inputTokens: number;
    outputTokens: number;
    reasoningTokens: number;
    cachedInputTokens?: number;
  };
  modelId: string;
  percentage?: number;
}

// 检查点
export interface Checkpoint {
  id: string;
  label: string;
  tooltip?: string;
  threadId?: string;
  timestamp: number;
  state?: Record<string, any>;
}

// 增强的消息类型
export interface EnhancedMessage {
  // 基础字段
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;

  // 分支管理
  versions?: MessageVersion[];
  currentVersionIndex?: number;

  // AI Elements 组件数据
  chainOfThought?: ChainOfThought;
  reasoning?: Reasoning;
  tools?: ToolCall[];
  sources?: Source[];
  citations?: Citation[];
  plan?: Plan;
  tasks?: Task[];
  queue?: QueueItem[];
  contextUsage?: ContextUsage;
  checkpoints?: Checkpoint[];

  // 元数据
  metadata?: Record<string, any>;
}

// ===== 流式数据类型 =====

// SSE 流式数据块
export type StreamChunk =
  | { type: "start"; message: string }
  | { type: "chunk"; content: string }
  | { type: "tool"; data: ToolCall }
  | { type: "tool_result"; data: ToolCall }
  | { type: "reasoning"; data: Reasoning }
  | { type: "source"; data: Source }
  | { type: "sources"; data: Source[] }
  | { type: "plan"; data: Plan }
  | { type: "task"; data: Task }
  | { type: "queue"; data: QueueItem[] }
  | { type: "context"; data: ContextUsage }
  | { type: "citation"; data: Citation }
  | { type: "chainOfThought"; data: ChainOfThought }
  | { type: "suggestions"; data: string[] }
  | { type: "end"; message: string }
  | { type: "error"; message: string; error: string };

// API 请求
export interface ChatRequest {
  message: string;
  chat_history?: Array<{ role: string; content: string }>;
  mode?: string;
  threadId?: string;
  sessionId?: string;
  use_tools?: boolean;
  config?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
  };
}

// 消息元数据（用于 AI Elements 组件）
export interface MessageMetadata {
  sources?: Source[];
  tools?: ToolCall[];
  reasoning?: string;
  plan?: PlanStep[];
  task?: Task;
  checkpoint?: Checkpoint;
  chainOfThought?: string;
}

// API 响应
export interface ChatResponse {
  message: string;
  metadata?: MessageMetadata;
  threadId?: string;
  error?: string;
}

// 模型配置
export interface ModelConfig {
  provider: "openai" | "anthropic" | "google" | "deepseek";
  model: string;
  displayName: string;
  maxTokens: number;
}

// 应用配置
export interface AppConfig {
  backendUrl: string;
  defaultModel: ModelConfig;
  enableGuardrails: boolean;
  streamingEnabled: boolean;
}
