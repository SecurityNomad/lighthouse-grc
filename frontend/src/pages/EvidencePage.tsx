import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { evidenceApi, type Evidence, type EvidenceUpdate } from '../api/evidence'
import { useForm } from 'react-hook-form'

const STATUS_COLORS: Record<string, string> = {
  Current: 'text-green-700 bg-green-50',
  Expiring: 'text-yellow-700 bg-yellow-50',
  Expired: 'text-red-700 bg-red-50',
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function EditModal({ evidence, onClose }: { evidence: Evidence; onClose: () => void }) {
  const qc = useQueryClient()
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<EvidenceUpdate>({
    defaultValues: {
      title: evidence.title,
      description: evidence.description,
      expiry_date: evidence.expiry_date,
    },
  })

  const updateMut = useMutation({
    mutationFn: (data: EvidenceUpdate) => evidenceApi.update(evidence.id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['evidence'] }); onClose() },
  })

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Edit Evidence</h2>
        </div>
        <form onSubmit={handleSubmit(data => updateMut.mutate(data))} className="px-6 py-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Title *</label>
            <input
              {...register('title', { required: true })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
            <textarea
              {...register('description')}
              rows={2}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Expiry Date</label>
            <input
              {...register('expiry_date')}
              type="date"
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50">
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || updateMut.isPending}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function EvidencePage() {
  const [editEvidence, setEditEvidence] = useState<Evidence | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('All')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const qc = useQueryClient()

  const { data: items = [], isLoading } = useQuery({
    queryKey: ['evidence'],
    queryFn: evidenceApi.list,
  })

  const uploadMut = useMutation({
    mutationFn: evidenceApi.upload,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['evidence'] }),
  })

  const deleteMut = useMutation({
    mutationFn: evidenceApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['evidence'] }),
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    fd.append('title', file.name)
    uploadMut.mutate(fd)
    e.target.value = ''
  }

  const filtered = statusFilter === 'All' ? items : items.filter(i => i.status === statusFilter)

  return (
    <>
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Evidence Collection</h1>
            <p className="text-sm text-gray-500 mt-1">
              {items.length} file{items.length !== 1 ? 's' : ''}
            </p>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadMut.isPending}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {uploadMut.isPending ? 'Uploading…' : '+ Upload Evidence'}
          </button>
          <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileChange} />
        </div>

        {/* Status filter */}
        <div className="flex gap-2 mb-4">
          {['All', 'Current', 'Expiring', 'Expired'].map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                statusFilter === s
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="text-sm text-gray-400 text-center py-16">Loading…</div>
        ) : filtered.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 py-16 text-center text-sm text-gray-400">
            {statusFilter === 'All'
              ? 'No evidence uploaded yet. Upload a file to get started.'
              : `No ${statusFilter.toLowerCase()} evidence.`}
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Title</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">File</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Expiry</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Uploaded</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map(e => (
                  <tr key={e.id} className="hover:bg-gray-50 group">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      <div>{e.title}</div>
                      {e.description && <div className="text-xs text-gray-400 truncate max-w-xs">{e.description}</div>}
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      <div className="text-xs">{e.file_name}</div>
                      <div className="text-xs text-gray-400">{formatBytes(e.file_size)}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[e.status] ?? 'text-gray-500 bg-gray-50'}`}>
                        {e.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">{e.expiry_date ?? '—'}</td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {new Date(e.uploaded_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => setEditEvidence(e)}
                          className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => {
                            if (confirm(`Delete "${e.title}"?`)) deleteMut.mutate(e.id)
                          }}
                          className="text-xs text-red-500 hover:text-red-700 font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {editEvidence && <EditModal evidence={editEvidence} onClose={() => setEditEvidence(null)} />}
    </>
  )
}
