import { useState } from 'react'
import type { MessageItem, MessagesSection } from '../types'

function MessageCard({ message }: { message: MessageItem }) {
  const [showOriginal, setShowOriginal] = useState(false)

  return (
    <div
      className={`rounded-xl border p-3 ${
        message.read ? 'border-slate-200 bg-slate-50' : 'border-indigo-200 bg-indigo-50'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold text-slate-800">
          {(showOriginal ? message.subject_de : message.subject_en) || '(no subject)'}
        </p>
        {!message.read && (
          <span className="shrink-0 rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
            New
          </span>
        )}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        {message.sender} · {message.sent_at ?? 'unknown date'}
        {message.has_attachments ? ' · 📎 attachment' : ''}
      </p>
      <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">
        {showOriginal ? message.text_de : message.text_en}
      </p>
      <button
        type="button"
        onClick={() => setShowOriginal((value) => !value)}
        className="mt-2 text-xs font-semibold text-indigo-600 hover:underline"
      >
        {showOriginal ? 'Show English translation' : 'Show original (German)'}
      </button>
    </div>
  )
}

export function MessagesPanel({ messages }: { messages: MessagesSection }) {
  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">Latest messages</h2>
        {messages.unread_count > 0 && (
          <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-semibold text-indigo-700">
            {messages.unread_count} new
          </span>
        )}
      </div>
      {messages.error && (
        <p className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">{messages.error}</p>
      )}
      <div className="flex flex-col gap-3">
        {messages.items.map((message) => (
          <MessageCard key={message.id} message={message} />
        ))}
        {messages.items.length === 0 && !messages.error && (
          <p className="text-sm text-slate-500">No messages.</p>
        )}
      </div>
    </section>
  )

}
