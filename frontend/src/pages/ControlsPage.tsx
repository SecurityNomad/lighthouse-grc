import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { controlsApi, type Framework } from '../api/controls'

const FRAMEWORK_BADGE: Record<string, string> = {
  soc2: 'badge badge-blue',
  iso27001: 'badge badge-green',
  cis_v8: 'badge badge-purple',
}

const FRAMEWORK_REF_BADGE: Record<string, string> = {
  soc2: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  iso27001: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  cis_v8: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
}

export default function ControlsPage() {
  const [selectedFramework, setSelectedFramework] = useState<Framework | null>(null)
  const [search, setSearch] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const { data: frameworks = [], isLoading: loadingFrameworks } = useQuery({
    queryKey: ['frameworks'],
    queryFn: controlsApi.listFrameworks,
  })

  useEffect(() => {
    if (!selectedFramework && frameworks.length > 0) setSelectedFramework(frameworks[0])
  }, [frameworks, selectedFramework])

  const { data: controls = [], isLoading: loadingControls } = useQuery({
    queryKey: ['controls', selectedFramework?.id, search],
    queryFn: () => controlsApi.listControls(selectedFramework!.id, search ? { search } : {}),
    enabled: !!selectedFramework,
  })

  if (loadingFrameworks) {
    return <div className="text-slate-500 dark:text-slate-400 text-sm">Loading frameworks…</div>
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="page-title">Control Framework Library</h1>
        <p className="page-subtitle">Browse controls across SOC 2, ISO 27001, and CIS Controls v8</p>
      </div>

      {/* Framework selector */}
      <div className="flex gap-3 mb-6 flex-wrap">
        {frameworks.map((fw) => (
          <button
            key={fw.id}
            onClick={() => { setSelectedFramework(fw); setSearch(''); setExpandedId(null) }}
            className={selectedFramework?.id === fw.id ? 'neu-pill-active' : 'neu-pill'}
          >
            <span>{fw.name.split(' ')[0] === 'SOC' ? 'SOC 2' : fw.name.split('/')[0].trim()}</span>
            <span className="ml-2 opacity-70">{fw.control_count}</span>
          </button>
        ))}
      </div>

      {selectedFramework && (
        <>
          {/* Framework meta */}
          <div className="neu-card p-4 mb-5 flex items-start justify-between gap-4">
            <div>
              <div className="font-semibold text-slate-900 dark:text-slate-100">{selectedFramework.name}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{selectedFramework.version}</div>
              {selectedFramework.description && (
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-2 max-w-2xl">
                  {selectedFramework.description.trim()}
                </p>
              )}
            </div>
            <span className={`shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full ${FRAMEWORK_BADGE[selectedFramework.slug] ?? 'badge badge-gray'}`}>
              {selectedFramework.control_count} controls
            </span>
          </div>

          {/* Search */}
          <div className="mb-5">
            <input
              type="text"
              placeholder="Search by ref, title, or domain…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setExpandedId(null) }}
              className="neu-input w-full sm:w-80"
            />
          </div>

          {/* Controls list */}
          <div className="neu-card overflow-hidden divide-y divide-slate-100 dark:divide-slate-800">
            {loadingControls ? (
              <div className="px-4 py-8 text-center text-sm text-slate-500 dark:text-slate-400">Loading controls…</div>
            ) : controls.length === 0 ? (
              <div className="px-4 py-8 text-center text-sm text-slate-500 dark:text-slate-400">No controls match your search.</div>
            ) : (
              controls.map((ctrl) => (
                <div key={ctrl.id}>
                  <button
                    className="w-full text-left px-4 py-3 hover:bg-indigo-50/40 dark:hover:bg-indigo-950/30 transition-colors"
                    onClick={() => setExpandedId(expandedId === ctrl.id ? null : ctrl.id)}
                  >
                    <div className="flex items-start gap-3">
                      <span className={`shrink-0 text-xs font-mono font-semibold px-2 py-0.5 rounded ${FRAMEWORK_REF_BADGE[selectedFramework.slug] ?? 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'}`}>
                        {ctrl.ref}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{ctrl.title}</span>
                        </div>
                        <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                          {ctrl.domain}
                        </span>
                      </div>
                      <span className="shrink-0 text-slate-400 text-xs mt-0.5">
                        {expandedId === ctrl.id ? '▲' : '▼'}
                      </span>
                    </div>
                  </button>
                  {expandedId === ctrl.id && ctrl.description && (
                    <div className="px-4 pb-4 pt-1">
                      <p className="text-sm text-slate-600 dark:text-slate-400 ml-14 leading-relaxed">
                        {ctrl.description.trim()}
                      </p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}
