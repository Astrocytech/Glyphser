import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface Settings {
  apiUrl: string
  useMockApi: boolean
  darkMode: boolean
  autoRefresh: boolean
  refreshInterval: number
}

const DEFAULT_SETTINGS: Settings = {
  apiUrl: 'http://localhost:8000',
  useMockApi: false,
  darkMode: false,
  autoRefresh: true,
  refreshInterval: 30,
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('glyphser-settings')
    if (stored) {
      try {
        setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(stored) })
      } catch {
        // ignore parse errors
      }
    }
  }, [])

  const handleSave = () => {
    localStorage.setItem('glyphser-settings', JSON.stringify(settings))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS)
    localStorage.removeItem('glyphser-settings')
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
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the console look and feel</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="darkMode"
              checked={settings.darkMode}
              onChange={(e) => updateSetting('darkMode', e.target.checked)}
              className="h-4 w-4"
            />
            <label htmlFor="darkMode" className="text-sm font-medium">Dark Mode</label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Data Refresh</CardTitle>
          <CardDescription>Configure automatic data refresh</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="autoRefresh"
              checked={settings.autoRefresh}
              onChange={(e) => updateSetting('autoRefresh', e.target.checked)}
              className="h-4 w-4"
            />
            <label htmlFor="autoRefresh" className="text-sm font-medium">Auto Refresh</label>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Refresh Interval (seconds)</label>
            <Input
              type="number"
              min={5}
              max={300}
              value={settings.refreshInterval}
              onChange={(e) => updateSetting('refreshInterval', parseInt(e.target.value) || 30)}
              disabled={!settings.autoRefresh}
            />
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
