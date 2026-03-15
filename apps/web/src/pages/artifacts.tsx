import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useRuns } from '@/features/runs/use-runs'
import { runStatusBadgeVariant, runStatusLabel } from '@/lib/status'
import LoadingState from '@/components/state/loading-state'
import ErrorState from '@/components/state/error-state'
import { FolderOpen } from 'lucide-react'

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export default function ArtifactsPage() {
  const runs = useRuns()

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="h-5 w-5" />
            Runs with Artifacts
          </CardTitle>
        </CardHeader>
        <CardContent>
          {runs.isLoading ? (
            <LoadingState label="Loading runs..." />
          ) : runs.isError ? (
            <ErrorState message={runs.error.message} onRetry={() => runs.refetch()} />
          ) : runs.data?.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              No runs yet. Start a verification to generate artifacts.
            </p>
          ) : (
            <div className="space-y-2">
              {runs.data?.map((run) => (
                <Link
                  key={run.id}
                  to={`/artifacts/${encodeURIComponent(run.id)}`}
                  className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-accent"
                >
                  <div className="space-y-1">
                    <div className="font-mono text-sm">{run.id}</div>
                    <div className="text-xs text-muted-foreground">{run.summary || 'No summary'}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{formatRelativeTime(run.started_at)}</span>
                    <Badge variant={runStatusBadgeVariant(run.status)}>{runStatusLabel(run.status)}</Badge>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
