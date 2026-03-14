import { Button } from '@/components/ui/button'

export default function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
}: {
  title?: string
  message?: string
  onRetry?: () => void
}) {
  return (
    <div className="rounded-lg border bg-card p-6">
      <div className="space-y-1">
        <h3 className="text-base font-semibold">{title}</h3>
        {message ? (
          <p className="text-sm text-destructive">{message}</p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Please try again in a moment.
          </p>
        )}
      </div>

      {onRetry ? (
        <div className="mt-4">
          <Button variant="secondary" onClick={onRetry}>
            Retry
          </Button>
        </div>
      ) : null}
    </div>
  )
}
