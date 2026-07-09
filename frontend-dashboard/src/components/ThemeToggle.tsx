import { motion } from 'framer-motion'
import clsx from 'clsx'
import { useTheme } from '../theme/useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      className={clsx(
        'glass rounded-full px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors',
        'hover:bg-white/80 dark:text-slate-200 dark:hover:bg-slate-800/80',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-slate-900',
      )}
    >
      <motion.span
        key={theme}
        initial={{ opacity: 0, y: -4 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
      >
        {isDark ? 'Dark mode' : 'Light mode'}
      </motion.span>
    </button>
  )
}
