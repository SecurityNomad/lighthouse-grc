import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { risksApi, type Risk } from '../api/risks'
import RiskTable from '../components/RiskTable'
import RiskModal from '../components/RiskModal'
import DeleteConfirmModal from '../components/DeleteConfirmModal'
import ControlMappingModal from '../components/ControlMappingModal'

const STATUSES = ['All', 'Open', 'In Treatment', 'Closed', 'Accepted'] as const

export default function RisksPage() {
  const [statusFilter, setStatusFilter] = useState<string>('All')
  const [addOpen, setAddOpen] = useState(false)
  const [editRisk, setEditRisk] = useState<Risk | null>(null)
  const [deleteRisk, setDeleteRisk] = useState<Risk | null>(null)
  const [mappingRisk, setMappingRisk] = useState<Risk | null>(null)

  const { data: risks = [], isLoading } = useQuery({
    queryKey: ['risks', statusFilter],
    queryFn: () => risksApi.list(statusFilter === 'All' ? undefined : statusFilter),
  })

  return (
    <>
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Risk Register</h1>
            <p className="text-sm text-gray-500 mt-1">
              {risks.length} risk{risks.length !== 1 ? 's' : ''}
              {statusFilter !== 'All' && ` · ${statusFilter}`}
            </p>
          </div>
          <button
            onClick={() => setAddOpen(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + Add Risk
          </button>
        </div>

        {/* Status filter */}
        <div className="flex gap-2 mb-4">
          {STATUSES.map((s) => (
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

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <RiskTable
            risks={risks}
            isLoading={isLoading}
            onEdit={setEditRisk}
            onDelete={setDeleteRisk}
            onMapControls={setMappingRisk}
          />
        </div>
      </div>

      {addOpen && <RiskModal onClose={() => setAddOpen(false)} />}
      {editRisk && <RiskModal risk={editRisk} onClose={() => setEditRisk(null)} />}
      {deleteRisk && <DeleteConfirmModal risk={deleteRisk} onClose={() => setDeleteRisk(null)} />}
      {mappingRisk && <ControlMappingModal risk={mappingRisk} onClose={() => setMappingRisk(null)} />}
    </>
  )
}
