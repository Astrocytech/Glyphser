import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/api/client'

const DOC_CATEGORIES = [
  { name: 'Getting Started', slug: 'START-HERE.md', description: 'Where to begin' },
  { name: 'Getting Started', slug: 'GETTING_STARTED.md', description: 'Quick start guide' },
  { name: 'Reference', slug: 'DOCS_INDEX.md', description: 'Documentation index' },
  { name: 'Reference', slug: 'DIAGRAMS.md', description: 'Architecture diagrams' },
  { name: 'Reference', slug: 'README.md', description: 'Project readme' },
  { name: 'Contributing', slug: 'CONTRIBUTING.md', description: 'Contribution guide' },
]

export default function DocsPage() {
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const [docContent, setDocContent] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const handleSelectDoc = async (slug: string) => {
    setSelectedDoc(slug)
    setLoading(true)
    try {
      const response = await api<{ content: string }>(`/explorer/read?root=docs&path=${encodeURIComponent(slug)}`)
      setDocContent(response.content || '')
    } catch {
      try {
        const response = await api<{ content: string }>(`/explorer/read?root=repo&path=${encodeURIComponent(`docs/${slug}`)}`)
        setDocContent(response.content || '')
      } catch {
        setDocContent('# Document not found\n\nThe selected document could not be loaded.')
      }
    } finally {
      setLoading(false)
    }
  }

  const groupedDocs = DOC_CATEGORIES.reduce((acc, doc) => {
    if (!acc[doc.name]) acc[doc.name] = []
    acc[doc.name].push(doc)
    return acc
  }, {} as Record<string, typeof DOC_CATEGORIES>)

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="grid gap-6 lg:grid-cols-[0.75fr_1.25fr]">
        <Card>
          <CardHeader>
            <CardTitle>Docs Index</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(groupedDocs).map(([category, docs]) => (
              <div key={category}>
                <div className="text-sm font-medium text-muted-foreground mb-2">{category}</div>
                <div className="space-y-2">
                  {docs.map((doc) => (
                    <div key={doc.slug} className={`cursor-pointer rounded-md border p-3 transition-colors ${selectedDoc === doc.slug ? 'border-primary bg-primary/10' : 'hover:bg-accent'}`} onClick={() => handleSelectDoc(doc.slug)}>
                      <div className="font-medium">{doc.slug.replace('.md', '').replace(/_/g, ' ')}</div>
                      <div className="text-sm text-muted-foreground">{doc.description}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{selectedDoc ? <span className="font-mono text-sm">{selectedDoc}</span> : 'Select a document'}</CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedDoc ? (
              <p className="text-muted-foreground">Select a document to read.</p>
            ) : loading ? (
              <p>Loading...</p>
            ) : (
              <pre className="max-h-[500px] overflow-auto whitespace-pre-wrap text-sm">{docContent}</pre>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
