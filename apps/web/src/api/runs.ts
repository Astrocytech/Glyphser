import { api, ApiError } from './client'
import type { RunDetails, RunRecord } from '@/types/run'
import { getMockRun, listMockRuns } from '@/api/mock/store'

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function mockGetRuns(): Promise<RunRecord[]> {
  await sleep(400)
  return listMockRuns()
}

async function mockGetRun(runId: string): Promise<RunDetails> {
  await sleep(350)
  const run = getMockRun(runId)
  if (!run) throw new ApiError('Run not found', 404, '')
  return run
}

export function getRuns() {
  if (import.meta.env.VITE_USE_MOCK_API === 'true') {
    return mockGetRuns()
  }

  return api<RunRecord[]>('/runs')
}

export function getRun(runId: string) {
  if (import.meta.env.VITE_USE_MOCK_API === 'true') {
    return mockGetRun(runId)
  }

  return api<RunDetails>(`/runs/${encodeURIComponent(runId)}`)
}
