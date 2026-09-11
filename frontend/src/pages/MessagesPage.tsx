import { MessagesPanel } from '../components/MessagesPanel'
import { useDashboard } from '../context/DashboardContext'

export function MessagesPage() {
  const { snapshot, isLoading } = useDashboard()

  if (isLoading || !snapshot) {
    return <p className="text-sm text-slate-500">Loading messages…</p>
  }

  return <MessagesPanel messages={snapshot.messages} />
}
