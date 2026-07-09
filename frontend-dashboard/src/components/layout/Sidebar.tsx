import { NavLinks } from './NavLinks'

export function Sidebar({ appName }: { appName: string }) {
  return (
    <nav
      aria-label="Primary"
      className="glass hidden w-56 shrink-0 flex-col gap-1 border-r p-4 md:flex"
    >
      <span data-testid="app-name" className="mb-4 px-2 text-lg font-semibold">
        {appName}
      </span>
      <NavLinks />
    </nav>
  )
}
