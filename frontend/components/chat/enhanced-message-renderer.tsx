/**
 * 增强的消息渲染器
 * 集成所有 AI Elements 组件，展示完整的消息信息
 */

"use client";

import React from 'react';
import type { EnhancedMessage } from '@/lib/types';
import { Message, MessageContent, MessageResponse } from '@/components/ai-elements/message';
import {
  Tool,
  ToolHeader,
  ToolContent,
  ToolInput,
  ToolOutput,
} from '@/components/ai-elements/tool';
import {
  Sources,
  SourcesTrigger,
  SourcesContent,
  Source,
} from '@/components/ai-elements/sources';
import {
  Reasoning,
  ReasoningTrigger,
  ReasoningContent,
} from '@/components/ai-elements/reasoning';
import {
  Plan,
  PlanHeader,
  PlanTitle,
  PlanDescription,
  PlanAction,
  PlanTrigger,
  PlanContent,
} from '@/components/ai-elements/plan';
import {
  Queue,
  QueueSection,
  QueueSectionTrigger,
  QueueSectionLabel,
  QueueSectionContent,
  QueueList,
  QueueItem,
  QueueItemIndicator,
  QueueItemContent,
  QueueItemDescription,
} from '@/components/ai-elements/queue';
import {
  Task,
  TaskTrigger,
  TaskContent,
  TaskItem,
  TaskItemFile,
} from '@/components/ai-elements/task';
import {
  ChainOfThought,
  ChainOfThoughtHeader,
  ChainOfThoughtContent,
  ChainOfThoughtStep,
} from '@/components/ai-elements/chain-of-thought';
import {
  Context,
  ContextTrigger,
  ContextContent,
  ContextContentHeader,
  ContextContentBody,
  ContextInputUsage,
  ContextOutputUsage,
  ContextReasoningUsage,
  ContextContentFooter,
} from '@/components/ai-elements/context';
import {
  Checkpoint,
  CheckpointTrigger,
  CheckpointIcon,
} from '@/components/ai-elements/checkpoint';
import { Shimmer } from '@/components/ai-elements/shimmer';

export interface EnhancedMessageRendererProps {
  message: EnhancedMessage;
  isStreaming?: boolean;
}

/**
 * 渲染带引用的内容
 */
function getDisplayContent(message: EnhancedMessage): string {
  const trimmed = message.content?.trim();
  if (trimmed) {
    return message.content;
  }

  const toolResult = message.tools?.find(tool => tool.result && tool.result.trim());
  if (toolResult?.result) {
    return toolResult.result;
  }

  return "";
}

/**
 * 增强的消息渲染器
 */
