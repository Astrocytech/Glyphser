import EmptyState from '@/components/state/empty-state'

export default function ArtifactsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Artifacts</h1>
        <p className="text-sm text-muted-foreground">
          Browse files produced by verification runs.
        </p>
      </div>
      <EmptyState
        title="Choose a run"
        message="Open a run details page and click “Open explorer”."
      />
    </div>
  )
}
