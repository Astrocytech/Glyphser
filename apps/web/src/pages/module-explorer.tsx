import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { api } from '@/api/client'

const REPO_MODULES = [
  { name: 'glyphser/public', description: 'Public package surfaces', category: 'glyphser' },
  { name: 'glyphser/internal', description: 'Internal implementation', category: 'glyphser' },
  { name: 'runtime/glyphser/api', description: 'Runtime API service', category: 'runtime' },
  { name: 'runtime/glyphser/backend', description: 'Runtime backend', category: 'runtime' },
  { name: 'runtime/glyphser/cert', description: 'Certification module', category: 'runtime' },
  { name: 'runtime/glyphser/checkpoint', description: 'Checkpoint management', category: 'runtime' },
  { name: 'runtime/glyphser/config', description: 'Configuration', category: 'runtime' },
  { name: 'runtime/glyphser/contract', description: 'Contract definitions', category: 'runtime' },
  { name: 'runtime/glyphser/security', description: 'Security module', category: 'runtime' },
  { name: 'runtime/glyphser/trace', description: 'Trace handling', category: 'runtime' },
  { name: 'specs/contracts', description: 'Contract specifications', category: 'specs' },
  { name: 'tests/api', description: 'API tests', category: 'tests' },
  { name: 'tests/commands', description: 'Commands tests', category: 'tests' },
  { name: 'tooling/commands', description: 'Tooling commands', category: 'tooling' },
]

const CATEGORIES = ['all', 'glyphser', 'runtime', 'specs', 'tests', 'tooling'] as const

export default function ModuleExplorerPage() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string>('all')
  const [selectedModule, setSelectedModule] = useState<string | null>(null)
  const [moduleFiles, setModuleFiles] = useState<Array<{ name: string; is_dir: boolean }>>([])
  const [loading, setLoading] = useState(false)

  const filtered = REPO_MODULES.filter((m) => {
    const matchesSearch = m.name.toLowerCase().includes(search.toLowerCase()) || m.description.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = category === 'all' || m.category === category
    return matchesSearch && matchesCategory
  })

  const handleSelectModule = async (moduleName: string) => {
    setSelectedModule(moduleName)
    setLoading(true)
    try {
      const response = await api<{ entries: Array<{ name: string; is_dir: boolean }> }>(`/explorer/list?root=repo&path=${encodeURIComponent(moduleName)}`)
      setModuleFiles(response.entries || [])
    } catch {
      setModuleFiles([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Repository Index</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input placeholder="Search modules..." value={search} onChange={(e) => setSearch(e.target.value)} />

            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => (
                <Badge key={cat} variant={category === cat ? 'default' : 'outline'} className="cursor-pointer" onClick={() => setCategory(cat)}>
                  {cat}
                </Badge>
              ))}
            </div>

            <div className="space-y-2 max-h-[400px] overflow-auto">
              {filtered.map((module) => (
                <div key={module.name} className={`cursor-pointer rounded-md border p-3 transition-colors ${selectedModule === module.name ? 'border-primary bg-primary/10' : 'hover:bg-accent'}`} onClick={() => handleSelectModule(module.name)}>
                  <div className="font-mono text-sm">{module.name}</div>
                  <div className="text-sm text-muted-foreground">{module.description}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{selectedModule ? <span className="font-mono">{selectedModule}</span> : 'Select a module'}</CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedModule ? (
              <p className="text-muted-foreground">Click a module to view its contents.</p>
            ) : loading ? (
              <p>Loading...</p>
            ) : moduleFiles.length === 0 ? (
              <p className="text-muted-foreground">No files found or module not accessible.</p>
            ) : (
              <div className="space-y-2">
                {moduleFiles.map((file) => (
                  <div key={file.name} className="flex items-center justify-between rounded-md border p-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-xs">{file.is_dir ? 'DIR' : 'FILE'}</Badge>
                      <span className="font-mono text-sm">{file.name}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
