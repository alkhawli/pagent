import type { Recommendation } from '../types'
import { PriorityBadge } from './PriorityBadge'

export function RecommendationsPanel({ recommendations }: { recommendations: Recommendation[] }) {
  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">Recommendations of the day</h2>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {recommendations.map((item, index) => (
          <div key={index} className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center justify-between gap-2">
              <PriorityBadge priority={item.priority} />
              <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{item.category}</span>
            </div>
            <p className="text-sm font-semibold text-slate-800">{item.title}</p>
            <p className="text-sm text-slate-500">{item.detail}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
