import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { ApiError, getDashboard, refreshDashboard } from '../api'
import type { DashboardSnapshot } from '../types'

const NOT_READY_POLL_INTERVAL_MS = 5000

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
  const pollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const load = useCallback(async () => {
    try {
      const data = await getDashboard()
      setSnapshot(data)
      setError(null)
      setIsLoading(false)
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        // Backend hasn't generated a snapshot yet (e.g. right after startup) - keep polling
        // instead of surfacing an error, so the dashboard fills in on its own once ready.
        pollTimeoutRef.current = setTimeout(() => void load(), NOT_READY_POLL_INTERVAL_MS)
        return
      }
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data.')
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
    return () => {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current)
      }
    }
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
