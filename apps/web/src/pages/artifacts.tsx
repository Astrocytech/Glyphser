import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useRuns } from '@/features/runs/use-runs'
import { runStatusBadgeVariant, runStatusLabel } from '@/lib/status'
import { useDebounce } from '@/lib/debounce'
import LoadingState from '@/components/state/loading-state'
import ErrorState from '@/components/state/error-state'
import { FolderOpen, Search, ChevronLeft, ChevronRight } from 'lucide-react'

const PAGE_SIZE = 10

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
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [page, setPage] = useState(1)
  const debouncedSearch = useDebounce(search, 300)

  const filteredRuns = useMemo(() => {
    return runs.data?.filter((run) => {
      const matchesSearch =
        !debouncedSearch ||
        run.id.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        run.summary?.toLowerCase().includes(debouncedSearch.toLowerCase())
      const matchesStatus = statusFilter === 'all' || run.status === statusFilter
      return matchesSearch && matchesStatus
    }) ?? []
  }, [runs.data, debouncedSearch, statusFilter])

  const totalPages = Math.ceil(filteredRuns.length / PAGE_SIZE)
  const paginatedRuns = filteredRuns.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleFilterChange = () => {
    setPage(1)
  }

  const statusOptions = ['all', 'passed', 'failed', 'running', 'queued']

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by ID or summary..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="pl-9"
          />
        </div>
        <div className="flex gap-1 flex-wrap">
          {statusOptions.map((status) => (
            <Button
              key={status}
              variant={statusFilter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => { setStatusFilter(status); handleFilterChange(); }}
            >
              {status === 'all' ? 'All' : runStatusLabel(status as 'passed' | 'failed' | 'running' | 'queued')}
            </Button>
          ))}
        </div>
      </div>

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
          ) : filteredRuns.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              {search || statusFilter !== 'all'
                ? "No runs match your search."
                : "No runs yet. Start a verification to generate artifacts."}
            </p>
          ) : (
            <div className="space-y-2">
              {paginatedRuns.map((run) => (
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

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p - 1)}
            disabled={page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p + 1)}
            disabled={page === totalPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
