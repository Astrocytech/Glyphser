export default function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center rounded-lg border bg-card p-10 text-sm text-muted-foreground">
      {label}
    </div>
  )
}
