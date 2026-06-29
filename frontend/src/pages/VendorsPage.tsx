import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { vendorsApi, type Vendor, type VendorCreate } from '../api/tprm'
import { useForm } from 'react-hook-form'

const TIER_BADGE: Record<number, string> = {
  1: 'badge-red',
  2: 'badge-orange',
  3: 'badge-blue',
}

const TIER_LABELS: Record<number, string> = {
  1: 'Tier 1 — Critical',
  2: 'Tier 2 — Important',
  3: 'Tier 3 — Standard',
}

const RATING_BADGE: Record<string, string> = {
  Critical: 'badge-red',
  High: 'badge-orange',
  Medium: 'badge-yellow',
  Low: 'badge-green',
  Unrated: 'badge-gray',
}

const VENDOR_STATUS_BADGE: Record<string, string> = {
  Active: 'badge-green',
  'Under Review': 'badge-orange',
  Offboarded: 'badge-gray',
}

function VendorModal({ vendor, onClose }: { vendor?: Vendor; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<VendorCreate>({
    defaultValues: vendor ? {
      name: vendor.name,
      description: vendor.description,
      category: vendor.category,
      website: vendor.website,
      tier: vendor.tier,
      status: vendor.status,
      contact_name: vendor.contact_name,
      contact_email: vendor.contact_email,
      contract_start: vendor.contract_start,
      contract_end: vendor.contract_end,
    } : { tier: 3, status: 'Active' },
  })

  const createMut = useMutation({
    mutationFn: vendorsApi.create,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['vendors'] }); onClose() },
  })
  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: string; data: VendorCreate }) => vendorsApi.update(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['vendors'] }); onClose() },
  })

  const onSubmit = (data: VendorCreate) => {
    if (vendor) updateMut.mutate({ id: vendor.id, data })
    else createMut.mutate(data)
  }

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="modal-header sticky top-0 bg-slate-50 dark:bg-slate-800 rounded-t-2xl z-10">
          <h2 className="modal-title">{vendor ? 'Edit Vendor' : 'Add Vendor'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="modal-body">
            <div>
              <label className="form-label">Name <span className="text-red-500">*</span></label>
              <input {...register('name', { required: 'Required' })} className="neu-input" />
              {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name.message}</p>}
            </div>
            <div>
              <label className="form-label">Category <span className="text-red-500">*</span></label>
              <input
                {...register('category', { required: 'Required' })}
                placeholder="e.g. Cloud Infrastructure, SaaS, Professional Services"
                className="neu-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Tier</label>
                <select {...register('tier', { valueAsNumber: true })} className="neu-select">
                  <option value={1}>Tier 1 — Critical</option>
                  <option value={2}>Tier 2 — Important</option>
                  <option value={3}>Tier 3 — Standard</option>
                </select>
              </div>
              <div>
                <label className="form-label">Status</label>
                <select {...register('status')} className="neu-select">
                  <option>Active</option>
                  <option>Under Review</option>
                  <option>Offboarded</option>
                </select>
              </div>
            </div>
            <div>
              <label className="form-label">Website</label>
              <input {...register('website')} className="neu-input" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Contact Name</label>
                <input {...register('contact_name')} className="neu-input" />
              </div>
              <div>
                <label className="form-label">Contact Email</label>
                <input {...register('contact_email')} type="email" className="neu-input" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Contract Start</label>
                <input {...register('contract_start')} type="date" className="neu-input" />
              </div>
              <div>
                <label className="form-label">Contract End</label>
                <input {...register('contract_end')} type="date" className="neu-input" />
              </div>
            </div>
            <div>
              <label className="form-label">Description</label>
              <textarea {...register('description')} rows={2} className="neu-input" />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button
              type="submit"
              disabled={isSubmitting || createMut.isPending || updateMut.isPending}
              className="btn-primary"
            >
              {vendor ? 'Save Changes' : 'Add Vendor'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function VendorsPage() {
  const [addOpen, setAddOpen] = useState(false)
  const [editVendor, setEditVendor] = useState<Vendor | null>(null)
  const qc = useQueryClient()

  const { data: vendors = [], isLoading } = useQuery({
    queryKey: ['vendors'],
    queryFn: vendorsApi.list,
  })

  const { data: ratings = [] } = useQuery({
    queryKey: ['vendorRatings'],
    queryFn: vendorsApi.riskRatings,
  })

  const deleteMut = useMutation({
    mutationFn: vendorsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }),
  })

  const ratingMap = Object.fromEntries(ratings.map(r => [r.vendor_id, r]))

  return (
    <>
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="page-title">Vendor Register</h1>
            <p className="page-subtitle">{vendors.length} vendor{vendors.length !== 1 ? 's' : ''}</p>
          </div>
          <button onClick={() => setAddOpen(true)} className="btn-primary">
            + Add Vendor
          </button>
        </div>

        {isLoading ? (
          <div className="text-sm text-slate-400 text-center py-16">Loading…</div>
        ) : vendors.length === 0 ? (
          <div className="neu-card py-16 text-center text-sm text-slate-400">
            No vendors yet. Add your first vendor to start building your TPRM register.
          </div>
        ) : (
          <div className="neu-table-wrap">
            <table className="neu-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Category</th>
                  <th>Tier</th>
                  <th>Status</th>
                  <th>Risk Rating</th>
                  <th>Contract End</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {vendors.map(v => {
                  const rating = ratingMap[v.id]
                  const ratingLabel = rating?.risk_rating ?? 'Unrated'
                  return (
                    <tr key={v.id} className="group">
                      <td>
                        <div className="font-medium text-slate-900 dark:text-slate-100">{v.name}</div>
                        {v.contact_email && (
                          <div className="text-xs text-slate-400">{v.contact_email}</div>
                        )}
                      </td>
                      <td className="text-slate-600 dark:text-slate-400">{v.category}</td>
                      <td>
                        <span className={`badge ${TIER_BADGE[v.tier] ?? 'badge-gray'}`}>
                          {TIER_LABELS[v.tier] ?? `Tier ${v.tier}`}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${VENDOR_STATUS_BADGE[v.status] ?? 'badge-gray'}`}>
                          {v.status}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${RATING_BADGE[ratingLabel] ?? 'badge-gray'}`}>
                          {ratingLabel}
                          {rating?.overall_score != null && (
                            <span className="ml-1 opacity-60">({rating.overall_score.toFixed(0)}%)</span>
                          )}
                        </span>
                      </td>
                      <td className="text-slate-500 dark:text-slate-400 text-xs">
                        {v.contract_end ?? '—'}
                      </td>
                      <td>
                        <div className="flex gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => setEditVendor(v)}
                            className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-medium"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => { if (confirm(`Delete vendor "${v.name}"?`)) deleteMut.mutate(v.id) }}
                            className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {addOpen && <VendorModal onClose={() => setAddOpen(false)} />}
      {editVendor && <VendorModal vendor={editVendor} onClose={() => setEditVendor(null)} />}
    </>
  )
}
