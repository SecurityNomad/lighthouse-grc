import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { soaApi, IMPLEMENTATION_STATUSES, type ImplementationStatus, type SoARow } from '../api/soa'
import { controlsApi } from '../api/controls'

/** Semantic only — status carries meaning, so colour is allowed to. */
const STATUS_BADGE: Record<ImplementationStatus, string> = {
  'Implemented': 'badge-green',
  'Partially Implemented': 'badge-orange',
  'Planned': 'badge-blue',
  'Not Implemented': 'badge-gray',
}

const FILTERS = ['All', ...IMPLEMENTATION_STATUSES, 'Excluded'] as const
type Filter = typeof FILTERS[number]

function Meter({ label, pct, sub }: { label: string; pct: number; sub: string }) {
  const tone =
    pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-orange-500' : 'bg-red-500'
  return (
    <div className="neu-card p-5">
      <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wide font-semibold">
        {label}
      </p>
      <p className="text-3xl font-bold mt-1 text-slate-900 dark:text-slate-100">
        {pct.toFixed(0)}%
      </p>
      <div
        className="mt-3 h-1.5 w-full rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden"
        role="img"
        aria-label={`${label}: ${pct.toFixed(0)} percent`}
      >
        <div className={`h-full rounded-full ${tone}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
      <p className="text-xs text-slate-600 dark:text-slate-400 mt-2">{sub}</p>
    </div>
  )
}

export default function SoAPage() {
  const qc = useQueryClient()
  const [slug, setSlug] = useState('iso27001')
  const [filter, setFilter] = useState<Filter>('All')
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<SoARow | null>(null)

  const { data: frameworks } = useQuery({
    queryKey: ['frameworks'],
    queryFn: controlsApi.listFrameworks,
  })

  const { data, isLoading, isError } = useQuery({
    queryKey: ['soa', slug],
    queryFn: () => soaApi.get(slug),
  })

  const mutation = useMutation({
    mutationFn: ({ controlId, payload }: { controlId: string; payload: Parameters<typeof soaApi.update>[1] }) =>
      soaApi.update(controlId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['soa', slug] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      setEditing(null)
    },
  })

  const rows = useMemo(() => {
    if (!data) return []
    const term = search.trim().toLowerCase()
    return data.rows.filter(r => {
      if (filter === 'Excluded' && r.applicable) return false
      if (filter !== 'All' && filter !== 'Excluded') {
        if (!r.applicable || r.implementation_status !== filter) return false
      }
      if (!term) return true
      return (
        r.ref.toLowerCase().includes(term) ||
        r.title.toLowerCase().includes(term) ||
        r.domain.toLowerCase().includes(term)
      )
    })
  }, [data, filter, search])

  if (isLoading) return <p className="text-slate-600 dark:text-slate-400">Loading Statement of Applicability…</p>
  if (isError || !data) return <p className="text-red-600 dark:text-red-400">Could not load the Statement of Applicability.</p>

  const s = data.summary

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="page-title">Statement of Applicability</h1>
          <p className="page-subtitle">
            {s.framework_name} · every control accounted for, with justification
          </p>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <span className="sr-only">Framework</span>
          <select
            className="neu-input"
            value={slug}
            onChange={e => { setSlug(e.target.value); setFilter('All') }}
          >
            {(frameworks ?? []).map(f => (
              <option key={f.slug} value={f.slug}>{f.name}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Meter
          label="Readiness"
          pct={s.readiness_pct}
          sub={`weighted across ${s.applicable} applicable control${s.applicable !== 1 ? 's' : ''}`}
        />
        <Meter
          label="Assessed"
          pct={s.coverage_pct}
          sub={`${s.assessed} of ${s.total_controls} controls have a recorded position`}
        />
        <div className="neu-card p-5">
          <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wide font-semibold">
            Implementation
          </p>
          <dl className="mt-2 space-y-1 text-sm">
            <div className="flex justify-between"><dt className="text-slate-600 dark:text-slate-400">Implemented</dt><dd className="font-semibold">{s.implemented}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-600 dark:text-slate-400">Partial</dt><dd className="font-semibold">{s.partially_implemented}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-600 dark:text-slate-400">Planned</dt><dd className="font-semibold">{s.planned}</dd></div>
            <div className="flex justify-between"><dt className="text-slate-600 dark:text-slate-400">Not implemented</dt><dd className="font-semibold">{s.not_implemented}</dd></div>
          </dl>
        </div>
        <div className="neu-card p-5">
          <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wide font-semibold">
            Scope
          </p>
          <p className="text-3xl font-bold mt-1 text-slate-900 dark:text-slate-100">{s.excluded}</p>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
            control{s.excluded !== 1 ? 's' : ''} excluded with justification
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            aria-pressed={filter === f}
            className={`px-3 py-1.5 rounded-lg text-sm transition-shadow outline-none
                        focus-visible:ring-2 focus-visible:ring-indigo-500
                        ${filter === f ? 'neu-pressed font-semibold text-slate-900 dark:text-slate-100'
                                       : 'neu-card text-slate-600 dark:text-slate-400'}`}
          >
            {f}
          </button>
        ))}
        <input
          className="neu-input ml-auto w-full sm:w-64"
          placeholder="Search ref, title, or domain…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Search controls"
        />
      </div>

      <div className="neu-card overflow-x-auto">
        <table className="w-full text-sm">
          <caption className="sr-only">
            {s.framework_name} Statement of Applicability — {rows.length} controls shown
          </caption>
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-600 dark:text-slate-400">
              <th scope="col" className="px-4 py-3 font-semibold">Ref</th>
              <th scope="col" className="px-4 py-3 font-semibold">Control</th>
              <th scope="col" className="px-4 py-3 font-semibold">Applicable</th>
              <th scope="col" className="px-4 py-3 font-semibold">Status</th>
              <th scope="col" className="px-4 py-3 font-semibold">Owner</th>
              <th scope="col" className="px-4 py-3 font-semibold"><span className="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.control_id} className="border-t border-slate-200/60 dark:border-slate-700/60 align-top">
                <td className="px-4 py-3 font-mono text-xs whitespace-nowrap">{r.ref}</td>
                <td className="px-4 py-3">
                  <p className="font-medium text-slate-900 dark:text-slate-100">{r.title}</p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">{r.domain}</p>
                  {r.justification && (
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 max-w-prose">{r.justification}</p>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span className={r.applicable ? 'badge-blue' : 'badge-gray'}>
                    {r.applicable ? 'Yes' : 'Excluded'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {r.applicable
                    ? <span className={STATUS_BADGE[r.implementation_status]}>{r.implementation_status}</span>
                    : <span className="text-xs text-slate-500">—</span>}
                </td>
                <td className="px-4 py-3 text-xs text-slate-600 dark:text-slate-400">{r.owner ?? '—'}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => setEditing(r)}
                    className="text-indigo-600 dark:text-indigo-400 hover:underline text-xs font-medium"
                  >
                    Edit
                  </button>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-slate-600 dark:text-slate-400">
                  No controls match this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {editing && (
        <SoAEditModal
          row={editing}
          saving={mutation.isPending}
          onClose={() => setEditing(null)}
          onSave={payload => mutation.mutate({ controlId: editing.control_id, payload })}
        />
      )}
    </div>
  )
}

function SoAEditModal({ row, saving, onClose, onSave }: {
  row: SoARow
  saving: boolean
  onClose: () => void
  onSave: (payload: { applicable: boolean; justification: string; implementation_status: ImplementationStatus; owner: string }) => void
}) {
  const [applicable, setApplicable] = useState(row.applicable)
  const [status, setStatus] = useState<ImplementationStatus>(row.implementation_status)
  const [justification, setJustification] = useState(row.justification ?? '')
  const [owner, setOwner] = useState(row.owner ?? '')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="soa-edit-title"
        className="neu-card w-full max-w-lg p-6 space-y-4 bg-slate-100 dark:bg-slate-800"
      >
        <div>
          <h2 id="soa-edit-title" className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {row.ref} — {row.title}
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400">{row.domain}</p>
        </div>

        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={applicable} onChange={e => setApplicable(e.target.checked)} />
          <span>Applicable to the ISMS scope</span>
        </label>

        <label className="block text-sm">
          <span className="block mb-1 font-medium">Implementation status</span>
          <select
            className="neu-input w-full"
            value={status}
            disabled={!applicable}
            onChange={e => setStatus(e.target.value as ImplementationStatus)}
          >
            {IMPLEMENTATION_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>

        <label className="block text-sm">
          <span className="block mb-1 font-medium">
            Justification {applicable ? '(why it applies and how)' : '(why it is excluded)'}
          </span>
          <textarea
            className="neu-input w-full h-28"
            value={justification}
            onChange={e => setJustification(e.target.value)}
          />
        </label>

        <label className="block text-sm">
          <span className="block mb-1 font-medium">Owner</span>
          <input className="neu-input w-full" value={owner} onChange={e => setOwner(e.target.value)} />
        </label>

        <div className="flex justify-end gap-2 pt-2">
          <button onClick={onClose} className="neu-card px-4 py-2 text-sm">Cancel</button>
          <button
            onClick={() => onSave({ applicable, justification, implementation_status: status, owner })}
            disabled={saving}
            className="neu-card px-4 py-2 text-sm font-semibold text-indigo-600 dark:text-indigo-400 disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
