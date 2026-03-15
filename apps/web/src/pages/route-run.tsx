import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { runRouteRun, type RouteRunResponse } from '@/api/runtime-cli'
import { getVerdictVariant, getVerdictLabel } from '@/lib/status'

const PROFILES = ['auto', 'available_local', 'available_local_partial', 'strict_universal']

export default function RouteRunPage() {
  const [profile, setProfile] = useState('auto')
  const [doctorRunId, setDoctorRunId] = useState('')
  const [runId, setRunId] = useState('')
  const [result, setResult] = useState<RouteRunResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    try {
      const res = await runRouteRun({
        profile: profile === 'auto' ? 'auto' : profile,
        doctor_run_id: doctorRunId || undefined,
        run_id: runId || undefined,
      })
      setResult(res)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Route Decision</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Profile</label>
              <div className="flex flex-wrap gap-2">
                {PROFILES.map((p) => (
                  <Badge key={p} variant={profile === p ? 'default' : 'outline'} className="cursor-pointer" onClick={() => setProfile(p)}>
                    {p}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Doctor Run ID (optional)</label>
              <Input value={doctorRunId} onChange={(e) => setDoctorRunId(e.target.value)} placeholder="Use existing doctor manifest" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Run ID (optional)</label>
              <Input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="Custom run ID" />
            </div>

            <Button onClick={handleRun} disabled={loading}>
              {loading ? 'Running...' : 'Determine Route'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Route Decision Output</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Generated Files</label>
              <div className="space-y-2">
                <div className="rounded-md border border-sky-500/30 bg-sky-500/10 p-3 font-mono text-sm">route_decision.json</div>
                <div className="rounded-md border border-sky-500/30 bg-sky-500/10 p-3 font-mono text-sm">route-policy-hash.json</div>
                <div className="rounded-md border border-sky-500/30 bg-sky-500/10 p-3 font-mono text-sm">fallback-policy.json</div>
                <div className="rounded-md border border-sky-500/30 bg-sky-500/10 p-3 font-mono text-sm">route-replay-check.json</div>
              </div>
            </div>

            {result && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={getVerdictVariant(result.status)}>{getVerdictLabel(result.status)}</Badge>
                  <Badge variant="outline">{result.classification}</Badge>
                </div>
                <pre className="max-h-64 overflow-auto rounded-md bg-muted p-3 text-xs font-mono">{JSON.stringify(result.route, null, 2)}</pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
