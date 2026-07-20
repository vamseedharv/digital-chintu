import { useCallback, useEffect, useState } from 'react'
import { fetchSettings, updateSettings } from './settings'
import type { SettingsResponse, SettingsUpdate } from './settings'

export type SettingsState =
  { kind: 'loading' } | { kind: 'success'; data: SettingsResponse } | { kind: 'error' }

export type SaveState =
  { kind: 'idle' } | { kind: 'saving' } | { kind: 'success' } | { kind: 'error' }

export interface UseSettingsResult {
  state: SettingsState
  saveState: SaveState
  save: (update: SettingsUpdate) => Promise<void>
}

export function useSettings(): UseSettingsResult {
  const [state, setState] = useState<SettingsState>({ kind: 'loading' })
  const [saveState, setSaveState] = useState<SaveState>({ kind: 'idle' })

  useEffect(() => {
    let cancelled = false

    fetchSettings()
      .then((data) => {
        if (!cancelled) setState({ kind: 'success', data })
      })
      .catch(() => {
        if (!cancelled) setState({ kind: 'error' })
      })

    return () => {
      cancelled = true
    }
  }, [])

  const save = useCallback(async (update: SettingsUpdate) => {
    setSaveState({ kind: 'saving' })
    try {
      const data = await updateSettings(update)
      setState({ kind: 'success', data })
      setSaveState({ kind: 'success' })
    } catch {
      setSaveState({ kind: 'error' })
    }
  }, [])

  return { state, saveState, save }
}
