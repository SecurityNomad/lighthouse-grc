import type { ReactNode } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import RisksPage from './pages/RisksPage'
import ControlsPage from './pages/ControlsPage'
import EvidencePage from './pages/EvidencePage'
import VendorsPage from './pages/VendorsPage'
import AuditPage from './pages/AuditPage'
import DashboardPage from './pages/DashboardPage'

function NavItem({ to, label }: { to: string; label: string }) {
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
          <NavItem to="/evidence" label="Evidence" />
          <NavItem to="/vendors" label="Vendors" />
          <NavItem to="/audits" label="Audits" />
          <NavItem to="/dashboard" label="Dashboard" />
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
          <Route path="/" element={<DashboardPage />} />
          <Route path="/risks" element={<RisksPage />} />
          <Route path="/controls" element={<ControlsPage />} />
          <Route path="/evidence" element={<EvidencePage />} />
          <Route path="/vendors" element={<VendorsPage />} />
          <Route path="/audits" element={<AuditPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
