import type { ChatResponse, DashboardSnapshot } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8020'

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
    throw new Error(`Request to ${path} failed (${response.status}): ${body}`)
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
