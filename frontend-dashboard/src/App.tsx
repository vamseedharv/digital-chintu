import { useEffect } from 'react'
import { useHealth } from './api/useHealth'
import { HealthStatus } from './components/HealthStatus'
import { ThemeToggle } from './components/ThemeToggle'

const DEFAULT_APP_NAME = 'Digital Chintu'

function App() {
  const health = useHealth()
  const appName = health.kind === 'success' ? health.data.app_name : DEFAULT_APP_NAME

  useEffect(() => {
    document.title = appName
  }, [appName])

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between px-6 py-4">
        <h1 className="text-xl font-semibold">{appName}</h1>
        <ThemeToggle />
      </header>

      <main className="mx-auto max-w-2xl px-6 py-8">
        <HealthStatus health={health} />
      </main>
    </div>
  )
}

export default App
