import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { runDoctor, type DoctorResponse } from '@/api/runtime-cli'
import { getVerdictVariant, getVerdictLabel } from '@/lib/status'

export default function DoctorPage() {
  const [runId, setRunId] = useState('')
  const [result, setResult] = useState<DoctorResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    try {
      const res = await runDoctor({ run_id: runId || undefined })
      setResult(res)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const capabilities = result?.manifest?.capabilities as Record<string, boolean> | undefined

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Run Doctor</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Run ID (optional)</label>
            <Input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="Enter run ID for workspace naming" />
          </div>

          <Button onClick={handleRun} disabled={loading}>
            {loading ? 'Running...' : 'Run Doctor'}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Doctor Manifest</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant={getVerdictVariant(result.status)}>{getVerdictLabel(result.status)}</Badge>
                <Badge variant="outline">{result.classification}</Badge>
              </div>

              <pre className="max-h-64 overflow-auto rounded-md bg-muted p-4 text-xs font-mono">
                {JSON.stringify(result.manifest, null, 2)}
              </pre>
            </CardContent>
          </Card>

          {capabilities && (
            <Card>
              <CardHeader>
                <CardTitle>Capability Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="rounded-md border p-4">
                    <div className="text-sm text-muted-foreground">Python</div>
                    <div className="mt-2 text-2xl font-semibold">{capabilities.python_version ? 'Available' : 'N/A'}</div>
                  </div>
                  <div className="rounded-md border p-4">
                    <div className="text-sm text-muted-foreground">PyTorch</div>
                    <div className="mt-2 text-2xl font-semibold">{capabilities.torch_present ? 'Available' : 'Not found'}</div>
                  </div>
                  <div className="rounded-md border p-4">
                    <div className="text-sm text-muted-foreground">GPU</div>
                    <div className="mt-2 text-2xl font-semibold">{capabilities.gpu_present ? 'Available' : 'Not found'}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
