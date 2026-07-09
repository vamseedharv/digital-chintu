import clsx from 'clsx'
import { NavLink } from 'react-router'
import { navItems } from '../../app/navigation'

export interface NavLinksProps {
  /** Called after navigating — e.g. MobileNav closes itself on link click. */
  onNavigate?: () => void
}

/** Shared by Sidebar (desktop) and MobileNav (mobile drawer) so the two
 * responsive variants of the same navigation can't drift out of sync. */
export function NavLinks({ onNavigate }: NavLinksProps) {
  return (
    <>
      {navItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          end={item.path === '/'}
          onClick={onNavigate}
          className={({ isActive }) =>
            clsx(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
              isActive
                ? 'bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-400'
                : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800',
            )
          }
        >
          <item.icon aria-hidden="true" className="h-4 w-4" />
          {item.label}
        </NavLink>
      ))}
    </>
  )
}
