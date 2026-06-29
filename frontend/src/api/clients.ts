import api from './client'

export interface Client {
  id: string
  name: string
  industry: string
  description?: string
  country?: string
  created_at: string
  updated_at?: string
}

export type ClientCreate = Omit<Client, 'id' | 'created_at' | 'updated_at'>
export type ClientUpdate = Partial<ClientCreate>

export const clientsApi = {
  list: () => api.get<Client[]>('/clients').then(r => r.data),
  get: (id: string) => api.get<Client>(`/clients/${id}`).then(r => r.data),
  create: (data: ClientCreate) => api.post<Client>('/clients', data).then(r => r.data),
  update: (id: string, data: ClientUpdate) => api.patch<Client>(`/clients/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/clients/${id}`),
}
