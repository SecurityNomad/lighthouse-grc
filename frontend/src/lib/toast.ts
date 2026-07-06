// Tiny framework-agnostic toast bus. Lives outside React so it can be driven
// from the TanStack Query MutationCache (which is created outside the tree) as
// well as from components via useToast().

export type ToastType = 'error' | 'success' | 'info'

export interface Toast {
  id: number
  message: string
  type: ToastType
}

type Listener = (toasts: Toast[]) => void

let toasts: Toast[] = []
const listeners = new Set<Listener>()
let nextId = 1

function emit() {
  for (const listener of listeners) listener(toasts)
}

export function pushToast(message: string, type: ToastType = 'error', timeoutMs = 5000): number {
  const id = nextId++
  toasts = [...toasts, { id, message, type }]
  emit()
  if (timeoutMs > 0) {
    setTimeout(() => dismissToast(id), timeoutMs)
  }
  return id
}

export function dismissToast(id: number) {
  toasts = toasts.filter(t => t.id !== id)
  emit()
}

export function subscribeToasts(listener: Listener): () => void {
  listeners.add(listener)
  listener(toasts)
  return () => {
    listeners.delete(listener)
  }
}
