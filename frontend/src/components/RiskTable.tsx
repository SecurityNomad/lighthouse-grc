import { Risk } from '../api/risks'

interface RiskTableProps {
  risks: Risk[]
  isLoading: boolean
  onEdit: (risk: Risk) => void
  onDelete: (risk: Risk) => void
  onMapControls: (risk: Risk) => void
}

const impactBadge: Record<string, string> = {
  Critical: 'badge-red',
  High: 'badge-orange',
  Medium: 'badge-yellow',
  Low: 'badge-green',
}

const statusBadge: Record<string, string> = {
  Open: 'badge-blue',
  'In Treatment': 'badge-purple',
  Closed: 'badge-gray',
  Accepted: 'badge-green',
}

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {Array.from({ length: 8 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4" />
        </td>
      ))}
    </tr>
  )
}

export default function RiskTable({ risks, isLoading, onEdit, onDelete, onMapControls }: RiskTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="neu-table">
        <thead>
          <tr>
            {['Title', 'Impact', 'Likelihood', 'Treatment', 'Owner', 'Status', 'Review Date', 'Controls', ''].map(
              (col, i) => (
                <th key={i}>{col}</th>
              )
            )}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </>
          ) : risks.length === 0 ? (
            <tr>
              <td colSpan={9} className="px-4 py-16 text-center">
                <div className="flex flex-col items-center gap-3 text-slate-400">
                  <span className="text-4xl" role="img" aria-label="shield">🛡️</span>
                  <p className="text-sm font-medium">No risks recorded yet</p>
                  <p className="text-xs">Click &quot;+ Add Risk&quot; to register your first risk.</p>
                </div>
              </td>
            </tr>
          ) : (
            risks.map((risk) => (
              <tr key={risk.id} className="group">
                <td>
                  <div className="text-sm font-medium text-slate-900 dark:text-slate-100 max-w-xs truncate">
                    {risk.title}
                  </div>
                  {risk.description && (
                    <div className="text-xs text-slate-400 dark:text-slate-500 mt-0.5 max-w-xs truncate">
                      {risk.description}
                    </div>
                  )}
                </td>
                <td className="whitespace-nowrap">
                  <span className={`badge ${impactBadge[risk.impact] ?? 'badge-gray'}`}>{risk.impact}</span>
                </td>
                <td className="whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                  {risk.likelihood}
                </td>
                <td className="whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                  {risk.treatment}
                </td>
                <td className="whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                  {risk.owner ?? <span className="text-slate-300 dark:text-slate-600">—</span>}
                </td>
                <td className="whitespace-nowrap">
                  <span className={`badge ${statusBadge[risk.status] ?? 'badge-gray'}`}>{risk.status}</span>
                </td>
                <td className="whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
                  {risk.review_date ?? <span className="text-slate-300 dark:text-slate-600">—</span>}
                </td>
                <td className="whitespace-nowrap">
                  <button
                    onClick={() => onMapControls(risk)}
                    className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium px-2 py-1 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
                  >
                    Map Controls
                  </button>
                </td>
                <td className="whitespace-nowrap text-right">
                  <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onEdit(risk)}
                      className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-200 font-medium px-2 py-1 rounded hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(risk)}
                      className="text-xs text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 font-medium px-2 py-1 rounded hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
