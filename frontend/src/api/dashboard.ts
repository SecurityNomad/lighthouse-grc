import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export interface DashboardData {
  open_risks_by_impact: { impact: string; count: number }[]
  high_risks_open: number
  control_coverage_pct: number
  evidence_expiring_soon: number
  evidence_expired: number
  vendors_by_tier: { tier: number; count: number }[]
  vendors_under_review: number
  open_findings: number
  audits_active: number
}

export const dashboardApi = {
  get: () => api.get<DashboardData>('/dashboard').then(r => r.data),
}
