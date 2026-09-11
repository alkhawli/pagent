export interface Student {
  personId: number
  personType: number
  displayName: string
}

export interface HomeworkItem {
  id: number
  subject: string
  teacher: string | null
  text: string
  assigned_date: string | null
  due_date: string | null
  completed: boolean
}

export interface ScheduleItem {
  start_time: string | null
  end_time: string | null
  subject: string
  room: string
  cancelled: boolean
}

export interface MessageItem {
  id: number
  subject_de: string
  subject_en: string
  sender: string
  sent_at: string | null
  read: boolean
  has_attachments: boolean
  text_de: string
  text_en: string
  translated_at: string | null
}

export type RecommendationPriority = 'high' | 'medium' | 'low' | 'info'

export interface Recommendation {
  priority: RecommendationPriority
  category: string
  title: string
  detail: string
  date: string | null
}

export interface DashboardSection<T> {
  items: T[]
  error: string | null
}

export interface ScheduleSection {
  range_start: string
  range_end: string
  by_date: Record<string, ScheduleItem[]>
  error: string | null
}

export interface MessagesSection extends DashboardSection<MessageItem> {
  unread_count: number
}

export interface DashboardSnapshot {
  generated_at: string
  today: string
  student: Student | null
  recommendations: Recommendation[]
  homework: DashboardSection<HomeworkItem>
  messages: MessagesSection
  schedule: ScheduleSection
}

export interface ChatToolCall {
  tool: string
  arguments: Record<string, unknown>
  result: unknown
}

export interface ChatResponse {
  answer: string
  tool_calls: ChatToolCall[]
}
