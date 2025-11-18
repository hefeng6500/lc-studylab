"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Sources, 
  SourcesTrigger, 
  SourcesContent, 
  Source 
} from "@/components/ai-elements/sources"
import { 
  Reasoning, 
  ReasoningTrigger, 
  ReasoningContent 
} from "@/components/ai-elements/reasoning"
import { 
  Tool, 
  ToolHeader, 
  ToolContent, 
  ToolInput, 
  ToolOutput 
} from "@/components/ai-elements/tool"
import { MessageMetadata } from "@/lib/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ChatRightPanelProps {
  metadata?: MessageMetadata
  rawJson?: any
}

export function ChatRightPanel({ metadata, rawJson }: ChatRightPanelProps) {
  const [activeTab, setActiveTab] = useState("sources")

  const hasSources = metadata?.sources && metadata.sources.length > 0
  const hasTools = metadata?.tools && metadata.tools.length > 0
  const hasReasoning = !!metadata?.reasoning
  const hasChainOfThought = !!metadata?.chainOfThought

  return (
    <div className="w-80 border-l bg-background flex flex-col h-full">
      <div className="p-4 border-b">
        <h3 className="font-semibold">详细信息</h3>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="grid w-full grid-cols-4 px-4">
          <TabsTrigger value="sources" className="relative">
            来源
            {hasSources && (
              <Badge variant="secondary" className="ml-1 h-5 w-5 rounded-full p-0 text-xs">
                {metadata.sources!.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="tools" className="relative">
            工具
            {hasTools && (
              <Badge variant="secondary" className="ml-1 h-5 w-5 rounded-full p-0 text-xs">
                {metadata.tools!.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="reasoning">推理</TabsTrigger>
          <TabsTrigger value="json">JSON</TabsTrigger>
        </TabsList>

        <ScrollArea className="flex-1">
          <TabsContent value="sources" className="p-4 space-y-4">
            {hasSources ? (
              <Sources>
                <SourcesTrigger count={metadata.sources!.length} />
                <SourcesContent>
                  {metadata.sources!.map((source, idx) => (
                    <Source 
                      key={idx} 
                      href={source.href || "#"} 
                      title={source.title || `来源 ${idx + 1}`}
                    >
                      {source.content && (
                        <span className="block text-xs text-muted-foreground mt-1">
                          {source.content}
                        </span>
                      )}
                    </Source>
                  ))}
                </SourcesContent>
              </Sources>
            ) : (
              <EmptyState message="暂无来源信息" />
            )}
          </TabsContent>

          <TabsContent value="tools" className="p-4 space-y-4">
            {hasTools ? (
              metadata.tools!.map((tool) => (
                <Tool key={tool.id}>
                  <ToolHeader 
                    title={tool.name} 
                    type={tool.type as `tool-${string}`} 
                    state={tool.state} 
                  />
                  <ToolContent>
                    <ToolInput input={tool.parameters} />
                    {(tool.result || tool.error) && (
                      <ToolOutput 
                        output={tool.result} 
                        errorText={tool.error} 
                      />
                    )}
                  </ToolContent>
                </Tool>
              ))
            ) : (
              <EmptyState message="暂无工具调用" />
            )}
          </TabsContent>

          <TabsContent value="reasoning" className="p-4 space-y-4">
            {hasReasoning || hasChainOfThought ? (
              <>
                {hasReasoning && (
                  <Reasoning>
                    <ReasoningTrigger />
                    <ReasoningContent>
                      {metadata.reasoning!}
                    </ReasoningContent>
                  </Reasoning>
                )}
                {hasChainOfThought && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">思维链</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {metadata.chainOfThought}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <EmptyState message="暂无推理信息" />
            )}
          </TabsContent>

          <TabsContent value="json" className="p-4">
            {rawJson ? (
              <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto">
                {JSON.stringify(rawJson, null, 2)}
              </pre>
            ) : (
              <EmptyState message="暂无 JSON 数据" />
            )}
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-32 text-sm text-muted-foreground">
      {message}
    </div>
  )
}

