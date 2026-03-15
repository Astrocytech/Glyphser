import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { runSetup, type SetupResponse } from '@/api/runtime-cli'
import { getVerdictVariant, getVerdictLabel } from '@/lib/status'

const PROFILES = ['available_local', 'available_local_partial', 'strict_universal']

export default function SetupPage() {
  const [profile, setProfile] = useState('available_local')
  const [doctorRunId, setDoctorRunId] = useState('')
  const [dryRun, setDryRun] = useState(true)
  const [offline, setOffline] = useState(false)
  const [maxRetries, setMaxRetries] = useState(1)
  const [timeoutSec, setTimeoutSec] = useState(300)
  const [result, setResult] = useState<SetupResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    try {
      const res = await runSetup({
        profile,
        doctor_run_id: doctorRunId || undefined,
        dry_run: dryRun,
        offline,
        max_retries: maxRetries,
        timeout_sec: timeoutSec,
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
            <CardTitle>Setup Configuration</CardTitle>
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

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Max Retries</label>
                <Input type="number" value={maxRetries} onChange={(e) => setMaxRetries(parseInt(e.target.value) || 1)} min={0} max={10} />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Timeout (seconds)</label>
                <Input type="number" value={timeoutSec} onChange={(e) => setTimeoutSec(parseInt(e.target.value) || 300)} min={60} max={3600} />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} className="rounded border-input" />
                <span className="text-sm">Dry Run</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={offline} onChange={(e) => setOffline(e.target.checked)} className="rounded border-input" />
                <span className="text-sm">Offline</span>
              </label>
            </div>

            <Button onClick={handleRun} disabled={loading}>
              {loading ? 'Running...' : dryRun ? 'Dry Run' : 'Apply Setup'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Generated Outputs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Generated Artifacts</label>
              <div className="space-y-2">
                <div className="rounded-md border border-violet-500/30 bg-violet-500/10 p-3 font-mono text-sm">setup-plan.json</div>
                <div className="rounded-md border border-violet-500/30 bg-violet-500/10 p-3 font-mono text-sm">profile.lock.json</div>
                <div className="rounded-md border border-violet-500/30 bg-violet-500/10 p-3 font-mono text-sm">rollback-plan.json</div>
              </div>
            </div>

            {result && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={getVerdictVariant(result.status)}>{getVerdictLabel(result.status)}</Badge>
                  <Badge variant="outline">{result.classification}</Badge>
                </div>
                <pre className="max-h-48 overflow-auto rounded-md bg-muted p-3 text-xs font-mono">{JSON.stringify(result, null, 2)}</pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
