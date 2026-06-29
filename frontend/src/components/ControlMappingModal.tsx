import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { controlsApi, type ControlWithMapping } from '../api/controls'
import type { Risk } from '../api/risks'

interface Props {
  risk: Risk
  onClose: () => void
}

const FRAMEWORK_BADGE: Record<string, string> = {
  soc2: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  iso27001: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  cis_v8: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
}

export default function ControlMappingModal({ risk, onClose }: Props) {
  const [search, setSearch] = useState('')
  const [selectedFramework, setSelectedFramework] = useState<string | null>(null)
  const qc = useQueryClient()

  const { data: frameworks = [] } = useQuery({
    queryKey: ['frameworks'],
    queryFn: controlsApi.listFrameworks,
  })

  const activeFramework = selectedFramework ?? frameworks[0]?.id ?? null

  const { data: mappedControls = [], isLoading: loadingMapped } = useQuery({
    queryKey: ['riskControls', risk.id],
    queryFn: () => controlsApi.listRiskControls(risk.id),
  })

  const { data: allControls = [], isLoading: loadingControls } = useQuery({
    queryKey: ['controls', activeFramework, search],
    queryFn: () => controlsApi.listControls(activeFramework!, search ? { search } : {}),
    enabled: !!activeFramework,
  })

  const mappedIds = new Set(mappedControls.map((c: ControlWithMapping) => c.id))

  const addMut = useMutation({
    mutationFn: (controlId: string) => controlsApi.addRiskControl(risk.id, controlId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['riskControls', risk.id] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  const removeMut = useMutation({
    mutationFn: (controlId: string) => controlsApi.removeRiskControl(risk.id, controlId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['riskControls', risk.id] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  const activeFrameworkObj = frameworks.find(f => f.id === activeFramework)

  return (
    <div className="modal-overlay">
      <div className="modal-panel max-w-2xl max-h-[90vh] flex flex-col">
        <div className="modal-header">
          <div>
            <h2 className="modal-title">Map Controls</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate max-w-md">{risk.title}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl leading-none">✕</button>
        </div>

        <div className="flex flex-1 min-h-0 divide-x divide-slate-100 dark:divide-slate-700">
          {/* Left: currently mapped */}
          <div className="w-5/12 flex flex-col p-4 overflow-y-auto">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Mapped Controls ({mappedControls.length})
            </h3>
            {loadingMapped ? (
              <p className="text-xs text-slate-400">Loading…</p>
            ) : mappedControls.length === 0 ? (
              <p className="text-xs text-slate-400">No controls mapped yet.</p>
            ) : (
              <div className="space-y-2">
                {mappedControls.map((c: ControlWithMapping) => (
                  <div key={c.id} className="flex items-start justify-between gap-2 bg-slate-100 dark:bg-slate-700 rounded-lg p-2">
                    <div className="min-w-0">
                      <span className="text-xs font-mono font-semibold text-slate-700 dark:text-slate-300">{c.ref}</span>
                      <p className="text-xs text-slate-600 dark:text-slate-400 truncate">{c.title}</p>
                    </div>
                    <button
                      onClick={() => removeMut.mutate(c.id)}
                      disabled={removeMut.isPending}
                      className="shrink-0 text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right: browse and add */}
          <div className="flex-1 flex flex-col p-4 min-h-0">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
              Browse Controls
            </h3>

            <div className="flex gap-2 mb-3 flex-wrap">
              {frameworks.map(fw => (
                <button
                  key={fw.id}
                  onClick={() => { setSelectedFramework(fw.id); setSearch('') }}
                  className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                    activeFramework === fw.id
                      ? FRAMEWORK_BADGE[fw.slug] ?? 'bg-slate-200 dark:bg-slate-600 text-slate-800 dark:text-slate-200'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-600'
                  }`}
                >
                  {fw.slug === 'soc2' ? 'SOC 2' : fw.slug === 'iso27001' ? 'ISO 27001' : 'CIS v8'}
                </button>
              ))}
            </div>

            <input
              type="text"
              placeholder="Search ref, title, or domain…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="neu-input text-xs mb-3"
            />

            <div className="flex-1 overflow-y-auto space-y-1">
              {loadingControls ? (
                <p className="text-xs text-slate-400 text-center py-8">Loading…</p>
              ) : allControls.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-8">No controls match.</p>
              ) : (
                allControls.map(ctrl => {
                  const isMapped = mappedIds.has(ctrl.id)
                  return (
                    <div
                      key={ctrl.id}
                      className={`flex items-start justify-between gap-2 p-2 rounded-lg transition-colors ${
                        isMapped
                          ? 'bg-indigo-50 dark:bg-indigo-900/20'
                          : 'hover:bg-slate-100 dark:hover:bg-slate-700/50'
                      }`}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className={`text-xs font-mono font-semibold px-1.5 py-0.5 rounded ${FRAMEWORK_BADGE[activeFrameworkObj?.slug ?? ''] ?? 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'}`}>
                            {ctrl.ref}
                          </span>
                          <span className="text-xs text-slate-500 dark:text-slate-400">{ctrl.domain}</span>
                        </div>
                        <p className="text-xs text-slate-700 dark:text-slate-300 mt-0.5 truncate">{ctrl.title}</p>
                      </div>
                      <button
                        onClick={() => !isMapped && addMut.mutate(ctrl.id)}
                        disabled={isMapped || addMut.isPending}
                        className={`shrink-0 text-xs font-semibold px-2 py-0.5 rounded transition-colors ${
                          isMapped
                            ? 'text-indigo-600 dark:text-indigo-400 cursor-default'
                            : 'text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 hover:bg-indigo-50 dark:hover:bg-indigo-900/30'
                        }`}
                      >
                        {isMapped ? 'Mapped' : '+ Add'}
                      </button>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>

        <div className="px-6 py-3 border-t border-slate-100 dark:border-slate-700 flex justify-end">
          <button onClick={onClose} className="neu-btn">Done</button>
        </div>
      </div>
    </div>
  )
}
