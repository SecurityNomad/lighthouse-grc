import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export interface Framework {
  id: string
  slug: string
  name: string
  version: string
  description?: string
  control_count: number
}

export interface Control {
  id: string
  framework_id: string
  ref: string
  domain: string
  title: string
  description?: string
}

export interface ControlWithMapping extends Control {
  notes?: string
  mapped_at: string
}

export const controlsApi = {
  listFrameworks: () => api.get<Framework[]>('/frameworks').then(r => r.data),
  listControls: (frameworkId: string, params?: { search?: string; domain?: string }) =>
    api.get<Control[]>(`/frameworks/${frameworkId}/controls`, { params }).then(r => r.data),
  getControl: (controlId: string) => api.get<Control>(`/controls/${controlId}`).then(r => r.data),
  listRiskControls: (riskId: string) =>
    api.get<ControlWithMapping[]>(`/risks/${riskId}/controls`).then(r => r.data),
  addRiskControl: (riskId: string, controlId: string, notes?: string) =>
    api.post(`/risks/${riskId}/controls`, { control_id: controlId, notes }).then(r => r.data),
  removeRiskControl: (riskId: string, controlId: string) =>
    api.delete(`/risks/${riskId}/controls/${controlId}`),
}
