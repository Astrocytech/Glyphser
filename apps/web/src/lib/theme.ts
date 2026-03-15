import { useEffect } from 'react'

export function useTheme() {
  useEffect(() => {
    const stored = localStorage.getItem('glyphser-settings')
    let darkMode = false
    
    if (stored) {
      try {
        const settings = JSON.parse(stored)
        darkMode = settings.darkMode ?? false
      } catch {
        darkMode = false
      }
    }

    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [])
}
