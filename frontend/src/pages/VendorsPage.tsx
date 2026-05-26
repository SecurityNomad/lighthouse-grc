import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { vendorsApi, type Vendor, type VendorCreate } from '../api/tprm'
import { useForm } from 'react-hook-form'

const TIER_LABELS: Record<number, string> = {
  1: 'Tier 1 — Critical',
  2: 'Tier 2 — Important',
  3: 'Tier 3 — Standard',
}

const TIER_COLORS: Record<number, string> = {
  1: 'text-red-700 bg-red-50 border-red-200',
  2: 'text-orange-700 bg-orange-50 border-orange-200',
  3: 'text-blue-700 bg-blue-50 border-blue-200',
}

const RATING_COLORS: Record<string, string> = {
  Critical: 'text-red-700 bg-red-50',
  High: 'text-orange-700 bg-orange-50',
  Medium: 'text-yellow-700 bg-yellow-50',
  Low: 'text-green-700 bg-green-50',
  Unrated: 'text-gray-500 bg-gray-50',
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {vendor ? 'Edit Vendor' : 'Add Vendor'}
          </h2>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Name *</label>
            <input
              {...register('name', { required: 'Required' })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.name && <p className="text-xs text-red-600 mt-1">{errors.name.message}</p>}
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Category *</label>
            <input
              {...register('category', { required: 'Required' })}
              placeholder="e.g. Cloud Infrastructure, SaaS, Professional Services"
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Tier</label>
              <select
                {...register('tier', { valueAsNumber: true })}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>Tier 1 — Critical</option>
                <option value={2}>Tier 2 — Important</option>
                <option value={3}>Tier 3 — Standard</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
              <select
                {...register('status')}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option>Active</option>
                <option>Under Review</option>
                <option>Offboarded</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Website</label>
            <input
              {...register('website')}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Contact Name</label>
              <input
                {...register('contact_name')}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Contact Email</label>
              <input
                {...register('contact_email')}
                type="email"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Contract Start</label>
              <input
                {...register('contract_start')}
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Contract End</label>
              <input
                {...register('contract_end')}
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea
              {...register('description')}
              rows={2}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || createMut.isPending || updateMut.isPending}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
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
            <h1 className="text-2xl font-bold text-gray-900">Vendor Register</h1>
            <p className="text-sm text-gray-500 mt-1">
              {vendors.length} vendor{vendors.length !== 1 ? 's' : ''}
            </p>
          </div>
          <button
            onClick={() => setAddOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + Add Vendor
          </button>
        </div>

        {isLoading ? (
          <div className="text-sm text-gray-400 text-center py-16">Loading…</div>
        ) : vendors.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 py-16 text-center text-sm text-gray-400">
            No vendors yet. Add your first vendor to start building your TPRM register.
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Vendor</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Category</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Tier</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Risk Rating</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Contract End</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {vendors.map(v => {
                  const rating = ratingMap[v.id]
                  const ratingLabel = rating?.risk_rating ?? 'Unrated'
                  return (
                    <tr key={v.id} className="hover:bg-gray-50 group">
                      <td className="px-4 py-3 font-medium text-gray-900">
                        <div>{v.name}</div>
                        {v.contact_email && (
                          <div className="text-xs text-gray-400">{v.contact_email}</div>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-600">{v.category}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${TIER_COLORS[v.tier] ?? 'text-gray-600 bg-gray-50 border-gray-200'}`}>
                          {TIER_LABELS[v.tier] ?? `Tier ${v.tier}`}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs font-medium ${v.status === 'Active' ? 'text-green-700' : v.status === 'Under Review' ? 'text-orange-700' : 'text-gray-500'}`}>
                          {v.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${RATING_COLORS[ratingLabel] ?? 'text-gray-500 bg-gray-50'}`}>
                          {ratingLabel}
                          {rating?.overall_score != null && (
                            <span className="ml-1 opacity-60">({rating.overall_score.toFixed(0)}%)</span>
                          )}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">
                        {v.contract_end ?? '—'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => setEditVendor(v)}
                            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => {
                              if (confirm(`Delete vendor "${v.name}"?`)) deleteMut.mutate(v.id)
                            }}
                            className="text-xs text-red-500 hover:text-red-700 font-medium"
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
