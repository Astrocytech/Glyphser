import EmptyState from '@/components/state/empty-state'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Configure backend endpoints and console behavior.
        </p>
      </div>
      <EmptyState title="Settings not implemented" message="This page will be wired after the API contract stabilizes." />
    </div>
  )
}
