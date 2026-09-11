import type { HomeworkItem, ScheduleItem } from '../types'

interface DayDetailModalProps {
  dateIso: string
  lessons: ScheduleItem[]
  homework: HomeworkItem[]
  onClose: () => void
}

export function DayDetailModal({ dateIso, lessons, homework, onClose }: DayDetailModalProps) {
  const label = new Date(`${dateIso}T00:00:00`).toLocaleDateString(undefined, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-6 shadow-xl"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-800">{label}</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-2 py-1 text-sm text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <section className="mb-5">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-green-700">Schedule</h4>
          {lessons.length === 0 ? (
            <p className="text-sm text-slate-500">No lessons scheduled.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {lessons.map((lesson, index) => (
                <li key={index} className="flex items-center justify-between gap-3 py-2 text-sm">
                  <span className="w-24 shrink-0 text-slate-400">
                    {lesson.start_time}–{lesson.end_time}
                  </span>
                  <span className={`flex-1 font-medium ${lesson.cancelled ? 'text-slate-400 line-through' : 'text-slate-700'}`}>
                    {lesson.subject}
                  </span>
                  <span className="text-slate-400">{lesson.room}</span>
                  {lesson.cancelled && (
                    <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-600">Cancelled</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-red-700">Homework due</h4>
          {homework.length === 0 ? (
            <p className="text-sm text-slate-500">No homework due this day.</p>
          ) : (
            <ul className="flex flex-col gap-2">
              {homework.map((item) => (
                <li key={item.id} className="rounded-lg border border-red-100 bg-red-50 p-3 text-sm">
                  <p className="font-semibold text-slate-700">
                    {item.subject}
                    {item.teacher ? ` · ${item.teacher}` : ''}
                  </p>
                  <p className="mt-1 text-slate-600">{item.text || 'No description provided.'}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}
