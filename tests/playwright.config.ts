import { defineConfig, devices } from '@playwright/test'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Detect by which interpreter actually exists (not by host OS name), so this
// agrees with scripts/setup.sh's detection instead of independently guessing
// from process.platform — a .venv created on a different OS than this is
// running on would otherwise compute a path that doesn't exist.
const posixPython = path.join(__dirname, '../backend/.venv/bin/python')
const backendPython = existsSync(posixPython)
  ? posixPython
  : path.join(__dirname, '../backend/.venv/Scripts/python.exe')

const FRONTEND_URL = process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:5173'
const BACKEND_URL = process.env.PLAYWRIGHT_BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  reporter: 'list',
  use: {
    baseURL: FRONTEND_URL,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  // Requires `backend/.venv` to already exist (see scripts/setup.sh /
  // scripts/setup.ps1) and frontend-dashboard dependencies to be installed.
  webServer: [
    {
      command: `"${backendPython}" -m uvicorn app.main:app --port 8000`,
      cwd: path.join(__dirname, '../backend'),
      url: `${BACKEND_URL}/api/v1/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: 'npm run dev',
      cwd: path.join(__dirname, '../frontend-dashboard'),
      url: FRONTEND_URL,
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
  ],
})
