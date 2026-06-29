import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { auditsApi, type AuditPlanSummary, type AuditPlanCreate } from '../api/audit'
import { useForm } from 'react-hook-form'

const PLAN_STATUS_BADGE: Record<string, string> = {
  Draft: 'badge-gray',
  Active: 'badge-blue',
  Completed: 'badge-green',
  Cancelled: 'badge-red',
}

const FINDING_SEVERITY_BADGE: Record<string, string> = {
  Critical: 'badge-red',
  High: 'badge-orange',
  Medium: 'badge-yellow',
  Low: 'badge-green',
}

const TEST_RESULT_COLORS: Record<string, string> = {
  Pass: 'text-green-600 dark:text-green-400',
  Fail: 'text-red-600 dark:text-red-400',
  Exception: 'text-orange-600 dark:text-orange-400',
  'Not Tested': 'text-slate-400',
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
    <div className="modal-overlay">
      <div className="modal-panel max-w-md">
        <div className="modal-header">
          <h2 className="modal-title">{plan ? 'Edit Audit Plan' : 'New Audit Plan'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="modal-body">
            <div>
              <label className="form-label">Title <span className="text-red-500">*</span></label>
              <input {...register('title', { required: 'Required' })} className="neu-input" />
              {errors.title && <p className="text-xs text-red-500 mt-1">{errors.title.message}</p>}
            </div>
            <div>
              <label className="form-label">Scope</label>
              <textarea {...register('scope')} rows={2} className="neu-input" />
            </div>
            <div>
              <label className="form-label">Status</label>
              <select {...register('status')} className="neu-select">
                <option>Draft</option>
                <option>Active</option>
                <option>Completed</option>
                <option>Cancelled</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Start Date</label>
                <input {...register('audit_start')} type="date" className="neu-input" />
              </div>
              <div>
                <label className="form-label">End Date</label>
                <input {...register('audit_end')} type="date" className="neu-input" />
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button
              type="submit"
              disabled={isSubmitting || createMut.isPending || updateMut.isPending}
              className="btn-primary"
            >
              {plan ? 'Save Changes' : 'Create Plan'}
            </button>
          </div>
        </form>
      </div>
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
    <div className="modal-overlay">
      <div className="modal-panel max-w-md">
        <div className="modal-header">
          <h2 className="modal-title">Add Test Item</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(data => createMut.mutate(data))}>
          <div className="modal-body">
            <div>
              <label className="form-label">Description <span className="text-red-500">*</span></label>
              <textarea {...register('description', { required: 'Required' })} rows={3} className="neu-input" />
              {errors.description && <p className="text-xs text-red-500 mt-1">{errors.description.message}</p>}
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button type="submit" disabled={isSubmitting || createMut.isPending} className="btn-primary">Add Item</button>
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
    <div className="modal-overlay">
      <div className="modal-panel max-w-md">
        <div className="modal-header">
          <h2 className="modal-title">Add Finding</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(data => createMut.mutate(data))}>
          <div className="modal-body">
            <div>
              <label className="form-label">Title <span className="text-red-500">*</span></label>
              <input {...register('title', { required: 'Required' })} className="neu-input" />
            </div>
            <div>
              <label className="form-label">Description <span className="text-red-500">*</span></label>
              <textarea {...register('description', { required: 'Required' })} rows={2} className="neu-input" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Severity</label>
                <select {...register('severity')} className="neu-select">
                  <option>Critical</option>
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
              </div>
              <div>
                <label className="form-label">Due Date</label>
                <input {...register('due_date')} type="date" className="neu-input" />
              </div>
            </div>
            <div>
              <label className="form-label">Owner</label>
              <input {...register('owner')} className="neu-input" />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button type="submit" disabled={isSubmitting || createMut.isPending} className="btn-primary">Add Finding</button>
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

  const updateFindingMut = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      auditsApi.updateFinding(plan.id, id, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['auditFindings', plan.id] })
      qc.invalidateQueries({ queryKey: ['auditPlans'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  const deleteFindingMut = useMutation({
    mutationFn: (id: string) => auditsApi.deleteFinding(plan.id, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['auditFindings', plan.id] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 flex-wrap">
        <button
          onClick={onBack}
          className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-medium"
        >
          ← Back to Plans
        </button>
        <h1 className="page-title">{plan.title}</h1>
        <span className={`badge ${PLAN_STATUS_BADGE[plan.status] ?? 'badge-gray'}`}>{plan.status}</span>
      </div>
      {plan.scope && <p className="text-sm text-slate-600 dark:text-slate-400">{plan.scope}</p>}

      {/* Test Items */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="section-title">Test Items ({items.length})</h2>
          <button
            onClick={() => setAddItem(true)}
            className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-semibold"
          >
            + Add Item
          </button>
        </div>
        {items.length === 0 ? (
          <p className="text-sm text-slate-400">No test items yet.</p>
        ) : (
          <div className="neu-table-wrap">
            <table className="neu-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Result</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id} className="group">
                    <td className="text-slate-800 dark:text-slate-200">{item.description}</td>
                    <td>
                      <select
                        value={item.test_result}
                        onChange={e => updateItemMut.mutate({ id: item.id, data: { test_result: e.target.value } })}
                        className={`text-xs font-semibold border-0 bg-transparent focus:outline-none cursor-pointer ${TEST_RESULT_COLORS[item.test_result] ?? 'text-slate-600 dark:text-slate-400'}`}
                      >
                        <option>Not Tested</option>
                        <option>Pass</option>
                        <option>Fail</option>
                        <option>Exception</option>
                      </select>
                    </td>
                    <td>
                      <button
                        onClick={() => { if (confirm('Delete this item?')) deleteItemMut.mutate(item.id) }}
                        className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 opacity-0 group-hover:opacity-100"
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
          <h2 className="section-title">Findings ({findings.length})</h2>
          <button
            onClick={() => setAddFinding(true)}
            className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-semibold"
          >
            + Add Finding
          </button>
        </div>
        {findings.length === 0 ? (
          <p className="text-sm text-slate-400">No findings recorded.</p>
        ) : (
          <div className="space-y-2">
            {findings.map(f => (
              <div key={f.id} className="neu-card-sm p-4 group">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`badge ${FINDING_SEVERITY_BADGE[f.severity] ?? 'badge-gray'}`}>
                        {f.severity}
                      </span>
                      <select
                        value={f.status}
                        onChange={e => updateFindingMut.mutate({ id: f.id, status: e.target.value })}
                        className={`text-xs font-semibold border-0 bg-transparent focus:outline-none cursor-pointer ${
                          f.status === 'Open' ? 'text-red-600 dark:text-red-400' : f.status === 'Closed' ? 'text-green-700 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'
                        }`}
                      >
                        <option>Open</option>
                        <option>In Remediation</option>
                        <option>Closed</option>
                      </select>
                    </div>
                    <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{f.title}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{f.description}</p>
                    {f.owner && <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Owner: {f.owner}</p>}
                    {f.due_date && <p className="text-xs text-slate-400 dark:text-slate-500">Due: {f.due_date}</p>}
                  </div>
                  <button
                    onClick={() => { if (confirm('Delete this finding?')) deleteFindingMut.mutate(f.id) }}
                    className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 opacity-0 group-hover:opacity-100"
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
            <h1 className="page-title">Audit Management</h1>
            <p className="page-subtitle">{plans.length} plan{plans.length !== 1 ? 's' : ''}</p>
          </div>
          <button onClick={() => setAddPlanOpen(true)} className="btn-primary">
            + New Plan
          </button>
        </div>

        {isLoading ? (
          <div className="text-sm text-slate-400 text-center py-16">Loading…</div>
        ) : plans.length === 0 ? (
          <div className="neu-card py-16 text-center text-sm text-slate-400">
            No audit plans yet. Create your first plan to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {plans.map(plan => (
              <div
                key={plan.id}
                className="neu-card p-4 hover:ring-2 hover:ring-indigo-300 dark:hover:ring-indigo-700 transition-all cursor-pointer group"
                onClick={() => setSelectedPlan(plan)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">{plan.title}</h3>
                      <span className={`badge flex-shrink-0 ${PLAN_STATUS_BADGE[plan.status] ?? 'badge-gray'}`}>
                        {plan.status}
                      </span>
                    </div>
                    {plan.scope && <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{plan.scope}</p>}
                    <div className="flex gap-4 mt-2 text-xs text-slate-400">
                      <span>{plan.item_count} items</span>
                      <span className="text-green-600 dark:text-green-400">{plan.pass_count} pass</span>
                      <span className="text-red-500 dark:text-red-400">{plan.fail_count} fail</span>
                      {plan.open_findings > 0 && (
                        <span className="text-orange-600 dark:text-orange-400">
                          {plan.open_findings} open finding{plan.open_findings !== 1 ? 's' : ''}
                        </span>
                      )}
                      {plan.audit_start && <span>{plan.audit_start} → {plan.audit_end ?? '…'}</span>}
                    </div>
                  </div>
                  <div
                    className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                    onClick={e => e.stopPropagation()}
                  >
                    <button
                      onClick={() => setEditPlan(plan)}
                      className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-medium"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => { if (confirm(`Delete plan "${plan.title}"?`)) deleteMut.mutate(plan.id) }}
                      className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium"
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
