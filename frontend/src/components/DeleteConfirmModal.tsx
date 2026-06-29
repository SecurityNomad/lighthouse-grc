import { useMutation, useQueryClient } from '@tanstack/react-query'
import { risksApi, type Risk } from '../api/risks'

interface Props {
  risk: Risk
  onClose: () => void
}

export default function DeleteConfirmModal({ risk, onClose }: Props) {
  const qc = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => risksApi.delete(risk.id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['risks'] }); onClose() },
  })

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-sm">
        <div className="modal-header">
          <h2 className="modal-title">Delete Risk</h2>
        </div>
        <div className="modal-body">
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Are you sure you want to delete{' '}
            <span className="font-semibold text-slate-900 dark:text-slate-100">"{risk.title}"</span>?
            This cannot be undone.
          </p>
          {mutation.error && (
            <p className="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
              Failed to delete. Please try again.
            </p>
          )}
        </div>
        <div className="modal-footer">
          <button onClick={onClose} className="modal-cancel">Cancel</button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="btn-danger"
          >
            {mutation.isPending ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  )
}
