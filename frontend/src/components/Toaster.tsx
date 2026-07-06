import { useEffect, useState } from 'react'
import { subscribeToasts, dismissToast, pushToast, type Toast } from '../lib/toast'

const TYPE_STYLES: Record<Toast['type'], string> = {
  error: 'border-red-500/40 bg-red-50 text-red-800 dark:bg-red-950/60 dark:text-red-200',
  success: 'border-green-500/40 bg-green-50 text-green-800 dark:bg-green-950/60 dark:text-green-200',
  info: 'border-indigo-500/40 bg-indigo-50 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-200',
}

const TYPE_ICON: Record<Toast['type'], string> = {
  error: '⚠',
  success: '✓',
  info: 'ℹ',
}

export default function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => subscribeToasts(setToasts), [])

  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-full max-w-sm"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map(t => (
        <div
          key={t.id}
          role={t.type === 'error' ? 'alert' : 'status'}
          className={`flex items-start gap-2 rounded-xl border px-4 py-3 text-sm shadow-lg ${TYPE_STYLES[t.type]}`}
        >
          <span aria-hidden="true" className="mt-0.5 font-bold">{TYPE_ICON[t.type]}</span>
          <span className="flex-1">{t.message}</span>
          <button
            onClick={() => dismissToast(t.id)}
            aria-label="Dismiss notification"
            className="text-lg leading-none opacity-60 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}

// Convenience hook for components that want to raise a toast (e.g. success
// confirmations). Error toasts for mutations are raised globally.
export function useToast() {
  return {
    toast: (message: string, type: Toast['type'] = 'info') => pushToast(message, type),
  }
}
