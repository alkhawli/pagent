import { Globe2, Newspaper, RefreshCw } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getNews, refreshNews } from '../api'
import type { NewsItem, NewsSnapshot } from '../types'

function NewsSection({ title, items }: { title: string; items: NewsItem[] }) {
  if (items.length === 0) return null

  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold text-slate-800">{title}</h2>
      <div className="grid gap-3 md:grid-cols-2">
        {items.map((item, index) => (
          <a
            key={index}
            href={item.url || undefined}
            target="_blank"
            rel="noreferrer"
            className="block rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md"
          >
            <p className="font-medium text-slate-800">{item.title}</p>
            <p className="mt-1 text-sm text-slate-600">{item.summary}</p>
            {item.source && <p className="mt-2 text-xs text-slate-400">{item.source}</p>}
          </a>
        ))}
      </div>
    </div>
  )
}

export function NewsPage() {
  const [news, setNews] = useState<NewsSnapshot | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getNews()
      .then(setNews)
      .catch(() => {
        // Ignore errors on initial load; the refresh button lets the user retry.
      })
  }, [])

  const handleRefresh = async () => {
    setIsLoading(true)
    setError(null)
    try {
      setNews(await refreshNews())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not refresh news')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Newspaper size={22} className="text-indigo-600" />
          <h1 className="text-xl font-bold text-slate-800">Daily News</h1>
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          disabled={isLoading}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
        >
          <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {!news && !error && (
        <p className="flex items-center gap-2 text-sm text-slate-500">
          <Globe2 size={16} /> News is not ready yet. Try refreshing.
        </p>
      )}

      {news && (
        <>
          <p className="text-xs text-slate-400">
            Updated {new Intl.DateTimeFormat('en-US', { dateStyle: 'medium', timeStyle: 'short' }).format(
              new Date(news.generated_at),
            )}
          </p>
          <NewsSection title="World" items={news.world} />
          <NewsSection title="Technology" items={news.tech} />
          <NewsSection title="Football" items={news.football} />
        </>
      )}
    </div>
  )
}
