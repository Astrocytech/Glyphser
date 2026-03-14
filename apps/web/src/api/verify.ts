import { api } from './client'
import { addMockRun, listMockArtifacts } from '@/api/mock/store'
import type { VerifyRequest, VerifyResponse } from '@/types/verify'

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function mockVerify(payload: VerifyRequest): Promise<VerifyResponse> {
  await sleep(600)

  const looksValid = Boolean(payload.path || payload.manifest)

  const run = addMockRun({
    status: looksValid ? 'passed' : 'failed',
    summary: looksValid
      ? 'Mock verification completed successfully.'
      : 'No artifact path or manifest was provided.',
    inputs: { path: payload.path, manifest: payload.manifest },
    artifacts: [
      {
        path: 'request.json',
        contentType: 'application/json',
        content: JSON.stringify(payload, null, 2),
      },
      {
        path: 'result.json',
        contentType: 'application/json',
        content: JSON.stringify(
          {
            status: looksValid ? 'PASS' : 'FAIL',
            run_id: 'pending',
            summary: looksValid
              ? 'Mock verification completed successfully.'
              : 'No artifact path or manifest was provided.',
          },
          null,
          2,
        ),
      },
    ],
  })

  const artifacts = listMockArtifacts(run.id)

  return {
    status: looksValid ? 'PASS' : 'FAIL',
    run_id: run.id,
    summary: looksValid
      ? `Mock verification completed successfully. Produced ${artifacts.length} artifacts.`
      : 'No artifact path or manifest was provided.',
  }
}

export function postVerify(payload: VerifyRequest) {
  if (import.meta.env.VITE_USE_MOCK_API === 'true') {
    return mockVerify(payload)
  }

  return api<VerifyResponse>('/verify', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
