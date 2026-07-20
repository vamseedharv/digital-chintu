import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router'
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

export function OnboardingPage() {
  const { state, saveState, save } = useSettings()
  const navigate = useNavigate()
  const [appNameDraft, setAppNameDraft] = useState('')
  const [themeDraft, setThemeDraft] = useState<ThemePreference>('system')

  useEffect(() => {
    if (state.kind === 'success') {
      setAppNameDraft(state.data.app_name)
      setThemeDraft(state.data.default_theme)
    }
  }, [state])

  useEffect(() => {
    if (saveState.kind === 'success') {
      navigate('/', { replace: true })
    }
  }, [saveState, navigate])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void save({ app_name: appNameDraft, default_theme: themeDraft, onboarding_complete: true })
  }

  function handleSkip() {
    void save({ onboarding_complete: true })
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <Heading level={1}>Welcome</Heading>
          <Text variant="muted" className="mt-1">
            Let's get your assistant set up. You can change any of this later from Settings.
          </Text>
        </div>

        <Card>
          {state.kind === 'loading' && (
            <div className="space-y-3" role="status">
              <span className="sr-only">Loading current settings…</span>
              <Skeleton className="h-9 w-full" />
              <Skeleton className="h-9 w-full" />
            </div>
          )}

          {state.kind === 'error' && (
            <p className="text-red-600 dark:text-red-400" role="alert">
              Could not load current settings. Is the backend running?
            </p>
          )}

          {state.kind === 'success' && (
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <TextField
                label="What should we call your assistant?"
                description="Used throughout the app and in voice/greeting features."
                value={appNameDraft}
                onChange={(event) => setAppNameDraft(event.target.value)}
                maxLength={64}
                required
                autoFocus
              />

              <SelectField
                label="Theme"
                description="You can switch light/dark anytime from the header."
                options={THEME_OPTIONS}
                value={themeDraft}
                onChange={(event) => setThemeDraft(event.target.value as ThemePreference)}
              />

              {saveState.kind === 'error' && (
                <Text variant="body" role="alert" className="text-red-600 dark:text-red-400">
                  Could not save your settings. Try again.
                </Text>
              )}

              <div className="flex items-center gap-3">
                <Button type="submit" loading={saveState.kind === 'saving'}>
                  Get started
                </Button>
                <Button type="button" variant="ghost" onClick={handleSkip}>
                  Skip for now
                </Button>
              </div>
            </form>
          )}
        </Card>
      </div>
    </div>
  )
}
