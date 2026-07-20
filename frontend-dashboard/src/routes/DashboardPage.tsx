import { useOutletContext } from 'react-router'
import { Bell, CheckSquare, CloudSun, ShoppingCart } from 'lucide-react'
import type { AppShellContext } from '../app/AppShell'
import { ClockWidget } from '../components/dashboard/ClockWidget'
import { GreetingWidget } from '../components/dashboard/GreetingWidget'
import { PlaceholderWidget } from '../components/dashboard/PlaceholderWidget'
import { HealthStatus } from '../components/HealthStatus'

export function DashboardPage() {
  const { health, appName } = useOutletContext<AppShellContext>()

  return (
    <div className="space-y-6">
      <GreetingWidget appName={appName} />

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <ClockWidget />
        <HealthStatus health={health} />
        <PlaceholderWidget
          icon={CloudSun}
          title="Weather"
          description="Local weather at a glance."
        />
        <PlaceholderWidget
          icon={Bell}
          title="Reminders"
          description="Upcoming reminders and alarms."
        />
        <PlaceholderWidget icon={CheckSquare} title="To-do" description="Your to-do list." />
        <PlaceholderWidget
          icon={ShoppingCart}
          title="Shopping list"
          description="A shared shopping list."
        />
      </div>
    </div>
  )
}
