import { afterEach, describe, expect, it, vi } from 'vitest'
import { API_BASE_URL } from '../../api/client'
import { fetchHealth } from '../../api/health'

describe('fetchHealth', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls the /api/v1/health endpoint and returns the parsed response', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok', app_name: 'Chintu', environment: 'test' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await fetchHealth()

    expect(fetchMock).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/health`)
    expect(result).toEqual({ status: 'ok', app_name: 'Chintu', environment: 'test' })
  })
})
