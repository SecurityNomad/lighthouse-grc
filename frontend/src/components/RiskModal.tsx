import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { risksApi, type Risk, type RiskCreate } from '../api/risks'

interface Props {
  risk?: Risk | null
  onClose: () => void
}

export default function RiskModal({ risk, onClose }: Props) {
  const isEdit = !!risk
  const qc = useQueryClient()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RiskCreate>({
    defaultValues: {
      title: '',
      description: '',
      threat: '',
      scenario: '',
      impact: 'Medium',
      likelihood: 'Possible',
      treatment: 'Mitigate',
      treatment_notes: '',
      owner: '',
      status: 'Open',
      review_date: undefined,
    },
  })

  useEffect(() => {
    if (risk) reset({ ...risk, review_date: risk.review_date ?? undefined })
    else reset({
      title: '', description: '', threat: '', scenario: '',
      impact: 'Medium', likelihood: 'Possible', treatment: 'Mitigate',
      treatment_notes: '', owner: '', status: 'Open', review_date: undefined,
    })
  }, [risk, reset])

  const createMutation = useMutation({
    mutationFn: (data: RiskCreate) => risksApi.create(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['risks'] }); onClose() },
  })

  const updateMutation = useMutation({
    mutationFn: (data: RiskCreate) => risksApi.update(risk!.id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['risks'] }); onClose() },
  })

  const onSubmit = (data: RiskCreate) => {
    const clean = Object.fromEntries(
      Object.entries(data).map(([k, v]) => [k, v === '' ? undefined : v])
    ) as RiskCreate
    if (isEdit) updateMutation.mutate(clean)
    else createMutation.mutate(clean)
  }

  const error = createMutation.error || updateMutation.error

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="modal-header sticky top-0 bg-slate-50 dark:bg-slate-800 rounded-t-2xl z-10">
          <h2 className="modal-title">{isEdit ? 'Edit Risk' : 'Add Risk'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none transition-colors">✕</button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="modal-body space-y-4">
          <div>
            <label className="form-label">Title <span className="text-red-500">*</span></label>
            <input className="neu-input" {...register('title', { required: 'Title is required' })} />
            {errors.title && <p className="text-xs text-red-500 mt-1">{errors.title.message}</p>}
          </div>

          <div>
            <label className="form-label">Description</label>
            <textarea rows={2} className="neu-input" {...register('description')} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Threat</label>
              <input className="neu-input" {...register('threat')} />
            </div>
            <div>
              <label className="form-label">Scenario</label>
              <input className="neu-input" {...register('scenario')} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Impact <span className="text-red-500">*</span></label>
              <select className="neu-select" {...register('impact', { required: true })}>
                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </div>
            <div>
              <label className="form-label">Likelihood <span className="text-red-500">*</span></label>
              <select className="neu-select" {...register('likelihood', { required: true })}>
                <option>Likely</option>
                <option>Possible</option>
                <option>Unlikely</option>
                <option>Rare</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Treatment <span className="text-red-500">*</span></label>
              <select className="neu-select" {...register('treatment', { required: true })}>
                <option>Mitigate</option>
                <option>Accept</option>
                <option>Transfer</option>
                <option>Avoid</option>
              </select>
            </div>
            <div>
              <label className="form-label">Status <span className="text-red-500">*</span></label>
              <select className="neu-select" {...register('status', { required: true })}>
                <option>Open</option>
                <option>In Treatment</option>
                <option>Closed</option>
                <option>Accepted</option>
              </select>
            </div>
          </div>

          <div>
            <label className="form-label">Treatment Notes</label>
            <textarea rows={2} className="neu-input" {...register('treatment_notes')} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="form-label">Owner</label>
              <input className="neu-input" {...register('owner')} />
            </div>
            <div>
              <label className="form-label">Review Date</label>
              <input type="date" className="neu-input" {...register('review_date')} />
            </div>
          </div>

          {error && (
            <p className="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
              Failed to save. Please try again.
            </p>
          )}
        </form>

        <div className="modal-footer">
          <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
          <button
            type="button"
            onClick={handleSubmit(onSubmit)}
            disabled={isSubmitting || createMutation.isPending || updateMutation.isPending}
            className="btn-primary"
          >
            {createMutation.isPending || updateMutation.isPending
              ? 'Saving…'
              : isEdit ? 'Save Changes' : 'Add Risk'}
          </button>
        </div>
      </div>
    </div>
  )
}
