"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { AgentInfo, AgentNode, AgentEdge } from "@/types/agent"
import { Network } from "lucide-react"

interface AgentRelationshipViewProps {
  agents: AgentInfo[]
}

export function AgentRelationshipView({ agents }: AgentRelationshipViewProps) {
  const { nodes, edges } = useMemo(() => {
    const nodes: AgentNode[] = agents.map((agent, index) => ({
      id: agent.agent_id,
      label: agent.purpose.length > 20 ? agent.purpose.slice(0, 20) + "..." : agent.purpose,
      status: agent.status,
      x: (index % 3) * 200 + 100,
      y: Math.floor(index / 3) * 150 + 100,
    }))

    const edges: AgentEdge[] = agents
      .filter((agent) => agent.parent_agent_id)
      .map((agent) => ({
        from: agent.parent_agent_id!,
        to: agent.agent_id,
        label: "委任",
      }))

    return { nodes, edges }
  }, [agents])

  const getNodeColor = (status: AgentInfo["status"]) => {
    switch (status) {
      case "pending":
        return "#fbbf24" // yellow
      case "in_progress":
        return "#3b82f6" // blue
      case "completed":
        return "#10b981" // green
      case "failed":
        return "#ef4444" // red
      default:
        return "#6b7280" // gray
    }
  }

  if (agents.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            エージェント関係性ビュー
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-8">エージェントが生成されると関係性が表示されます</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Network className="h-5 w-5" />
          エージェント関係性ビュー ({agents.length} エージェント)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative bg-gray-50 rounded-lg p-4 min-h-[400px] overflow-auto">
          <svg width="100%" height="400" className="absolute inset-0">
            {/* エッジ（線）を描画 */}
            {edges.map((edge, index) => {
              const fromNode = nodes.find((n) => n.id === edge.from)
              const toNode = nodes.find((n) => n.id === edge.to)
              if (!fromNode || !toNode) return null

              return (
                <g key={index}>
                  <line
                    x1={fromNode.x}
                    y1={fromNode.y}
                    x2={toNode.x}
                    y2={toNode.y}
                    stroke="#6b7280"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
                  <text
                    x={(fromNode.x + toNode.x) / 2}
                    y={(fromNode.y + toNode.y) / 2 - 5}
                    textAnchor="middle"
                    className="text-xs fill-gray-600"
                  >
                    {edge.label}
                  </text>
                </g>
              )
            })}

            {/* 矢印マーカーの定義 */}
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="#6b7280" />
              </marker>
            </defs>
          </svg>

          {/* ノード（エージェント）を描画 */}
          {nodes.map((node) => (
            <div
              key={node.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2"
              style={{
                left: node.x,
                top: node.y,
              }}
            >
              <div
                className="w-24 h-16 rounded-lg border-2 flex items-center justify-center text-xs font-medium text-white shadow-lg"
                style={{
                  backgroundColor: getNodeColor(node.status),
                  borderColor: getNodeColor(node.status),
                }}
              >
                <div className="text-center">
                  <div className="truncate w-20">{node.label}</div>
                  <div className="text-xs opacity-80 mt-1">{node.status}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* ステータス凡例 */}
        <div className="flex flex-wrap gap-4 mt-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-yellow-400"></div>
            <span>実行待ち</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-blue-500"></div>
            <span>実行中</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-green-500"></div>
            <span>完了</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-red-500"></div>
            <span>失敗</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
