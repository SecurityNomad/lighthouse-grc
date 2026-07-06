import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { pluginsApi, type Plugin, type PluginRunResult } from '../api/plugins'
import { useToast } from '../components/Toaster'
import { Cloud, ShieldAlert, Bell, Play } from 'lucide-react'

const TYPE_ICON: Record<string, typeof Cloud> = {
  aws_config: Cloud,
  misp: ShieldAlert,
  slack: Bell,
}

const MODE_BADGE: Record<string, string> = {
  live: 'badge-green',
  demo: 'badge-yellow',
  disabled: 'badge-gray',
}

const TYPE_LABEL: Record<string, string> = {
  risk_source: 'Risk source',
  notification: 'Notification',
}

export default function PluginsPage() {
  const qc = useQueryClient()
  const { toast } = useToast()

  const { data: plugins = [], isLoading } = useQuery({
    queryKey: ['plugins'],
    queryFn: pluginsApi.list,
  })

  const runMut = useMutation({
    mutationFn: (name: string) => pluginsApi.run(name),
    onSuccess: (result: PluginRunResult) => {
      qc.invalidateQueries({ queryKey: ['risks'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      qc.invalidateQueries({ queryKey: ['plugins'] })
      const detail = result.created || result.skipped
        ? `Imported ${result.created}, skipped ${result.skipped}.`
        : result.message
      toast(`${result.plugin}: ${detail}`, 'success')
    },
  })

  return (
    <div>
      <div className="mb-6">
        <h1 className="page-title">Plugins</h1>
        <p className="page-subtitle">
          Optional integrations that pull findings into the register and push notifications out.
          Each runs in <span className="font-medium">live</span> or <span className="font-medium">demo</span> mode.
        </p>
      </div>

      {isLoading ? (
        <div className="text-sm text-slate-400 text-center py-16">Loading…</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {plugins.map((p: Plugin) => {
            const Icon = TYPE_ICON[p.name] ?? Cloud
            const running = runMut.isPending && runMut.variables === p.name
            return (
              <div key={p.name} className="neu-card p-5 flex flex-col">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center shrink-0">
                    <Icon size={20} className="text-slate-600 dark:text-slate-300" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-semibold text-slate-900 dark:text-slate-100">{p.display_name}</h3>
                      <span className={`badge ${MODE_BADGE[p.status.mode] ?? 'badge-gray'}`}>{p.status.mode}</span>
                      <span className="badge badge-gray">{TYPE_LABEL[p.type] ?? p.type}</span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{p.description}</p>
                  </div>
                </div>

                <p className="text-xs text-slate-500 dark:text-slate-400 mt-3 bg-slate-100 dark:bg-slate-800/60 rounded-lg px-3 py-2">
                  {p.status.message}
                </p>

                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs text-slate-400">v{p.version}</span>
                  <button
                    onClick={() => runMut.mutate(p.name)}
                    disabled={!p.status.healthy || running}
                    className="btn-primary flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    <Play size={14} />
                    {running
                      ? 'Running…'
                      : p.type === 'notification' ? 'Send test' : 'Run import'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
