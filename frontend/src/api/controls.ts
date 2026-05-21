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

export const controlsApi = {
  listFrameworks: () => api.get<Framework[]>('/frameworks').then(r => r.data),
  listControls: (frameworkId: string, params?: { search?: string; domain?: string }) =>
    api.get<Control[]>(`/frameworks/${frameworkId}/controls`, { params }).then(r => r.data),
  getControl: (controlId: string) => api.get<Control>(`/controls/${controlId}`).then(r => r.data),
}
