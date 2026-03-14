import '@testing-library/jest-dom/vitest'
import { beforeEach, vi } from 'vitest'
import { resetMockStore } from '@/api/mock/store'

vi.stubEnv('VITE_API_BASE_URL', 'http://127.0.0.1:8000')
vi.stubEnv('VITE_USE_MOCK_API', 'true')

beforeEach(() => {
  resetMockStore()
})

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Radix UI primitives (e.g. ScrollArea) rely on ResizeObserver.
globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver
