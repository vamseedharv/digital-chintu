import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiGet, ApiError, API_BASE_URL } from '../../api/client'

describe('apiGet', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('resolves with the parsed JSON body on a successful response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ hello: 'world' }),
      }),
    )

    await expect(apiGet<{ hello: string }>('/some/path')).resolves.toEqual({ hello: 'world' })
  })

  it('requests the given path against the configured API base URL', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) })
    vi.stubGlobal('fetch', fetchMock)

    await apiGet('/api/v1/health')

    expect(fetchMock).toHaveBeenCalledWith(`${API_BASE_URL}/api/v1/health`)
  })

  it('throws an ApiError carrying the HTTP status when the response is not ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ ok: false, status: 503, json: async () => ({}) }),
    )

    const error = await apiGet('/broken').catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(503)
    expect((error as ApiError).name).toBe('ApiError')
  })

  it('propagates a network failure without wrapping it', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(apiGet('/unreachable')).rejects.toThrow('Failed to fetch')
  })
})

describe('ApiError', () => {
  beforeEach(() => {
    vi.unstubAllGlobals()
  })

  it('is a real Error subclass with the message and status it was given', () => {
    const error = new ApiError('boom', 500)

    expect(error).toBeInstanceOf(Error)
    expect(error.message).toBe('boom')
    expect(error.status).toBe(500)
  })
})
