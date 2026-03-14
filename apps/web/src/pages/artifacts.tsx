import EmptyState from '@/components/state/empty-state'

export default function ArtifactsPage() {
  return (
    <div className="space-y-6">
      <EmptyState
        title="Choose a run"
        message="Open a run details page and click 'Open explorer'."
      />
    </div>
  )
}
