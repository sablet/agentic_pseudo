"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { AgentInfo } from "@/types/agent"
import { Play, Clock, CheckCircle, XCircle, ArrowRight } from "lucide-react"

interface AgentStatusListProps {
  agents: AgentInfo[]
  onExecuteAgent: (agentId: string) => void
}

export function AgentStatusList({ agents, onExecuteAgent }: AgentStatusListProps) {
  const getStatusIcon = (status: AgentInfo["status"]) => {
    switch (status) {
      case "todo":
        return <Clock className="h-4 w-4" />
      case "doing":
        return <ArrowRight className="h-4 w-4 animate-pulse" />
      case "waiting":
        return <CheckCircle className="h-4 w-4" />
      case "needs_input":
        return <XCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: AgentInfo["status"]) => {
    switch (status) {
      case "todo":
        return "bg-blue-100 text-blue-800"
      case "doing":
        return "bg-green-100 text-green-800"
      case "waiting":
        return "bg-yellow-100 text-yellow-800"
      case "needs_input":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const pendingAgents = agents.filter((agent) => agent.status === "todo")
  const activeAgents = agents.filter((agent) => ["doing", "waiting", "needs_input"].includes(agent.status))

  return (
    <div className="space-y-4">
      {/* 実行待ちエージェント */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">実行待ちエージェント ({pendingAgents.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            <div className="space-y-3">
              {pendingAgents.length === 0 ? (
                <p className="text-gray-500 text-sm">実行待ちのエージェントはありません</p>
              ) : (
                pendingAgents.map((agent) => (
                  <div key={agent.agent_id} className="border rounded-lg p-3 space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-sm">{agent.purpose}</p>
                        <p className="text-xs text-gray-600">目的: {agent.purpose}</p>
                      </div>
                      <Button size="sm" onClick={() => onExecuteAgent(agent.agent_id)} className="ml-2">
                        <Play className="h-3 w-3 mr-1" />
                        実行
                      </Button>
                    </div>
                    <div className="text-xs text-gray-600 bg-gray-50 p-2 rounded">{agent.context}</div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* 実行中・完了エージェント */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">実行中・完了エージェント ({activeAgents.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            <div className="space-y-3">
              {activeAgents.length === 0 ? (
                <p className="text-gray-500 text-sm">実行中・完了のエージェントはありません</p>
              ) : (
                activeAgents.map((agent) => (
                  <div key={agent.agent_id} className="border rounded-lg p-3 space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium text-sm">{agent.purpose}</p>
                          <Badge className={`text-xs ${getStatusColor(agent.status)}`}>
                            <span className="flex items-center gap-1">
                              {getStatusIcon(agent.status)}
                              {agent.status}
                            </span>
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600">目的: {agent.purpose}</p>
                        <p className="text-xs text-gray-600">更新: {agent.updated_at.toLocaleString("ja-JP")}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}
