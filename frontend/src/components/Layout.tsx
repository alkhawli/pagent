import { Outlet } from 'react-router-dom'
import { useDashboard } from '../context/DashboardContext'
import { Sidebar } from './Sidebar'

export function Layout() {
  const { snapshot, isRefreshing, error, refresh } = useDashboard()

  return (
    <div className="flex h-screen bg-slate-100">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
          <div>
            <p className="text-sm font-medium text-slate-800">
              {snapshot?.student?.displayName ?? 'No student found'}
            </p>
            <p className="text-xs text-slate-400">
              {snapshot ? `Updated ${new Date(snapshot.generated_at).toLocaleString()}` : 'Loading…'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => void refresh()}
            disabled={isRefreshing}
            className="rounded-lg bg-white px-4 py-1.5 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-slate-200 hover:bg-slate-50 disabled:opacity-50"
          >
            {isRefreshing ? 'Refreshing…' : 'Refresh now'}
          </button>
        </header>
        <main className="flex-1 overflow-y-auto px-6 py-6">
          {error && (
            <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</p>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  )
}
