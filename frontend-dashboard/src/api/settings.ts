import { apiGet, apiPatch } from './client'

export type ThemePreference = 'light' | 'dark' | 'system'

export interface SettingsResponse {
  app_name: string
  default_theme: ThemePreference
}

export interface SettingsUpdate {
  app_name?: string
  default_theme?: ThemePreference
}

export function fetchSettings(): Promise<SettingsResponse> {
  return apiGet<SettingsResponse>('/api/v1/settings')
}

export function updateSettings(update: SettingsUpdate): Promise<SettingsResponse> {
  return apiPatch<SettingsResponse>('/api/v1/settings', update)
}
