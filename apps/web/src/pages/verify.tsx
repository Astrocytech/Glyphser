import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import ErrorState from '@/components/state/error-state'
import { useVerify } from '@/features/verify/use-verify'

const MAX_PATH_CHARS = 2048
const MAX_MANIFEST_CHARS = 100_000

export default function VerifyPage() {
  const [path, setPath] = useState('')
  const [manifest, setManifest] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)
  const verify = useVerify()

  const onSubmit = () => {
    const trimmedPath = path.trim()
    const trimmedManifest = manifest.trim()

    if (!trimmedPath && !trimmedManifest) {
      setValidationError('Provide at least an artifact path/run ID or a manifest payload.')
      return
    }

    if (trimmedPath.length > MAX_PATH_CHARS) {
      setValidationError(`Path is too long (max ${MAX_PATH_CHARS} characters).`)
      return
    }

    if (trimmedManifest.length > MAX_MANIFEST_CHARS) {
      setValidationError(
        `Manifest/payload is too large (max ${MAX_MANIFEST_CHARS.toLocaleString()} characters).`,
      )
      return
    }

    setValidationError(null)
    verify.mutate({
      path: trimmedPath || undefined,
      manifest: trimmedManifest || undefined,
    })
  }

  const result = verify.data

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Verification Request</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Artifact path or run ID"
            value={path}
            onChange={(e) => setPath(e.target.value)}
          />
          <Textarea
            placeholder="Paste manifest or verification JSON here..."
            className="min-h-56"
            value={manifest}
            onChange={(e) => setManifest(e.target.value)}
          />
          <div className="flex justify-end">
            <Button onClick={onSubmit} disabled={verify.isPending}>
              {verify.isPending ? 'Running…' : 'Run verification'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {validationError ? <ErrorState title="Invalid request" message={validationError} /> : null}

      {verify.isError ? <ErrorState message={verify.error.message} /> : null}

      {result ? (
        <Card>
          <CardHeader>
            <CardTitle>Verification Result</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Badge
              variant={result.status === 'PASS' ? 'default' : 'destructive'}
            >
              {result.status}
            </Badge>
            {result.run_id ? (
              <p className="text-sm">
                <span className="font-medium">Run ID:</span> {result.run_id}
              </p>
            ) : null}
            {result.summary ? (
              <p className="text-sm text-muted-foreground">{result.summary}</p>
            ) : null}
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
