import { motion } from 'framer-motion'
import type { HealthState } from '../api/useHealth'

export function HealthStatus({ health }: { health: HealthState }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="rounded-2xl border border-slate-200 bg-white/70 p-6 shadow-sm backdrop-blur-md
        dark:border-slate-700 dark:bg-slate-800/50"
    >
      <h2 className="text-lg font-semibold">Backend connection</h2>

      {health.kind === 'loading' && (
        <p className="mt-2 text-slate-500 dark:text-slate-400" role="status">
          Checking backend health…
        </p>
      )}

      {health.kind === 'success' && (
        <p className="mt-2 text-emerald-600 dark:text-emerald-400" role="status">
          {health.data.app_name} backend is {health.data.status} ({health.data.environment})
        </p>
      )}

      {health.kind === 'error' && (
        <p className="mt-2 text-red-600 dark:text-red-400" role="alert">
          Could not reach the backend. Is it running?
        </p>
      )}
    </motion.div>
  )
}
