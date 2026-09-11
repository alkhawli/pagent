import type { RecommendationPriority } from '../types'

const STYLES: Record<RecommendationPriority, string> = {
  high: 'bg-red-100 text-red-700 border-red-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-blue-100 text-blue-700 border-blue-200',
  info: 'bg-slate-100 text-slate-600 border-slate-200',
}

const LABELS: Record<RecommendationPriority, string> = {
  high: 'High priority',
  medium: 'Medium priority',
  low: 'Heads up',
  info: 'Info',
}

export function PriorityBadge({ priority }: { priority: RecommendationPriority }) {
  return (
    <span className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold ${STYLES[priority]}`}>
      {LABELS[priority]}
    </span>
  )
}
