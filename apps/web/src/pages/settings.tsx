import { useState, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Info, RefreshCw, Trash2 } from 'lucide-react'
import { toast } from '@/lib/toast'

interface Settings {
  apiUrl: string
  useMockApi: boolean
}

const DEFAULT_SETTINGS: Settings = {
  apiUrl: 'http://localhost:8000',
  useMockApi: false,
}

const APP_VERSION = '1.0.0'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('glyphser-settings')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setSettings({
          apiUrl: parsed.apiUrl ?? DEFAULT_SETTINGS.apiUrl,
          useMockApi: parsed.useMockApi ?? DEFAULT_SETTINGS.useMockApi,
        })
      } catch {
        // ignore parse errors
      }
    }
  }, [])

  const handleSave = () => {
    const stored = localStorage.getItem('glyphser-settings')
    const existing = stored ? JSON.parse(stored) : {}
    localStorage.setItem('glyphser-settings', JSON.stringify({ ...existing, ...settings }))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS)
    const stored = localStorage.getItem('glyphser-settings')
    if (stored) {
      const parsed = JSON.parse(stored)
      delete parsed.apiUrl
      delete parsed.useMockApi
      localStorage.setItem('glyphser-settings', JSON.stringify(parsed))
    }
  }

  const handleClearCache = async () => {
    await queryClient.clear()
    toast({ title: 'Cache cleared', description: 'All cached data has been cleared.', variant: 'success' })
  }

  const updateSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
          <CardDescription>Configure the backend API endpoint</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">API Base URL</label>
            <Input
              value={settings.apiUrl}
              onChange={(e) => updateSetting('apiUrl', e.target.value)}
              placeholder="http://localhost:8000"
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useMockApi"
              checked={settings.useMockApi}
              onChange={(e) => updateSetting('useMockApi', e.target.checked)}
              className="h-4 w-4"
            />
            <label htmlFor="useMockApi" className="text-sm font-medium">Use Mock API</label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Cache & Data
          </CardTitle>
          <CardDescription>Manage cached data</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={handleClearCache}>
            <Trash2 className="h-4 w-4 mr-2" />
            Clear Query Cache
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-4 w-4" />
            About
          </CardTitle>
          <CardDescription>Application information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Version</span>
            <span>{APP_VERSION}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Framework</span>
            <span>React + Vite</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">UI Library</span>
            <span>Shadcn/UI</span>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-4">
        <Button onClick={handleSave}>{saved ? 'Saved!' : 'Save Settings'}</Button>
        <Button variant="outline" onClick={handleReset}>Reset to Defaults</Button>
      </div>
    </div>
  )
}
