import type { ArtifactFileResponse } from '@/types/artifact'
import EmptyState from '@/components/state/empty-state'

function tryFormatJson(text: string) {
  try {
    const parsed = JSON.parse(text)
    return JSON.stringify(parsed, null, 2)
  } catch {
    return null
  }
}

export default function FileViewer({ file }: { file: ArtifactFileResponse | null }) {
  if (!file) {
    return (
      <EmptyState
        title="Select a file"
        message="Choose an artifact to preview it."
      />
    )
  }

  const contentType = file.contentType.toLowerCase()
  const looksJson =
    contentType.includes('application/json') || file.path.endsWith('.json')

  if (looksJson) {
    const formatted = tryFormatJson(file.content)
    return (
      <pre className="max-h-[320px] overflow-auto rounded-md border bg-muted/20 p-3 text-xs leading-relaxed">
        {formatted ?? file.content}
      </pre>
    )
  }

  const looksText =
    contentType.startsWith('text/') ||
    contentType.includes('application/yaml') ||
    file.path.endsWith('.txt') ||
    file.path.endsWith('.log') ||
    file.path.endsWith('.yaml') ||
    file.path.endsWith('.yml')

  if (looksText) {
    return (
      <pre className="max-h-[320px] overflow-auto rounded-md border bg-muted/20 p-3 text-xs leading-relaxed">
        {file.content}
      </pre>
    )
  }

  return (
    <EmptyState
      title="Unsupported preview"
      message={`No viewer for content type: ${file.contentType}`}
    />
  )
}

