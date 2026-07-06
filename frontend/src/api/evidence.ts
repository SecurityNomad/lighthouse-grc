import api from './client'

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
  list: () => api.get<Evidence[]>('/evidence/').then(r => r.data),
  get: (id: string) => api.get<Evidence>(`/evidence/${id}`).then(r => r.data),
  upload: (formData: FormData) =>
    api.post<Evidence>('/evidence/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data),
  update: (id: string, data: EvidenceUpdate) =>
    api.patch<Evidence>(`/evidence/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/evidence/${id}`),
  // Fetch through axios so the Authorization header is attached, then trigger
  // a browser download from the returned blob.
  download: async (id: string, fileName: string) => {
    const resp = await api.get(`/evidence/${id}/download`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(resp.data as Blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },
}
