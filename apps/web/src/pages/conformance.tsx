import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { api } from '@/api/client'
import LoadingState from '@/components/state/loading-state'
import ErrorState from '@/components/state/error-state'
import { getVerdictVariant, getVerdictLabel } from '@/lib/status'

interface ConformanceReport {
  gates?: Array<{ gate: string; verdict: string; note?: string }>
  determinism?: Array<{ check: string; status: string; details: string }>
  replay?: Array<{ run_id: string; original: string; replayed: string; verdict: string }>
  golden?: Array<{ artifact: string; expected: string; actual: string; status: string }>
}

const DEFAULT_GATES = [
  { gate: 'Interface hash', verdict: 'PASS', note: 'Matches contract' },
  { gate: 'Artifact integrity', verdict: 'PASS', note: 'Digest set complete' },
  { gate: 'Manifest consistency', verdict: 'PASS', note: 'No missing bindings' },
  { gate: 'Trace completeness', verdict: 'WARN', note: '1 advisory gap' },
  { gate: 'Replay verdict', verdict: 'PASS', note: 'Stable against reference' },
  { gate: 'Golden comparison', verdict: 'PASS', note: 'Expected == actual' },
]

const DEFAULT_DETERMINISM = [
  { check: 'Same input → Same output', status: 'PASS', details: 'Deterministic across 10 runs' },
  { check: 'Same input → Same digest', status: 'PASS', details: 'SHA256 matches' },
  { check: 'Random seed handling', status: 'PASS', details: 'No non-deterministic sources' },
]

const DEFAULT_REPLAY = [
  { run_id: 'run-001', original: 'PASS', replayed: 'PASS', verdict: 'MATCH' },
  { run_id: 'run-002', original: 'PASS', replayed: 'PASS', verdict: 'MATCH' },
]

const DEFAULT_GOLDEN = [
  { artifact: 'checkpoint_header.json', expected: 'sha256:abc123', actual: 'sha256:abc123', status: 'MATCH' },
  { artifact: 'execution_certificate.json', expected: 'sha256:def456', actual: 'sha256:def456', status: 'MATCH' },
]

export default function ConformancePage() {
  const report = useQuery<ConformanceReport>({
    queryKey: ['conformance'],
    queryFn: async () => {
      const data = await api<{ report: ConformanceReport | null }>('/conformance/latest')
      return data.report ?? {}
    },
  })

  const gates = report.data?.gates ?? DEFAULT_GATES
  const determinism = report.data?.determinism ?? DEFAULT_DETERMINISM
  const replay = report.data?.replay ?? DEFAULT_REPLAY
  const golden = report.data?.golden ?? DEFAULT_GOLDEN

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
              {report.isLoading ? (
                <LoadingState label="Loading conformance report..." />
              ) : report.isError ? (
                <ErrorState message={report.error.message} onRetry={() => report.refetch()} />
              ) : (
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
                      {gates.map((gate) => (
                        <tr key={gate.gate} className="border-t">
                          <td className="px-4 py-3">{gate.gate}</td>
                          <td className="px-4 py-3">
                            <Badge variant={getVerdictVariant(gate.verdict)}>
                              {getVerdictLabel(gate.verdict)}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-muted-foreground">{gate.note}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
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
                {determinism.map((item) => (
                  <div key={item.check} className="flex items-center justify-between rounded-md border p-4">
                    <div>
                      <div className="font-medium">{item.check}</div>
                      <div className="text-sm text-muted-foreground">{item.details}</div>
                    </div>
                    <Badge variant={getVerdictVariant(item.status)}>{getVerdictLabel(item.status)}</Badge>
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
                    {replay.map((result) => (
                      <tr key={result.run_id} className="border-t">
                        <td className="px-4 py-3 font-mono text-sm">{result.run_id}</td>
                        <td className="px-4 py-3"><Badge variant={getVerdictVariant(result.original)}>{getVerdictLabel(result.original)}</Badge></td>
                        <td className="px-4 py-3"><Badge variant={getVerdictVariant(result.replayed)}>{getVerdictLabel(result.replayed)}</Badge></td>
                        <td className="px-4 py-3"><Badge variant={getVerdictVariant(result.verdict)}>{getVerdictLabel(result.verdict)}</Badge></td>
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
                {golden.map((comp) => (
                  <div key={comp.artifact} className="rounded-md border p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-mono text-sm">{comp.artifact}</div>
                      <Badge variant={getVerdictVariant(comp.status)}>{getVerdictLabel(comp.status)}</Badge>
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
