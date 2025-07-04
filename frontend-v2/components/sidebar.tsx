"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Separator } from "@/components/ui/separator"
import type { AgentInfo, ChatSession } from "@/types/agent"
import { Menu, Play, Clock, CheckCircle, XCircle, ArrowRight, Settings, MessageSquare, Users } from "lucide-react"

interface SidebarProps {
  agents: AgentInfo[]
  chatSessions: ChatSession[]
  activeSessionId: string | null
  onExecuteAgent: (agentId: string) => void
  onOpenSettings: () => void
  onSelectSession: (sessionId: string | null) => void
}

export function Sidebar({
  agents,
  chatSessions,
  activeSessionId,
  onExecuteAgent,
  onOpenSettings,
  onSelectSession,
}: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false)

  const getStatusIcon = (status: AgentInfo["status"]) => {
    switch (status) {
      case "pending":
        return <Clock className="h-4 w-4" />
      case "in_progress":
        return <ArrowRight className="h-4 w-4 animate-pulse" />
      case "completed":
        return <CheckCircle className="h-4 w-4" />
      case "failed":
        return <XCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusBadgeClass = (status: AgentInfo["status"]) => {
    switch (status) {
      case "pending":
        return "status-pending"
      case "in_progress":
        return "status-progress"
      case "completed":
        return "status-completed"
      case "failed":
        return "status-error"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusText = (status: AgentInfo["status"]) => {
    switch (status) {
      case "pending":
        return "実行待ち"
      case "in_progress":
        return "実行中"
      case "completed":
        return "完了"
      case "failed":
        return "失敗"
      default:
        return "不明"
    }
  }

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="fixed top-6 left-6 z-50 bg-white shadow-md border-slate-300 hover:bg-slate-50"
        >
          <Menu className="h-4 w-4 text-slate-700" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-96 bg-white">
        <SheetHeader className="border-b border-slate-200 pb-4">
          <SheetTitle className="flex items-center justify-between text-slate-900">
            <span className="font-semibold">ワークスペース</span>
            <Button
              variant="outline"
              size="sm"
              onClick={onOpenSettings}
              className="border-slate-300 hover:bg-slate-50 bg-transparent"
            >
              <Settings className="h-4 w-4 mr-1 text-slate-600" />
              設定
            </Button>
          </SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* チャットセッション */}
          <div>
            <h3 className="font-medium mb-3 flex items-center gap-2 text-slate-900">
              <MessageSquare className="h-4 w-4 text-slate-600" />
              チャットセッション
            </h3>
            <div className="space-y-2">
              {chatSessions.map((session) => (
                <Button
                  key={session.agent_id || "main"}
                  variant={activeSessionId === session.agent_id ? "default" : "outline"}
                  className={`w-full justify-start text-left h-auto p-3 ${
                    activeSessionId === session.agent_id
                      ? "bg-slate-700 text-white hover:bg-slate-800"
                      : "border-slate-200 hover:bg-slate-50"
                  }`}
                  onClick={() => {
                    onSelectSession(session.agent_id)
                    setIsOpen(false)
                  }}
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{session.agent_name}</p>
                    <p className={`text-xs ${activeSessionId === session.agent_id ? "opacity-70" : "text-slate-500"}`}>
                      {session.messages.length} メッセージ
                      {session.agent_id && ` • ID: ${session.agent_id.slice(-8)}`}
                    </p>
                  </div>
                </Button>
              ))}
            </div>
          </div>

          <Separator className="bg-slate-200" />

          {/* エージェント一覧 */}
          <div>
            <h3 className="font-medium mb-3 flex items-center gap-2 text-slate-900">
              <Users className="h-4 w-4 text-slate-600" />
              エージェント一覧 ({agents.length})
            </h3>
            <ScrollArea className="h-[calc(100vh-400px)]">
              <div className="space-y-3">
                {agents.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-slate-500 text-sm">エージェントがありません</p>
                    <p className="text-slate-400 text-xs mt-1">チャットでエージェントを生成してください</p>
                  </div>
                ) : (
                  agents.map((agent) => (
                    <div key={agent.agent_id} className="business-card p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge className={`text-xs border ${getStatusBadgeClass(agent.status)}`}>
                              <span className="flex items-center gap-1">
                                {getStatusIcon(agent.status)}
                                {getStatusText(agent.status)}
                              </span>
                            </Badge>
                          </div>
                          <p className="font-medium text-sm text-slate-900 truncate mb-1" title={agent.purpose}>
                            {agent.purpose}
                          </p>
                          <div className="space-y-1 text-xs text-slate-500">
                            <p>ID: {agent.agent_id.slice(-8)}</p>
                            <p>タイプ: {agent.delegation_type}</p>
                            {agent.parent_agent_id && <p>親: {agent.parent_agent_id.slice(-8)}</p>}
                            <p>更新: {agent.updated_at.toLocaleString("ja-JP")}</p>
                          </div>
                        </div>
                        {agent.status === "pending" && (
                          <Button
                            size="sm"
                            onClick={() => {
                              onExecuteAgent(agent.agent_id)
                              setIsOpen(false)
                            }}
                            className="ml-3 bg-blue-600 hover:bg-blue-700 text-white"
                          >
                            <Play className="h-3 w-3 mr-1" />
                            実行
                          </Button>
                        )}
                      </div>
                      <div className="text-xs text-slate-600 bg-slate-50 p-3 rounded border border-slate-100">
                        {agent.context}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
