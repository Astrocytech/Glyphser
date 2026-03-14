import type { RunStatus } from '@/types/run'

export type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline'

export function runStatusLabel(status: RunStatus): string {
  switch (status) {
    case 'queued':
      return 'Queued'
    case 'running':
      return 'Running'
    case 'passed':
      return 'Passed'
    case 'failed':
      return 'Failed'
    case 'partial':
      return 'Partial'
    case 'unknown':
      return 'Unknown'
    default: {
      const exhaustive: never = status
      return exhaustive
    }
  }
}

export function runStatusBadgeVariant(status: RunStatus): BadgeVariant {
  switch (status) {
    case 'failed':
      return 'destructive'
    case 'passed':
      return 'default'
    case 'queued':
    case 'running':
      return 'secondary'
    case 'partial':
    case 'unknown':
      return 'outline'
    default: {
      const exhaustive: never = status
      return exhaustive
    }
  }
}

