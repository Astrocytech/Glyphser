export type RunStatus =
  | 'queued'
  | 'running'
  | 'passed'
  | 'failed'
  | 'partial'
  | 'unknown'

export type RunRecord = {
  id: string
  status: RunStatus
  started_at: string
  finished_at?: string
  summary?: string
}

export type RunDetails = RunRecord & {
  inputs?: {
    path?: string
    manifest?: string
  }
  artifacts?: {
    path: string
    contentType?: string
  }[]
}

export type RunDetail = RunDetails
