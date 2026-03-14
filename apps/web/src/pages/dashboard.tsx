import EmptyState from '@/components/state/empty-state'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <EmptyState title="No dashboard widgets yet" message="This area will show KPIs and recent activity." />
    </div>
  )
}
