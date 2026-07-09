import { motion } from 'framer-motion'
import { useTheme } from '../theme/useTheme'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      className="rounded-full border border-slate-300 bg-white/60 px-4 py-2 text-sm font-medium
        text-slate-700 shadow-sm backdrop-blur transition-colors hover:bg-white/80
        dark:border-slate-700 dark:bg-slate-800/60 dark:text-slate-200 dark:hover:bg-slate-800/80"
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
