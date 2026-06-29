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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-2xl w-full max-w-md p-6">
        <h2 className="font-semibold text-lg text-gray-900 dark:text-white mb-4">
          {initial.name ? 'Edit Client' : 'New Client'}
        </h2>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-gray-600 dark:text-slate-300 block mb-1">Name *</label>
            <input
              value={form.name}
              onChange={e => set('name', e.target.value)}
              className="w-full border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 dark:text-slate-300 block mb-1">Industry *</label>
            <input
              value={form.industry}
              onChange={e => set('industry', e.target.value)}
              placeholder="e.g. Healthcare, Finance, Airlines"
              className="w-full border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 dark:text-slate-300 block mb-1">Country</label>
            <input
              value={form.country ?? ''}
              onChange={e => set('country', e.target.value)}
              className="w-full border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-sm text-gray-600 dark:text-slate-300 block mb-1">Description</label>
            <textarea
              value={form.description ?? ''}
              onChange={e => set('description', e.target.value)}
              rows={3}
              className="w-full border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-5">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 dark:text-slate-300 hover:text-gray-800 dark:hover:text-white">
            Cancel
          </button>
          <button
            onClick={() => onSave(form)}
            disabled={!form.name || !form.industry}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 disabled:opacity-50"
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

  if (isLoading) return <div className="text-gray-400">Loading clients…</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Clients</h1>
          <p className="text-sm text-gray-500 dark:text-slate-400 mt-0.5">
            Manage client engagements — select one to scope all GRC data
          </p>
        </div>
        <button
          onClick={() => setModal({ mode: 'create' })}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-500 transition-colors"
        >
          <Plus size={16} />
          New Client
        </button>
      </div>

      {clients.length === 0 ? (
        <div className="text-center py-16 text-gray-400 dark:text-slate-500">
          <Building2 size={40} className="mx-auto mb-3 opacity-40" />
          <p>No clients yet. Create your first client to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {clients.map(client => {
            const isActive = selectedClient?.id === client.id
            return (
              <div
                key={client.id}
                onClick={() => selectClient(isActive ? null : client)}
                className={`relative rounded-xl p-5 border cursor-pointer transition-all ${
                  isActive
                    ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                    : 'border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-indigo-300 dark:hover:border-indigo-600'
                }`}
              >
                {isActive && (
                  <span className="absolute top-3 right-3 text-indigo-600 dark:text-indigo-400">
                    <Check size={16} />
                  </span>
                )}
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center shrink-0">
                    <Building2 size={20} className="text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">{client.name}</h3>
                    <p className="text-xs text-gray-500 dark:text-slate-400 mt-0.5">{client.industry}</p>
                    {client.country && (
                      <p className="text-xs text-gray-400 dark:text-slate-500">{client.country}</p>
                    )}
                  </div>
                </div>
                {client.description && (
                  <p className="text-xs text-gray-500 dark:text-slate-400 mt-3 line-clamp-2">{client.description}</p>
                )}
                <div className="flex gap-1 mt-3 justify-end" onClick={e => e.stopPropagation()}>
                  <button
                    onClick={() => setModal({ mode: 'edit', client })}
                    className="p-1.5 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 rounded"
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
                    className="p-1.5 text-gray-400 hover:text-red-500 rounded"
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
