"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  Target, 
  Play, 
  Pause, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Users,
  ArrowUp,
  ArrowDown,
  MoreVertical,
  MessageSquare
} from "lucide-react"
import type { AgentInfo } from "@/types/agent"

interface AgentListProps {
  agents: AgentInfo[]
  selectedAgentId: string | null
  onSelectAgent: (agentId: string) => void
  onExecuteAgent: (agentId: string) => void
  onCreateAgent: () => void
  getMessageCount?: (agentId: string) => number
}

export function AgentList({
  agents,
  selectedAgentId,
  onSelectAgent,
  onExecuteAgent,
  onCreateAgent,
  getMessageCount,
}: AgentListProps) {
  const getStatusColor = (status: AgentInfo["status"]) => {
    switch (status) {
      case "todo":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "doing":
        return "bg-green-100 text-green-800 border-green-200"
      case "waiting":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "needs_input":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getStatusIcon = (status: AgentInfo["status"]) => {
    switch (status) {
      case "todo":
        return <Clock className="h-4 w-4" />
      case "doing":
        return <Play className="h-4 w-4" />
      case "waiting":
        return <Pause className="h-4 w-4" />
      case "needs_input":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusText = (status: AgentInfo["status"]) => {
    switch (status) {
      case "todo":
        return "実行待ち"
      case "doing":
        return "実行中"
      case "waiting":
        return "待機中"
      case "needs_input":
        return "入力待ち"
      default:
        return "不明"
    }
  }

  const getLevelColor = (level: number) => {
    const colors = [
      "bg-purple-100 text-purple-800", // Level 0
      "bg-blue-100 text-blue-800",     // Level 1
      "bg-green-100 text-green-800",   // Level 2
      "bg-orange-100 text-orange-800", // Level 3+
    ]
    return colors[Math.min(level, colors.length - 1)]
  }

  // Group agents by status
  const groupedAgents = {
    todo: agents.filter((agent) => agent.status === "todo"),
    doing: agents.filter((agent) => agent.status === "doing"),
    waiting: agents.filter((agent) => agent.status === "waiting"),
    needs_input: agents.filter((agent) => agent.status === "needs_input"),
  }

  const renderAgentCard = (agent: AgentInfo) => {
    const isSelected = selectedAgentId === agent.agent_id
    const hasChildren = agents.some((a) => a.parent_agent_id === agent.agent_id)
    const hasParent = agent.parent_agent_id !== null

    return (
      <Card
        key={agent.agent_id}
        className={`cursor-pointer transition-all hover:shadow-md ${
          isSelected ? "ring-2 ring-blue-500 bg-blue-50" : ""
        }`}
        onClick={() => onSelectAgent(agent.agent_id)}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-sm font-medium truncate">
                {agent.purpose}
              </CardTitle>
              <div className="flex items-center gap-2 mt-2">
                <Badge className={`text-xs ${getStatusColor(agent.status)}`}>
                  <span className="flex items-center gap-1">
                    {getStatusIcon(agent.status)}
                    {getStatusText(agent.status)}
                  </span>
                </Badge>
                <Badge className={`text-xs ${getLevelColor(agent.level)}`}>
                  Level {agent.level}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-1 ml-2">
              {hasParent && (
                <ArrowUp className="h-3 w-3 text-slate-400" />
              )}
              {hasChildren && (
                <ArrowDown className="h-3 w-3 text-slate-400" />
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            <p className="text-xs text-slate-600 line-clamp-2">
              {agent.purpose}
            </p>
            
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-500 space-y-1">
                <p>更新: {agent.updated_at.toLocaleString("ja-JP", { 
                  month: "short", 
                  day: "numeric", 
                  hour: "2-digit", 
                  minute: "2-digit" 
                })}</p>
                {getMessageCount && (
                  <div className="flex items-center gap-1">
                    <MessageSquare className="h-3 w-3" />
                    <span>{getMessageCount(agent.agent_id)} メッセージ</span>
                  </div>
                )}
              </div>
              
              {agent.status === "todo" && (
                <Button
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation()
                    onExecuteAgent(agent.agent_id)
                  }}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Play className="h-3 w-3 mr-1" />
                  実行
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderAgentGroup = (title: string, agents: AgentInfo[], status: string) => {
    if (agents.length === 0) return null

    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-slate-900">{title}</h3>
          <Badge variant="outline" className="text-xs">
            {agents.length}
          </Badge>
        </div>
        <div className="grid gap-3">
          {agents.map(renderAgentCard)}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-slate-600" />
            <h2 className="text-lg font-semibold text-slate-900">エージェント</h2>
            <Badge variant="outline" className="text-xs">
              {agents.length}
            </Badge>
          </div>
          <Button
            onClick={onCreateAgent}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Target className="h-4 w-4 mr-1" />
            テンプレート選択
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        <div className="space-y-8">
          {agents.length === 0 ? (
            <div className="text-center py-12">
              <Users className="h-12 w-12 mx-auto mb-4 text-slate-300" />
              <p className="text-slate-500 mb-2">エージェントがありません</p>
              <p className="text-slate-400 text-sm">「新規作成」ボタンでエージェントを作成してください</p>
            </div>
          ) : (
            <>
              {renderAgentGroup("実行中", groupedAgents.doing, "doing")}
              {renderAgentGroup("実行待ち", groupedAgents.todo, "todo")}
              {renderAgentGroup("待機中", groupedAgents.waiting, "waiting")}
              {renderAgentGroup("入力待ち", groupedAgents.needs_input, "needs_input")}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}