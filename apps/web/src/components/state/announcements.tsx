import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Announcement {
  id: string
  title: string
  message: string
  date: string
}

const ANNOUNCEMENTS: Announcement[] = [
  { id: '1', title: 'New Feature: Favorites', message: 'You can now star runs to keep them at the top!', date: '2026-03-14' },
  { id: '2', title: 'Dark Mode Support', message: 'The app now respects your system dark mode preference.', date: '2026-03-13' },
]

export function Announcements() {
  const [dismissed, setDismissed] = useState<string[]>(() => {
    const saved = localStorage.getItem('glyphser-dismissed-announcements')
    return saved ? JSON.parse(saved) : []
  })

  const visible = ANNOUNCEMENTS.filter(a => !dismissed.includes(a.id))

  const dismiss = (id: string) => {
    const newDismissed = [...dismissed, id]
    setDismissed(newDismissed)
    localStorage.setItem('glyphser-dismissed-announcements', JSON.stringify(newDismissed))
  }

  if (visible.length === 0) return null

  return (
    <div className="space-y-2">
      {visible.map(ann => (
        <div key={ann.id} className="flex items-center justify-between bg-muted/50 rounded-lg p-3 border">
          <div>
            <div className="font-medium text-sm">{ann.title}</div>
            <div className="text-xs text-muted-foreground">{ann.message}</div>
          </div>
          <Button variant="ghost" size="icon-sm" onClick={() => dismiss(ann.id)}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  )
}