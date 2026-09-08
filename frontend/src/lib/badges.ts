// Badge class maps shared across pages. Colour here is semantic only —
// severity and framework identity carry meaning, so they are allowed to.

/** Critical → Low. Used for risk impact, audit finding severity, vendor rating. */
export const SEVERITY_BADGE: Record<string, string> = {
  Critical: 'badge-red',
  High: 'badge-orange',
  Medium: 'badge-yellow',
  Low: 'badge-green',
}

/** Framework identity, for the monospace control-ref chips. */
export const FRAMEWORK_REF_BADGE: Record<string, string> = {
  soc2: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  iso27001: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  cis_v8: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
}
