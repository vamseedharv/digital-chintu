import { Home, Settings } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export interface NavItem {
  label: string
  path: string
  icon: LucideIcon
}

// Add a { label, path, icon } here and a matching route in app/router.tsx
// when a new top-level page lands. Don't add placeholder entries for pages
// that don't exist yet.
export const navItems: NavItem[] = [
  { label: 'Home', path: '/', icon: Home },
  { label: 'Settings', path: '/settings', icon: Settings },
]
