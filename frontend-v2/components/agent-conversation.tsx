"use client"

import React, { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { 
  Send, 
  User, 
  Bot, 
  MessageSquare,
  Clock
} from "lucide-react"
import type { ConversationMessage, AgentInfo } from "@/types/agent"

interface AgentConversationProps {
  agent: AgentInfo | null
  conversationHistory: ConversationMessage[]
  onSendMessage: (content: string) => void
  isLoading?: boolean
}

export function AgentConversation({
  agent,
  conversationHistory,
  onSendMessage,
  isLoading = false,
}: AgentConversationProps) {
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput("")
    }
  }

  const renderMessage = (message: ConversationMessage) => {
    const isUser = message.role === "user"
    
    return (
      <div
        key={message.id}
        className={`flex gap-3 mb-6 ${isUser ? "justify-end" : "justify-start"}`}
      >
        <div className={`flex gap-3 max-w-[80%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
          <div className="flex-shrink-0 mt-1">
            {isUser ? (
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
            ) : (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                <Bot className="h-4 w-4 text-white" />
              </div>
            )}
          </div>
          <div
            className={`rounded-lg p-4 shadow-sm ${
              isUser 
                ? "bg-slate-700 text-white" 
                : "bg-white text-slate-900 border border-slate-200"
            }`}
          >
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
            <p className={`text-xs mt-2 ${isUser ? "opacity-70" : "text-slate-500"}`}>
              {message.timestamp.toLocaleTimeString("ja-JP")}
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-50">
        <div className="text-center text-slate-500">
          <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-30" />
          <p className="text-sm">エージェントを選択してください</p>
          <p className="text-xs mt-1">左側のリストからエージェントを選択すると会話を開始できます</p>
        </div>
      </div>
    )
  }

  return (
    <Card className="h-full flex flex-col shadow-lg border-slate-200">
      <CardHeader className="border-b border-slate-200 pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CardTitle className="text-lg font-semibold text-slate-900">
              {agent.purpose}
            </CardTitle>
            <Badge variant="outline" className="text-xs">
              ID: {agent.agent_id.slice(-8)}
            </Badge>
            <Badge 
              className={`text-xs ${
                agent.status === "todo" ? "bg-blue-100 text-blue-800" :
                agent.status === "doing" ? "bg-green-100 text-green-800" :
                agent.status === "waiting" ? "bg-yellow-100 text-yellow-800" :
                "bg-red-100 text-red-800"
              }`}
            >
              {agent.status === "todo" ? "実行待ち" :
               agent.status === "doing" ? "実行中" :
               agent.status === "waiting" ? "待機中" :
               "入力待ち"}
            </Badge>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Clock className="h-4 w-4" />
            <span>{conversationHistory.length} メッセージ</span>
          </div>
        </div>
        <p className="text-sm text-slate-600 mt-2">
          {agent.purpose}
        </p>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Conversation History */}
        <ScrollArea className="flex-1 px-6 py-4">
          {conversationHistory.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div className="text-slate-500">
                <MessageSquare className="h-8 w-8 mx-auto mb-3 opacity-50" />
                <p className="text-sm">会話を開始してください</p>
                <p className="text-xs mt-1">下部のテキストエリアにメッセージを入力してください</p>
              </div>
            </div>
          ) : (
            <div className="space-y-0">
              {conversationHistory.map(renderMessage)}
              {isLoading && (
                <div className="flex gap-3 mb-6">
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="bg-white text-slate-900 border border-slate-200 rounded-lg p-4 shadow-sm">
                    <div className="flex items-center gap-2">
                      <div className="animate-bounce w-2 h-2 bg-slate-400 rounded-full"></div>
                      <div className="animate-bounce w-2 h-2 bg-slate-400 rounded-full" style={{ animationDelay: "0.1s" }}></div>
                      <div className="animate-bounce w-2 h-2 bg-slate-400 rounded-full" style={{ animationDelay: "0.2s" }}></div>
                      <span className="text-xs text-slate-500 ml-2">エージェントが応答中...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Message Input */}
        <div className="border-t border-slate-200 p-6 bg-white">
          <form onSubmit={handleSubmit} className="space-y-3">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="エージェントにメッセージを送信..."
              className="min-h-[80px] resize-none border-slate-300 focus:border-blue-500 focus:ring-blue-500"
              disabled={isLoading || agent.status === "needs_input" || agent.status === "waiting"}
            />
            <div className="flex justify-between items-center">
              <div className="text-xs text-slate-500">
                {agent.status === "needs_input" && (
                  <span className="text-red-600">入力待ちのため送信が制限されています</span>
                )}
                {agent.status === "waiting" && (
                  <span className="text-yellow-600">待機中のため送信が制限されています</span>
                )}
              </div>
              <Button 
                type="submit" 
                disabled={!input.trim() || isLoading || agent.status === "needs_input" || agent.status === "waiting"}
                className="bg-slate-700 hover:bg-slate-800 text-white"
              >
                <Send className="h-4 w-4 mr-2" />
                送信
              </Button>
            </div>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}