"use client";

import { useState } from "react";
import { AgentMode, MessageMetadata, type EnhancedMessage } from "@/lib/types";
import { useSession } from "@/providers/session-provider";
import { useEnhancedChat } from "@/hooks/use-enhanced-chat";
import { ChatHeader } from "./chat-header";
import { ChatRightPanel } from "./chat-right-panel";
import { Conversation } from "@/components/ai-elements/conversation";
import { Message, MessageContent } from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputBody,
  PromptInputSubmit,
  PromptInputTextarea,
  type PromptInputMessage,
} from "@/components/ai-elements/prompt-input";
import {
  Plan,
  PlanHeader,
  PlanTitle,
  PlanContent,
  PlanDescription,
} from "@/components/ai-elements/plan";
import { Task } from "@/components/ai-elements/task";
import { Checkpoint } from "@/components/ai-elements/checkpoint";
import {
  ChainOfThought,
  ChainOfThoughtHeader,
  ChainOfThoughtContent,
  ChainOfThoughtStep,
} from "@/components/ai-elements/chain-of-thought";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";

interface ChatPanelProps {
  initialMode?: AgentMode;
}

export function ChatPanel({ initialMode = "basic-agent" }: ChatPanelProps) {
  const [mode, setMode] = useState<AgentMode>(initialMode);
  const [showDebug, setShowDebug] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [selectedMessageMetadata, setSelectedMessageMetadata] =
    useState<MessageMetadata>();
  const [input, setInput] = useState("");

  const { currentSession, updateCurrentSession } = useSession();

  // 使用增强的聊天 hook
  const { messages, isStreaming, sendMessage, stopStreaming, error } =
    useEnhancedChat({
      mode,
      onError: (error) => {
        toast.error("发送消息失败", {
          description: error.message,
        });
      },
      onStreamEnd: () => {
        // 更新会话消息计数
        if (currentSession) {
          const firstMessage = messages.find((m) => m.role === "user");
          const content = firstMessage?.content || "";
          updateCurrentSession({
            messageCount: messages.length,
            title: content.slice(0, 50) || currentSession.title,
          });
        }
      },
    });

  // 模式切换时的处理
  const handleModeChange = (newMode: AgentMode) => {
    setMode(newMode);
    if (currentSession) {
      updateCurrentSession({ mode: newMode });
    }
  };

  // 建议提示词
  const suggestions = [
    { text: "介绍一下 LangChain 的核心概念", icon: "💡" },
    { text: "帮我创建一个学习计划", icon: "📚" },
    { text: "搜索并总结最新的 AI 技术", icon: "🔍" },
    { text: "解释一下 RAG 的工作原理", icon: "🤖" },
  ];

  return (
    <div className="flex flex-col h-full">
      <ChatHeader
        mode={mode}
        onModeChange={handleModeChange}
        onDebugToggle={() => setShowDebug(!showDebug)}
        showDebug={showDebug}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* 主对话区 */}
        <div className="flex-1 flex flex-col">
          {/* 消息列表 */}
          <ScrollArea className="flex-1">
            <div className="container max-w-4xl mx-auto py-6 px-4 min-h-full">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center min-h-full py-12">
                  <h2 className="text-2xl font-bold text-center">
                    您今天在想什么？
                  </h2>
                </div>
              ) : (
                <Conversation>
                  {messages.map((message: EnhancedMessage) => {
                    // 从消息中提取元数据
                    const metadata: MessageMetadata = {
                      sources: message.sources,
                      tools: message.tools,
                      reasoning: message.reasoning?.content,
                      plan: message.plan?.steps,
                      task: message.tasks?.[0],
                      checkpoint: message.checkpoints?.[0],
                      chainOfThought: message.chainOfThought?.steps
                        ?.map((s) => s.label)
                        .join("\n"),
                    };

                    return (
                      <div key={message.id} className="space-y-4">
                        <Message
                          from={message.role}
                          onClick={() => {
                            setSelectedMessageMetadata(metadata);
                            setShowRightPanel(true);
                          }}
                        >
                          <MessageContent>{message.content}</MessageContent>
                        </Message>

                        {/* 显示计划 */}
                        {message.plan &&
                          message.plan.steps &&
                          message.plan.steps.length > 0 && (
                            <Plan>
                              <PlanHeader>
                                <PlanTitle>
                                  {message.plan.title || "执行计划"}
                                </PlanTitle>
                                <PlanDescription>
                                  {message.plan.description ||
                                    `共 ${message.plan.steps.length} 个步骤`}
                                </PlanDescription>
                              </PlanHeader>
                              <PlanContent>
                                <ul className="space-y-2">
                                  {message.plan.steps.map((step, idx) => (
                                    <li
                                      key={step.id || idx}
                                      className="flex items-start gap-2"
                                    >
                                      <span className="text-muted-foreground">
                                        {idx + 1}.
                                      </span>
                                      <div>
                                        <div className="font-medium">
                                          {step.title}
                                        </div>
                                        {step.description && (
                                          <div className="text-sm text-muted-foreground">
                                            {step.description}
                                          </div>
                                        )}
                                      </div>
                                    </li>
                                  ))}
                                </ul>
                              </PlanContent>
                            </Plan>
                          )}

                        {/* 显示任务 */}
                        {message.tasks &&
                          message.tasks.length > 0 &&
                          message.tasks.map((task) => (
                            <Task key={task.id} {...task} />
                          ))}

                        {/* 显示检查点 */}
                        {message.checkpoints &&
                          message.checkpoints.length > 0 &&
                          message.checkpoints.map((checkpoint) => (
                            <Checkpoint key={checkpoint.id} {...checkpoint} />
                          ))}

                        {/* 显示思维链 */}
                        {message.chainOfThought &&
                          message.chainOfThought.steps &&
                          message.chainOfThought.steps.length > 0 && (
                            <ChainOfThought>
                              <ChainOfThoughtHeader>
                                思维链
                              </ChainOfThoughtHeader>
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
                      </div>
                    );
                  })}

                  {/* 加载状态 */}
                  {isStreaming && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                      <span>思考中...</span>
                    </div>
                  )}
                </Conversation>
              )}
            </div>
          </ScrollArea>

          {/* 输入区 */}
          <div className="border-t bg-background p-4">
            <div className="container max-w-4xl mx-auto">
              <PromptInput
                onSubmit={async (message: PromptInputMessage) => {
                  if (message.text?.trim()) {
                    sendMessage(message.text);
                    setInput("");
                  }
                }}
              >
                <PromptInputBody>
                  <PromptInputTextarea
                    placeholder={`在 ${mode} 模式下输入消息...`}
                    disabled={isStreaming}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                  />
                </PromptInputBody>
                <PromptInputSubmit disabled={isStreaming || !input.trim()} />
                {isStreaming && (
                  <button
                    type="button"
                    onClick={stopStreaming}
                    className="absolute right-2 top-2 rounded-md p-1 text-muted-foreground hover:bg-muted"
                  >
                    停止
                  </button>
                )}
              </PromptInput>
            </div>
          </div>
        </div>

        {/* 右侧面板 */}
        {showRightPanel && (
          <ChatRightPanel
            metadata={selectedMessageMetadata}
            rawJson={showDebug ? { messages, mode, currentSession } : undefined}
          />
        )}
      </div>
    </div>
  );
}
