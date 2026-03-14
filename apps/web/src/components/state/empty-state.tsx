export default function EmptyState({
  title = 'Nothing here yet',
  message = 'No results to show.',
}: {
  title?: string
  message?: string
}) {
  return (
    <div className="rounded-lg border bg-card p-10 text-center">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{message}</p>
    </div>
  )
}
