import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RefreshCw } from 'lucide-react'
import EmptyState from '@/components/state/empty-state'
import ErrorState from '@/components/state/error-state'
import LoadingState from '@/components/state/loading-state'
import { useRun } from '@/features/runs/use-run'
import { runStatusBadgeVariant, runStatusLabel } from '@/lib/status'

export default function RunDetailsPage() {
  const { runId = '' } = useParams()
  const run = useRun(runId)

  useEffect(() => {
    if (run.data?.status === 'running' || run.data?.status === 'queued') {
      const interval = setInterval(() => run.refetch(), 5000)
      return () => clearInterval(interval)
    }
  }, [run.data?.status, run.refetch])

  if (run.isLoading) return <LoadingState label="Loading run…" />
  if (run.isError)
    return <ErrorState message={run.error.message} onRetry={() => run.refetch()} />
  if (!run.data) return <EmptyState title="Run not found" message="No data returned." />

  const data = run.data

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h1 className="truncate text-2xl font-semibold tracking-tight">
            Run <span className="font-mono">{data.id}</span>
          </h1>
          <p className="text-sm text-muted-foreground">
            Details for a single verification run.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={runStatusBadgeVariant(data.status)}>
            {runStatusLabel(data.status)}
          </Badge>
          <Button variant="outline" size="sm" onClick={() => run.refetch()} disabled={run.isFetching}>
            <RefreshCw className={`h-4 w-4 mr-2 ${run.isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button asChild variant="secondary">
            <Link to="/runs">Back to runs</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>
              <span className="font-medium">Status:</span> {runStatusLabel(data.status)}
            </div>
            <div>
              <span className="font-medium">Started:</span>{' '}
              {new Date(data.started_at).toLocaleString()}
            </div>
            {data.finished_at ? (
              <div>
                <span className="font-medium">Finished:</span>{' '}
                {new Date(data.finished_at).toLocaleString()}
              </div>
            ) : null}
            {data.summary ? (
              <div>
                <span className="font-medium">Summary:</span> {data.summary}
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Inputs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {data.inputs?.path ? (
              <div>
                <span className="font-medium">Path:</span>{' '}
                <span className="font-mono">{data.inputs.path}</span>
              </div>
            ) : null}
            {data.inputs?.manifest ? (
              <div>
                <span className="font-medium">Manifest:</span>{' '}
                <span className="font-mono">{data.inputs.manifest}</span>
              </div>
            ) : (
              <p className="text-muted-foreground">No manifest provided.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Artifacts</CardTitle>
          <Button asChild variant="secondary">
            <Link to={`/artifacts/${encodeURIComponent(data.id)}`}>Open explorer</Link>
          </Button>
        </CardHeader>
        <CardContent className="text-sm">
          {data.artifacts && data.artifacts.length > 0 ? (
            <ul className="space-y-2">
              {data.artifacts.map((a) => (
                <li key={a.path} className="flex items-center justify-between rounded-md border p-2">
                  <span className="font-mono">{a.path}</span>
                  <span className="text-muted-foreground">{a.contentType ?? '—'}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No artifacts recorded for this run yet.</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

