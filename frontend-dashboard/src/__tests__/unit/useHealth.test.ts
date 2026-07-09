import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useHealth } from '../../api/useHealth'

describe('useHealth', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('starts in the loading state', () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }))

    const { result } = renderHook(() => useHealth())

    expect(result.current).toEqual({ kind: 'loading' })
  })

  it('transitions to success with the fetched data', async () => {
    const data = { status: 'ok', app_name: 'Chintu', environment: 'test' }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => data }))

    const { result } = renderHook(() => useHealth())

    await waitFor(() => {
      expect(result.current).toEqual({ kind: 'success', data })
    })
  })

  it('transitions to error when the request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network error')))

    const { result } = renderHook(() => useHealth())

    await waitFor(() => {
      expect(result.current).toEqual({ kind: 'error' })
    })
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

    const { result, unmount } = renderHook(() => useHealth())
    unmount()

    resolveFetch({ ok: true, json: async () => ({ status: 'ok' }) })
    await new Promise((resolve) => setTimeout(resolve, 0))

    // Still whatever it was at unmount time — the cancelled flag in
    // useHealth prevented a state update on an unmounted component.
    expect(result.current).toEqual({ kind: 'loading' })
  })

  it('does not update state after unmounting when the request later fails', async () => {
    let rejectFetch!: (reason: unknown) => void
    vi.stubGlobal(
      'fetch',
      vi.fn().mockReturnValue(
        new Promise((_resolve, reject) => {
          rejectFetch = reject
        }),
      ),
    )

    const { result, unmount } = renderHook(() => useHealth())
    unmount()

    rejectFetch(new Error('network error'))
    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(result.current).toEqual({ kind: 'loading' })
  })
})
