import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export interface Evidence {
  id: string
  title: string
  description?: string
  control_id?: string
  expiry_date?: string
  file_name: string
  file_size: number
  mime_type: string
  uploaded_at: string
  status: string
}

export type EvidenceUpdate = {
  title?: string
  description?: string
  control_id?: string
  expiry_date?: string
}

export const evidenceApi = {
  list: () => api.get<Evidence[]>('/evidence').then(r => r.data),
  get: (id: string) => api.get<Evidence>(`/evidence/${id}`).then(r => r.data),
  upload: (formData: FormData) =>
    api.post<Evidence>('/evidence', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data),
  update: (id: string, data: EvidenceUpdate) =>
    api.put<Evidence>(`/evidence/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/evidence/${id}`),
}
