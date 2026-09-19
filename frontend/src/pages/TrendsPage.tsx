import { RefreshCw, Sparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getTrends, refreshTrends } from '../api'
import type { TrendsSnapshot } from '../types'

export function TrendsPage() {
  const [trends, setTrends] = useState<TrendsSnapshot | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getTrends()
      .then(setTrends)
      .catch(() => {
        // Ignore errors on initial load; the refresh button lets the user retry.
      })
  }, [])

  const handleRefresh = async () => {
    setIsLoading(true)
    setError(null)
    try {
      setTrends(await refreshTrends())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not refresh trends')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles size={22} className="text-indigo-600" />
          <h1 className="text-xl font-bold text-slate-800">Weekly AI &amp; GitHub Trends</h1>
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

      {!trends && !error && (
        <p className="text-sm text-slate-500">Trends are not ready yet. Try refreshing.</p>
      )}

      {trends && (
        <>
          <p className="text-xs text-slate-400">
            Updated {new Intl.DateTimeFormat('en-US', { dateStyle: 'medium', timeStyle: 'short' }).format(
              new Date(trends.generated_at),
            )}
          </p>

          {trends.ai_trends.length > 0 && (
            <div>
              <h2 className="mb-3 text-lg font-semibold text-slate-800">Latest AI Trends</h2>
              <div className="grid gap-3 md:grid-cols-2">
                {trends.ai_trends.map((item, index) => (
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
          )}

          {trends.github_repos.length > 0 && (
            <div>
              <h2 className="mb-3 text-lg font-semibold text-slate-800">
                Top Trending GitHub Repos
              </h2>
              <div className="grid gap-3 md:grid-cols-2">
                {trends.github_repos.map((repo, index) => (
                  <a
                    key={index}
                    href={repo.url || undefined}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md"
                  >
                    <p className="font-medium text-slate-800">{repo.name}</p>
                    <p className="mt-1 text-sm text-slate-600">{repo.description}</p>
                    <div className="mt-2 flex gap-3 text-xs text-slate-400">
                      {repo.language && <span>{repo.language}</span>}
                      {repo.stars && <span>★ {repo.stars}</span>}
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
