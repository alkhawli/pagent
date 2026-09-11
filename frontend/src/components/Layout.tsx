import { Outlet, useNavigate } from 'react-router-dom'
import { useDashboard } from '../context/DashboardContext'
import { Sidebar } from './Sidebar'

export function Layout() {
  const { snapshot, isRefreshing, error, refresh } = useDashboard()
  const navigate = useNavigate()

  const handleLogout = () => {
    sessionStorage.clear()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-slate-100">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-4 md:px-6">
          <div className="ml-12 md:ml-0">
            <p className="text-sm font-medium text-slate-800 truncate max-w-[150px] sm:max-w-none">
              {snapshot?.student?.displayName ?? 'No student found'}
            </p>
            <p className="text-xs text-slate-400 hidden sm:block">
              {snapshot ? `Updated ${new Date(snapshot.generated_at).toLocaleString()}` : 'Loading…'}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => void refresh()}
              disabled={isRefreshing}
              className="rounded-lg bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 shadow-sm ring-1 ring-slate-200 hover:bg-slate-50 disabled:opacity-50 md:px-4"
            >
              <span className="hidden sm:inline">{isRefreshing ? 'Refreshing…' : 'Refresh now'}</span>
              <span className="sm:hidden">↻</span>
            </button>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg bg-white px-3 py-1.5 text-sm font-semibold text-red-600 shadow-sm ring-1 ring-slate-200 hover:bg-red-50 md:px-4"
            >
              <span className="hidden sm:inline">Logout</span>
              <span className="sm:hidden">→</span>
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto px-4 py-4 md:px-6 md:py-6">
          {error && (
            <p className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</p>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  )
}
