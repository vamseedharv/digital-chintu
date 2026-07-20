import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useSettings } from '../api/useSettings'
import type { ThemePreference } from '../api/settings'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Heading } from '../components/ui/Heading'
import { SelectField } from '../components/ui/SelectField'
import { Skeleton } from '../components/ui/Skeleton'
import { Text } from '../components/ui/Text'
import { TextField } from '../components/ui/TextField'

const THEME_OPTIONS: { value: ThemePreference; label: string }[] = [
  { value: 'system', label: 'Match system' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
]

export function SettingsPage() {
  const { state, saveState, save } = useSettings()
  const [appNameDraft, setAppNameDraft] = useState('')
  const [themeDraft, setThemeDraft] = useState<ThemePreference>('system')

  useEffect(() => {
    if (state.kind === 'success') {
      setAppNameDraft(state.data.app_name)
      setThemeDraft(state.data.default_theme)
    }
  }, [state])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void save({ app_name: appNameDraft, default_theme: themeDraft })
  }

  return (
    <div className="space-y-6">
      <Heading level={1}>Settings</Heading>

      <Card>
        {state.kind === 'loading' && (
          <div className="space-y-3" role="status">
            <span className="sr-only">Loading settings…</span>
            <Skeleton className="h-9 w-full" />
            <Skeleton className="h-9 w-full" />
          </div>
        )}

        {state.kind === 'error' && (
          <p className="text-red-600 dark:text-red-400" role="alert">
            Could not load settings. Is the backend running?
          </p>
        )}

        {state.kind === 'success' && (
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <TextField
              label="Assistant name"
              description="Shown throughout the app and used in voice/greeting features."
              value={appNameDraft}
              onChange={(event) => setAppNameDraft(event.target.value)}
              maxLength={64}
              required
            />

            <SelectField
              label="Theme"
              description="The default for a browser that hasn't chosen light or dark itself yet."
              options={THEME_OPTIONS}
              value={themeDraft}
              onChange={(event) => setThemeDraft(event.target.value as ThemePreference)}
            />

            <div className="flex items-center gap-3">
              <Button type="submit" loading={saveState.kind === 'saving'}>
                Save
              </Button>
              {saveState.kind === 'success' && (
                <Text variant="muted" role="status">
                  Saved.
                </Text>
              )}
              {saveState.kind === 'error' && (
                <Text variant="body" role="alert" className="text-red-600 dark:text-red-400">
                  Could not save settings.
                </Text>
              )}
            </div>
          </form>
        )}
      </Card>
    </div>
  )
}
