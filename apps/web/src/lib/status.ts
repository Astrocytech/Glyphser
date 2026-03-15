import { badgeVariants } from '@/components/ui/badge'
import type { VariantProps } from 'class-variance-authority'

export type BadgeVariant = VariantProps<typeof badgeVariants>['variant']

export type VerdictStatus = 'PASS' | 'FAIL' | 'WARN' | 'MATCH' | 'MISMATCH' | 'SKIP'

export type RunStatus = 'queued' | 'running' | 'passed' | 'failed' | 'partial' | 'unknown'

export function getVerdictLabel(status: string): string {
  switch (status) {
    case 'PASS':
      return 'Pass'
    case 'FAIL':
      return 'Fail'
    case 'WARN':
      return 'Warning'
    case 'MATCH':
      return 'Match'
    case 'MISMATCH':
      return 'Mismatch'
    case 'SKIP':
      return 'Skipped'
    default:
      return status
  }
}

export function getVerdictVariant(status: string): BadgeVariant {
  switch (status) {
    case 'PASS':
    case 'MATCH':
      return 'default'
    case 'FAIL':
    case 'MISMATCH':
      return 'destructive'
    case 'WARN':
      return 'secondary'
    case 'SKIP':
    case 'unknown':
      return 'outline'
    default:
      return 'outline'
  }
}

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
