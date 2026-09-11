import { CalendarView } from '../components/CalendarView'
import { RecommendationsPanel } from '../components/RecommendationsPanel'
import { useDashboard } from '../context/DashboardContext'

export function OverviewPage() {
  const { snapshot, isLoading } = useDashboard()

  if (isLoading || !snapshot) {
    return <p className="text-sm text-slate-500">Loading dashboard…</p>
  }

  return (
    <div className="flex flex-col gap-6">
      <RecommendationsPanel recommendations={snapshot.recommendations} />
      <CalendarView
        homework={snapshot.homework.items}
        todayIso={snapshot.today}
        scheduleByDate={snapshot.schedule.by_date}
      />
    </div>
  )
}
