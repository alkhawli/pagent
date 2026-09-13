import { useMemo, useState } from 'react'
import type { HomeworkItem, ScheduleItem } from '../types'
import { buildMonthGrid, toIsoDate } from '../utils/calendar'
import { DayDetailModal } from './DayDetailModal'

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
const MONTH_LABELS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

interface CalendarViewProps {
  homework: HomeworkItem[]
  todayIso: string
  scheduleByDate: Record<string, ScheduleItem[]>
}

export function CalendarView({ homework, todayIso, scheduleByDate }: CalendarViewProps) {
  const today = useMemo(() => (todayIso ? new Date(`${todayIso}T00:00:00`) : new Date()), [todayIso])
  const [viewYear, setViewYear] = useState(today.getFullYear())
  const [viewMonth, setViewMonth] = useState(today.getMonth())
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  const weeks = useMemo(() => buildMonthGrid(viewYear, viewMonth), [viewYear, viewMonth])
  const resolvedTodayIso = todayIso || toIsoDate(new Date())

  const homeworkByDate = useMemo(() => {
    const map = new Map<string, HomeworkItem[]>()
    for (const item of homework) {
      if (!item.due_date) continue
      const list = map.get(item.due_date) ?? []
      list.push(item)
      map.set(item.due_date, list)
    }
    return map
  }, [homework])

  function goToPreviousMonth() {
    const prev = new Date(viewYear, viewMonth - 1, 1)
    setViewYear(prev.getFullYear())
    setViewMonth(prev.getMonth())
  }

  function goToNextMonth() {
    const next = new Date(viewYear, viewMonth + 1, 1)
    setViewYear(next.getFullYear())
    setViewMonth(next.getMonth())
  }

  function goToToday() {
    setViewYear(today.getFullYear())
    setViewMonth(today.getMonth())
  }

  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">Calendar</h2>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={goToPreviousMonth}
            className="rounded-md px-2 py-1 text-sm text-slate-500 hover:bg-slate-100"
            aria-label="Previous month"
          >
            ←
          </button>
          <span className="w-36 text-center text-sm font-semibold text-slate-700">
            {MONTH_LABELS[viewMonth]} {viewYear}
          </span>
          <button
            type="button"
            onClick={goToNextMonth}
            className="rounded-md px-2 py-1 text-sm text-slate-500 hover:bg-slate-100"
            aria-label="Next month"
          >
            →
          </button>
          <button
            type="button"
            onClick={goToToday}
            className="ml-2 rounded-md border border-slate-200 px-2 py-1 text-xs font-semibold text-slate-500 hover:bg-slate-100"
          >
            Today
          </button>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-1 text-center text-xs font-semibold uppercase tracking-wide text-slate-400">
        {WEEKDAY_LABELS.map((label) => (
          <div key={label} className="py-1">
            {label}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-5 gap-1">
        {weeks
          .flat()
          .filter((day) => day.date.getDay() !== 0 && day.date.getDay() !== 6)
          .map((day) => {
          const dueHomework = homeworkByDate.get(day.iso) ?? []
          const lessons = scheduleByDate[day.iso] ?? []
          const isToday = day.iso === resolvedTodayIso
          return (
            <button
              type="button"
              key={day.iso}
              onClick={() => setSelectedDate(day.iso)}
              className={`flex min-h-[110px] flex-col gap-1 rounded-lg border p-1.5 text-left transition hover:ring-2 hover:ring-indigo-300 ${
                isToday
                  ? 'border-2 border-indigo-600 bg-indigo-100 ring-2 ring-indigo-400 shadow-md'
                  : day.inCurrentMonth
                    ? 'border-slate-100 bg-white'
                    : 'border-transparent bg-slate-50 text-slate-300'
              }`}
            >
              <span className={`text-xs font-bold ${isToday ? 'text-indigo-900' : 'text-slate-500'}`}>
                {day.date.getDate()}
                {isToday && <span className="ml-1 rounded bg-indigo-700 px-1.5 py-0.5 text-[10px] font-bold text-white">TODAY</span>}
              </span>
              <div className="flex flex-col gap-0.5">
                {lessons.slice(0, 3).map((lesson, index) => (
                  <span
                    key={index}
                    title={`${lesson.start_time ?? ''}-${lesson.end_time ?? ''} ${lesson.subject}${lesson.room ? ` (${lesson.room})` : ''}`}
                    className={`truncate rounded px-1 py-0.5 text-[10px] font-medium ${
                      lesson.cancelled ? 'bg-slate-200 text-slate-500 line-through' : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {lesson.start_time} {lesson.subject}
                  </span>
                ))}
                {lessons.length > 3 && (
                  <span className="text-[10px] font-medium text-slate-400">+{lessons.length - 3} more lessons</span>
                )}
                {dueHomework.slice(0, 2).map((item) => (
                  <span
                    key={item.id}
                    title={item.text}
                    className="truncate rounded bg-red-100 px-1 py-0.5 text-[10px] font-medium text-red-700"
                  >
                    {item.subject}: {item.text || 'Homework'}
                  </span>
                ))}
                {dueHomework.length > 2 && (
                  <span className="text-[10px] font-medium text-slate-400">+{dueHomework.length - 2} more</span>
                )}
              </div>
            </button>
          )
        })}
      </div>

      {selectedDate && (
        <DayDetailModal
          dateIso={selectedDate}
          lessons={scheduleByDate[selectedDate] ?? []}
          homework={homeworkByDate.get(selectedDate) ?? []}
          onClose={() => setSelectedDate(null)}
        />
      )}
    </section>
  )
}
