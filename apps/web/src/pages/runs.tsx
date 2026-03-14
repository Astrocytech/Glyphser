import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import EmptyState from '@/components/state/empty-state'
import ErrorState from '@/components/state/error-state'
import LoadingState from '@/components/state/loading-state'
import { useRuns } from '@/features/runs/use-runs'
import { runStatusBadgeVariant, runStatusLabel } from '@/lib/status'

export default function RunsPage() {
  const runs = useRuns()

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Runs</h1>
        <p className="text-sm text-muted-foreground">
          Recent verification runs across artifacts and manifests.
        </p>
      </div>

      {runs.isLoading ? <LoadingState label="Loading runs…" /> : null}

      {runs.isError ? (
        <ErrorState message={runs.error.message} onRetry={() => runs.refetch()} />
      ) : null}

      {runs.data && runs.data.length === 0 ? (
        <EmptyState
          title="No runs yet"
          message="When you run a verification, it will appear here."
        />
      ) : null}

      {runs.data && runs.data.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Recent runs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {runs.data.map((run) => (
              <Link
                key={run.id}
                to={`/runs/${encodeURIComponent(run.id)}`}
                className="block rounded-md border p-3 transition-colors hover:bg-accent/40"
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="truncate font-mono text-sm">{run.id}</span>
                      <Badge variant={runStatusBadgeVariant(run.status)}>
                        {runStatusLabel(run.status)}
                      </Badge>
                    </div>
                    {run.summary ? (
                      <p className="mt-1 text-sm text-muted-foreground">
                        {run.summary}
                      </p>
                    ) : null}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <span className="font-medium">Started:</span>{' '}
                    {new Date(run.started_at).toLocaleString()}
                  </div>
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
