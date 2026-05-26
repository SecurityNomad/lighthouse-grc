import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export interface Risk {
  id: string
  title: string
  description?: string
  threat?: string
  scenario?: string
  impact: 'Critical' | 'High' | 'Medium' | 'Low'
  likelihood: 'Likely' | 'Possible' | 'Unlikely' | 'Rare'
  treatment: 'Accept' | 'Mitigate' | 'Transfer' | 'Avoid'
  treatment_notes?: string
  owner?: string
  status: 'Open' | 'In Treatment' | 'Closed' | 'Accepted'
  tags?: string[]
  review_date?: string
  created_at: string
  updated_at?: string
}

export type RiskCreate = Omit<Risk, 'id' | 'created_at' | 'updated_at'>
export type RiskUpdate = Partial<RiskCreate>

export const risksApi = {
  list: (status?: string) =>
    api.get<Risk[]>('/risks/', { params: status ? { status } : {} }).then(r => r.data),
  get: (id: string) => api.get<Risk>(`/risks/${id}`).then(r => r.data),
  create: (data: RiskCreate) => api.post<Risk>('/risks/', data).then(r => r.data),
  update: (id: string, data: RiskUpdate) => api.put<Risk>(`/risks/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/risks/${id}`),
}
