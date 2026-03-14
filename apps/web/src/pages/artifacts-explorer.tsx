import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import LoadingState from '@/components/state/loading-state'
import ErrorState from '@/components/state/error-state'
import EmptyState from '@/components/state/empty-state'
import { useArtifacts } from '@/features/artifacts/use-artifacts'
import { useArtifactFile } from '@/features/artifacts/use-artifact-file'
import FileViewer from '@/features/artifacts/components/file-viewer'

export default function ArtifactsExplorerPage() {
  const { runId = '' } = useParams()
  const [filter, setFilter] = useState('')
  const [selectedPath, setSelectedPath] = useState<string>('')

  const artifacts = useArtifacts(runId)

  const filtered = useMemo(() => {
    const list = artifacts.data ?? []
    const q = filter.trim().toLowerCase()
    if (!q) return list
    return list.filter((e) => e.path.toLowerCase().includes(q))
  }, [artifacts.data, filter])

  const file = useArtifactFile(runId, selectedPath)

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <h1 className="truncate text-2xl font-semibold tracking-tight">
            Artifacts <span className="font-mono">/ {runId}</span>
          </h1>
          <p className="text-sm text-muted-foreground">
            Browse produced files for this run.
          </p>
        </div>
        <Link className="text-sm text-muted-foreground hover:underline" to={`/runs/${encodeURIComponent(runId)}`}>
          Back to run
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-[320px_1fr]">
        <Card className="min-h-[420px]">
          <CardHeader>
            <CardTitle>Files</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input
              placeholder="Filter…"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />

            {artifacts.isLoading ? <LoadingState label="Loading artifacts…" /> : null}
            {artifacts.isError ? (
              <ErrorState
                message={artifacts.error.message}
                onRetry={() => artifacts.refetch()}
              />
            ) : null}
            {artifacts.data && filtered.length === 0 ? (
              <EmptyState title="No files" message="No artifacts match your filter." />
            ) : null}

            {filtered.length > 0 ? (
              <ScrollArea className="h-[300px] rounded-md border">
                <div className="p-2">
                  {filtered.map((e) => {
                    const active = e.path === selectedPath
                    return (
                      <button
                        key={e.path}
                        type="button"
                        onClick={() => setSelectedPath(e.path)}
                        className={[
                          'w-full rounded-md px-2 py-1 text-left text-sm font-mono transition-colors',
                          active
                            ? 'bg-primary text-primary-foreground'
                            : 'hover:bg-accent hover:text-accent-foreground',
                        ].join(' ')}
                      >
                        {e.path}
                      </button>
                    )
                  })}
                </div>
              </ScrollArea>
            ) : null}
          </CardContent>
        </Card>

        <Card className="min-h-[420px]">
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedPath ? <FileViewer file={null} /> : null}

            {selectedPath && file.isLoading ? <LoadingState label="Loading file…" /> : null}
            {selectedPath && file.isError ? (
              <ErrorState message={file.error.message} onRetry={() => file.refetch()} />
            ) : null}

            {selectedPath && file.data ? (
              <div className="space-y-2">
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium">Type:</span> {file.data.contentType}
                </div>
                <FileViewer file={file.data} />
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
