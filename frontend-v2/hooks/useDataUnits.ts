"use client"

import { useState, useEffect, useCallback } from "react"
import { dataUnitManager, type DataUnitConfig, type DataUnitCategoryInfo } from "@/lib/data-units-config"
import type { DataUnit, DataUnitCategory } from "@/types/agent"

export function useDataUnits() {
  const [dataUnits, setDataUnits] = useState<DataUnitConfig[]>([])
  const [categories, setCategories] = useState<DataUnitCategoryInfo[]>([])
  const [loading, setLoading] = useState(true)

  const loadData = useCallback(() => {
    setLoading(true)
    try {
      setDataUnits(dataUnitManager.getAllDataUnits())
      setCategories(dataUnitManager.getAllCategories())
    } catch (error) {
      console.error("Failed to load data units:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const getDataUnitsByCategory = useCallback((categoryName: string) => {
    return dataUnits.filter(unit => unit.category === categoryName)
  }, [dataUnits])

  const getDataUnitConfig = useCallback((value: DataUnit) => {
    return dataUnits.find(unit => unit.value === value)
  }, [dataUnits])

  const getDisplayLabel = useCallback((value: DataUnit) => {
    const config = getDataUnitConfig(value)
    return config ? config.label : value
  }, [getDataUnitConfig])

  const getGroupedDataUnits = useCallback(() => {
    return dataUnits.reduce((acc, unit) => {
      if (!acc[unit.category]) {
        acc[unit.category] = []
      }
      acc[unit.category].push(unit)
      return acc
    }, {} as Record<string, DataUnitConfig[]>)
  }, [dataUnits])

  const addDataUnit = useCallback((unit: Omit<DataUnitConfig, "editable">) => {
    try {
      dataUnitManager.addDataUnit(unit)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to add data unit:", error)
      return false
    }
  }, [loadData])

  const updateDataUnit = useCallback((oldValue: DataUnit, newUnit: DataUnitConfig) => {
    try {
      dataUnitManager.updateDataUnit(oldValue, newUnit)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to update data unit:", error)
      return false
    }
  }, [loadData])

  const deleteDataUnit = useCallback((value: DataUnit) => {
    try {
      dataUnitManager.deleteDataUnit(value)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to delete data unit:", error)
      return false
    }
  }, [loadData])

  const addCategory = useCallback((category: Omit<DataUnitCategoryInfo, "editable">) => {
    try {
      dataUnitManager.addCategory(category)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to add category:", error)
      return false
    }
  }, [loadData])

  const updateCategory = useCallback((oldId: string, newCategory: DataUnitCategoryInfo) => {
    try {
      dataUnitManager.updateCategory(oldId, newCategory)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to update category:", error)
      return false
    }
  }, [loadData])

  const deleteCategory = useCallback((id: string) => {
    try {
      dataUnitManager.deleteCategory(id)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to delete category:", error)
      return false
    }
  }, [loadData])

  const exportDataUnits = useCallback(() => {
    try {
      return dataUnitManager.exportDataUnits()
    } catch (error) {
      console.error("Failed to export data units:", error)
      return null
    }
  }, [])

  const importDataUnits = useCallback((jsonData: string) => {
    try {
      dataUnitManager.importDataUnits(jsonData)
      loadData()
      return true
    } catch (error) {
      console.error("Failed to import data units:", error)
      return false
    }
  }, [loadData])

  const clearCustomData = useCallback(() => {
    try {
      dataUnitManager.clearCustomData()
      loadData()
      return true
    } catch (error) {
      console.error("Failed to clear custom data:", error)
      return false
    }
  }, [loadData])

  const refreshData = useCallback(() => {
    loadData()
  }, [loadData])

  return {
    // Data
    dataUnits,
    categories,
    loading,
    
    // Getters
    getDataUnitsByCategory,
    getDataUnitConfig,
    getDisplayLabel,
    getGroupedDataUnits,
    
    // Data Unit Operations
    addDataUnit,
    updateDataUnit,
    deleteDataUnit,
    
    // Category Operations
    addCategory,
    updateCategory,
    deleteCategory,
    
    // Import/Export
    exportDataUnits,
    importDataUnits,
    clearCustomData,
    
    // Utility
    refreshData,
  }
}

export default useDataUnits