"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import type { ChatMessage, AgentInfo, ChatSession } from "@/types/agent"
import { Send, CheckCircle, ArrowRight, Info, Bot, User, Clock } from "lucide-react"

interface ChatInterfaceProps {
  activeSession: ChatSession
  agents: AgentInfo[]
  onSendMessage: (content: string) => void
  onApproveAgent: (proposal: any) => void
  onCompleteAgent: (agentId: string) => void
}

export function ChatInterface({
  activeSession,
  agents,
  onSendMessage,
  onApproveAgent,
  onCompleteAgent,
}: ChatInterfaceProps) {
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      onSendMessage(input.trim())
      setInput("")
    }
  }

  const handleApproveAgent = (proposal: any) => {
    onApproveAgent(proposal)
  }

  const inProgressAgents = agents.filter((agent) => agent.status === "doing")

  const renderMessage = (message: ChatMessage) => {
    if (message.role === "system_notification") {
      return (
        <div key={message.id} className="flex justify-center my-6">
          <div className="bg-slate-100 border border-slate-200 rounded-full px-4 py-2 flex items-center gap-2 max-w-md shadow-sm">
            <Info className="h-4 w-4 text-slate-600 flex-shrink-0" />
            <p className="text-sm text-slate-700 text-center font-medium">{message.content}</p>
          </div>
        </div>
      )
    }

    return (
      <div key={message.id} className={`flex gap-4 mb-6 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
        <div className={`flex gap-3 max-w-[75%] ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
          <div className="flex-shrink-0 mt-1">
            {message.role === "user" ? (
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
              message.role === "user" ? "bg-slate-700 text-white" : "bg-white text-slate-900 border border-slate-200"
            }`}
          >
            <p className="text-sm leading-relaxed">{message.content}</p>
            {message.agent_proposal && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs font-semibold mb-3 text-blue-900">エージェント生成提案</p>
                <div className="space-y-2 text-xs text-blue-800">
                  <p>
                    <strong>目的:</strong> {message.agent_proposal.purpose}
                  </p>
                  <p>
                    <strong>タイプ:</strong> {message.agent_proposal.delegation_type}
                  </p>
                  <p>
                    <strong>コンテキスト:</strong> {message.agent_proposal.context}
                  </p>
                </div>
                <Button
                  size="sm"
                  onClick={() => handleApproveAgent(message.agent_proposal)}
                  className="mt-3 bg-blue-600 hover:bg-blue-700 text-white text-xs"
                >
                  承認して生成
                </Button>
              </div>
            )}
            <p className="text-xs opacity-60 mt-2">{message.timestamp.toLocaleTimeString("ja-JP")}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <Card className="h-full flex flex-col shadow-lg border-slate-200">
      <CardContent className="flex-1 flex flex-col gap-0 p-0">
        {/* セッション情報ヘッダー */}
        <div className="business-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="font-semibold text-slate-900">{activeSession.agent_name}</h2>
              {activeSession.agent_id && (
                <Badge variant="outline" className="text-xs bg-slate-100 text-slate-600 border-slate-300">
                  ID: {activeSession.agent_id.slice(-8)}
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Clock className="h-4 w-4" />
              <span>{activeSession.messages.length} メッセージ</span>
            </div>
          </div>
        </div>

        {/* 実行中エージェント表示（メインチャットのみ） */}
        {!activeSession.agent_id && inProgressAgents.length > 0 && (
          <div className="mx-6 mt-4 mb-2">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
                <ArrowRight className="h-4 w-4 animate-pulse" />
                実行中のエージェント ({inProgressAgents.length})
              </h4>
              <div className="space-y-3">
                {inProgressAgents.map((agent) => (
                  <div
                    key={agent.agent_id}
                    className="flex items-center justify-between bg-white p-3 rounded-lg border border-blue-100"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{agent.purpose}</p>
                      <p className="text-xs text-slate-500">ID: {agent.agent_id.slice(-8)}</p>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => onCompleteAgent(agent.agent_id)}
                      className="ml-3 bg-green-600 hover:bg-green-700 text-white"
                    >
                      <CheckCircle className="h-3 w-3 mr-1" />
                      完了
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* チャットメッセージエリア */}
        <ScrollArea className="flex-1 px-6 py-4">
          <div className="space-y-0">{activeSession.messages.map(renderMessage)}</div>
        </ScrollArea>

        {/* メッセージ入力エリア */}
        <div className="border-t border-slate-200 p-6 bg-white">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="メッセージを入力してください..."
              className="flex-1 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
            />
            <Button type="submit" size="icon" className="bg-slate-700 hover:bg-slate-800 text-white">
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}
