import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { RefreshCw, ShieldCheck, ArrowRight } from 'lucide-react'
import { dashboardApi, type DashboardData } from '../api/dashboard'
import { useClient } from '../contexts/ClientContext'

const IMPACT_COLORS: Record<string, string> = {
  Critical: 'bg-red-500',
  High: 'bg-orange-400',
  Medium: 'bg-yellow-400',
  Low: 'bg-green-400',
}

type Severity = 'critical' | 'high'

const SEVERITY = {
  critical: {
    dot: 'bg-red-500',
    value: 'text-red-600 dark:text-red-400',
    ring: 'ring-1 ring-red-500/30 dark:ring-red-400/25',
    chip: 'text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-950/40',
  },
  high: {
    dot: 'bg-orange-500',
    value: 'text-orange-600 dark:text-orange-400',
    ring: 'ring-1 ring-orange-500/30 dark:ring-orange-400/25',
    chip: 'text-orange-700 dark:text-orange-300 bg-orange-50 dark:bg-orange-950/40',
  },
} as const

interface Signal {
  label: string
  detail: string
  severity: Severity
  to: string
}

/** Rank the posture into the handful of things that actually need attention,
 *  worst first. This is the lighthouse job: signal danger before it grounds you. */
function computeSignals(data: DashboardData): Signal[] {
  const signals: Signal[] = []
  if (data.evidence_expired > 0)
    signals.push({ label: 'Evidence expired', detail: `${data.evidence_expired} file${data.evidence_expired !== 1 ? 's' : ''}`, severity: 'critical', to: '/evidence' })
  if (data.high_risks_open > 0)
    signals.push({ label: 'High / Critical risks open', detail: `${data.high_risks_open} risk${data.high_risks_open !== 1 ? 's' : ''}`, severity: 'critical', to: '/risks' })
  if (data.open_findings > 0)
    signals.push({ label: 'Open audit findings', detail: `${data.open_findings}`, severity: 'high', to: '/audits' })
  if (data.evidence_expiring_soon > 0)
    signals.push({ label: 'Evidence expiring soon', detail: `${data.evidence_expiring_soon} file${data.evidence_expiring_soon !== 1 ? 's' : ''}`, severity: 'high', to: '/evidence' })
  if (data.control_coverage_pct < 50)
    signals.push({ label: 'Low control coverage', detail: `${data.control_coverage_pct.toFixed(0)}%`, severity: 'high', to: '/risks' })
  const order: Record<Severity, number> = { critical: 0, high: 1 }
  return signals.sort((a, b) => order[a.severity] - order[b.severity])
}

/** The lead. When something needs attention it stands up off the surface with a
 *  severity ring and ranks the issues; when all-clear it stays quiet and calm. */
