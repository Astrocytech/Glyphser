import EmptyState from '@/components/state/empty-state'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Overview of verification activity.
        </p>
      </div>
      <EmptyState title="No dashboard widgets yet" message="This area will show KPIs and recent activity." />
    </div>
  )
}
