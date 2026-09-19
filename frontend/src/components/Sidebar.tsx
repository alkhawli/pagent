import { Bot, LayoutDashboard, Menu, MessagesSquare, Newspaper, Sparkles, UtensilsCrossed, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/messages', label: 'Messages', icon: MessagesSquare, end: false },
  { to: '/chat', label: 'Chat', icon: Bot, end: false },
  { to: '/meal-plan', label: 'برنامج الأكل', icon: UtensilsCrossed, end: false },
  { to: '/news', label: 'News', icon: Newspaper, end: false },
  { to: '/trends', label: 'AI & GitHub Trends', icon: Sparkles, end: false },
]

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)

  const closeSidebar = () => setIsOpen(false)

  return (
    <>
      {/* Mobile menu button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="fixed left-4 top-4 z-50 rounded-lg bg-white p-2 shadow-lg ring-1 ring-slate-200 md:hidden"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 backdrop-blur-sm md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 flex h-screen w-60 shrink-0 flex-col border-r border-slate-200 bg-white transition-transform duration-200 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex items-center gap-2 px-5 py-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
            PA
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800">PAGENT</p>
            <p className="text-xs text-slate-400">Family Assistant</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={closeSidebar}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  )
}
