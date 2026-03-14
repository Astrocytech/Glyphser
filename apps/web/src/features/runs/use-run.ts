import { useQuery } from '@tanstack/react-query'
import { getRun } from '@/api/runs'
import type { RunDetails } from '@/types/run'
import { queryKeys } from '@/lib/query-keys'

export function useRun(runId: string) {
  return useQuery<RunDetails, Error>({
    queryKey: queryKeys.run(runId),
    queryFn: () => getRun(runId),
    enabled: Boolean(runId),
  })
}