export function EnhancedMessageRenderer({
  message,
  isStreaming = false,
}: EnhancedMessageRendererProps) {
  // 用户消息：只显示内容
  if (message.role === 'user') {
    return (
      <Message from={message.role}>
        <MessageContent>
          <div className="text-foreground">{message.content}</div>
        </MessageContent>
      </Message>
    );
  }

  // AI 消息：显示完整信息
  return (
    <Message from={message.role}>
      <div className="space-y-4">
        {/* 1. Chain of Thought (思维链) */}
        {message.chainOfThought && (
          <ChainOfThought>
            <ChainOfThoughtHeader />
            <ChainOfThoughtContent>
              {message.chainOfThought.steps.map((step) => (
                <ChainOfThoughtStep
                  key={step.id}
                  label={step.label}
                  description={step.description}
                  status={step.status}
                />
              ))}
            </ChainOfThoughtContent>
          </ChainOfThought>
        )}

        {/* 2. Plan (计划) */}
        {message.plan && (
          <Plan isStreaming={isStreaming && message.plan.isStreaming}>
            <PlanHeader>
              <div className="flex-1">
                <PlanTitle>{message.plan.title}</PlanTitle>
                <PlanDescription>{message.plan.description}</PlanDescription>
              </div>
              <PlanAction>
                <PlanTrigger />
              </PlanAction>
            </PlanHeader>
            <PlanContent>
              <div className="space-y-2">
                {message.plan.steps.map((step, index) => (
                  <div key={step.id} className="flex items-start gap-2">
                    <span className="text-muted-foreground">{index + 1}.</span>
                    <div className="flex-1">
                      <div className="font-medium">{step.title}</div>
                      {step.description && (
                        <div className="text-sm text-muted-foreground">
                          {step.description}
                        </div>
                      )}
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        step.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : step.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : step.status === 'failed'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {step.status}
                    </span>
                  </div>
                ))}
              </div>
            </PlanContent>
          </Plan>
        )}

        {/* 3. Queue (队列) */}
        {message.queue && message.queue.length > 0 && (
          <Queue>
            <QueueSection>
              <QueueSectionTrigger>
                <QueueSectionLabel count={message.queue.length} label="项目" />
              </QueueSectionTrigger>
              <QueueSectionContent>
                <QueueList>
                  {message.queue.map((item) => (
                    <QueueItem key={item.id}>
                      <div className="flex items-start gap-2">
                        <QueueItemIndicator completed={item.status === 'completed'} />
                        <div className="flex-1">
                          <QueueItemContent completed={item.status === 'completed'}>
                            {item.title}
                          </QueueItemContent>
                          {item.description && (
                            <QueueItemDescription completed={item.status === 'completed'}>
                              {item.description}
                            </QueueItemDescription>
                          )}
                        </div>
                      </div>
                    </QueueItem>
                  ))}
                </QueueList>
              </QueueSectionContent>
            </QueueSection>
          </Queue>
        )}

        {/* 4. Tasks (任务) */}
        {message.tasks && message.tasks.length > 0 && (
          <div className="space-y-2">
            {message.tasks.map((task) => (
              <Task key={task.id}>
                <TaskTrigger title={task.title} />
                <TaskContent>
                  <TaskItem>
                    {task.description || task.title}
                    {task.files && task.files.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {task.files.map((file, idx) => (
                          <TaskItemFile key={idx}>{file}</TaskItemFile>
                        ))}
                      </div>
                    )}
                  </TaskItem>
                </TaskContent>
              </Task>
            ))}
          </div>
        )}

        {/* 5. Tools (工具调用) */}
        {message.tools && message.tools.length > 0 && (
          <div className="space-y-2">
            {message.tools.map((tool) => (
              <Tool key={tool.id}>
                <ToolHeader 
                  title={tool.name} 
                  type={tool.type as `tool-${string}`} 
                  state={tool.state} 
                />
                <ToolContent>
                  <ToolInput input={tool.parameters} />
                  {(tool.result || tool.error) && (
                    <ToolOutput output={tool.result} errorText={tool.error} />
                  )}
                </ToolContent>
              </Tool>
            ))}
          </div>
        )}

        {/* 6. Sources (来源引用) */}
        {message.sources && message.sources.length > 0 && (
          <Sources>
            <SourcesTrigger count={message.sources.length} />
            <SourcesContent>
              {message.sources.map((source, idx) => (
                <Source key={idx} href={source.href} title={source.title} />
              ))}
            </SourcesContent>
          </Sources>
        )}

        {/* 7. Reasoning (推理过程) */}
        {message.reasoning && (
          <Reasoning isStreaming={isStreaming} duration={message.reasoning.duration}>
            <ReasoningTrigger />
            <ReasoningContent>{message.reasoning.content}</ReasoningContent>
          </Reasoning>
        )}

        {/* 8. Main Content (主要内容) */}
        <MessageContent>
          {(() => {
            const displayContent = getDisplayContent(message);
            const hasContent = Boolean(displayContent.trim());
            if (!hasContent && isStreaming) {
              return <Shimmer>正在思考...</Shimmer>;
            }
            if (!hasContent) {
              return null;
            }
            return <MessageResponse>{displayContent}</MessageResponse>;
          })()}
        </MessageContent>

        {/* 9. Context Usage (上下文使用) */}
        {/* {message.contextUsage && (
          <Context
            usedTokens={message.contextUsage.usedTokens}
            maxTokens={message.contextUsage.maxTokens}
            usage={message.contextUsage.usage}
            modelId={message.contextUsage.modelId}
          >
            <ContextTrigger />
            <ContextContent>
              <ContextContentHeader />
              <ContextContentBody>
                <ContextInputUsage />
                <ContextOutputUsage />
                {message.contextUsage.usage.reasoningTokens > 0 && (
                  <ContextReasoningUsage />
                )}
              </ContextContentBody>
              <ContextContentFooter />
            </ContextContent>
          </Context>
        )} */}

        {/* 10. Checkpoints (检查点) */}
        {message.checkpoints && message.checkpoints.length > 0 && (
          <Checkpoint>
            {message.checkpoints.map((cp) => (
              <CheckpointTrigger key={cp.id} tooltip={cp.tooltip}>
                <CheckpointIcon />
                {cp.label}
              </CheckpointTrigger>
            ))}
          </Checkpoint>
        )}
      </div>
    </Message>
  );
}
