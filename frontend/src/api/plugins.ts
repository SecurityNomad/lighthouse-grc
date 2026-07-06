import api from './client'

export interface PluginStatus {
  configured: boolean
  healthy: boolean
  mode: 'live' | 'demo' | 'disabled'
  message: string
}

export interface Plugin {
  name: string
  display_name: string
  type: 'risk_source' | 'notification'
  version: string
  description: string
  status: PluginStatus
}

export interface PluginRunResult {
  plugin: string
  ok: boolean
  created: number
  skipped: number
  message: string
  errors: string[]
}

export const pluginsApi = {
  list: () => api.get<Plugin[]>('/plugins').then(r => r.data),
  run: (name: string) =>
    api.post<PluginRunResult>(`/plugins/${name}/run`).then(r => r.data),
}
