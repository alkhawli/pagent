import { useState } from 'react'
import type { FormEvent } from 'react'
import { sendChatMessage } from '../api'

interface ChatEntry {
  role: 'user' | 'assistant'
  text: string
}

export function ChatPanel() {
  const [entries, setEntries] = useState<ChatEntry[]>([
    { role: 'assistant', text: 'Ask me anything about homework, schedule, exams, or messages.' },
  ])
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = message.trim()
    if (!trimmed || isSending) return

    setEntries((prev) => [...prev, { role: 'user', text: trimmed }])
    setMessage('')
    setIsSending(true)
    setError(null)

    try {
      const response = await sendChatMessage(trimmed)
      setEntries((prev) => [...prev, { role: 'assistant', text: response.answer }])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat request failed.')
    } finally {
      setIsSending(false)
    }
  }

  return (
    <section className="flex h-full flex-col rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">Ask the assistant</h2>
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {entries.map((entry, index) => (
          <div
            key={index}
            className={`max-w-[85%] rounded-xl px-3 py-2 text-sm whitespace-pre-wrap ${
              entry.role === 'user'
                ? 'ml-auto bg-indigo-600 text-white'
                : 'bg-slate-100 text-slate-700'
            }`}
          >
            {entry.text}
          </div>
        ))}
        {isSending && <div className="max-w-[85%] rounded-xl bg-slate-100 px-3 py-2 text-sm text-slate-400">Thinking…</div>}
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="e.g. What homework is due this week?"
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={isSending}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </section>
  )
}
