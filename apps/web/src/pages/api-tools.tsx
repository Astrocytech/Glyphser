import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { api } from '@/api/client'

const ERROR_CODES = ['AUTH_MISSING', 'AUTH_INVALID', 'SCOPE_MISSING', 'RATE_LIMIT_EXCEEDED', 'REPLAY_COOLDOWN_ACTIVE', 'LOCKDOWN_BLOCKED', 'PAYLOAD_LIMIT_EXCEEDED']

const API_TOOLS_TABS = ['Signature Validator', 'Error Classifier'] as const

export default function ApiToolsPage() {
  const [activeTab, setActiveTab] = useState<string>('Signature Validator')

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          {API_TOOLS_TABS.map((tab) => (<TabsTrigger key={tab} value={tab}>{tab}</TabsTrigger>))}
        </TabsList>

        <TabsContent value="Signature Validator">
          <SignatureValidatorPanel />
        </TabsContent>

        <TabsContent value="Error Classifier">
          <ErrorClassifierPanel />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function SignatureValidatorPanel() {
  const [record, setRecord] = useState('{"operator_id": "train.mnist", "surface": "runtime_api"}')
  const [allowedOps, setAllowedOps] = useState('')
  const [result, setResult] = useState<{ status: string } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleValidate = async () => {
    try {
      setError(null)
      const res = await api<{ status: string }>('/runtime/api-tools/validate-signature', {
        method: 'POST',
        body: JSON.stringify({ record: JSON.parse(record), allowed_ops: allowedOps ? JSON.parse(allowedOps) : undefined }),
      })
      setResult(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Validation failed')
      setResult(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Signature Validator</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">Record (JSON)</label>
            <Textarea value={record} onChange={(e) => setRecord(e.target.value)} rows={8} className="font-mono text-xs" placeholder='{"operator_id": "train.mnist", "surface": "runtime_api"}' />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Allowed Operations (JSON, optional)</label>
            <Textarea value={allowedOps} onChange={(e) => setAllowedOps(e.target.value)} rows={8} className="font-mono text-xs" placeholder='["train.*", "infer.*"]' />
          </div>
        </div>

        <Button onClick={handleValidate}>Validate Signature</Button>

        {error && <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>}

        {result && (
          <div className="rounded-md bg-muted p-4">
            <Badge variant="default">Valid</Badge>
            <pre className="mt-2 text-xs font-mono">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ErrorClassifierPanel() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<{ code: string } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleClassify = async () => {
    try {
      setError(null)
      const res = await api<{ code: string }>('/runtime/api-tools/classify-error', {
        method: 'POST',
        body: JSON.stringify({ message }),
      })
      setResult(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Classification failed')
      setResult(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Runtime Error Classifier</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Error Message</label>
          <Input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Enter error message to classify" />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Known Error Codes</label>
          <div className="flex flex-wrap gap-2">
            {ERROR_CODES.map((code) => (<Badge key={code} variant="outline" className="font-mono">{code}</Badge>))}
          </div>
        </div>

        <Button onClick={handleClassify}>Classify Error</Button>

        {error && <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>}

        {result && (
          <div className="rounded-md bg-muted p-4">
            <Badge variant="default">{result.code}</Badge>
            <pre className="mt-2 text-xs font-mono">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
