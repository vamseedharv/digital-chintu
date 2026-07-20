# 09 UI Design System

Status: **implemented** — theme engine, design tokens, typography, icon system, and a
reusable component library all exist (see `docs/features/006_Theme_Engine.md`).
Grows further as real UI features (Dashboard, Settings) need more primitives.

## Styling

- **Tailwind CSS v4** via `@tailwindcss/vite` — no `tailwind.config.js`;
  configuration lives in `src/index.css` (`@import 'tailwindcss'` +
  `@custom-variant dark` + a `@theme` block for design tokens).
- **Framer Motion** for transitions (`Card`'s built-in fade-in, theme
  toggle label transition, mobile nav drawer slide-in + backdrop fade).
  Wrapped in `<MotionConfig reducedMotion="user">` at the app root
  (`main.tsx`) — every animation automatically respects
  `prefers-reduced-motion` in one place, rather than each component
  checking it individually. `MobileNav`'s backdrop and drawer share one
  `DRAWER_TRANSITION` constant so the two can't drift to different
  durations.

## Design tokens

`src/index.css`'s `@theme` block defines a brand color ramp
(`--color-brand-50` through `--color-brand-700`), used by the primary
`Button` variant, active nav-link styling, and focus rings. Tailwind's
default spacing/sizing/radius/breakpoint scales are used as-is elsewhere —
no need to reinvent those until a real feature needs something they don't
cover.

## Glassmorphism

Formalized as a Tailwind `@utility glass` class (translucent background +
`backdrop-blur-md` + border, both themes) — used by the `Card` component and
the `Sidebar`/`MobileNav` surfaces. Previously hand-typed inline per
component; now there's exactly one definition to change.

## Typography

Two components (`components/ui/Heading.tsx`, `components/ui/Text.tsx`) wrap
a small fixed set of Tailwind class combinations (heading levels 1–4, text
variants body/muted/caption) — chosen over a bare token list because it
enforces consistency where remembering the right class combo every time
wouldn't.

## Icon system

`lucide-react` — free, tree-shakeable, MIT-licensed. Used directly (no
wrapper component); nav items reference a `LucideIcon` type in
`app/navigation.ts`.

## Component library

`frontend-dashboard/src/components/ui/`: `Button` (variants: primary/
secondary/ghost; sizes; loading state; its styling is factored into
`buttonStyles.ts`'s `buttonClasses()` so non-`<button>` elements can share
it), `LinkButton` (a react-router `Link` styled like `Button` — used
wherever a navigation action must be a real link, e.g. 404/error pages'
"Back to Home"), `Card` (glass surface with a built-in mount fade-in),
`Spinner` (accessible loading indicator, `role="status"`), `Skeleton`
(visual loading placeholder, `aria-hidden`), `EmptyState` (icon + heading +
description + action — used by 404/error pages, reusable for future "no
data yet" states), `Heading`, `Text`, `TextField`/`SelectField` (the first
form primitives — labeled input/select with `useId()`-based label
association, optional description, and an error state with
`aria-invalid`/`role="alert"`; added for the Settings form, `008_Settings`).

`frontend-dashboard/src/components/layout/`: `PageContainer` (consistent
max-width/padding — `max-w-5xl`, widened from `max-w-2xl` for the
Dashboard's multi-column widget grid), `NavLinks` (the actual nav-item
list — shared by both `Sidebar` and `MobileNav` so the desktop/mobile
variants of the same navigation can't drift out of sync with each other),
`Sidebar` (desktop nav), `MobileNav` (drawer nav: focus moves to its close
button on open, Escape closes it, and Tab is trapped inside it while open
so keyboard focus can't leave the drawer into the page behind it).

`frontend-dashboard/src/components/dashboard/`: the Dashboard feature's
first extracted primitive, `WidgetCard` (glass `Card` + optional icon +
`<h2>` title + content slot) — every dashboard tile (built-in or a future
feature's) renders through it, so a new widget only writes its content.
`GreetingWidget`, `ClockWidget`, and `PlaceholderWidget` build on it; see
[docs/SDS/01_UI/012_Dashboard.md](../SDS/01_UI/012_Dashboard.md).

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

## Accessibility

Semantic landmarks (`header`, `nav`, `main`), a skip-to-content link
(`AppShell.tsx`), visible focus rings (`focus-visible:ring-2` on every
interactive primitive, verified against real computed contrast — see
below), `aria-label`s on icon-only controls, keyboard-navigable nav
(`Sidebar`/`MobileNav`), and a full Tab focus trap inside `MobileNav` while
it's open (in addition to Escape-to-close and initial focus on its close
button). `prefers-reduced-motion` is respected globally via
`MotionConfig` (see Styling above).

Text contrast verified empirically (canvas-based sRGB extraction + WCAG
relative-luminance formula, not eyeballed): `Text variant="muted"`
(`text-slate-500`/`dark:text-slate-400`) against the page background
measures 4.55:1 in light mode and 6.78:1 in dark mode — both pass WCAG AA
for normal-size text (4.5:1 minimum).

`EmptyState`'s icon-plus-heading pattern was reviewed for redundant
announcement: the icon carries `aria-hidden="true"`, and `Heading` is the
only element with accessible text, so a screen reader announces the heading
once, not the icon plus the heading. Confirmed by code inspection, not an
actual screen reader — that still needs a human pass.

## Not implemented yet

No custom spacing scale (Tailwind's default is sufficient so far) — the
Dashboard and Settings each needed a shared primitive (`WidgetCard`,
`TextField`/`SelectField`) but nothing beyond Tailwind's existing spacing
tokens. Extract further shared primitives once another real UI feature
(Notifications, and later Settings itself as more managed settings arrive)
needs them — see [ROADMAP.md](../../ROADMAP.md)'s Phase 6.
