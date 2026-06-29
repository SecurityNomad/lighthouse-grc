import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { controlsApi, type ControlWithMapping } from '../api/controls'
import type { Risk } from '../api/risks'

interface Props {
  risk: Risk
  onClose: () => void
}

const FRAMEWORK_BADGE: Record<string, string> = {
  soc2: 'bg-blue-100 text-blue-800',
  iso27001: 'bg-green-100 text-green-800',
  cis_v8: 'bg-purple-100 text-purple-800',
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Map Controls</h2>
            <p className="text-xs text-gray-500 mt-0.5 truncate max-w-md">{risk.title}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">✕</button>
        </div>

        <div className="flex flex-1 min-h-0 divide-x divide-gray-100">
          {/* Left: currently mapped */}
          <div className="w-5/12 flex flex-col p-4 overflow-y-auto">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Mapped Controls ({mappedControls.length})
            </h3>
            {loadingMapped ? (
              <p className="text-xs text-gray-400">Loading…</p>
            ) : mappedControls.length === 0 ? (
              <p className="text-xs text-gray-400">No controls mapped yet.</p>
            ) : (
              <div className="space-y-2">
                {mappedControls.map((c: ControlWithMapping) => (
                  <div key={c.id} className="flex items-start justify-between gap-2 bg-gray-50 rounded-lg p-2">
                    <div className="min-w-0">
                      <span className="text-xs font-mono font-semibold text-gray-700">{c.ref}</span>
                      <p className="text-xs text-gray-600 truncate">{c.title}</p>
                    </div>
                    <button
                      onClick={() => removeMut.mutate(c.id)}
                      disabled={removeMut.isPending}
                      className="shrink-0 text-xs text-red-500 hover:text-red-700 font-medium"
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
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Browse Controls
            </h3>

            {/* Framework selector */}
            <div className="flex gap-2 mb-3 flex-wrap">
              {frameworks.map(fw => (
                <button
                  key={fw.id}
                  onClick={() => { setSelectedFramework(fw.id); setSearch('') }}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                    activeFramework === fw.id
                      ? FRAMEWORK_BADGE[fw.slug] ?? 'bg-gray-200 text-gray-800'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
              className="w-full px-3 py-1.5 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
            />

            <div className="flex-1 overflow-y-auto space-y-1">
              {loadingControls ? (
                <p className="text-xs text-gray-400 text-center py-8">Loading…</p>
              ) : allControls.length === 0 ? (
                <p className="text-xs text-gray-400 text-center py-8">No controls match.</p>
              ) : (
                allControls.map(ctrl => {
                  const isMapped = mappedIds.has(ctrl.id)
                  return (
                    <div
                      key={ctrl.id}
                      className={`flex items-start justify-between gap-2 p-2 rounded-lg ${isMapped ? 'bg-blue-50' : 'hover:bg-gray-50'}`}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className={`text-xs font-mono font-semibold px-1.5 py-0.5 rounded ${FRAMEWORK_BADGE[activeFrameworkObj?.slug ?? ''] ?? 'bg-gray-100 text-gray-700'}`}>
                            {ctrl.ref}
                          </span>
                          <span className="text-xs text-gray-500">{ctrl.domain}</span>
                        </div>
                        <p className="text-xs text-gray-700 mt-0.5 truncate">{ctrl.title}</p>
                      </div>
                      <button
                        onClick={() => !isMapped && addMut.mutate(ctrl.id)}
                        disabled={isMapped || addMut.isPending}
                        className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded transition-colors ${
                          isMapped
                            ? 'text-blue-600 cursor-default'
                            : 'text-blue-600 hover:text-blue-800 hover:bg-blue-100'
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

        <div className="px-6 py-3 border-t border-gray-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  )
}
