import type { RunDetails, RunRecord, RunStatus } from '@/types/run'
import type { ArtifactEntry, ArtifactFileResponse } from '@/types/artifact'

type ArtifactStoreEntry = ArtifactFileResponse

type RunStoreRecord = RunDetails & {
  artifacts: ArtifactStoreEntry[]
}

let counter = 4

const nowIso = () => new Date().toISOString()

const initialStore: RunStoreRecord[] = [
  {
    id: 'run_mock_004',
    status: 'running',
    started_at: nowIso(),
    summary: 'Verification in progress.',
    inputs: { path: '/tmp/artifact.bin' },
    artifacts: [
      {
        path: 'request.json',
        contentType: 'application/json',
        content: JSON.stringify({ path: '/tmp/artifact.bin' }, null, 2),
      },
    ],
  },
  {
    id: 'run_mock_003',
    status: 'passed',
    started_at: nowIso(),
    finished_at: nowIso(),
    summary: 'All checks passed.',
    inputs: { path: '/tmp/artifact_v2.bin' },
    artifacts: [
      {
        path: 'result.json',
        contentType: 'application/json',
        content: JSON.stringify(
          { status: 'PASS', summary: 'Mock verification completed successfully.' },
          null,
          2,
        ),
      },
    ],
  },
  {
    id: 'run_mock_002',
    status: 'failed',
    started_at: nowIso(),
    finished_at: nowIso(),
    summary: 'One or more checks failed.',
    inputs: { manifest: '{"example":true}' },
    artifacts: [
      {
        path: 'evidence.txt',
        contentType: 'text/plain',
        content: 'Mock evidence: checksum mismatch at offset 0x10.',
      },
    ],
  },
  {
    id: 'run_mock_001',
    status: 'queued',
    started_at: nowIso(),
    summary: 'Queued for execution.',
    inputs: {},
    artifacts: [],
  },
]

const store: RunStoreRecord[] = structuredClone(initialStore)

export function resetMockStore() {
  counter = 4
  store.length = 0
  store.push(...structuredClone(initialStore))
}

export function listMockRuns(): RunRecord[] {
  return store
    .slice()
    .sort((a, b) => b.started_at.localeCompare(a.started_at))
    .map(({ artifacts: _artifacts, ...run }) => run)
}

export function getMockRun(runId: string): RunDetails | undefined {
  const found = store.find((r) => r.id === runId)
  if (!found) return undefined
  const { artifacts, ...run } = found
  return {
    ...run,
    artifacts: artifacts.map((a) => ({
      path: a.path,
      contentType: a.contentType,
    })),
  }
}

export function listMockArtifacts(runId: string): ArtifactEntry[] {
  const found = store.find((r) => r.id === runId)
  if (!found) return []
  return found.artifacts.map((a: ArtifactFileResponse): ArtifactEntry => ({
    path: a.path,
    contentType: a.contentType,
  }))
}

export function getMockArtifactFile(
  runId: string,
  path: string,
): ArtifactFileResponse | undefined {
  const found = store.find((r) => r.id === runId)
  if (!found) return undefined
  return found.artifacts.find(
    (a: ArtifactFileResponse): boolean => a.path === path,
  )
}

export function addMockRun(params: {
  status: RunStatus
  summary?: string
  inputs?: RunDetails['inputs']
  artifacts?: ArtifactStoreEntry[]
}): RunStoreRecord {
  counter += 1
  const id = `run_mock_${String(counter).padStart(3, '0')}`
  const started_at = nowIso()

  const record: RunStoreRecord = {
    id,
    status: params.status,
    started_at,
    finished_at: params.status === 'running' || params.status === 'queued' ? undefined : nowIso(),
    summary: params.summary,
    inputs: params.inputs,
    artifacts: params.artifacts ?? [],
  }

  store.unshift(record)
  return record
}
