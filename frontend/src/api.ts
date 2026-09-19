import type { ChatResponse, DashboardSnapshot, MealPlan, NewsSnapshot, TrendsSnapshot } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8020'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const apiKey = sessionStorage.getItem('apiKey')
  const headers: HeadersInit = { 'Content-Type': 'application/json' }

  if (apiKey) {
    headers['X-API-Key'] = apiKey
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers,
    ...init,
  })
  if (!response.ok) {
    const body = await response.text().catch(() => '')
    throw new ApiError(`Request to ${path} failed (${response.status}): ${body}`, response.status)
  }
  return (await response.json()) as T
}

export function getDashboard(): Promise<DashboardSnapshot> {
  return request<DashboardSnapshot>('/dashboard')
}

export function refreshDashboard(): Promise<DashboardSnapshot> {
  return request<DashboardSnapshot>('/dashboard/refresh', { method: 'POST' })
}

export function sendChatMessage(message: string): Promise<ChatResponse> {
  return request<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function getMealPlan(): Promise<MealPlan> {
  return request<MealPlan>('/meal-plan')
}

export function generateMealPlan(): Promise<MealPlan> {
  return request<MealPlan>('/meal-plan/generate', { method: 'POST' })
}

export function getFoodWishes(): Promise<{ wishes: string[] }> {
  return request<{ wishes: string[] }>('/meal-plan/wishes')
}

export function addFoodWish(text: string): Promise<{ wishes: string[] }> {
  return request<{ wishes: string[] }>('/meal-plan/wishes', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export function deleteFoodWish(index: number): Promise<{ wishes: string[] }> {
  return request<{ wishes: string[] }>(`/meal-plan/wishes/${index}`, {
    method: 'DELETE',
  })
}

export function getNews(): Promise<NewsSnapshot> {
  return request<NewsSnapshot>('/news')
}

export function refreshNews(): Promise<NewsSnapshot> {
  return request<NewsSnapshot>('/news/refresh', { method: 'POST' })
}

export function getTrends(): Promise<TrendsSnapshot> {
  return request<TrendsSnapshot>('/trends')
}

export function refreshTrends(): Promise<TrendsSnapshot> {
  return request<TrendsSnapshot>('/trends/refresh', { method: 'POST' })
}
