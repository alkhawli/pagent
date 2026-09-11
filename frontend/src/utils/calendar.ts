export interface CalendarDay {
  date: Date
  iso: string
  inCurrentMonth: boolean
}

export function toIsoDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/** Builds a 6-week Monday-start grid for the given month, including padding days from adjacent months. */
export function buildMonthGrid(year: number, month: number): CalendarDay[][] {
  const firstOfMonth = new Date(year, month, 1)
  const startOffset = (firstOfMonth.getDay() + 6) % 7 // Monday = 0
  const cursor = new Date(year, month, 1 - startOffset)

  const weeks: CalendarDay[][] = []
  for (let week = 0; week < 6; week++) {
    const days: CalendarDay[] = []
    for (let day = 0; day < 7; day++) {
      days.push({
        date: new Date(cursor),
        iso: toIsoDate(cursor),
        inCurrentMonth: cursor.getMonth() === month,
      })
      cursor.setDate(cursor.getDate() + 1)
    }
    weeks.push(days)
  }
  return weeks
}
