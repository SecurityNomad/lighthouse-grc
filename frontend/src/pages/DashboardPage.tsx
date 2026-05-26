import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../api/dashboard'

const IMPACT_COLORS: Record<string, string> = {
  Critical: 'bg-red-500',
  High: 'bg-orange-400',
  Medium: 'bg-yellow-400',
  Low: 'bg-green-400',
}

function StatCard({ label, value, sub, color = 'text-gray-900' }: {
  label: string
  value: number | string
  sub?: string
  color?: string
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
      <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
    refetchInterval: 30_000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        Loading dashboard…
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400 text-sm">
        Failed to load dashboard data.
      </div>
    )
  }

  const totalRisks = data.open_risks_by_impact.reduce((s, r) => s + r.count, 0)
  const totalVendors = data.vendors_by_tier.reduce((s, v) => s + v.count, 0)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Live GRC posture overview</p>
      </div>

      {/* Key metrics row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Open Risks"
          value={totalRisks}
          sub={`${data.high_risks_open} High/Critical`}
          color={data.high_risks_open > 0 ? 'text-orange-600' : 'text-gray-900'}
        />
        <StatCard
          label="Control Coverage"
          value={`${data.control_coverage_pct.toFixed(0)}%`}
          sub="risks with ≥1 control mapped"
          color={data.control_coverage_pct < 50 ? 'text-red-600' : data.control_coverage_pct < 80 ? 'text-orange-600' : 'text-green-600'}
        />
        <StatCard
          label="Evidence Alerts"
          value={data.evidence_expired + data.evidence_expiring_soon}
          sub={`${data.evidence_expired} expired · ${data.evidence_expiring_soon} expiring soon`}
          color={(data.evidence_expired + data.evidence_expiring_soon) > 0 ? 'text-red-600' : 'text-gray-900'}
        />
        <StatCard
          label="Open Findings"
          value={data.open_findings}
          sub={`${data.audits_active} active audit${data.audits_active !== 1 ? 's' : ''}`}
          color={data.open_findings > 0 ? 'text-orange-600' : 'text-gray-900'}
        />
      </div>

      {/* Second row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk by impact */}
        <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Open Risks by Impact</h2>
          {data.open_risks_by_impact.length === 0 ? (
            <p className="text-sm text-gray-400">No open risks.</p>
          ) : (
            <div className="space-y-3">
              {['Critical', 'High', 'Medium', 'Low'].map(impact => {
                const entry = data.open_risks_by_impact.find(r => r.impact === impact)
                const count = entry?.count ?? 0
                const pct = totalRisks > 0 ? (count / totalRisks) * 100 : 0
                return (
                  <div key={impact}>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>{impact}</span>
                      <span className="font-medium">{count}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${IMPACT_COLORS[impact] ?? 'bg-gray-400'}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Vendors by tier */}
        <div className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">
            Vendors ({totalVendors} total · {data.vendors_under_review} under review)
          </h2>
          {data.vendors_by_tier.length === 0 ? (
            <p className="text-sm text-gray-400">No vendors registered.</p>
          ) : (
            <div className="space-y-3">
              {[1, 2, 3].map(tier => {
                const entry = data.vendors_by_tier.find(v => v.tier === tier)
                const count = entry?.count ?? 0
                const pct = totalVendors > 0 ? (count / totalVendors) * 100 : 0
                const tierLabel = tier === 1 ? 'Tier 1 — Critical' : tier === 2 ? 'Tier 2 — Important' : 'Tier 3 — Standard'
                return (
                  <div key={tier}>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>{tierLabel}</span>
                      <span className="font-medium">{count}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${tier === 1 ? 'bg-red-400' : tier === 2 ? 'bg-orange-400' : 'bg-blue-400'}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
