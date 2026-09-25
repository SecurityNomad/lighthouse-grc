import { useState, type ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Sidebar from './components/Sidebar'
import LoginPage from './pages/LoginPage'
import RisksPage from './pages/RisksPage'
import ControlsPage from './pages/ControlsPage'
import SoAPage from './pages/SoAPage'
import EvidencePage from './pages/EvidencePage'
import VendorsPage from './pages/VendorsPage'
import AuditPage from './pages/AuditPage'
import DashboardPage from './pages/DashboardPage'
import ClientsPage from './pages/ClientsPage'
import PluginsPage from './pages/PluginsPage'
import AdminPage from './pages/AdminPage'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppLayout({ children }: { children: ReactNode }) {
  // index.html sets the initial class before paint; persist only explicit toggles.
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'))

  function toggleDark() {
    const next = !dark
    document.documentElement.classList.toggle('dark', next)
    localStorage.setItem('lh_dark', String(next))
    setDark(next)
  }

  return (
    <div className="flex min-h-screen bg-slate-100 dark:bg-slate-900">
      <Sidebar dark={dark} onToggleDark={toggleDark} />
      <main className="flex-1 min-w-0 overflow-auto p-4 md:p-6">
        {children}
      </main>
    </div>
  )
}

function NotFound() {
  return (
    <div className="max-w-md">
      <h1 className="page-title">Page not found</h1>
      <p className="page-subtitle mb-5">This address doesn't match any part of Lighthouse.</p>
      <Link to="/dashboard" className="btn-primary inline-block">Go to dashboard</Link>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Routes>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/risks" element={<RisksPage />} />
                  <Route path="/controls" element={<ControlsPage />} />
                  <Route path="/soa" element={<SoAPage />} />
                  <Route path="/evidence" element={<EvidencePage />} />
                  <Route path="/vendors" element={<VendorsPage />} />
                  <Route path="/audits" element={<AuditPage />} />
                  <Route path="/clients" element={<ClientsPage />} />
                  <Route path="/plugins" element={<PluginsPage />} />
                  <Route path="/admin" element={<AdminPage />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </AppLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
