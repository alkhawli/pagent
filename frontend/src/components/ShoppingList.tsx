import { ShoppingCart, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { ShoppingItem } from '../types'

interface ShoppingListProps {
  shoppingList: ShoppingItem[]
}

const CHECKED_ITEMS_KEY = 'mealPlan_checkedItems'

export function ShoppingList({ shoppingList }: ShoppingListProps) {
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set())

  // Load checked items from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(CHECKED_ITEMS_KEY)
    if (stored) {
      try {
        setCheckedItems(new Set(JSON.parse(stored)))
      } catch {
        // Ignore parse errors
      }
    }
  }, [])

  // Save checked items to localStorage
  useEffect(() => {
    localStorage.setItem(CHECKED_ITEMS_KEY, JSON.stringify([...checkedItems]))
  }, [checkedItems])

  const toggleItem = (item: string) => {
    const newChecked = new Set(checkedItems)
    if (newChecked.has(item)) {
      newChecked.delete(item)
    } else {
      newChecked.add(item)
    }
    setCheckedItems(newChecked)
  }

  const clearAll = () => {
    setCheckedItems(new Set())
  }

  const totalItems = shoppingList.reduce((sum, category) => sum + category.items.length, 0)
  const checkedCount = checkedItems.size

  return (
    <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4 md:px-6">
        <div className="flex items-center gap-3">
          <ShoppingCart className="text-indigo-600" size={24} />
          <div className="text-right">
            <h3 className="text-lg font-bold text-slate-800">ليستة التسوّق</h3>
            <p className="text-xs text-slate-500">
              {checkedCount} من {totalItems} إنعمل
            </p>
          </div>
        </div>
        {checkedCount > 0 && (
          <button
            type="button"
            onClick={clearAll}
            className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            <X size={16} />
            <span className="hidden sm:inline">امسح كلشي</span>
          </button>
        )}
      </div>

      {/* Categories */}
      <div className="divide-y divide-slate-100 px-4 py-2 md:px-6">
        {shoppingList.map((category, catIdx) => (
          <div key={catIdx} className="py-4">
            <h4 className="mb-3 text-right text-base font-semibold text-slate-800">{category.category}</h4>
            <ul className="space-y-2">
              {category.items.map((item, itemIdx) => {
                const itemKey = `${catIdx}-${itemIdx}-${item}`
                const isChecked = checkedItems.has(itemKey)

                return (
                  <li key={itemIdx} className="flex items-center justify-end gap-3">
                    <label
                      className={`flex-1 cursor-pointer text-right text-sm transition ${
                        isChecked ? 'text-slate-400 line-through' : 'text-slate-700'
                      }`}
                    >
                      {item}
                    </label>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleItem(itemKey)}
                      className="h-5 w-5 cursor-pointer rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                    />
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </div>

      {shoppingList.length === 0 && (
        <div className="px-4 py-8 text-center text-sm text-slate-500 md:px-6">
          ما في شي بالليستة
        </div>
      )}
    </div>
  )
}
