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
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-sm m-4 p-6">
        <h2 className="text-base font-semibold text-gray-900 mb-2">Delete Risk</h2>
        <p className="text-sm text-gray-600 mb-6">
          Are you sure you want to delete{' '}
          <span className="font-medium text-gray-900">"{risk.title}"</span>? This cannot be undone.
        </p>
        {mutation.error && (
          <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2 mb-4">
            Failed to delete. Please try again.
          </p>
        )}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            {mutation.isPending ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  )
}
