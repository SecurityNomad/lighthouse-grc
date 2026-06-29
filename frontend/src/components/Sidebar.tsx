import { useState, useEffect } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Shield, BookOpen, FileCheck, Building2,
  ClipboardList, Users, ChevronLeft, ChevronRight, Sun, Moon, LogOut,
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useClient } from '../contexts/ClientContext'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/risks', icon: Shield, label: 'Risk Register' },
  { to: '/controls', icon: BookOpen, label: 'Controls' },
  { to: '/evidence', icon: FileCheck, label: 'Evidence' },
  { to: '/vendors', icon: Building2, label: 'Vendors' },
  { to: '/audits', icon: ClipboardList, label: 'Audits' },
  { to: '/clients', icon: Users, label: 'Clients' },
]

interface SidebarProps {
  dark: boolean
  onToggleDark: () => void
}

export default function Sidebar({ dark, onToggleDark }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem('lh_sidebar_collapsed') === 'true')
  const { user, logout } = useAuth()
  const { clients, selectedClient, selectClient } = useClient()
  const navigate = useNavigate()

  useEffect(() => {
    localStorage.setItem('lh_sidebar_collapsed', String(collapsed))
  }, [collapsed])

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const w = collapsed ? 'w-16' : 'w-60'

  return (
    <aside className={`${w} flex-shrink-0 bg-slate-900 flex flex-col transition-all duration-200 min-h-screen`}>
      {/* Logo + collapse */}
      <div className="flex items-center justify-between px-3 h-14 border-b border-slate-700">
        {!collapsed && (
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-indigo-400 font-bold text-lg leading-none">L</span>
            <span className="text-white font-semibold text-sm truncate">Lighthouse</span>
            <span className="text-xs text-slate-400 bg-slate-700 px-1.5 py-0.5 rounded shrink-0">GRC</span>
          </div>
        )}
        {collapsed && <span className="text-indigo-400 font-bold text-lg mx-auto">L</span>}
        <button
          onClick={() => setCollapsed(c => !c)}
          className="text-slate-400 hover:text-white p-1 rounded ml-auto"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Client selector */}
      {!collapsed && (
        <div className="px-3 py-2 border-b border-slate-700">
          <p className="text-xs text-slate-500 mb-1 uppercase tracking-wide">Client</p>
          <select
            value={selectedClient?.id ?? ''}
            onChange={e => {
              const found = clients.find(c => c.id === e.target.value)
              selectClient(found ?? null)
            }}
            className="w-full bg-slate-800 text-slate-200 text-sm rounded px-2 py-1.5 border border-slate-600 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All clients</option>
            {clients.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
      )}

      {/* Nav links */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 mx-2 my-0.5 rounded-md text-sm transition-colors ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`
            }
          >
            <Icon size={18} className="shrink-0" />
            {!collapsed && <span className="truncate">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Bottom: dark mode + user + logout */}
      <div className="border-t border-slate-700 p-3 space-y-1">
        <button
          onClick={onToggleDark}
          className="flex items-center gap-3 w-full px-2 py-2 rounded-md text-slate-400 hover:bg-slate-800 hover:text-white text-sm transition-colors"
        >
          {dark ? <Sun size={18} className="shrink-0" /> : <Moon size={18} className="shrink-0" />}
          {!collapsed && <span>{dark ? 'Light mode' : 'Dark mode'}</span>}
        </button>
        {!collapsed && user && (
          <div className="px-2 py-1">
            <p className="text-xs text-slate-300 font-medium truncate">{user.full_name}</p>
            <p className="text-xs text-slate-500 truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-2 py-2 rounded-md text-slate-400 hover:bg-slate-800 hover:text-red-400 text-sm transition-colors"
        >
          <LogOut size={18} className="shrink-0" />
          {!collapsed && <span>Log out</span>}
        </button>
      </div>
    </aside>
  )
}
