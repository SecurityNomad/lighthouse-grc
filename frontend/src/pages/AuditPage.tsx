import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { auditsApi, type AuditPlanSummary, type AuditPlanCreate } from '../api/audit'
import { useForm } from 'react-hook-form'

const PLAN_STATUS_COLORS: Record<string, string> = {
  Draft: 'text-gray-600 bg-gray-100',
  Active: 'text-blue-700 bg-blue-50',
  Completed: 'text-green-700 bg-green-50',
  Cancelled: 'text-red-600 bg-red-50',
}

const FINDING_SEVERITY_COLORS: Record<string, string> = {
  Critical: 'text-red-700 bg-red-50',
  High: 'text-orange-700 bg-orange-50',
  Medium: 'text-yellow-700 bg-yellow-50',
  Low: 'text-green-700 bg-green-50',
}

const TEST_RESULT_COLORS: Record<string, string> = {
  Pass: 'text-green-700',
  Fail: 'text-red-600',
  Exception: 'text-orange-600',
  'Not Tested': 'text-gray-400',
}

function PlanModal({ plan, onClose }: { plan?: AuditPlanSummary; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<AuditPlanCreate>({
    defaultValues: plan ? {
      title: plan.title,
      scope: plan.scope,
      status: plan.status,
      audit_start: plan.audit_start,
      audit_end: plan.audit_end,
    } : { status: 'Draft' },
  })

  const createMut = useMutation({
    mutationFn: auditsApi.createPlan,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['auditPlans'] }); onClose() },
  })
  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AuditPlanCreate }) => auditsApi.updatePlan(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['auditPlans'] }); onClose() },
  })

  const onSubmit = (data: AuditPlanCreate) => {
    if (plan) updateMut.mutate({ id: plan.id, data })
    else createMut.mutate(data)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">{plan ? 'Edit Audit Plan' : 'New Audit Plan'}</h2>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Title *</label>
            <input
              {...register('title', { required: 'Required' })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.title && <p className="text-xs text-red-600 mt-1">{errors.title.message}</p>}
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Scope</label>
            <textarea
              {...register('scope')}
              rows={2}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Status</label>
            <select
              {...register('status')}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option>Draft</option>
              <option>Active</option>
              <option>Completed</option>
              <option>Cancelled</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Start Date</label>
              <input
                {...register('audit_start')}
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">End Date</label>
              <input
                {...register('audit_end')}
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
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
              {plan ? 'Save Changes' : 'Create Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function PlanDetail({ plan, onBack }: { plan: AuditPlanSummary; onBack: () => void }) {
  const qc = useQueryClient()
  const [addItem, setAddItem] = useState(false)
  const [addFinding, setAddFinding] = useState(false)

  const { data: items = [] } = useQuery({
    queryKey: ['auditItems', plan.id],
    queryFn: () => auditsApi.listItems(plan.id),
  })

  const { data: findings = [] } = useQuery({
    queryKey: ['auditFindings', plan.id],
    queryFn: () => auditsApi.listFindings(plan.id),
  })

  const updateItemMut = useMutation({
    mutationFn: ({ id, data }: { id: string; data: { test_result: string } }) =>
      auditsApi.updateItem(plan.id, id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['auditItems', plan.id] })
      qc.invalidateQueries({ queryKey: ['auditPlans'] })
    },
  })

  const deleteItemMut = useMutation({
    mutationFn: (id: string) => auditsApi.deleteItem(plan.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['auditItems', plan.id] }),
  })

  const deleteFindingMut = useMutation({
    mutationFn: (id: string) => auditsApi.deleteFinding(plan.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['auditFindings', plan.id] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-sm text-blue-600 hover:text-blue-800">← Back to Plans</button>
        <h1 className="text-2xl font-bold text-gray-900">{plan.title}</h1>
        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${PLAN_STATUS_COLORS[plan.status] ?? 'text-gray-600 bg-gray-100'}`}>
          {plan.status}
        </span>
      </div>
      {plan.scope && <p className="text-sm text-gray-600">{plan.scope}</p>}

      {/* Items */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-700">Test Items ({items.length})</h2>
          <button
            onClick={() => setAddItem(true)}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            + Add Item
          </button>
        </div>
        {items.length === 0 ? (
          <p className="text-sm text-gray-400">No test items yet.</p>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="text-left px-4 py-2 text-xs font-medium text-gray-500 uppercase">Result</th>
                  <th className="px-4 py-2" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map(item => (
                  <tr key={item.id} className="group hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-800">{item.description}</td>
                    <td className="px-4 py-3">
                      <select
                        value={item.test_result}
                        onChange={e => updateItemMut.mutate({ id: item.id, data: { test_result: e.target.value } })}
                        className={`text-xs font-medium border-0 bg-transparent focus:outline-none cursor-pointer ${TEST_RESULT_COLORS[item.test_result] ?? 'text-gray-600'}`}
                      >
                        <option>Not Tested</option>
                        <option>Pass</option>
                        <option>Fail</option>
                        <option>Exception</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => {
                          if (confirm('Delete this item?')) deleteItemMut.mutate(item.id)
                        }}
                        className="text-xs text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Findings */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-gray-700">Findings ({findings.length})</h2>
          <button
            onClick={() => setAddFinding(true)}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            + Add Finding
          </button>
        </div>
        {findings.length === 0 ? (
          <p className="text-sm text-gray-400">No findings recorded.</p>
        ) : (
          <div className="space-y-2">
            {findings.map(f => (
              <div key={f.id} className="bg-white rounded-lg border border-gray-200 p-4 group">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${FINDING_SEVERITY_COLORS[f.severity] ?? 'text-gray-600 bg-gray-50'}`}>
                        {f.severity}
                      </span>
                      <span className={`text-xs font-medium ${f.status === 'Open' ? 'text-red-600' : f.status === 'Remediated' ? 'text-green-700' : 'text-gray-500'}`}>
                        {f.status}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-gray-900">{f.title}</p>
                    <p className="text-xs text-gray-500 mt-1">{f.description}</p>
                    {f.owner && <p className="text-xs text-gray-400 mt-1">Owner: {f.owner}</p>}
                    {f.due_date && <p className="text-xs text-gray-400">Due: {f.due_date}</p>}
                  </div>
                  <button
                    onClick={() => {
                      if (confirm('Delete this finding?')) deleteFindingMut.mutate(f.id)
                    }}
                    className="text-xs text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {addItem && <AddItemModal planId={plan.id} onClose={() => setAddItem(false)} />}
      {addFinding && <AddFindingModal planId={plan.id} onClose={() => setAddFinding(false)} />}
    </div>
  )
}

