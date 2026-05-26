import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

export interface AuditPlan {
  id: string
  title: string
  scope?: string
  status: string
  audit_start?: string
  audit_end?: string
  created_at: string
  updated_at?: string
}

export interface AuditPlanSummary extends AuditPlan {
  item_count: number
  pass_count: number
  fail_count: number
  exception_count: number
  not_tested_count: number
  open_findings: number
}

export type AuditPlanCreate = Omit<AuditPlan, 'id' | 'created_at' | 'updated_at'>
export type AuditPlanUpdate = Partial<AuditPlanCreate>

export interface AuditItem {
  id: string
  plan_id: string
  control_id?: string
  description: string
  test_result: string
  notes?: string
}

export type AuditItemCreate = Omit<AuditItem, 'id'>
export type AuditItemUpdate = Partial<Omit<AuditItem, 'id' | 'plan_id'>>

export interface AuditFinding {
  id: string
  plan_id: string
  title: string
  description: string
  severity: string
  status: string
  owner?: string
  due_date?: string
  closed_at?: string
  created_at: string
  updated_at?: string
}

export type AuditFindingCreate = Omit<AuditFinding, 'id' | 'created_at' | 'updated_at'>
export type AuditFindingUpdate = Partial<Omit<AuditFinding, 'id' | 'plan_id' | 'created_at' | 'updated_at'>>

export const auditsApi = {
  listPlans: () => api.get<AuditPlanSummary[]>('/audits').then(r => r.data),
  createPlan: (data: AuditPlanCreate) => api.post<AuditPlan>('/audits', data).then(r => r.data),
  updatePlan: (id: string, data: AuditPlanUpdate) => api.put<AuditPlan>(`/audits/${id}`, data).then(r => r.data),
  deletePlan: (id: string) => api.delete(`/audits/${id}`),
  listItems: (planId: string) => api.get<AuditItem[]>(`/audits/${planId}/items`).then(r => r.data),
  createItem: (data: AuditItemCreate) => api.post<AuditItem>(`/audits/${data.plan_id}/items`, data).then(r => r.data),
  updateItem: (planId: string, id: string, data: AuditItemUpdate) => api.put<AuditItem>(`/audits/${planId}/items/${id}`, data).then(r => r.data),
  deleteItem: (planId: string, id: string) => api.delete(`/audits/${planId}/items/${id}`),
  listFindings: (planId: string) => api.get<AuditFinding[]>(`/audits/${planId}/findings`).then(r => r.data),
  createFinding: (data: AuditFindingCreate) => api.post<AuditFinding>(`/audits/${data.plan_id}/findings`, data).then(r => r.data),
  updateFinding: (planId: string, id: string, data: AuditFindingUpdate) => api.put<AuditFinding>(`/audits/${planId}/findings/${id}`, data).then(r => r.data),
  deleteFinding: (planId: string, id: string) => api.delete(`/audits/${planId}/findings/${id}`),
}
