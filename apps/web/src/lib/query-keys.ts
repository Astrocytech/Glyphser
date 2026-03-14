export const queryKeys = {
  runs: ['runs'] as const,
  run: (id: string) => ['runs', id] as const,
  artifacts: (runId: string) => ['artifacts', runId] as const,
  artifactFile: (runId: string, path: string) =>
    ['artifacts', runId, 'file', path] as const,
} as const

