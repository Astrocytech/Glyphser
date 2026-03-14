import { api } from './client'

export interface DoctorRequest {
  run_id?: string
}

export interface DoctorResponse {
  status: string
  classification: string
  profile: string
  run_id: string
  manifest: Record<string, unknown>
  manifest_path: string
  manifest_sha256: string
}

export interface SetupRequest {
  profile: string
  doctor_run_id?: string
  doctor_manifest?: Record<string, unknown>
  dry_run: boolean
  offline: boolean
  max_retries: number
  timeout_sec: number
  run_id?: string
}

export interface SetupResponse {
  run_id: string
  result_path: string
  plan_path: string
  status: string
  classification: string
  failed_actions: string[]
}

export interface RouteRunRequest {
  profile?: string
  doctor_run_id?: string
  doctor_manifest?: Record<string, unknown>
  run_id?: string
}

export interface RouteRunResponse {
  run_id: string
  route_path: string
  route: Record<string, unknown>
  status: string
  classification: string
}

export interface CertifyRequest {
  profile: string
  run_id?: string
}

export interface CertifyResponse {
  run_id: string
  status: string
  out_dir: string
  bundle: Record<string, unknown>
}

export async function runDoctor(request: DoctorRequest): Promise<DoctorResponse> {
  return api<DoctorResponse>('/runtime/cli/doctor', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function runSetup(request: SetupRequest): Promise<SetupResponse> {
  return api<SetupResponse>('/runtime/cli/setup', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function runRouteRun(request: RouteRunRequest): Promise<RouteRunResponse> {
  return api<RouteRunResponse>('/runtime/cli/run', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function runCertify(request: CertifyRequest): Promise<CertifyResponse> {
  return api<CertifyResponse>('/runtime/cli/certify', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