function AttentionBanner({ signals }: { signals: Signal[] }) {
  if (signals.length === 0) {
    return (
      <div className="neu-card p-5 flex items-center gap-4">
        <div className="w-11 h-11 rounded-2xl bg-green-100 dark:bg-green-950/50 flex items-center justify-center shrink-0">
          <ShieldCheck size={22} className="text-green-600 dark:text-green-400" />
        </div>
        <div>
          <p className="text-base font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: '"Plus Jakarta Sans", Inter, sans-serif' }}>
            Posture stable
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">No urgent items across risks, evidence, or findings.</p>
        </div>
      </div>
    )
  }

  const top = signals[0]
  return (
    <div className={`neu-card p-5 ${SEVERITY[top.severity].ring}`}>
      <div className="flex items-start gap-4">
        <div className={`w-11 h-11 rounded-2xl ${SEVERITY[top.severity].chip} flex items-center justify-center shrink-0`}>
          <span className={`w-3 h-3 rounded-full ${SEVERITY[top.severity].dot}`} aria-hidden="true" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-base font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: '"Plus Jakarta Sans", Inter, sans-serif' }}>
            {signals.length} area{signals.length !== 1 ? 's' : ''} need attention
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
            Most pressing: <span className={`font-semibold ${SEVERITY[top.severity].value}`}>{top.label.toLowerCase()}</span> ({top.detail}).
          </p>
          <div className="flex flex-wrap gap-2 mt-3">
            {signals.map(s => (
              <Link
                key={s.label}
                to={s.to}
                className={`group inline-flex items-center gap-1.5 rounded-full pl-2.5 pr-2 py-1 text-xs font-medium ${SEVERITY[s.severity].chip}
                            outline-none focus-visible:ring-2 focus-visible:ring-indigo-500`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${SEVERITY[s.severity].dot}`} aria-hidden="true" />
                {s.label} · {s.detail}
                <ArrowRight size={12} className="opacity-60 transition-transform motion-safe:group-hover:translate-x-0.5" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

/** A KPI tile that links into the list it summarises. `alert` raises the tile
 *  off the surface with a severity ring + dot; calm tiles stay quiet. */
function StatCard({ label, value, sub, to, color = 'text-slate-900 dark:text-slate-100', alert }: {
  label: string
  value: number | string
  sub?: string
  to: string
  color?: string
  alert?: Severity
}) {
  return (
    <Link
      to={to}
      aria-label={`${label}: ${value}${sub ? `. ${sub}` : ''}. View details.`}
      className={`neu-card p-5 block outline-none transition-shadow
                  focus-visible:ring-2 focus-visible:ring-indigo-500 dark:focus-visible:ring-indigo-400
                  ${alert ? SEVERITY[alert].ring : ''}`}
    >
      <div className="flex items-center gap-1.5">
        {alert && <span className={`w-2 h-2 rounded-full ${SEVERITY[alert].dot}`} aria-hidden="true" />}
        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wide font-semibold">{label}</p>
      </div>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{sub}</p>}
    </Link>
  )
}

function BarRow({ label, count, total, barClass }: { label: string; count: number; total: number; barClass: string }) {
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
  const signals = computeSignals(data)

  const evidenceAlerts = data.evidence_expired + data.evidence_expiring_soon
  // Shared threshold for framework readiness meters: below half is a problem,
  // 80%+ is audit-ready. Matches the SoA page so the two never disagree.
  const readinessColor = (pct: number) =>
    pct < 50 ? 'text-red-600 dark:text-red-400'
      : pct < 80 ? 'text-orange-600 dark:text-orange-400'
        : 'text-green-600 dark:text-green-400'
  const coverageColor = data.control_coverage_pct < 50
    ? 'text-red-600 dark:text-red-400'
    : data.control_coverage_pct < 80 ? 'text-orange-600 dark:text-orange-400' : 'text-green-600 dark:text-green-400'

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

      {/* Lead: what needs attention, worst first */}
      <AttentionBanner signals={signals} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Open Risks"
          value={totalRisks}
          to="/risks"
          sub={`${data.high_risks_open} High/Critical`}
          color={data.high_risks_open > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-slate-900 dark:text-slate-100'}
          alert={data.high_risks_open > 0 ? 'critical' : undefined}
        />
        <StatCard
          label="Control Coverage"
          value={`${data.control_coverage_pct.toFixed(0)}%`}
          to="/risks"
          sub="risks with ≥1 control mapped"
          color={coverageColor}
          alert={data.control_coverage_pct < 50 ? 'high' : undefined}
        />
        <StatCard
          label="ISO 27001 SoA"
          value={`${data.iso_soa_readiness_pct.toFixed(0)}%`}
          to="/soa"
          sub={`readiness · ${data.iso_soa_coverage_pct.toFixed(0)}% of Annex A assessed`}
          color={readinessColor(data.iso_soa_readiness_pct)}
        />
        <StatCard
          label="SOC 2 Readiness"
          value={`${data.soc2_readiness_pct.toFixed(0)}%`}
          to="/soa"
          sub={`${data.soc2_cc_assessed} of ${data.soc2_cc_total} Common Criteria assessed`}
          color={readinessColor(data.soc2_readiness_pct)}
        />
        <StatCard
          label="Evidence Alerts"
          value={evidenceAlerts}
          to="/evidence"
          sub={`${data.evidence_expired} expired · ${data.evidence_expiring_soon} expiring soon`}
          color={evidenceAlerts > 0 ? 'text-red-600 dark:text-red-400' : 'text-slate-900 dark:text-slate-100'}
          alert={data.evidence_expired > 0 ? 'critical' : data.evidence_expiring_soon > 0 ? 'high' : undefined}
        />
        <StatCard
          label="Open Findings"
          value={data.open_findings}
          to="/audits"
          sub={`${data.audits_active} active audit${data.audits_active !== 1 ? 's' : ''}`}
          color={data.open_findings > 0 ? 'text-orange-600 dark:text-orange-400' : 'text-slate-900 dark:text-slate-100'}
          alert={data.open_findings > 0 ? 'high' : undefined}
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
                  <BarRow key={impact} label={impact} count={entry?.count ?? 0} total={totalRisks} barClass={IMPACT_COLORS[impact] ?? 'bg-slate-400'} />
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
                return <BarRow key={tier} label={tierLabel} count={entry?.count ?? 0} total={totalVendors} barClass={barClass} />
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
