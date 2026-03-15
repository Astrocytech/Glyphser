import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface Settings {
  apiUrl: string
  useMockApi: boolean
  darkMode: boolean
}

const DEFAULT_SETTINGS: Settings = {
  apiUrl: 'http://localhost:8000',
  useMockApi: false,
  darkMode: false,
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
    setSettings((prev) => {
      const newSettings = { ...prev, [key]: value }
      
      if (key === 'darkMode') {
        if (value) {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
      }
      
      return newSettings
    })
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

      <div className="flex gap-4">
        <Button onClick={handleSave}>{saved ? 'Saved!' : 'Save Settings'}</Button>
        <Button variant="outline" onClick={handleReset}>Reset to Defaults</Button>
      </div>
    </div>
  )
}
