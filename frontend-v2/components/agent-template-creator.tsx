"use client"

import React, { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DataUnitSelector } from "@/components/data-unit-selector"
import { 
  Plus, 
  X, 
  Target, 
  FileText,
  Save,
  Cpu
} from "lucide-react"
import type { DataUnit, ExecutionEngine } from "@/types/agent"

interface AgentTemplate {
  delegation_type: string
  purpose: DataUnit
  context: DataUnit[]
  execution_engine: ExecutionEngine
  parameters: Record<string, any>
}

interface AgentTemplateCreatorProps {
  isOpen: boolean
  onClose: () => void
  onCreateAgent: (template: AgentTemplate) => void
}

export function AgentTemplateCreator({
  isOpen,
  onClose,
  onCreateAgent,
}: AgentTemplateCreatorProps) {
  const [formData, setFormData] = useState({
    delegation_type: "",
    purpose: "" as DataUnit,
    context: [] as DataUnit[],
    execution_engine: "gemini-2.5-flash" as ExecutionEngine,
    parameters: "{}",
  })

  const resetForm = () => {
    setFormData({
      delegation_type: "",
      purpose: "" as DataUnit,
      context: [] as DataUnit[],
      execution_engine: "gemini-2.5-flash" as ExecutionEngine,
      parameters: "{}",
    })
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  const handleAddContext = () => {
    setFormData((prev) => ({
      ...prev,
      context: [...prev.context, "" as DataUnit],
    }))
  }

  const handleRemoveContext = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      context: prev.context.filter((_, i) => i !== index),
    }))
  }

  const handleContextChange = (index: number, value: DataUnit) => {
    setFormData((prev) => ({
      ...prev,
      context: prev.context.map((item, i) => 
        i === index ? value : item
      ),
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.delegation_type || !formData.purpose || formData.context.length === 0) {
      alert("委任タイプ（表示名）、目的、コンテキストは必須項目です")
      return
    }

    const filteredContexts = formData.context.filter(context => context.trim() !== "")
    
    try {
      const parameters = JSON.parse(formData.parameters)
      const template: AgentTemplate = {
        delegation_type: formData.delegation_type,
        purpose: formData.purpose,
        context: filteredContexts,
        execution_engine: formData.execution_engine,
        parameters,
      }

      onCreateAgent(template)
      handleClose()
    } catch (error) {
      alert("パラメータのJSON形式が正しくありません")
    }
  }

  // Sample delegation types for suggestions
  const commonDelegationTypes = [
    "データ分析",
    "コンテンツ作成",
    "リサーチ",
    "競合分析",
    "顧客分析",
    "市場調査",
    "技術レビュー",
    "品質保証",
    "企画立案",
    "レポート作成",
  ]

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            新しいエージェントテンプレート作成
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="max-h-[70vh] pr-4">
          <form onSubmit={handleSubmit} className="space-y-6 mt-4">
            {/* 委任タイプ（表示名） */}
            <div>
              <Label htmlFor="delegation_type" className="text-sm font-medium">
                委任タイプ（表示名） <span className="text-red-500">*</span>
              </Label>
              <Input
                id="delegation_type"
                value={formData.delegation_type}
                onChange={(e) => setFormData((prev) => ({ ...prev, delegation_type: e.target.value }))}
                placeholder="例: 競合分析"
                className="mt-1"
              />
              <div className="mt-2 flex flex-wrap gap-1">
                <p className="text-xs text-slate-500 w-full mb-1">よく使われるタイプ:</p>
                {commonDelegationTypes.slice(0, 6).map((type) => (
                  <Badge
                    key={type}
                    variant="outline"
                    className="text-xs cursor-pointer hover:bg-slate-100"
                    onClick={() => setFormData((prev) => ({ ...prev, delegation_type: type }))}
                  >
                    {type}
                  </Badge>
                ))}
              </div>
            </div>

            {/* 目的（DataUnit） */}
            <div>
              <DataUnitSelector
                value={formData.purpose}
                onChange={(value) => setFormData((prev) => ({ ...prev, purpose: value }))}
                label="目的"
                placeholder="このエージェントが生成するデータユニットを選択"
                required={true}
              />
              <p className="text-xs text-slate-500 mt-1">
                このエージェントが生成する成果物の種類を選択してください
              </p>
            </div>

            {/* コンテキスト（DataUnit配列） */}
            <div>
              <Label className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                コンテキスト <span className="text-red-500">*</span>
              </Label>
              <p className="text-xs text-slate-500 mt-1 mb-3">
                このエージェントが作業に必要とする入力データの種類を選択してください
              </p>
              
              <div className="space-y-2">
                {formData.context.length === 0 ? (
                  <div className="text-center py-4 border-2 border-dashed border-slate-300 rounded-lg">
                    <p className="text-sm text-slate-500 mb-2">コンテキストが設定されていません</p>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleAddContext}
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      コンテキストを追加
                    </Button>
                  </div>
                ) : (
                  <>
                    {formData.context.map((contextItem, index) => (
                      <div key={index} className="flex gap-2">
                        <div className="flex-1">
                          <DataUnitSelector
                            value={contextItem}
                            onChange={(value) => handleContextChange(index, value)}
                            placeholder="コンテキストを選択"
                            required={true}
                          />
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          size="icon"
                          onClick={() => handleRemoveContext(index)}
                          className="flex-shrink-0"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                    
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleAddContext}
                      className="w-full"
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      コンテキストを追加
                    </Button>
                  </>
                )}
              </div>
            </div>

            {/* 実行エンジン */}
            <div>
              <Label className="text-sm font-medium flex items-center gap-2">
                <Cpu className="h-4 w-4" />
                実行エンジン <span className="text-red-500">*</span>
              </Label>
              <Select
                value={formData.execution_engine}
                onValueChange={(value: ExecutionEngine) => setFormData((prev) => ({ ...prev, execution_engine: value }))}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="実行エンジンを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gemini-2.5-flash">Gemini 2.5 Flash</SelectItem>
                  <SelectItem value="claude-code">Claude Code</SelectItem>
                  <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                  <SelectItem value="gpt-4o-mini">GPT-4o Mini</SelectItem>
                  <SelectItem value="claude-3.5-sonnet">Claude 3.5 Sonnet</SelectItem>
                  <SelectItem value="gemini-1.5-pro">Gemini 1.5 Pro</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-slate-500 mt-1">
                このエージェントを実行するAIエンジンを選択してください
              </p>
            </div>


            {/* パラメータ */}
            <div>
              <Label htmlFor="parameters" className="text-sm font-medium">
                追加パラメータ (JSON)
              </Label>
              <Textarea
                id="parameters"
                value={formData.parameters}
                onChange={(e) => setFormData((prev) => ({ ...prev, parameters: e.target.value }))}
                placeholder='{"option1": "value1", "option2": "value2"}'
                rows={4}
                className="mt-1 font-mono text-sm"
              />
              <p className="text-xs text-slate-500 mt-1">
                エージェント実行時に使用する追加設定をJSON形式で入力
              </p>
            </div>

            {/* プレビュー */}
            {formData.delegation_type && formData.purpose && formData.context && (
              <Card className="bg-slate-50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">プレビュー</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2 text-sm">
                    <p><strong>表示名:</strong> {formData.delegation_type}</p>
                    <p><strong>目的:</strong> {formData.purpose}</p>
                    <div>
                      <strong>コンテキスト:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {formData.context.map((contextItem, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {contextItem}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <p><strong>実行エンジン:</strong> {formData.execution_engine}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* ボタン */}
            <div className="flex gap-3 pt-4">
              <Button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700">
                <Save className="h-4 w-4 mr-2" />
                エージェントを作成
              </Button>
              <Button type="button" variant="outline" onClick={handleClose} className="flex-1">
                キャンセル
              </Button>
            </div>
          </form>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}