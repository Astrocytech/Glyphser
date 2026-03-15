import { useMutation, useQueryClient } from '@tanstack/react-query'
import { postVerify } from '@/api/verify'
import { queryKeys } from '@/lib/query-keys'
import { toast } from '@/lib/toast'
import type { VerifyRequest, VerifyResponse } from '@/types/verify'

export function useVerify() {
  const queryClient = useQueryClient()

  return useMutation<VerifyResponse, Error, VerifyRequest>({
    mutationFn: postVerify,
    onMutate: () => {
      toast({
        title: 'Verification started',
        description: 'Running verification...',
        variant: 'default',
      })
    },
    onSuccess: async (data) => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.runs })
      toast({
        title: 'Verification complete',
        description: `Status: ${data.status}`,
        variant: data.status === 'passed' ? 'success' : 'destructive',
      })
    },
    onError: (error) => {
      toast({
        title: 'Verification failed',
        description: error.message,
        variant: 'destructive',
      })
    },
  })
}
