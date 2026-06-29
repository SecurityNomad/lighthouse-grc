import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { clientsApi, type Client, type ClientCreate } from '../api/clients'
import { useClient } from '../contexts/ClientContext'
import { Plus, Building2, Edit2, Trash2, Check } from 'lucide-react'

const EMPTY_FORM: ClientCreate = { name: '', industry: '', description: '', country: '' }

function ClientModal({
  initial,
  onClose,
  onSave,
}: {
  initial: ClientCreate
  onClose: () => void
  onSave: (data: ClientCreate) => void
}) {
  const [form, setForm] = useState<ClientCreate>(initial)

  function set(field: keyof ClientCreate, value: string) {
    setForm(f => ({ ...f, [field]: value }))
  }

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-md">
        <div className="modal-header">
          <h2 className="modal-title">{initial.name ? 'Edit Client' : 'New Client'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>
        <div className="modal-body">
          <div>
            <label className="form-label">Name <span className="text-red-500">*</span></label>
            <input
              value={form.name}
              onChange={e => set('name', e.target.value)}
              className="neu-input"
            />
          </div>
          <div>
            <label className="form-label">Industry <span className="text-red-500">*</span></label>
            <input
              value={form.industry}
              onChange={e => set('industry', e.target.value)}
              placeholder="e.g. Healthcare, Finance, Airlines"
              className="neu-input"
            />
          </div>
          <div>
            <label className="form-label">Country</label>
            <input
              value={form.country ?? ''}
              onChange={e => set('country', e.target.value)}
              className="neu-input"
            />
          </div>
          <div>
            <label className="form-label">Description</label>
            <textarea
              value={form.description ?? ''}
              onChange={e => set('description', e.target.value)}
              rows={3}
              className="neu-input resize-none"
            />
          </div>
        </div>
        <div className="modal-footer">
          <button onClick={onClose} className="modal-cancel">Cancel</button>
          <button
            onClick={() => onSave(form)}
            disabled={!form.name || !form.industry}
            className="btn-primary"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

export default function ClientsPage() {
  const qc = useQueryClient()
  const { selectedClient, selectClient } = useClient()
  const [modal, setModal] = useState<{ mode: 'create' | 'edit'; client?: Client } | null>(null)

  const { data: clients = [], isLoading } = useQuery({
    queryKey: ['clients'],
    queryFn: clientsApi.list,
  })

  const createMut = useMutation({
    mutationFn: clientsApi.create,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['clients'] }); setModal(null) },
  })

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ClientCreate }) => clientsApi.update(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['clients'] }); setModal(null) },
  })

  const deleteMut = useMutation({
    mutationFn: clientsApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }),
  })

  function handleSave(data: ClientCreate) {
    if (modal?.mode === 'edit' && modal.client) {
      updateMut.mutate({ id: modal.client.id, data })
    } else {
      createMut.mutate(data)
    }
  }

  if (isLoading) return <div className="text-slate-400 text-sm">Loading clients…</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">Clients</h1>
          <p className="page-subtitle">Manage client engagements — select one to scope all GRC data</p>
        </div>
        <button
          onClick={() => setModal({ mode: 'create' })}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={16} />
          New Client
        </button>
      </div>

      {clients.length === 0 ? (
        <div className="text-center py-16 text-slate-400 dark:text-slate-500">
          <Building2 size={40} className="mx-auto mb-3 opacity-40" />
          <p className="text-sm">No clients yet. Create your first client to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {clients.map(client => {
            const isActive = selectedClient?.id === client.id
            return (
              <div
                key={client.id}
                onClick={() => selectClient(isActive ? null : client)}
                className={`neu-card p-5 cursor-pointer transition-all ${
                  isActive
                    ? 'ring-2 ring-indigo-500 dark:ring-indigo-400'
                    : 'hover:ring-2 hover:ring-indigo-200 dark:hover:ring-indigo-800'
                }`}
              >
                {isActive && (
                  <span className="absolute top-3 right-3 text-indigo-600 dark:text-indigo-400">
                    <Check size={16} />
                  </span>
                )}
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                    isActive ? 'bg-indigo-100 dark:bg-indigo-900/50' : 'bg-slate-200 dark:bg-slate-700'
                  }`}>
                    <Building2 size={20} className={isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400'} />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">{client.name}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{client.industry}</p>
                    {client.country && (
                      <p className="text-xs text-slate-400 dark:text-slate-500">{client.country}</p>
                    )}
                  </div>
                </div>
                {client.description && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-3 line-clamp-2">{client.description}</p>
                )}
                <div className="flex gap-1 mt-3 justify-end" onClick={e => e.stopPropagation()}>
                  <button
                    onClick={() => setModal({ mode: 'edit', client })}
                    className="p-1.5 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded transition-colors"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(`Delete ${client.name}?`)) {
                        if (isActive) selectClient(null)
                        deleteMut.mutate(client.id)
                      }
                    }}
                    className="p-1.5 text-slate-400 hover:text-red-500 dark:hover:text-red-400 rounded transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {modal && (
        <ClientModal
          initial={modal.mode === 'edit' && modal.client
            ? { name: modal.client.name, industry: modal.client.industry, description: modal.client.description, country: modal.client.country }
            : EMPTY_FORM
          }
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}
    </div>
  )
}
