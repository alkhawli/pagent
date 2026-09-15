import { Plus, RefreshCw, UtensilsCrossed, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { addFoodWish, deleteFoodWish, generateMealPlan, getFoodWishes, getMealPlan } from '../api'
import { ShoppingList } from '../components/ShoppingList'
import { WeeklyMealCalendar } from '../components/WeeklyMealCalendar'
import type { MealPlan } from '../types'

export function MealPlanPage() {
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null)
  const [wishes, setWishes] = useState<string[]>([])
  const [newWish, setNewWish] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingWishes, setIsLoadingWishes] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load meal plan from backend on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [plan, wishesData] = await Promise.all([
          getMealPlan().catch(() => null),
          getFoodWishes().catch(() => ({ wishes: [] })),
        ])
        if (plan) setMealPlan(plan)
        setWishes(wishesData.wishes)
      } catch {
        // Ignore errors on initial load
      }
    }
    void loadData()
  }, [])

  const handleRefresh = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const newPlan = await generateMealPlan()
      setMealPlan(newPlan)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ما قدرنا نعمل برنامج الأكل')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddWish = async () => {
    if (!newWish.trim()) return

    setIsLoadingWishes(true)
    try {
      const result = await addFoodWish(newWish.trim())
      setWishes(result.wishes)
      setNewWish('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ما قدرنا نضيف الرغبة')
    } finally {
      setIsLoadingWishes(false)
    }
  }

  const handleDeleteWish = async (index: number) => {
    setIsLoadingWishes(true)
    try {
      const result = await deleteFoodWish(index)
      setWishes(result.wishes)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'ما قدرنا نحذف الرغبة')
    } finally {
      setIsLoadingWishes(false)
    }
  }

  const formatTimestamp = (isoString: string) => {
    try {
      const date = new Date(isoString)
      return new Intl.DateTimeFormat('ar-SA', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(date)
    } catch {
      return isoString
    }
  }

  return (
    <div dir="rtl" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white px-4 py-6 shadow-sm md:flex-row md:items-center md:justify-between md:px-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100">
            <UtensilsCrossed className="text-indigo-600" size={28} />
          </div>
          <div className="text-right">
            <h1 className="text-2xl font-bold text-slate-800">برنامج الأكل للأسبوع</h1>
            <p className="text-sm text-slate-500">أكل صحّي وسريع للعيلة</p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          <button
            type="button"
            onClick={() => void handleRefresh()}
            disabled={isLoading}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-50"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            <span>{isLoading ? 'عم نعمل البرنامج...' : 'جدّد البرنامج'}</span>
          </button>

          {mealPlan && (
            <p className="text-xs text-slate-500">انعمل بتاريخ: {formatTimestamp(mealPlan.generated_at)}</p>
          )}
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-right text-sm text-red-700 ring-1 ring-red-200">
          {error}
        </div>
      )}

      {/* Empty state */}
      {!mealPlan && !isLoading && (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center">
          <UtensilsCrossed className="mx-auto mb-4 text-slate-400" size={48} />
          <h3 className="mb-2 text-lg font-semibold text-slate-700">ما في برنامج أكل حالياً</h3>
          <p className="mb-4 text-sm text-slate-500">دوس على "جدّد البرنامج" لتعمل برنامج جديد</p>
        </div>
      )}

      {/* Loading state */}
      {isLoading && !mealPlan && (
        <div className="rounded-lg border border-slate-200 bg-white px-4 py-12 text-center shadow-sm">
          <RefreshCw className="mx-auto mb-4 animate-spin text-indigo-600" size={48} />
          <p className="text-sm text-slate-600">عم نعمل برنامج الأكل...</p>
          <p className="mt-2 text-xs text-slate-500">ممكن ياخد شوي وقت</p>
        </div>
      )}

      {/* Food wishes section */}
      <div className="rounded-lg border border-slate-200 bg-white px-4 py-6 shadow-sm md:px-6">
        <h2 className="mb-4 text-right text-xl font-bold text-slate-800">رغبات الأكل</h2>
        <p className="mb-4 text-right text-sm text-slate-600">
          اكتب أكلات بتحبّها وبنحاول نحطّها بالبرنامج الجاي
        </p>

        {/* Add wish input */}
        <div className="mb-4 flex flex-col gap-2 md:flex-row">
          <input
            type="text"
            value={newWish}
            onChange={(e) => setNewWish(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void handleAddWish()
            }}
            placeholder="مثلاً: مجدرة، يخنة، مقلوبة..."
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-right text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
            disabled={isLoadingWishes}
          />
          <button
            type="button"
            onClick={() => void handleAddWish()}
            disabled={isLoadingWishes || !newWish.trim()}
            className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-50"
          >
            <Plus size={16} />
            <span>ضيف</span>
          </button>
        </div>

        {/* Wishes list */}
        {wishes.length > 0 ? (
          <ul className="space-y-2">
            {wishes.map((wish, index) => (
              <li
                key={index}
                className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3 text-right"
              >
                <span className="text-sm text-slate-700">{wish}</span>
                <button
                  type="button"
                  onClick={() => void handleDeleteWish(index)}
                  disabled={isLoadingWishes}
                  className="text-slate-400 transition hover:text-red-600 disabled:opacity-50"
                  aria-label="احذف"
                >
                  <X size={18} />
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-center text-sm text-slate-500">ما في رغبات حالياً</p>
        )}
      </div>

      {/* Meal plan content */}
      {mealPlan && (
        <>
          {/* Weekly calendar */}
          <div>
            <h2 className="mb-4 text-right text-xl font-bold text-slate-800">أكل الأسبوع</h2>
            <WeeklyMealCalendar days={mealPlan.days} />
          </div>

          {/* Shopping list */}
          <div>
            <ShoppingList shoppingList={mealPlan.shopping_list} />
          </div>
        </>
      )}
    </div>
  )
}
