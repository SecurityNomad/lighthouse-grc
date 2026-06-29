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
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="page-title">Risk Register</h1>
            <p className="page-subtitle">
              {risks.length} risk{risks.length !== 1 ? 's' : ''}
              {statusFilter !== 'All' && ` · ${statusFilter}`}
            </p>
          </div>
          <button onClick={() => setAddOpen(true)} className="btn-primary">
            + Add Risk
          </button>
        </div>

        <div className="flex gap-2 mb-5 flex-wrap">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={statusFilter === s ? 'neu-pill-active' : 'neu-pill'}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="neu-table-wrap">
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
