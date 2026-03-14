import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { runCertify, type CertifyResponse } from '@/api/runtime-cli'

const PROFILES = ['available_local', 'available_local_partial', 'strict_universal']

export default function CertifyPage() {
  const [profile, setProfile] = useState('available_local')
  const [runId, setRunId] = useState('')
  const [result, setResult] = useState<CertifyResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async () => {
    setLoading(true)
    try {
      const res = await runCertify({ profile, run_id: runId || undefined })
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
            <CardTitle>Certification Builder</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Profile / Scope</label>
              <div className="flex flex-wrap gap-2">
                {PROFILES.map((p) => (
                  <Badge key={p} variant={profile === p ? 'default' : 'outline'} className="cursor-pointer" onClick={() => setProfile(p)}>
                    {p}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Run ID (optional)</label>
              <Input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="Link to specific run" />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Required Evidence</label>
              <div className="space-y-2 text-sm text-muted-foreground">
                <div>- Setup lock (profile.lock.json)</div>
                <div>- Route decision (route_decision.json)</div>
                <div>- Verification outputs</div>
              </div>
            </div>

            <Button onClick={handleRun} disabled={loading}>
              {loading ? 'Running...' : 'Generate Certification'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Bundle Review</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Generated Artifacts</label>
              <div className="space-y-2">
                <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-sm">certification-scope.json</div>
                <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-sm">compatibility-matrix.json</div>
                <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-sm">certification-bundle.json</div>
                <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-sm">signature-verification.json</div>
                <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-sm">bundle-signature.asc</div>
                <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-sm">claim-language-check.json</div>
              </div>
            </div>

            {result && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant={result.status === 'PASS' ? 'default' : 'destructive'}>{result.status}</Badge>
                </div>
                <pre className="max-h-64 overflow-auto rounded-md bg-muted p-3 text-xs font-mono">{JSON.stringify(result.bundle, null, 2)}</pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
