import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export interface Vendor {
  id: string
  name: string
  description?: string
  category: string
  website?: string
  tier: number
  status: string
  contact_name?: string
  contact_email?: string
  contract_start?: string
  contract_end?: string
  created_at: string
  updated_at?: string
}

export type VendorCreate = Omit<Vendor, 'id' | 'created_at' | 'updated_at'>
export type VendorUpdate = Partial<VendorCreate>

export interface VendorQuestion {
  id: string
  ref: string
  category: string
  text: string
  question_type: string
  max_score: number
  weight: number
}

export interface VendorAssessment {
  id: string
  vendor_id: string
  status: string
  overall_score?: number
  created_at: string
  updated_at?: string
}

export interface VendorAnswerUpsert {
  question_id: string
  score?: number
  text_response?: string
}

export interface VendorRiskRating {
  vendor_id: string
  vendor_name: string
  tier: number
  overall_score?: number
  risk_rating: string
  assessment_id?: string
  assessed_at?: string
}

export const vendorsApi = {
  list: () => api.get<Vendor[]>('/vendors').then(r => r.data),
  get: (id: string) => api.get<Vendor>(`/vendors/${id}`).then(r => r.data),
  create: (data: VendorCreate) => api.post<Vendor>('/vendors', data).then(r => r.data),
  update: (id: string, data: VendorUpdate) => api.put<Vendor>(`/vendors/${id}`, data).then(r => r.data),
  delete: (id: string) => api.delete(`/vendors/${id}`),
  riskRatings: () => api.get<VendorRiskRating[]>('/vendors/risk-ratings').then(r => r.data),
  questions: () => api.get<VendorQuestion[]>('/vendor-questions').then(r => r.data),
  createAssessment: (vendorId: string) =>
    api.post<VendorAssessment>('/vendor-assessments', { vendor_id: vendorId }).then(r => r.data),
  submitAnswers: (assessmentId: string, answers: VendorAnswerUpsert[]) =>
    api.put(`/vendor-assessments/${assessmentId}/answers`, answers).then(r => r.data),
  scoreAssessment: (assessmentId: string) =>
    api.post(`/vendor-assessments/${assessmentId}/score`).then(r => r.data),
}
