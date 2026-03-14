export type VerifyRequest = {
  path?: string
  manifest?: string
}

export type VerifyResponse = {
  status: 'PASS' | 'FAIL'
  run_id?: string
  summary?: string
}

