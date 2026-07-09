# frontend-dashboard

React + TypeScript + Vite web dashboard for Digital Chintu, styled with
Tailwind CSS v4 and Framer Motion, supporting dark and light themes.

```
src/
  main.tsx        Entry point, wraps App in ThemeProvider
  App.tsx          Root component
  theme/           Dark/light ThemeProvider + useTheme hook (class-based, persisted to localStorage)
  api/             Fetch client + typed calls to the backend
  components/      UI components (HealthStatus, ThemeToggle)
  __tests__/
    unit/          Isolated tests of one hook/component/module
    integration/   Tests of the composed App tree (theme + health fetch + rendering together)
```

## Setup

```bash
npm install
cp .env.example .env
```

## Run

```bash
npm run dev
```

Open `http://localhost:5173`. Requires the backend running at the URL
configured in `.env` (`VITE_API_BASE_URL`, default `http://localhost:8000`).

## Test

```bash
npm run test               # run once
npm run test:watch         # watch mode
npx vitest run --coverage  # writes coverage/ (text summary + HTML report)
```

## Lint, format, and type-check

```bash
npm run lint
npm run format         # write
npm run format:check   # check only
npm run typecheck
```

## Build

```bash
npm run build      # outputs to dist/
npm run preview    # preview the production build locally
```
