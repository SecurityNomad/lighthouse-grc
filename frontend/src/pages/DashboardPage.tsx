import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { RefreshCw } from 'lucide-react'
import { dashboardApi } from '../api/dashboard'
import { useClient } from '../contexts/ClientContext'

const IMPACT_COLORS: Record<string, string> = {
  Critical: 'bg-red-500',
  High: 'bg-orange-400',
  Medium: 'bg-yellow-400',
  Low: 'bg-green-400',
}

/** A KPI tile that links into the list it summarises. Keyboard-focusable, with
 *  an accessible label combining the metric, value, and supporting detail. */
function StatCard({ label, value, sub, to, color = 'text-slate-900 dark:text-slate-100' }: {
  label: string
  value: number | string
  sub?: string
  to: string
  color?: string
}) {
  return (
    <Link
      to={to}
      aria-label={`${label}: ${value}${sub ? `. ${sub}` : ''}. View details.`}
      className="neu-card p-5 block outline-none transition-shadow
                 focus-visible:ring-2 focus-visible:ring-indigo-500 dark:focus-visible:ring-indigo-400"
    >
      <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wide font-semibold">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{sub}</p>}
    </Link>
  )
}

/** A labelled horizontal magnitude bar, exposed to assistive tech as a
 *  progressbar with its real value. */
function BarRow({ label, count, total, barClass }: {
  label: string
  count: number
  total: number
  barClass: string
}) {
  const pct = total > 0 ? (count / total) * 100 : 0
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400 mb-1">
        <span>{label}</span>
        <span className="font-semibold">{count}</span>
      </div>
      <div
        role="progressbar"
        aria-label={`${label}: ${count} of ${total}`}
        aria-valuenow={count}
        aria-valuemin={0}
        aria-valuemax={total}
        className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2"
      >
        <div className={`h-2 rounded-full ${barClass}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { selectedClient } = useClient()
  const { data, isLoading, isError, isFetching, dataUpdatedAt, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.get,
    refetchInterval: 30_000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 dark:text-slate-400 text-sm">
        Loading dashboard…
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 text-center">
        <p className="text-sm text-red-600 dark:text-red-400">Couldn’t load the dashboard.</p>
        <button onClick={() => refetch()} className="btn-primary inline-flex items-center gap-2">
          <RefreshCw size={14} /> Retry
        </button>
      </div>
    )
  }

  const totalRisks = data.open_risks_by_impact.reduce((s, r) => s + r.count, 0)
  const totalVendors = data.vendors_by_tier.reduce((s, v) => s + v.count, 0)
  const scope = selectedClient ? selectedClient.name : 'All clients'

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">
            GRC posture · <span className="font-medium text-slate-700 dark:text-slate-300">{scope}</span>
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="neu-btn inline-flex items-center gap-2 text-xs disabled:opacity-60"
          aria-label="Refresh dashboard data"
        >
          <RefreshCw size={13} className={isFetching ? 'animate-spin motion-reduce:animate-none' : ''} />
          {isFetching ? 'Updating…' : `Updated ${new Date(dataUpdatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Open Risks"
          value={totalRisks}
          to="/risks"
          sub={`${data.high_risks_open} High/Critical`}
          color={data.high_risks_open > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-slate-900 dark:text-slate-100'}
        />
        <StatCard
          label="Control Coverage"
          value={`${data.control_coverage_pct.toFixed(0)}%`}
          to="/risks"
          sub="risks with ≥1 control mapped"
          color={data.control_coverage_pct < 50 ? 'text-red-600 dark:text-red-400' : data.control_coverage_pct < 80 ? 'text-orange-600 dark:text-orange-400' : 'text-green-600 dark:text-green-400'}
        />
        <StatCard
          label="Evidence Alerts"
          value={data.evidence_expired + data.evidence_expiring_soon}
          to="/evidence"
          sub={`${data.evidence_expired} expired · ${data.evidence_expiring_soon} expiring soon`}
          color={(data.evidence_expired + data.evidence_expiring_soon) > 0 ? 'text-red-600 dark:text-red-400' : 'text-slate-900 dark:text-slate-100'}
        />
        <StatCard
          label="Open Findings"
          value={data.open_findings}
          to="/audits"
          sub={`${data.audits_active} active audit${data.audits_active !== 1 ? 's' : ''}`}
          color={data.open_findings > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-slate-900 dark:text-slate-100'}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk by impact */}
        <div className="neu-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">Open Risks by Impact</h2>
            <Link to="/risks" className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline">View all →</Link>
          </div>
          {data.open_risks_by_impact.length === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400">No open risks — nothing to triage right now.</p>
          ) : (
            <div className="space-y-3">
              {['Critical', 'High', 'Medium', 'Low'].map(impact => {
                const entry = data.open_risks_by_impact.find(r => r.impact === impact)
                return (
                  <BarRow
                    key={impact}
                    label={impact}
                    count={entry?.count ?? 0}
                    total={totalRisks}
                    barClass={IMPACT_COLORS[impact] ?? 'bg-slate-400'}
                  />
                )
              })}
            </div>
          )}
        </div>

        {/* Vendors by tier */}
        <div className="neu-card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">
              Vendors ({totalVendors} total · {data.vendors_under_review} under review)
            </h2>
            <Link to="/vendors" className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline">View all →</Link>
          </div>
          {data.vendors_by_tier.length === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400">No vendors registered yet.</p>
          ) : (
            <div className="space-y-3">
              {[1, 2, 3].map(tier => {
                const entry = data.vendors_by_tier.find(v => v.tier === tier)
                const tierLabel = tier === 1 ? 'Tier 1 — Critical' : tier === 2 ? 'Tier 2 — Important' : 'Tier 3 — Standard'
                const barClass = tier === 1 ? 'bg-red-500' : tier === 2 ? 'bg-orange-400' : 'bg-green-400'
                return (
                  <BarRow key={tier} label={tierLabel} count={entry?.count ?? 0} total={totalVendors} barClass={barClass} />
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
