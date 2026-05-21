import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { risksApi, type Risk, type RiskCreate } from '../api/risks'

interface Props {
  risk?: Risk | null
  onClose: () => void
}

const FIELD_CLASS =
  'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
const LABEL_CLASS = 'block text-xs font-medium text-gray-700 mb-1'

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
    // strip empty strings to undefined so the backend treats them as null
    const clean = Object.fromEntries(
      Object.entries(data).map(([k, v]) => [k, v === '' ? undefined : v])
    ) as RiskCreate
    if (isEdit) updateMutation.mutate(clean)
    else createMutation.mutate(clean)
  }

  const error = createMutation.error || updateMutation.error

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* backdrop */}
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-xl">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEdit ? 'Edit Risk' : 'Add Risk'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-5 space-y-4">
          {/* Title */}
          <div>
            <label className={LABEL_CLASS}>Title <span className="text-red-500">*</span></label>
            <input
              className={FIELD_CLASS}
              {...register('title', { required: 'Title is required' })}
            />
            {errors.title && <p className="text-xs text-red-500 mt-1">{errors.title.message}</p>}
          </div>

          {/* Description */}
          <div>
            <label className={LABEL_CLASS}>Description</label>
            <textarea rows={2} className={FIELD_CLASS} {...register('description')} />
          </div>

          {/* Threat / Scenario */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={LABEL_CLASS}>Threat</label>
              <input className={FIELD_CLASS} {...register('threat')} />
            </div>
            <div>
              <label className={LABEL_CLASS}>Scenario</label>
              <input className={FIELD_CLASS} {...register('scenario')} />
            </div>
          </div>

          {/* Impact / Likelihood */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={LABEL_CLASS}>Impact <span className="text-red-500">*</span></label>
              <select className={FIELD_CLASS} {...register('impact', { required: true })}>
                <option>Critical</option>
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>
            </div>
            <div>
              <label className={LABEL_CLASS}>Likelihood <span className="text-red-500">*</span></label>
              <select className={FIELD_CLASS} {...register('likelihood', { required: true })}>
                <option>Likely</option>
                <option>Possible</option>
                <option>Unlikely</option>
                <option>Rare</option>
              </select>
            </div>
          </div>

          {/* Treatment / Status */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={LABEL_CLASS}>Treatment <span className="text-red-500">*</span></label>
              <select className={FIELD_CLASS} {...register('treatment', { required: true })}>
                <option>Mitigate</option>
                <option>Accept</option>
                <option>Transfer</option>
                <option>Avoid</option>
              </select>
            </div>
            <div>
              <label className={LABEL_CLASS}>Status <span className="text-red-500">*</span></label>
              <select className={FIELD_CLASS} {...register('status', { required: true })}>
                <option>Open</option>
                <option>In Treatment</option>
                <option>Closed</option>
                <option>Accepted</option>
              </select>
            </div>
          </div>

          {/* Treatment notes */}
          <div>
            <label className={LABEL_CLASS}>Treatment Notes</label>
            <textarea rows={2} className={FIELD_CLASS} {...register('treatment_notes')} />
          </div>

          {/* Owner / Review Date */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={LABEL_CLASS}>Owner</label>
              <input className={FIELD_CLASS} {...register('owner')} />
            </div>
            <div>
              <label className={LABEL_CLASS}>Review Date</label>
              <input type="date" className={FIELD_CLASS} {...register('review_date')} />
            </div>
          </div>

          {error && (
            <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
              Failed to save. Please try again.
            </p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || createMutation.isPending || updateMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {createMutation.isPending || updateMutation.isPending
                ? 'Saving…'
                : isEdit ? 'Save Changes' : 'Add Risk'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
