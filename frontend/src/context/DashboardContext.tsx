import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { getDashboard, refreshDashboard } from '../api'
import type { DashboardSnapshot } from '../types'

interface DashboardContextValue {
  snapshot: DashboardSnapshot | null
  isLoading: boolean
  isRefreshing: boolean
  error: string | null
  refresh: () => Promise<void>
}

const DashboardContext = createContext<DashboardContextValue | null>(null)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      setSnapshot(await getDashboard())
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const refresh = useCallback(async () => {
    setIsRefreshing(true)
    try {
      setSnapshot(await refreshDashboard())
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh dashboard data.')
    } finally {
      setIsRefreshing(false)
    }
  }, [])

  return (
    <DashboardContext.Provider value={{ snapshot, isLoading, isRefreshing, error, refresh }}>
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard(): DashboardContextValue {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error('useDashboard must be used within a DashboardProvider')
  }
  return context
}
