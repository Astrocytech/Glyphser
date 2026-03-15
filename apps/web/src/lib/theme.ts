import { useEffect } from 'react'

export function useTheme() {
  useEffect(() => {
    const stored = localStorage.getItem('glyphser-settings')
    let darkMode: boolean | null = null
    
    if (stored) {
      try {
        const settings = JSON.parse(stored)
        darkMode = settings.darkMode ?? null
      } catch {
        darkMode = null
      }
    }

    if (darkMode === null) {
      darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
    }

    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => {
      const stored = localStorage.getItem('glyphser-settings')
      let useSystem = true
      if (stored) {
        try {
          const settings = JSON.parse(stored)
          useSystem = settings.darkMode === undefined || settings.darkMode === null
        } catch {}
      }
      if (useSystem) {
        if (e.matches) {
          document.documentElement.classList.add('dark')
        } else {
          document.documentElement.classList.remove('dark')
        }
      }
    }
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])
}
