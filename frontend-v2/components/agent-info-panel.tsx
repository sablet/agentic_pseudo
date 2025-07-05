"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { 
  Target, 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Users, 
  Play, 
  Pause,
  Calendar,
  ArrowRight,
  ArrowUp,
  ArrowDown
} from "lucide-react"
import type { AgentMetaInfo, ContextStatus, WaitingInfo } from "@/types/agent"

interface AgentInfoPanelProps {
  agentInfo: AgentMetaInfo | null
  onUpdateContext?: (contextId: string, value: any) => void
  onExecuteAgent?: (agentId: string) => void
  onApproveAgent?: (agentId: string) => void
}

export function AgentInfoPanel({
  agentInfo,
  onUpdateContext,
  onExecuteAgent,
  onApproveAgent,
}: AgentInfoPanelProps) {
  if (!agentInfo) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-50 border-l border-slate-200">
        <div className="text-center text-slate-500">
          <Users className="h-12 w-12 mx-auto mb-4 opacity-30" />
          <p className="text-sm">エージェントを選択してください</p>
        </div>
      </div>
    )
  }

  const getContextStatusColor = (status: ContextStatus["status"]) => {
    switch (status) {
      case "sufficient":
        return "bg-green-100 text-green-800"
      case "insufficient":
        return "bg-red-100 text-red-800"
      case "pending":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getWaitingTypeIcon = (type: WaitingInfo["type"]) => {
    switch (type) {
      case "context":
        return <FileText className="h-4 w-4" />
      case "approval":
        return <CheckCircle className="h-4 w-4" />
      case "dependency":
        return <ArrowRight className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const renderContextInput = (context: ContextStatus) => {
    if (context.status === "sufficient") return null

    switch (context.type) {
      case "text":
        return (
          <div className="mt-2">
            <Input
              placeholder={`${context.name}を入力してください`}
              defaultValue={context.current_value || ""}
              onChange={(e) => onUpdateContext?.(context.id, e.target.value)}
            />
          </div>
        )
      case "file":
        return (
          <div className="mt-2">
            <Input
              type="file"
              onChange={(e) => onUpdateContext?.(context.id, e.target.files?.[0])}
            />
          </div>
        )
      case "selection":
        return (
          <div className="mt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onUpdateContext?.(context.id, "selected")}
            >
              選択
            </Button>
          </div>
        )
      case "approval":
        return (
          <div className="mt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onApproveAgent?.(agentInfo.agent_id)}
            >
              承認
            </Button>
          </div>
        )
      default:
        return null
    }
  }

  return (
    <div className="w-full h-full bg-white border-l border-slate-200 flex flex-col">
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold text-slate-900 truncate">
              {agentInfo.purpose}
            </h2>
          </div>
          <div className="flex gap-2 ml-4">
            <Button
              size="sm"
              onClick={() => onExecuteAgent?.(agentInfo.agent_id)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Play className="h-3 w-3 mr-1" />
              実行
            </Button>
          </div>
        </div>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <Badge className={`text-xs ${
              agentInfo.level === 0 ? "bg-purple-100 text-purple-800" :
              agentInfo.level === 1 ? "bg-blue-100 text-blue-800" :
              agentInfo.level === 2 ? "bg-green-100 text-green-800" :
              "bg-orange-100 text-orange-800"
            }`}>
              Level {agentInfo.level}
            </Badge>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        <div className="space-y-6">
          {/* エージェント説明 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Target className="h-4 w-4" />
                目的・説明
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm text-slate-700 leading-relaxed">
                {agentInfo.description}
              </p>
            </CardContent>
          </Card>

          {/* コンテキスト状況 */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="h-4 w-4" />
                必要なコンテキスト
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                {agentInfo.context_status.map((context) => (
                  <div key={context.id} className="border rounded-lg p-3">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium">{context.name}</span>
                          <Badge className={`text-xs ${getContextStatusColor(context.status)}`}>
                            {context.status}
                          </Badge>
                          {context.required && (
                            <Badge variant="outline" className="text-xs">
                              必須
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 mb-2">
                          {context.description}
                        </p>
                        {context.current_value && (
                          <p className="text-xs text-slate-600 bg-slate-50 p-2 rounded">
                            現在の値: {JSON.stringify(context.current_value)}
                          </p>
                        )}
                      </div>
                    </div>
                    {renderContextInput(context)}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 待機中の情報 */}
          {agentInfo.waiting_for.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  待機中
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {agentInfo.waiting_for.map((waiting, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
                      <div className="mt-0.5 text-yellow-600">
                        {getWaitingTypeIcon(waiting.type)}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-slate-900">
                          {waiting.description}
                        </p>
                        {waiting.estimated_time && (
                          <p className="text-xs text-slate-500 mt-1">
                            予想時間: {waiting.estimated_time}
                          </p>
                        )}
                        {waiting.dependencies && waiting.dependencies.length > 0 && (
                          <div className="mt-2">
                            <p className="text-xs text-slate-500 mb-1">依存関係:</p>
                            <div className="flex flex-wrap gap-1">
                              {waiting.dependencies.map((dep, depIndex) => (
                                <Badge key={depIndex} variant="outline" className="text-xs">
                                  {dep}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* 実行ログ */}
          {agentInfo.execution_log.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  実行ログ
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {agentInfo.execution_log.map((log, index) => (
                    <div key={index} className="text-xs text-slate-600 p-2 bg-slate-50 rounded">
                      {log}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* エージェント関係 */}
          {(agentInfo.parent_agent_summary || agentInfo.child_agent_summaries.length > 0) && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  エージェント関係
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-4">
                  {agentInfo.parent_agent_summary && (
                    <div className="border rounded-lg p-3 bg-slate-50">
                      <div className="flex items-center gap-2 mb-2">
                        <ArrowUp className="h-4 w-4 text-slate-400" />
                        <span className="text-sm font-medium">親エージェント</span>
                      </div>
                      <div className="ml-6">
                        <p className="text-sm font-medium text-slate-900 mb-1">
                          {agentInfo.parent_agent_summary.purpose}
                        </p>
                        <div className="flex items-center gap-2">
                          <Badge className={`text-xs ${
                            agentInfo.parent_agent_summary.level === 0 ? "bg-purple-100 text-purple-800" :
                            agentInfo.parent_agent_summary.level === 1 ? "bg-blue-100 text-blue-800" :
                            "bg-green-100 text-green-800"
                          }`}>
                            Level {agentInfo.parent_agent_summary.level}
                          </Badge>
                          <Badge className={`text-xs ${
                            agentInfo.parent_agent_summary.status === "todo" ? "bg-blue-100 text-blue-800" :
                            agentInfo.parent_agent_summary.status === "doing" ? "bg-green-100 text-green-800" :
                            agentInfo.parent_agent_summary.status === "waiting" ? "bg-yellow-100 text-yellow-800" :
                            agentInfo.parent_agent_summary.status === "needs_input" ? "bg-red-100 text-red-800" :
                            "bg-gray-100 text-gray-800"
                          }`}>
                            {agentInfo.parent_agent_summary.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {agentInfo.child_agent_summaries.length > 0 && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <ArrowDown className="h-4 w-4 text-slate-400" />
                        <span className="text-sm font-medium">子エージェント ({agentInfo.child_agent_summaries.length})</span>
                      </div>
                      <div className="ml-6 space-y-2">
                        {agentInfo.child_agent_summaries.map((child, index) => (
                          <div key={index} className="border rounded-lg p-3 bg-slate-50">
                            <p className="text-sm font-medium text-slate-900 mb-1">
                              {child.purpose}
                            </p>
                            <div className="flex items-center gap-2">
                              <Badge className={`text-xs ${
                                child.level === 0 ? "bg-purple-100 text-purple-800" :
                                child.level === 1 ? "bg-blue-100 text-blue-800" :
                                child.level === 2 ? "bg-green-100 text-green-800" :
                                "bg-orange-100 text-orange-800"
                              }`}>
                                Level {child.level}
                              </Badge>
                              <Badge className={`text-xs ${
                                child.status === "todo" ? "bg-blue-100 text-blue-800" :
                                child.status === "doing" ? "bg-green-100 text-green-800" :
                                child.status === "waiting" ? "bg-yellow-100 text-yellow-800" :
                                child.status === "needs_input" ? "bg-red-100 text-red-800" :
                                "bg-gray-100 text-gray-800"
                              }`}>
                                {child.status}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}