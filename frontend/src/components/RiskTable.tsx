import { Risk } from '../api/risks'

interface RiskTableProps {
  risks: Risk[]
  isLoading: boolean
  onEdit: (risk: Risk) => void
  onDelete: (risk: Risk) => void
  onMapControls: (risk: Risk) => void
}

const impactBadge: Record<string, string> = {
  Critical: 'bg-red-100 text-red-800',
  High: 'bg-orange-100 text-orange-800',
  Medium: 'bg-yellow-100 text-yellow-800',
  Low: 'bg-green-100 text-green-800',
}

const statusBadge: Record<string, string> = {
  Open: 'bg-blue-100 text-blue-800',
  'In Treatment': 'bg-purple-100 text-purple-800',
  Closed: 'bg-gray-100 text-gray-600',
  Accepted: 'bg-green-100 text-green-800',
}

function Badge({ label, colorClass }: { label: string; colorClass: string }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colorClass}`}>
      {label}
    </span>
  )
}

function SkeletonRow() {
  return (
    <tr className="animate-pulse">
      {Array.from({ length: 8 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </td>
      ))}
    </tr>
  )
}

export default function RiskTable({ risks, isLoading, onEdit, onDelete, onMapControls }: RiskTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {['Title', 'Impact', 'Likelihood', 'Treatment', 'Owner', 'Status', 'Review Date', 'Controls', ''].map(
              (col, i) => (
                <th
                  key={i}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                >
                  {col}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {isLoading ? (
            <>
              <SkeletonRow />
              <SkeletonRow />
              <SkeletonRow />
            </>
          ) : risks.length === 0 ? (
            <tr>
              <td colSpan={9} className="px-4 py-16 text-center">
                <div className="flex flex-col items-center gap-3 text-gray-400">
                  <span className="text-4xl" role="img" aria-label="shield">🛡️</span>
                  <p className="text-sm font-medium">No risks recorded yet</p>
                  <p className="text-xs">Click &quot;+ Add Risk&quot; to register your first risk.</p>
                </div>
              </td>
            </tr>
          ) : (
            risks.map((risk) => (
              <tr key={risk.id} className="hover:bg-gray-50 transition-colors group">
                <td className="px-4 py-3">
                  <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                    {risk.title}
                  </div>
                  {risk.description && (
                    <div className="text-xs text-gray-400 mt-0.5 max-w-xs truncate">
                      {risk.description}
                    </div>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <Badge label={risk.impact} colorClass={impactBadge[risk.impact] ?? 'bg-gray-100 text-gray-700'} />
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                  {risk.likelihood}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                  {risk.treatment}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                  {risk.owner ?? <span className="text-gray-300">—</span>}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <Badge label={risk.status} colorClass={statusBadge[risk.status] ?? 'bg-gray-100 text-gray-700'} />
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                  {risk.review_date ?? <span className="text-gray-300">—</span>}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <button
                    onClick={() => onMapControls(risk)}
                    className="text-xs text-indigo-600 hover:text-indigo-800 font-medium px-2 py-1 rounded hover:bg-indigo-50 transition-colors"
                  >
                    Map Controls
                  </button>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right">
                  <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => onEdit(risk)}
                      className="text-xs text-blue-600 hover:text-blue-800 font-medium px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => onDelete(risk)}
                      className="text-xs text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition-colors"
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
