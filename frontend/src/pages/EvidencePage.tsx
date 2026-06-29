import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { evidenceApi, type Evidence, type EvidenceUpdate } from '../api/evidence'
import { useForm } from 'react-hook-form'

const STATUS_BADGE: Record<string, string> = {
  Current: 'badge-green',
  Expiring: 'badge-yellow',
  Expired: 'badge-red',
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
    <div className="modal-overlay">
      <div className="modal-panel max-w-md">
        <div className="modal-header">
          <h2 className="modal-title">Edit Evidence</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={handleSubmit(data => updateMut.mutate(data))}>
          <div className="modal-body">
            <div>
              <label className="form-label">Title <span className="text-red-500">*</span></label>
              <input {...register('title', { required: true })} className="neu-input" />
            </div>
            <div>
              <label className="form-label">Description</label>
              <textarea {...register('description')} rows={2} className="neu-input" />
            </div>
            <div>
              <label className="form-label">Expiry Date</label>
              <input {...register('expiry_date')} type="date" className="neu-input" />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="modal-cancel">Cancel</button>
            <button
              type="submit"
              disabled={isSubmitting || updateMut.isPending}
              className="btn-primary"
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
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="page-title">Evidence Collection</h1>
            <p className="page-subtitle">{items.length} file{items.length !== 1 ? 's' : ''}</p>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadMut.isPending}
            className="btn-primary"
          >
            {uploadMut.isPending ? 'Uploading…' : '+ Upload Evidence'}
          </button>
          <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileChange} />
        </div>

        <div className="flex gap-2 mb-5 flex-wrap">
          {['All', 'Current', 'Expiring', 'Expired'].map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={statusFilter === s ? 'neu-pill-active' : 'neu-pill'}
            >
              {s}
            </button>
          ))}
        </div>

        {isLoading ? (
          <div className="text-sm text-slate-400 text-center py-16">Loading…</div>
        ) : filtered.length === 0 ? (
          <div className="neu-card py-16 text-center text-sm text-slate-400">
            {statusFilter === 'All'
              ? 'No evidence uploaded yet. Upload a file to get started.'
              : `No ${statusFilter.toLowerCase()} evidence.`}
          </div>
        ) : (
          <div className="neu-table-wrap">
            <table className="neu-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>File</th>
                  <th>Status</th>
                  <th>Expiry</th>
                  <th>Uploaded</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {filtered.map(e => (
                  <tr key={e.id} className="group">
                    <td>
                      <div className="font-medium text-slate-900 dark:text-slate-100">{e.title}</div>
                      {e.description && (
                        <div className="text-xs text-slate-400 truncate max-w-xs">{e.description}</div>
                      )}
                    </td>
                    <td>
                      <div className="text-xs text-slate-600 dark:text-slate-400">{e.file_name}</div>
                      <div className="text-xs text-slate-400 dark:text-slate-500">{formatBytes(e.file_size)}</div>
                    </td>
                    <td>
                      <span className={`badge ${STATUS_BADGE[e.status] ?? 'badge-gray'}`}>{e.status}</span>
                    </td>
                    <td className="text-xs text-slate-500 dark:text-slate-400">{e.expiry_date ?? '—'}</td>
                    <td className="text-xs text-slate-500 dark:text-slate-400">
                      {new Date(e.uploaded_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div className="flex gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => setEditEvidence(e)}
                          className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-medium"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => { if (confirm(`Delete "${e.title}"?`)) deleteMut.mutate(e.id) }}
                          className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium"
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
