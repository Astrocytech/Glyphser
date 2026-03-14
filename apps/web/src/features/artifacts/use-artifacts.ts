import { useQuery } from '@tanstack/react-query'
import { getArtifacts } from '@/api/artifacts'
import type { ArtifactEntry } from '@/types/artifact'
import { queryKeys } from '@/lib/query-keys'

export function useArtifacts(runId: string) {
  return useQuery<ArtifactEntry[], Error>({
    queryKey: queryKeys.artifacts(runId),
    queryFn: () => getArtifacts(runId),
    enabled: Boolean(runId),
  })
}
