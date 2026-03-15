import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import EmptyState from '@/components/state/empty-state'
import ErrorState from '@/components/state/error-state'
import { SkeletonList } from '@/components/state/skeleton'
import { useRuns } from '@/features/runs/use-runs'
import { runStatusBadgeVariant, runStatusLabel } from '@/lib/status'
import { Search } from 'lucide-react'

type StatusFilter = 'all' | 'passed' | 'failed' | 'running' | 'queued'

export default function RunsPage() {
  const runs = useRuns()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')

  const filteredRuns = runs.data?.filter((run) => {
    const matchesSearch =
      !search ||
      run.id.toLowerCase().includes(search.toLowerCase()) ||
      run.summary?.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === 'all' || run.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const statusOptions: StatusFilter[] = ['all', 'passed', 'failed', 'running', 'queued']

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by ID or summary..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-1 flex-wrap">
          {statusOptions.map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setStatusFilter(status)}
            >
              {status === 'all' ? 'All' : runStatusLabel(status as 'passed' | 'failed' | 'running' | 'queued')}
            </Button>
          ))}
        </div>
      </div>

      {runs.isError ? (
        <ErrorState message={runs.error.message} onRetry={() => runs.refetch()} />
      ) : null}

      {filteredRuns && filteredRuns.length === 0 && !runs.isLoading ? (
        <EmptyState
          title="No runs found"
          message={search || statusFilter !== 'all' ? "Try adjusting your search or filter." : "When you run a verification, it will appear here."}
        />
      ) : null}

      {filteredRuns && filteredRuns.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Recent runs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {filteredRuns.map((run) => (
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

      {runs.isLoading ? <SkeletonList items={5} /> : null}
    </div>
  )
}
