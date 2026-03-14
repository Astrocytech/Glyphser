import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useQuery } from '@tanstack/react-query'
import { submitJob, getJobsState, type JobSubmitResponse } from '@/api/jobs'

const JOBS_TABS = ['Submit', 'Status', 'Evidence', 'Replay'] as const

export default function JobsApiPage() {
  const [activeTab, setActiveTab] = useState<string>('Submit')

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          {JOBS_TABS.map((tab) => (
            <TabsTrigger key={tab} value={tab}>
              {tab}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="Submit">
          <SubmitPanel />
        </TabsContent>

        <TabsContent value="Status">
          <StatusPanel />
        </TabsContent>

        <TabsContent value="Evidence">
          <EvidencePanel />
        </TabsContent>

        <TabsContent value="Replay">
          <ReplayPanel />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function SubmitPanel() {
  const [payload, setPayload] = useState('{"example": "data"}')
  const [token, setToken] = useState('')
  const [scope, setScope] = useState('')
  const [idempotencyKey, setIdempotencyKey] = useState('')
  const [result, setResult] = useState<JobSubmitResponse | null>(null)

  const handleSubmit = async () => {
    try {
      const res = await submitJob({
        payload: JSON.parse(payload),
        token,
        scope,
        idempotency_key: idempotencyKey || undefined,
      })
      setResult(res)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Job</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">Payload (JSON)</label>
            <Textarea value={payload} onChange={(e) => setPayload(e.target.value)} rows={6} className="font-mono text-xs" />
          </div>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Token</label>
              <Input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Enter auth token" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Scope</label>
              <Input value={scope} onChange={(e) => setScope(e.target.value)} placeholder="e.g., jobs:write" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Idempotency Key</label>
              <Input value={idempotencyKey} onChange={(e) => setIdempotencyKey(e.target.value)} placeholder="Unique key" />
            </div>
          </div>
        </div>

        <Button onClick={handleSubmit}>Submit Job</Button>

        {result && (
          <div className="rounded-md bg-muted p-4">
            <Badge variant={result.accepted ? 'default' : 'destructive'}>
              {result.accepted ? 'Accepted' : 'Rejected'}
            </Badge>
            <pre className="mt-2 text-xs font-mono">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function StatusPanel() {
  const { data: jobsState } = useQuery({
    queryKey: ['jobsState'],
    queryFn: getJobsState,
    refetchInterval: 5000,
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Status</CardTitle>
      </CardHeader>
      <CardContent>
        {jobsState?.jobs && jobsState.jobs.length > 0 ? (
          <div className="space-y-2">
            {jobsState.jobs.map((job) => (
              <div key={job.job_id} className="flex items-center justify-between rounded-md border p-2">
                <code className="text-sm">{job.job_id}</code>
                <Badge variant="outline">{job.status}</Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No active jobs</p>
        )}
      </CardContent>
    </Card>
  )
}

function EvidencePanel() {
  const [jobId, setJobId] = useState('')

  const { data: jobsState } = useQuery({ queryKey: ['jobsState'], queryFn: getJobsState })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Evidence</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Job ID</label>
          <Input value={jobId} onChange={(e) => setJobId(e.target.value)} placeholder="Select or enter job ID" />
        </div>

        {jobsState?.jobs && (
          <div className="flex flex-wrap gap-2">
            {jobsState.jobs.map((job) => (
              <Badge key={job.job_id} variant={jobId === job.job_id ? 'default' : 'outline'} className="cursor-pointer" onClick={() => setJobId(job.job_id)}>
                {job.job_id}
              </Badge>
            ))}
          </div>
        )}

        <div className="rounded-md bg-muted p-4">
          <p className="text-sm text-muted-foreground">Evidence endpoint returns conformance status, bundle hash, and evidence file list.</p>
        </div>
      </CardContent>
    </Card>
  )
}

function ReplayPanel() {
  const [jobId, setJobId] = useState('')
  const { data: jobsState } = useQuery({ queryKey: ['jobsState'], queryFn: getJobsState })

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Replay</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Job ID</label>
          <Input value={jobId} onChange={(e) => setJobId(e.target.value)} placeholder="Select or enter job ID" />
        </div>

        {jobsState?.jobs && (
          <div className="flex flex-wrap gap-2">
            {jobsState.jobs.map((job) => (
              <Badge key={job.job_id} variant={jobId === job.job_id ? 'default' : 'outline'} className="cursor-pointer" onClick={() => setJobId(job.job_id)}>
                {job.job_id}
              </Badge>
            ))}
          </div>
        )}

        <div className="rounded-md bg-muted p-4">
          <p className="text-sm text-muted-foreground">Replay endpoint checks eligibility, cooldown status, and returns PASS/FAIL verdict.</p>
        </div>
      </CardContent>
    </Card>
  )
}
