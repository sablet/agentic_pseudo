"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog"
import { toast } from "@/components/ui/use-toast"
import { Plus, Edit2, Trash2, Download, Upload, Settings, X } from "lucide-react"
import type { DataUnit, DataUnitCategory } from "@/types/agent"
import { dataUnitManager, type DataUnitConfig, type DataUnitCategoryInfo } from "@/lib/data-units-config"

interface DataUnitManagerProps {
  onClose?: () => void
}

export function DataUnitManager({ onClose }: DataUnitManagerProps) {
  const [dataUnits, setDataUnits] = useState<DataUnitConfig[]>([])
  const [categories, setCategories] = useState<DataUnitCategoryInfo[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isCategoryDialogOpen, setIsCategoryDialogOpen] = useState(false)
  const [editingDataUnit, setEditingDataUnit] = useState<DataUnitConfig | null>(null)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<DataUnit | null>(null)
  const [newDataUnit, setNewDataUnit] = useState<Omit<DataUnitConfig, "editable">>({
    value: "",
    label: "",
    category: "",
  })
  const [newCategory, setNewCategory] = useState<Omit<DataUnitCategoryInfo, "editable">>({
    id: "",
    name: "",
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = () => {
    setDataUnits(dataUnitManager.getAllDataUnits())
    setCategories(dataUnitManager.getAllCategories())
  }

  const filteredDataUnits = dataUnits.filter(unit => {
    const matchesCategory = selectedCategory === "all" || unit.category === selectedCategory
    const matchesSearch = unit.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         unit.value.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const handleAddDataUnit = () => {
    if (!newDataUnit.value.trim() || !newDataUnit.label.trim() || !newDataUnit.category.trim()) {
      toast({
        title: "エラー",
        description: "すべてのフィールドを入力してください",
        variant: "destructive",
      })
      return
    }

    try {
      dataUnitManager.addDataUnit(newDataUnit)
      loadData()
      setIsAddDialogOpen(false)
      setNewDataUnit({ value: "", label: "", category: "" })
      toast({
        title: "成功",
        description: "データユニットが追加されました",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "データユニットの追加に失敗しました",
        variant: "destructive",
      })
    }
  }

  const handleEditDataUnit = () => {
    if (!editingDataUnit || !editingDataUnit.value.trim() || !editingDataUnit.label.trim()) {
      toast({
        title: "エラー",
        description: "すべてのフィールドを入力してください",
        variant: "destructive",
      })
      return
    }

    try {
      dataUnitManager.updateDataUnit(editingDataUnit.value, editingDataUnit)
      loadData()
      setIsEditDialogOpen(false)
      setEditingDataUnit(null)
      toast({
        title: "成功",
        description: "データユニットが更新されました",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "データユニットの更新に失敗しました",
        variant: "destructive",
      })
    }
  }

  const handleDeleteDataUnit = (value: DataUnit) => {
    setDeleteTarget(value)
    setDeleteConfirmOpen(true)
  }

  const confirmDelete = () => {
    if (deleteTarget) {
      try {
        dataUnitManager.deleteDataUnit(deleteTarget)
        loadData()
        toast({
          title: "成功",
          description: "データユニットが削除されました",
        })
      } catch (error) {
        toast({
          title: "エラー",
          description: "データユニットの削除に失敗しました",
          variant: "destructive",
        })
      }
    }
    setDeleteConfirmOpen(false)
    setDeleteTarget(null)
  }

  const handleAddCategory = () => {
    if (!newCategory.id.trim() || !newCategory.name.trim()) {
      toast({
        title: "エラー",
        description: "すべてのフィールドを入力してください",
        variant: "destructive",
      })
      return
    }

    try {
      dataUnitManager.addCategory(newCategory)
      loadData()
      setIsCategoryDialogOpen(false)
      setNewCategory({ id: "", name: "" })
      toast({
        title: "成功",
        description: "カテゴリが追加されました",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "カテゴリの追加に失敗しました",
        variant: "destructive",
      })
    }
  }

  const handleExport = () => {
    try {
      const exportData = dataUnitManager.exportDataUnits()
      const blob = new Blob([exportData], { type: "application/json" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `data-units-${new Date().toISOString().split("T")[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast({
        title: "成功",
        description: "データユニットがエクスポートされました",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "エクスポートに失敗しました",
        variant: "destructive",
      })
    }
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string
        dataUnitManager.importDataUnits(content)
        loadData()
        toast({
          title: "成功",
          description: "データユニットがインポートされました",
        })
      } catch (error) {
        toast({
          title: "エラー",
          description: "インポートに失敗しました。ファイル形式を確認してください",
          variant: "destructive",
        })
      }
    }
    reader.readAsText(file)
    event.target.value = ""
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-6xl h-[90vh] m-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>データユニット管理</CardTitle>
              <CardDescription>
                データユニットの追加、編集、削除を行います
              </CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="data-units" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="data-units">データユニット</TabsTrigger>
              <TabsTrigger value="categories">カテゴリ</TabsTrigger>
            </TabsList>
            
            <TabsContent value="data-units" className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="データユニットを検索..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="カテゴリ選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">すべてのカテゴリ</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.name}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-wrap gap-2">
                <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      データユニット追加
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>新しいデータユニット</DialogTitle>
                      <DialogDescription>
                        新しいデータユニットの情報を入力してください
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="value">値 (英語)</Label>
                        <Input
                          id="value"
                          value={newDataUnit.value}
                          onChange={(e) => setNewDataUnit({ ...newDataUnit, value: e.target.value })}
                          placeholder="例: custom_report"
                        />
                      </div>
                      <div>
                        <Label htmlFor="label">表示名 (日本語)</Label>
                        <Input
                          id="label"
                          value={newDataUnit.label}
                          onChange={(e) => setNewDataUnit({ ...newDataUnit, label: e.target.value })}
                          placeholder="例: カスタムレポート"
                        />
                      </div>
                      <div>
                        <Label htmlFor="category">カテゴリ</Label>
                        <Select value={newDataUnit.category} onValueChange={(value) => setNewDataUnit({ ...newDataUnit, category: value })}>
                          <SelectTrigger>
                            <SelectValue placeholder="カテゴリを選択" />
                          </SelectTrigger>
                          <SelectContent>
                            {categories.map((category) => (
                              <SelectItem key={category.id} value={category.name}>
                                {category.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex gap-2">
                        <Button onClick={handleAddDataUnit} className="flex-1">
                          追加
                        </Button>
                        <Button variant="outline" onClick={() => setIsAddDialogOpen(false)} className="flex-1">
                          キャンセル
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>

                <Button variant="outline" onClick={handleExport}>
                  <Download className="h-4 w-4 mr-2" />
                  エクスポート
                </Button>
                
                <Button variant="outline" className="relative">
                  <Upload className="h-4 w-4 mr-2" />
                  インポート
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleImport}
                    className="absolute inset-0 opacity-0 cursor-pointer"
                  />
                </Button>
              </div>

              <div className="rounded-md border">
                <ScrollArea className="h-[400px]">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>表示名</TableHead>
                        <TableHead>値</TableHead>
                        <TableHead>カテゴリ</TableHead>
                        <TableHead>状態</TableHead>
                        <TableHead className="text-right">操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredDataUnits.map((unit) => (
                        <TableRow key={unit.value}>
                          <TableCell className="font-medium">{unit.label}</TableCell>
                          <TableCell className="font-mono text-sm">{unit.value}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{unit.category}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={unit.editable ? "default" : "secondary"}>
                              {unit.editable ? "カスタム" : "デフォルト"}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex gap-2 justify-end">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => {
                                  setEditingDataUnit(unit)
                                  setIsEditDialogOpen(true)
                                }}
                              >
                                <Edit2 className="h-4 w-4" />
                              </Button>
                              {unit.editable && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleDeleteDataUnit(unit.value)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>
              </div>
            </TabsContent>

            <TabsContent value="categories" className="space-y-4">
              <div className="flex gap-2">
                <Dialog open={isCategoryDialogOpen} onOpenChange={setIsCategoryDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      カテゴリ追加
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>新しいカテゴリ</DialogTitle>
                      <DialogDescription>
                        新しいカテゴリの情報を入力してください
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="category-id">ID</Label>
                        <Input
                          id="category-id"
                          value={newCategory.id}
                          onChange={(e) => setNewCategory({ ...newCategory, id: e.target.value })}
                          placeholder="例: custom_category"
                        />
                      </div>
                      <div>
                        <Label htmlFor="category-name">名前</Label>
                        <Input
                          id="category-name"
                          value={newCategory.name}
                          onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                          placeholder="例: カスタムカテゴリ"
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button onClick={handleAddCategory} className="flex-1">
                          追加
                        </Button>
                        <Button variant="outline" onClick={() => setIsCategoryDialogOpen(false)} className="flex-1">
                          キャンセル
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>

              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>名前</TableHead>
                      <TableHead>ID</TableHead>
                      <TableHead>データユニット数</TableHead>
                      <TableHead>状態</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {categories.map((category) => (
                      <TableRow key={category.id}>
                        <TableCell className="font-medium">{category.name}</TableCell>
                        <TableCell className="font-mono text-sm">{category.id}</TableCell>
                        <TableCell>
                          {dataUnits.filter(unit => unit.category === category.name).length}
                        </TableCell>
                        <TableCell>
                          <Badge variant={category.editable ? "default" : "secondary"}>
                            {category.editable ? "カスタム" : "デフォルト"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          {category.editable && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                dataUnitManager.deleteCategory(category.id)
                                loadData()
                                toast({
                                  title: "成功",
                                  description: "カテゴリが削除されました",
                                })
                              }}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>データユニット編集</DialogTitle>
            <DialogDescription>
              データユニットの情報を編集してください
            </DialogDescription>
          </DialogHeader>
          {editingDataUnit && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="edit-value">値 (英語)</Label>
                <Input
                  id="edit-value"
                  value={editingDataUnit.value}
                  onChange={(e) => setEditingDataUnit({ ...editingDataUnit, value: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="edit-label">表示名 (日本語)</Label>
                <Input
                  id="edit-label"
                  value={editingDataUnit.label}
                  onChange={(e) => setEditingDataUnit({ ...editingDataUnit, label: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="edit-category">カテゴリ</Label>
                <Select value={editingDataUnit.category} onValueChange={(value) => setEditingDataUnit({ ...editingDataUnit, category: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.name}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleEditDataUnit} className="flex-1">
                  更新
                </Button>
                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)} className="flex-1">
                  キャンセル
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>データユニットを削除しますか？</AlertDialogTitle>
            <AlertDialogDescription>
              この操作は元に戻せません。データユニット「{deleteTarget}」を削除しますか？
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>キャンセル</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete}>削除</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}