import { api } from './client'

export interface JobSubmitRequest {
  payload: Record<string, unknown>
  token: string
  scope: string
  idempotency_key?: string
}

export interface JobSubmitResponse {
  job_id: string
  trace_id?: string
  accepted: boolean
}

export interface JobStatusRequest {
  job_id: string
  token: string
  scope: string
}

export interface JobStatusResponse {
  status: string
  state?: string
}

export interface JobEvidenceRequest {
  job_id: string
  token: string
  scope: string
}

export interface JobEvidenceResponse {
  conformance?: string
  bundle_hash?: string
  evidence_files?: string[]
}

export interface JobReplayRequest {
  job_id: string
  token: string
  scope: string
}

export interface JobReplayResponse {
  eligible: boolean
  verdict?: string
  reason?: string
}

export interface JobsStateResponse {
  state_path: string
  exists: boolean
  jobs: Array<{
    job_id: string
    status: string
    trace_id?: string
    api_version?: string
  }>
  quotas: Record<string, unknown>
}

export async function submitJob(request: JobSubmitRequest): Promise<JobSubmitResponse> {
  return api<JobSubmitResponse>('/runtime/jobs/submit', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function getJobStatus(request: JobStatusRequest): Promise<JobStatusResponse> {
  return api<JobStatusResponse>('/runtime/jobs/status', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function getJobEvidence(request: JobEvidenceRequest): Promise<JobEvidenceResponse> {
  return api<JobEvidenceResponse>('/runtime/jobs/evidence', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function replayJob(request: JobReplayRequest): Promise<JobReplayResponse> {
  return api<JobReplayResponse>('/runtime/jobs/replay', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function getJobsState(): Promise<JobsStateResponse> {
  return api<JobsStateResponse>('/runtime/jobs/state')
}
