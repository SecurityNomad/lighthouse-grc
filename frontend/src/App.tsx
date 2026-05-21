import type { ReactNode } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import RisksPage from './pages/RisksPage'
import ControlsPage from './pages/ControlsPage'

function NavItem({ to, label, disabled = false }: { to: string; label: string; disabled?: boolean }) {
  if (disabled) {
    return (
      <span className="px-3 py-2 text-sm text-gray-400 cursor-not-allowed">
        {label}
      </span>
    )
  }
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `px-3 py-2 text-sm rounded-md transition-colors ${
          isActive
            ? 'bg-blue-600 text-white'
            : 'text-gray-600 hover:bg-gray-100'
        }`
      }
    >
      {label}
    </NavLink>
  )
}

function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="text-xl">🏠</span>
          <span className="font-semibold text-gray-900">Lighthouse</span>
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">GRC</span>
        </div>
        <div className="flex items-center gap-1 ml-4">
          <NavItem to="/risks" label="Risk Register" />
          <NavItem to="/controls" label="Controls" />
          <NavItem to="/vendors" label="Vendors" disabled />
          <NavItem to="/audits" label="Audits" disabled />
          <NavItem to="/dashboard" label="Dashboard" disabled />
        </div>
      </nav>
      <main className="flex-1 px-6 py-6">
        {children}
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<RisksPage />} />
          <Route path="/risks" element={<RisksPage />} />
          <Route path="/controls" element={<ControlsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
