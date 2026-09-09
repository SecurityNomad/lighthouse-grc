import api from './client'

export type ImplementationStatus =
  | 'Implemented'
  | 'Partially Implemented'
  | 'Planned'
  | 'Not Implemented'

export const IMPLEMENTATION_STATUSES: ImplementationStatus[] = [
  'Implemented',
  'Partially Implemented',
  'Planned',
  'Not Implemented',
]

export interface SoARow {
  control_id: string
  ref: string
  domain: string
  title: string
  description?: string
  entry_id?: string | null
  applicable: boolean
  justification?: string | null
  implementation_status: ImplementationStatus
  owner?: string | null
  last_reviewed?: string | null
}

export interface SoASummary {
  framework_slug: string
  framework_name: string
  total_controls: number
  assessed: number
  applicable: number
  excluded: number
  implemented: number
  partially_implemented: number
  planned: number
  not_implemented: number
  coverage_pct: number
  readiness_pct: number
}

export interface SoAData {
  summary: SoASummary
  rows: SoARow[]
}

export interface SoAEntryUpdate {
  applicable?: boolean
  justification?: string | null
  implementation_status?: ImplementationStatus
  owner?: string | null
  last_reviewed?: string | null
}

export const soaApi = {
  get: (frameworkSlug: string) =>
    api.get<SoAData>(`/soa/${frameworkSlug}`).then(r => r.data),
  update: (controlId: string, payload: SoAEntryUpdate) =>
    api.put<SoARow>(`/soa/control/${controlId}`, payload).then(r => r.data),
}
