import { useMutation, useQueryClient } from '@tanstack/react-query'
import { postVerify } from '@/api/verify'
import { queryKeys } from '@/lib/query-keys'
import type { VerifyRequest, VerifyResponse } from '@/types/verify'

export function useVerify() {
  const queryClient = useQueryClient()

  return useMutation<VerifyResponse, Error, VerifyRequest>({
    mutationFn: postVerify,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.runs })
    },
  })
}
