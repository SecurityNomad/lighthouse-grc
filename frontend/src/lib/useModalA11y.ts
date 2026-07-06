import { useEffect, useRef } from 'react'

const FOCUSABLE = [
  'a[href]', 'button:not([disabled])', 'textarea:not([disabled])',
  'input:not([disabled])', 'select:not([disabled])', '[tabindex]:not([tabindex="-1"])',
].join(',')

/**
 * Accessibility plumbing shared by every modal dialog:
 *  - Escape closes the dialog
 *  - Tab / Shift+Tab are trapped inside the panel
 *  - focus moves into the panel on open and is restored to the trigger on close
 *  - background page scroll is locked while open
 *
 * Attach the returned ref to the dialog panel and give it
 * `role="dialog" aria-modal="true"`.
 */
export function useModalA11y<T extends HTMLElement = HTMLDivElement>(onClose: () => void) {
  const ref = useRef<T>(null)

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null
    const panel = ref.current

    // Move focus to the first focusable element (or the panel itself).
    const focusables = panel?.querySelectorAll<HTMLElement>(FOCUSABLE)
    if (focusables && focusables.length > 0) {
      focusables[0].focus()
    } else {
      panel?.focus()
    }

    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        e.stopPropagation()
        onClose()
        return
      }
      if (e.key !== 'Tab' || !panel) return
      const items = panel.querySelectorAll<HTMLElement>(FOCUSABLE)
      if (items.length === 0) return
      const first = items[0]
      const last = items[items.length - 1]
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault()
        last.focus()
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = prevOverflow
      previouslyFocused?.focus?.()
    }
  }, [onClose])

  return ref
}
