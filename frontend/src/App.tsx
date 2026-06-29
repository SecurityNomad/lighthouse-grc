import { useState, useEffect, type ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import Sidebar from './components/Sidebar'
import LoginPage from './pages/LoginPage'
import RisksPage from './pages/RisksPage'
import ControlsPage from './pages/ControlsPage'
import EvidencePage from './pages/EvidencePage'
import VendorsPage from './pages/VendorsPage'
import AuditPage from './pages/AuditPage'
import DashboardPage from './pages/DashboardPage'
import ClientsPage from './pages/ClientsPage'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppLayout({ children }: { children: ReactNode }) {
  const [dark, setDark] = useState(() => localStorage.getItem('lh_dark') === 'true')

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('lh_dark', String(dark))
  }, [dark])

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-slate-900">
      <Sidebar dark={dark} onToggleDark={() => setDark(d => !d)} />
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
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
                  <Route path="/evidence" element={<EvidencePage />} />
                  <Route path="/vendors" element={<VendorsPage />} />
                  <Route path="/audits" element={<AuditPage />} />
                  <Route path="/clients" element={<ClientsPage />} />
                </Routes>
              </AppLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