function AddItemModal({ planId, onClose }: { planId: string; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<{ description: string }>()
  const createMut = useMutation({
    mutationFn: (data: { description: string }) =>
      auditsApi.createItem({ plan_id: planId, description: data.description, test_result: 'Not Tested' }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['auditItems', planId] }); onClose() },
  })
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Add Test Item</h2>
        </div>
        <form onSubmit={handleSubmit(data => createMut.mutate(data))} className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Description *</label>
            <textarea
              {...register('description', { required: 'Required' })}
              rows={3}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.description && <p className="text-xs text-red-600 mt-1">{errors.description.message}</p>}
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">Cancel</button>
            <button type="submit" disabled={isSubmitting || createMut.isPending} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">Add Item</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function AddFindingModal({ planId, onClose }: { planId: string; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<{
    title: string; description: string; severity: string; owner?: string; due_date?: string
  }>({ defaultValues: { severity: 'Medium' } })
  const createMut = useMutation({
    mutationFn: (data: { title: string; description: string; severity: string; owner?: string; due_date?: string }) =>
      auditsApi.createFinding({ plan_id: planId, status: 'Open', ...data }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['auditFindings', planId] }); onClose() },
  })
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Add Finding</h2>
        </div>
        <form onSubmit={handleSubmit(data => createMut.mutate(data))} className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Title *</label>
            <input
              {...register('title', { required: 'Required' })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Description *</label>
            <textarea
              {...register('description', { required: 'Required' })}
              rows={2}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Severity</label>
              <select
                {...register('severity')}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Due Date</label>
              <input
                {...register('due_date')}
                type="date"
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Owner</label>
            <input
              {...register('owner')}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">Cancel</button>
            <button type="submit" disabled={isSubmitting || createMut.isPending} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">Add Finding</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function AuditPage() {
  const [addPlanOpen, setAddPlanOpen] = useState(false)
  const [editPlan, setEditPlan] = useState<AuditPlanSummary | null>(null)
  const [selectedPlan, setSelectedPlan] = useState<AuditPlanSummary | null>(null)
  const qc = useQueryClient()

  const { data: plans = [], isLoading } = useQuery({
    queryKey: ['auditPlans'],
    queryFn: auditsApi.listPlans,
  })

  const deleteMut = useMutation({
    mutationFn: auditsApi.deletePlan,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['auditPlans'] }),
  })

  if (selectedPlan) {
    const live = plans.find(p => p.id === selectedPlan.id) ?? selectedPlan
    return <PlanDetail plan={live} onBack={() => setSelectedPlan(null)} />
  }

  return (
    <>
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Audit Management</h1>
            <p className="text-sm text-gray-500 mt-1">
              {plans.length} plan{plans.length !== 1 ? 's' : ''}
            </p>
          </div>
          <button
            onClick={() => setAddPlanOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + New Plan
          </button>
        </div>

        {isLoading ? (
          <div className="text-sm text-gray-400 text-center py-16">Loading…</div>
        ) : plans.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 py-16 text-center text-sm text-gray-400">
            No audit plans yet. Create your first plan to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {plans.map(plan => (
              <div key={plan.id} className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:border-blue-300 transition-colors group cursor-pointer"
                onClick={() => setSelectedPlan(plan)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-gray-900 truncate">{plan.title}</h3>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium flex-shrink-0 ${PLAN_STATUS_COLORS[plan.status] ?? 'text-gray-600 bg-gray-100'}`}>
                        {plan.status}
                      </span>
                    </div>
                    {plan.scope && <p className="text-xs text-gray-500 truncate">{plan.scope}</p>}
                    <div className="flex gap-4 mt-2 text-xs text-gray-400">
                      <span>{plan.item_count} items</span>
                      <span className="text-green-600">{plan.pass_count} pass</span>
                      <span className="text-red-500">{plan.fail_count} fail</span>
                      {plan.open_findings > 0 && (
                        <span className="text-orange-600">{plan.open_findings} open finding{plan.open_findings !== 1 ? 's' : ''}</span>
                      )}
                      {plan.audit_start && <span>{plan.audit_start} → {plan.audit_end ?? '…'}</span>}
                    </div>
                  </div>
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" onClick={e => e.stopPropagation()}>
                    <button
                      onClick={() => setEditPlan(plan)}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        if (confirm(`Delete plan "${plan.title}"?`)) deleteMut.mutate(plan.id)
                      }}
                      className="text-xs text-red-500 hover:text-red-700 font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {addPlanOpen && <PlanModal onClose={() => setAddPlanOpen(false)} />}
      {editPlan && <PlanModal plan={editPlan} onClose={() => setEditPlan(null)} />}
    </>
  )
}
