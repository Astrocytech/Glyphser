export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
}

export function isMockMode(): boolean {
  const stored = localStorage.getItem('glyphser-use-mock-api')
  if (stored !== null) {
    return stored === 'true'
  }
  return import.meta.env.VITE_USE_MOCK_API === 'true'
}
