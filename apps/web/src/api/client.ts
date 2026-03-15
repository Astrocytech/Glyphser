import { toast } from '@/lib/toast'
import { env } from '@/lib/env'

export class ApiError extends Error {
  status: number
  body: string

  constructor(message: string, status: number, body: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

function parseErrorBody(body: string): string {
  try {
    const parsed = JSON.parse(body)
    return parsed.detail || parsed.message || parsed.error || body
  } catch {
    return body
  }
}

async function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  retries = 3,
  backoff = 1000
): Promise<Response> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const response = await fetch(url, options)

      if (!response.ok && attempt < retries - 1 && response.status >= 500) {
        const delay = backoff * Math.pow(2, attempt)
        await sleep(delay)
        continue
      }

      return response
    } catch (error) {
      lastError = error as Error
      if (attempt < retries - 1) {
        const delay = backoff * Math.pow(2, attempt)
        await sleep(delay)
      }
    }
  }

  throw lastError
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetchWithRetry(`${env.apiBaseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const body = await response.text()
    const message = parseErrorBody(body) || `Request failed with status ${response.status}`
    
    toast({
      title: 'API Error',
      description: message,
      variant: 'destructive',
    })
    
    throw new ApiError(message, response.status, body)
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('application/json')) {
    throw new ApiError('Expected JSON response from server', response.status, '')
  }

  return response.json() as Promise<T>
}
