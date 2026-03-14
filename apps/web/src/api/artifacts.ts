import { api, ApiError } from './client'
import {
  getMockArtifactFile,
  listMockArtifacts,
} from '@/api/mock/store'
import type { ArtifactEntry, ArtifactFileResponse } from '@/types/artifact'

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function mockGetArtifacts(runId: string): Promise<ArtifactEntry[]> {
  await sleep(250)
  return listMockArtifacts(runId)
}

async function mockGetArtifactFile(
  runId: string,
  path: string,
): Promise<ArtifactFileResponse> {
  await sleep(250)
  const file = getMockArtifactFile(runId, path)
  if (!file) throw new ApiError('Artifact not found', 404, '')
  return file
}

export function getArtifacts(runId: string) {
  if (import.meta.env.VITE_USE_MOCK_API === 'true') {
    return mockGetArtifacts(runId)
  }

  return api<ArtifactEntry[]>(`/artifacts/${encodeURIComponent(runId)}`)
}

export function getArtifactFile(runId: string, path: string) {
  if (import.meta.env.VITE_USE_MOCK_API === 'true') {
    return mockGetArtifactFile(runId, path)
  }

  const q = new URLSearchParams({ path }).toString()
  return api<ArtifactFileResponse>(
    `/artifacts/${encodeURIComponent(runId)}/file?${q}`,
  )
}
