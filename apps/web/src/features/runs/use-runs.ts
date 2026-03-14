import { useQuery } from '@tanstack/react-query'
import { getRuns } from '@/api/runs'
import type { RunRecord } from '@/types/run'
import { queryKeys } from '@/lib/query-keys'

export function useRuns() {
  return useQuery<RunRecord[], Error>({
    queryKey: queryKeys.runs,
    queryFn: getRuns,
  })
}
