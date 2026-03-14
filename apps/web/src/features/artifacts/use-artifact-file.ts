import { useQuery } from '@tanstack/react-query'
import { getArtifactFile } from '@/api/artifacts'
import type { ArtifactFileResponse } from '@/types/artifact'
import { queryKeys } from '@/lib/query-keys'

export function useArtifactFile(runId: string, path: string) {
  return useQuery<ArtifactFileResponse, Error>({
    queryKey: queryKeys.artifactFile(runId, path),
    queryFn: () => getArtifactFile(runId, path),
    enabled: Boolean(runId) && Boolean(path),
  })
}
