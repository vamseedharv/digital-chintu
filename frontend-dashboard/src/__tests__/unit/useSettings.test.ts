import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useSettings } from '../../api/useSettings'

describe('useSettings', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('starts in the loading state', () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }))

    const { result } = renderHook(() => useSettings())

    expect(result.current.state).toEqual({ kind: 'loading' })
    expect(result.current.saveState).toEqual({ kind: 'idle' })
  })

  it('transitions to success with the fetched settings', async () => {
    const data = { app_name: 'Chintu', default_theme: 'system' }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => data }))

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.state).toEqual({ kind: 'success', data })
    })
  })

  it('transitions to error when the request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.state).toEqual({ kind: 'error' })
    })
  })

  it('save() patches the settings and updates state with the response', async () => {
    const initial = { app_name: 'Chintu', default_theme: 'system' }
    const updated = { app_name: 'Jarvis', default_theme: 'system' }
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => initial })
      .mockResolvedValueOnce({ ok: true, json: async () => updated })
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.state).toEqual({ kind: 'success', data: initial })
    })

    await act(async () => {
      await result.current.save({ app_name: 'Jarvis' })
    })

    expect(result.current.state).toEqual({ kind: 'success', data: updated })
    expect(result.current.saveState).toEqual({ kind: 'success' })
  })

  it('save() sets an error save state when the request fails, without discarding current data', async () => {
    const initial = { app_name: 'Chintu', default_theme: 'system' }
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => initial })
      .mockRejectedValueOnce(new Error('network error'))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useSettings())

    await waitFor(() => {
      expect(result.current.state).toEqual({ kind: 'success', data: initial })
    })

    await act(async () => {
      await result.current.save({ app_name: 'Jarvis' })
    })

    expect(result.current.saveState).toEqual({ kind: 'error' })
    expect(result.current.state).toEqual({ kind: 'success', data: initial })
  })

  it('does not update state after unmounting (no act() warning from a late resolution)', async () => {
    let resolveFetch!: (value: unknown) => void
    vi.stubGlobal(
      'fetch',
      vi.fn().mockReturnValue(
        new Promise((resolve) => {
          resolveFetch = resolve
        }),
      ),
    )

    const { result, unmount } = renderHook(() => useSettings())
    unmount()

    resolveFetch({
      ok: true,
      json: async () => ({ app_name: 'Chintu', default_theme: 'system' }),
    })
    await new Promise((resolve) => setTimeout(resolve, 0))

    // Still whatever it was at unmount time — the cancelled flag prevented
    // a state update on an unmounted component.
    expect(result.current.state).toEqual({ kind: 'loading' })
  })
})
