import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { controlsApi, type Framework } from '../api/controls'

const FRAMEWORK_COLOURS: Record<string, string> = {
  soc2: 'bg-blue-100 text-blue-800',
  iso27001: 'bg-green-100 text-green-800',
  cis_v8: 'bg-purple-100 text-purple-800',
}

const DOMAIN_COLOUR = 'bg-gray-100 text-gray-700'

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
    return <div className="text-gray-500 text-sm">Loading frameworks…</div>
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Control Framework Library</h1>
        <p className="text-sm text-gray-500 mt-1">
          Browse controls across SOC 2, ISO 27001, and CIS Controls v8
        </p>
      </div>

      {/* Framework selector */}
      <div className="flex gap-3 mb-6">
        {frameworks.map((fw) => (
          <button
            key={fw.id}
            onClick={() => { setSelectedFramework(fw); setSearch(''); setExpandedId(null) }}
            className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
              selectedFramework?.id === fw.id
                ? 'border-blue-600 bg-blue-50 text-blue-700'
                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <span>{fw.name.split(' ')[0] === 'SOC' ? 'SOC 2' : fw.name.split('/')[0].trim()}</span>
            <span className="ml-2 text-xs text-gray-400">{fw.control_count}</span>
          </button>
        ))}
      </div>

      {selectedFramework && (
        <>
          {/* Framework meta */}
          <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4 flex items-start justify-between">
            <div>
              <div className="font-semibold text-gray-900">{selectedFramework.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">{selectedFramework.version}</div>
              {selectedFramework.description && (
                <p className="text-sm text-gray-600 mt-2 max-w-2xl">
                  {selectedFramework.description.trim()}
                </p>
              )}
            </div>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${FRAMEWORK_COLOURS[selectedFramework.slug] ?? 'bg-gray-100 text-gray-700'}`}>
              {selectedFramework.control_count} controls
            </span>
          </div>

          {/* Search */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search by ref, title, or domain…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setExpandedId(null) }}
              className="w-full sm:w-80 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Controls list */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-100">
            {loadingControls ? (
              <div className="px-4 py-8 text-center text-sm text-gray-500">Loading controls…</div>
            ) : controls.length === 0 ? (
              <div className="px-4 py-8 text-center text-sm text-gray-500">No controls match your search.</div>
            ) : (
              controls.map((ctrl) => (
                <div key={ctrl.id}>
                  <button
                    className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
                    onClick={() => setExpandedId(expandedId === ctrl.id ? null : ctrl.id)}
                  >
                    <div className="flex items-start gap-3">
                      <span className={`shrink-0 text-xs font-mono font-semibold px-2 py-0.5 rounded ${FRAMEWORK_COLOURS[selectedFramework.slug] ?? 'bg-gray-100 text-gray-700'}`}>
                        {ctrl.ref}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-medium text-gray-900">{ctrl.title}</span>
                        </div>
                        <span className={`inline-block mt-1 text-xs px-2 py-0.5 rounded ${DOMAIN_COLOUR}`}>
                          {ctrl.domain}
                        </span>
                      </div>
                      <span className="shrink-0 text-gray-400 text-xs mt-0.5">
                        {expandedId === ctrl.id ? '▲' : '▼'}
                      </span>
                    </div>
                  </button>
                  {expandedId === ctrl.id && ctrl.description && (
                    <div className="px-4 pb-4 pt-1">
                      <p className="text-sm text-gray-600 ml-14 leading-relaxed">
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
