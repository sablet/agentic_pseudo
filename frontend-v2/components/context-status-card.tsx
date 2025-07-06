"use client"

import React, { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  FileText, 
  Upload, 
  Edit3,
  Save,
  X
} from "lucide-react"
import type { ContextStatus } from "@/types/agent"

interface ContextStatusCardProps {
  context: ContextStatus
  onUpdate?: (contextId: string, value: any) => void
  onSave?: (contextId: string) => void
  showActions?: boolean
  editable?: boolean
}

export function ContextStatusCard({ 
  context, 
  onUpdate, 
  onSave, 
  showActions = true, 
  editable = true 
}: ContextStatusCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [localValue, setLocalValue] = useState(context.current_value || "")

  const getStatusColor = (status: ContextStatus["status"]) => {
    switch (status) {
      case "sufficient":
        return "bg-green-100 text-green-800 border-green-200"
      case "insufficient":
        return "bg-red-100 text-red-800 border-red-200"
      case "pending":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getStatusIcon = (status: ContextStatus["status"]) => {
    switch (status) {
      case "sufficient":
        return <CheckCircle className="h-4 w-4" />
      case "insufficient":
        return <AlertCircle className="h-4 w-4" />
      case "pending":
        return <Clock className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const handleSave = () => {
    if (onUpdate) {
      onUpdate(context.id, localValue)
    }
    if (onSave) {
      onSave(context.id)
    }
    setIsEditing(false)
  }

  const handleCancel = () => {
    setLocalValue(context.current_value || "")
    setIsEditing(false)
  }

  const renderInputField = () => {
    if (!editable || !isEditing) return null

    switch (context.type) {
      case "text":
        return (
          <div className="mt-3">
            <Label htmlFor={`context-${context.id}`} className="text-sm font-medium">
              {context.name}
            </Label>
            <Input
              id={`context-${context.id}`}
              value={localValue}
              onChange={(e) => setLocalValue(e.target.value)}
              placeholder={`${context.name}を入力してください`}
              className="mt-1"
            />
          </div>
        )
      case "file":
        return (
          <div className="mt-3">
            <Label htmlFor={`context-${context.id}`} className="text-sm font-medium">
              {context.name}
            </Label>
            <Input
              id={`context-${context.id}`}
              type="file"
              onChange={(e) => setLocalValue(e.target.files?.[0] || "")}
              className="mt-1"
            />
          </div>
        )
      case "selection":
        return (
          <div className="mt-3">
            <Label htmlFor={`context-${context.id}`} className="text-sm font-medium">
              {context.name}
            </Label>
            <Select value={localValue} onValueChange={setLocalValue}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="選択してください" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="option1">オプション1</SelectItem>
                <SelectItem value="option2">オプション2</SelectItem>
                <SelectItem value="option3">オプション3</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )
      case "approval":
        return (
          <div className="mt-3">
            <Label className="text-sm font-medium">{context.name}</Label>
            <div className="mt-2 space-y-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setLocalValue("approved")}
                className="mr-2"
              >
                承認
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setLocalValue("rejected")}
              >
                却下
              </Button>
            </div>
          </div>
        )
      default:
        return (
          <div className="mt-3">
            <Label htmlFor={`context-${context.id}`} className="text-sm font-medium">
              {context.name}
            </Label>
            <Textarea
              id={`context-${context.id}`}
              value={localValue}
              onChange={(e) => setLocalValue(e.target.value)}
              placeholder={`${context.name}を入力してください`}
              className="mt-1"
              rows={3}
            />
          </div>
        )
    }
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium">
            {context.name}
          </CardTitle>
          <div className="flex items-center gap-2">
            {context.required && (
              <Badge variant="outline" className="text-xs">
                必須
              </Badge>
            )}
            <Badge className={`text-xs ${getStatusColor(context.status)}`}>
              <span className="flex items-center gap-1">
                {getStatusIcon(context.status)}
                {context.status}
              </span>
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <p className="text-sm text-slate-600 leading-relaxed">
            {context.description}
          </p>

          {/* 現在の値の表示 */}
          {context.current_value && !isEditing && (
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <p className="text-xs text-slate-500 mb-1">現在の値:</p>
              <p className="text-sm text-slate-800">
                {typeof context.current_value === "object" 
                  ? JSON.stringify(context.current_value, null, 2)
                  : context.current_value
                }
              </p>
            </div>
          )}

          {/* 入力フィールド */}
          {renderInputField()}

          {/* アクション */}
          {showActions && editable && (
            <div className="flex items-center gap-2 pt-2">
              {!isEditing ? (
                <>
                  {context.status !== "sufficient" && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditing(true)}
                      className="flex items-center gap-1"
                    >
                      <Edit3 className="h-3 w-3" />
                      編集
                    </Button>
                  )}
                  {context.type === "file" && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex items-center gap-1"
                    >
                      <Upload className="h-3 w-3" />
                      アップロード
                    </Button>
                  )}
                </>
              ) : (
                <>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1"
                  >
                    <Save className="h-3 w-3" />
                    保存
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancel}
                    className="flex items-center gap-1"
                  >
                    <X className="h-3 w-3" />
                    キャンセル
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}