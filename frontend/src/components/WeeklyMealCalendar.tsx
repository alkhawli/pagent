import { ChevronDown, ChevronUp, Clock } from 'lucide-react'
import { useState } from 'react'
import type { DayMeal } from '../types'

interface WeeklyMealCalendarProps {
  days: DayMeal[]
}

export function WeeklyMealCalendar({ days }: WeeklyMealCalendarProps) {
  const [expandedDay, setExpandedDay] = useState<string | null>(null)
  const todayIso = new Date().toISOString().split('T')[0]

  const toggleDay = (date: string) => {
    setExpandedDay(expandedDay === date ? null : date)
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
      {days.map((day) => {
        const isExpanded = expandedDay === day.date
        const isToday = day.date === todayIso

        return (
          <div
            key={day.date}
            className={`overflow-hidden rounded-lg border shadow-sm transition-shadow hover:shadow-md ${
              isToday
                ? 'border-indigo-400 bg-indigo-50/50 ring-2 ring-indigo-300'
                : 'border-slate-200 bg-white'
            }`}
          >
            {/* Day header */}
            <div className={`border-b px-4 py-3 ${
              isToday ? 'border-indigo-200 bg-indigo-100' : 'border-slate-100 bg-indigo-50'
            }`}>
              <div className="text-right">
                <h3 className="text-lg font-bold text-indigo-900">
                  {day.day_name}
                  {isToday && (
                    <span className="mr-2 rounded bg-indigo-600 px-2 py-0.5 text-xs text-white">اليوم</span>
                  )}
                </h3>
                <p className="text-xs text-indigo-600">{day.date}</p>
              </div>
            </div>

            {/* Recipe name */}
            <div className="px-4 py-4">
              <h4 className="text-right text-base font-semibold text-slate-800">{day.recipe_name}</h4>

              {/* Prep time & serves */}
              <div className="mt-3 flex flex-col gap-2 text-right text-sm text-slate-600">
                {day.prep_time && (
                  <div className="flex items-center justify-end gap-2">
                    <span>{day.prep_time}</span>
                    <Clock size={16} className="text-slate-400" />
                  </div>
                )}
                {day.serves && <div className="text-xs text-slate-500">{day.serves}</div>}
              </div>

              {/* Expand button */}
              <button
                type="button"
                onClick={() => toggleDay(day.date)}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp size={16} />
                    <span>خبّي التفاصيل</span>
                  </>
                ) : (
                  <>
                    <ChevronDown size={16} />
                    <span>فرجيني التفاصيل</span>
                  </>
                )}
              </button>
            </div>

            {/* Expanded content */}
            {isExpanded && (
              <div className="border-t border-slate-100 bg-slate-50 px-4 py-4">
                {/* Ingredients */}
                {day.ingredients.length > 0 && (
                  <div className="mb-4">
                    <h5 className="mb-2 text-right text-sm font-semibold text-slate-800">المكوّنات:</h5>
                    <ul className="space-y-1 text-right text-sm text-slate-700">
                      {day.ingredients.map((ingredient, idx) => (
                        <li key={idx} className="flex items-start justify-end gap-2">
                          <span>{ingredient}</span>
                          <span className="text-indigo-600">•</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Instructions */}
                {day.instructions.length > 0 && (
                  <div>
                    <h5 className="mb-2 text-right text-sm font-semibold text-slate-800">طريقة التحضير:</h5>
                    <ol className="space-y-2 text-right text-sm text-slate-700">
                      {day.instructions.map((instruction, idx) => (
                        <li key={idx} className="flex items-start justify-end gap-2">
                          <span>{instruction}</span>
                          <span className="font-semibold text-indigo-600">{idx + 1}.</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
