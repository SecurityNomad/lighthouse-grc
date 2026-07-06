import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { risksApi, type Risk } from '../api/risks'
import RiskTable from '../components/RiskTable'
import RiskModal from '../components/RiskModal'
import DeleteConfirmModal from '../components/DeleteConfirmModal'
import ControlMappingModal from '../components/ControlMappingModal'

const STATUSES = ['All', 'Open', 'In Treatment', 'Closed', 'Accepted'] as const
const PAGE_SIZE = 25

export default function RisksPage() {
  const [statusFilter, setStatusFilter] = useState<string>('All')
  const [page, setPage] = useState(0)
  const [addOpen, setAddOpen] = useState(false)
  const [editRisk, setEditRisk] = useState<Risk | null>(null)
  const [deleteRisk, setDeleteRisk] = useState<Risk | null>(null)
  const [mappingRisk, setMappingRisk] = useState<Risk | null>(null)

  function changeStatus(s: string) {
    setStatusFilter(s)
    setPage(0)
  }

  const { data: risks = [], isLoading } = useQuery({
    queryKey: ['risks', statusFilter, page],
    queryFn: () => risksApi.list({
      status: statusFilter === 'All' ? undefined : statusFilter,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }),
  })

  // Without a total count from the API, "Next" is available whenever the page
  // came back full (i.e. there may be more rows).
  const hasNextPage = risks.length === PAGE_SIZE

  return (
    <>
      <div>
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="page-title">Risk Register</h1>
            <p className="page-subtitle">
              {risks.length} risk{risks.length !== 1 ? 's' : ''}
              {statusFilter !== 'All' && ` · ${statusFilter}`}
              {page > 0 && ` · page ${page + 1}`}
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
              onClick={() => changeStatus(s)}
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

        {(page > 0 || hasNextPage) && (
          <div className="flex items-center justify-between mt-4">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0 || isLoading}
              className="neu-pill disabled:opacity-40 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>
            <span className="text-xs text-slate-400">Page {page + 1}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={!hasNextPage || isLoading}
              className="neu-pill disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {addOpen && <RiskModal onClose={() => setAddOpen(false)} />}
      {editRisk && <RiskModal risk={editRisk} onClose={() => setEditRisk(null)} />}
      {deleteRisk && <DeleteConfirmModal risk={deleteRisk} onClose={() => setDeleteRisk(null)} />}
      {mappingRisk && <ControlMappingModal risk={mappingRisk} onClose={() => setMappingRisk(null)} />}
    </>
  )
}
