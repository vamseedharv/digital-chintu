import { useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'
import { NavLinks } from './NavLinks'

export interface MobileNavProps {
  appName: string
  open: boolean
  onClose: () => void
}

const FOCUSABLE_SELECTOR = 'a[href], button:not([disabled])'

// Shared by the backdrop and drawer below so their durations can't drift
// apart from each other.
const DRAWER_TRANSITION = { duration: 0.2 }

export function MobileNav({ appName, open, onClose }: MobileNavProps) {
  const navRef = useRef<HTMLElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!open) return

    closeButtonRef.current?.focus()

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose()
        return
      }

      // Trap Tab focus inside the drawer while it's open — without this,
      // tabbing past the last nav link would move focus into the page
      // content hidden behind the drawer's overlay.
      if (event.key === 'Tab' && navRef.current) {
        const focusable = Array.from(
          navRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR),
        )
        const first = focusable.at(0)
        const last = focusable.at(-1)
        if (!first || !last) return

        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault()
          last.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault()
          first.focus()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={DRAWER_TRANSITION}
            className="fixed inset-0 z-40 bg-black/40 md:hidden"
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.nav
            ref={navRef}
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', ...DRAWER_TRANSITION }}
            aria-label="Primary"
            className="glass fixed inset-y-0 left-0 z-50 flex w-64 flex-col gap-1 p-4 md:hidden"
          >
            <div className="mb-4 flex items-center justify-between">
              <span data-testid="app-name" className="text-lg font-semibold">
                {appName}
              </span>
              <button
                ref={closeButtonRef}
                type="button"
                onClick={onClose}
                aria-label="Close navigation"
                className="rounded-lg p-1.5 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 dark:hover:bg-slate-800"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <NavLinks onNavigate={onClose} />
          </motion.nav>
        </>
      )}
    </AnimatePresence>
  )
}
