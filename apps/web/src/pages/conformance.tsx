import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const CONFORMANCE_GATES = [
  { gate: 'Interface hash', verdict: 'PASS', note: 'Matches contract' },
  { gate: 'Artifact integrity', verdict: 'PASS', note: 'Digest set complete' },
  { gate: 'Manifest consistency', verdict: 'PASS', note: 'No missing bindings' },
  { gate: 'Trace completeness', verdict: 'WARN', note: '1 advisory gap' },
  { gate: 'Replay verdict', verdict: 'PASS', note: 'Stable against reference' },
  { gate: 'Golden comparison', verdict: 'PASS', note: 'Expected == actual' },
]

export default function ConformancePage() {
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Tabs defaultValue="gates">
        <TabsList>
          <TabsTrigger value="gates">Gate Matrix</TabsTrigger>
          <TabsTrigger value="determinism">Determinism</TabsTrigger>
          <TabsTrigger value="replay">Replay</TabsTrigger>
          <TabsTrigger value="golden">Golden Comparison</TabsTrigger>
        </TabsList>

        <TabsContent value="gates">
          <Card>
            <CardHeader>
              <CardTitle>Conformance Gates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-hidden rounded-md border">
                <table className="w-full">
                  <thead>
                    <tr className="bg-muted">
                      <th className="px-4 py-3 text-left text-sm font-medium">Gate</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Verdict</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {CONFORMANCE_GATES.map((gate) => (
                      <tr key={gate.gate} className="border-t">
                        <td className="px-4 py-3">{gate.gate}</td>
                        <td className="px-4 py-3">
                          <Badge variant={gate.verdict === 'PASS' ? 'default' : gate.verdict === 'FAIL' ? 'destructive' : 'outline'}>
                            {gate.verdict}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{gate.note}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="determinism">
          <Card>
            <CardHeader>
              <CardTitle>Determinism Checks</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { check: 'Same input → Same output', status: 'PASS', details: 'Deterministic across 10 runs' },
                  { check: 'Same input → Same digest', status: 'PASS', details: 'SHA256 matches' },
                  { check: 'Random seed handling', status: 'PASS', details: 'No non-deterministic sources' },
                ].map((item) => (
                  <div key={item.check} className="flex items-center justify-between rounded-md border p-4">
                    <div>
                      <div className="font-medium">{item.check}</div>
                      <div className="text-sm text-muted-foreground">{item.details}</div>
                    </div>
                    <Badge variant="default">{item.status}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="replay">
          <Card>
            <CardHeader>
              <CardTitle>Replay Verdicts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-hidden rounded-md border">
                <table className="w-full">
                  <thead>
                    <tr className="bg-muted">
                      <th className="px-4 py-3 text-left text-sm font-medium">Run ID</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Original</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Replayed</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { runId: 'run-001', original: 'PASS', replayed: 'PASS', verdict: 'MATCH' },
                      { runId: 'run-002', original: 'PASS', replayed: 'PASS', verdict: 'MATCH' },
                    ].map((result) => (
                      <tr key={result.runId} className="border-t">
                        <td className="px-4 py-3 font-mono text-sm">{result.runId}</td>
                        <td className="px-4 py-3"><Badge variant="default">{result.original}</Badge></td>
                        <td className="px-4 py-3"><Badge variant="default">{result.replayed}</Badge></td>
                        <td className="px-4 py-3"><Badge variant="outline">{result.verdict}</Badge></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="golden">
          <Card>
            <CardHeader>
              <CardTitle>Expected vs Actual Golden</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { artifact: 'checkpoint_header.json', expected: 'sha256:abc123', actual: 'sha256:abc123', status: 'MATCH' },
                  { artifact: 'execution_certificate.json', expected: 'sha256:def456', actual: 'sha256:def456', status: 'MATCH' },
                ].map((comp) => (
                  <div key={comp.artifact} className="rounded-md border p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-mono text-sm">{comp.artifact}</div>
                      <Badge variant="default">{comp.status}</Badge>
                    </div>
                    <div className="grid gap-2 text-sm">
                      <div className="flex justify-between"><span className="text-muted-foreground">Expected:</span><span className="font-mono">{comp.expected}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Actual:</span><span className="font-mono">{comp.actual}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
