import { useQuery } from '@tanstack/react-query'
import { risksApi } from '../api/risks'
import RiskTable from '../components/RiskTable'

export default function RisksPage() {
  const { data: risks = [], isLoading } = useQuery({
    queryKey: ['risks'],
    queryFn: () => risksApi.list(),
  })

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Register</h1>
          <p className="text-sm text-gray-500 mt-1">
            {risks.length} risk{risks.length !== 1 ? 's' : ''} recorded
          </p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors">
          + Add Risk
        </button>
      </div>
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        <RiskTable risks={risks} isLoading={isLoading} />
      </div>
    </div>
  )
}
