# 09 UI Design System

Status: **theme engine implemented** (dark/light toggle); the rest of a full design
system (typography scale, spacing scale, component library, glassmorphism tokens)
will grow with `docs/features/006_Theme_Engine.md` and later UI features.

## Styling

- **Tailwind CSS v4** via `@tailwindcss/vite` — no `tailwind.config.js`;
  configuration lives in `src/index.css` (`@import 'tailwindcss'` +
  `@custom-variant dark`).
- **Framer Motion** for transitions (currently: fade/slide-in on the health
  status card, a small label transition on the theme toggle).

## Dark / light theme

- `frontend-dashboard/src/theme/` — `ThemeProvider` (state + effects),
  `ThemeContext` (context object, split out so Fast Refresh doesn't
  re-mount on every edit — an ESLint rule enforces this split), `useTheme`
  (consumer hook).
- Class-based, not purely `prefers-color-scheme`: a `dark` class is toggled
  on `<html>`, so the user's explicit choice (persisted to `localStorage`
  under `chintu-theme`) always wins over the OS setting after their first
  toggle. On first load with nothing stored, it follows
  `prefers-color-scheme`.
- Current visual language: translucent/`backdrop-blur` cards
  (`bg-white/70 dark:bg-slate-800/50` + `backdrop-blur-md`), rounded corners
  (`rounded-2xl`), a soft border — the glassmorphism direction called for in
  the Foundation pack, applied so far only to the health-status card and
  theme toggle button.

## Not implemented yet

No typography scale, spacing scale, color token file, icon set, or shared
component library beyond the two components that exist
(`HealthStatus`, `ThemeToggle`). Establish these as real UI features
(dashboard, settings, notifications, etc.) are built — extract shared
primitives once there's more than one consumer, not before.
