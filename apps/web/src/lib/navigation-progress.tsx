import { useEffect, useState, useRef } from 'react'
import { useLocation } from 'react-router-dom'

export function NavigationProgress() {
  const location = useLocation()
  const [progress, setProgress] = useState(0)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setProgress(20)
    
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    
    timeoutRef.current = setTimeout(() => {
      setProgress(80)
      setTimeout(() => setProgress(0), 150)
    }, 100)

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [location.pathname])

  if (progress === 0) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-[9999] h-1 bg-transparent">
      <div 
        className="h-full bg-primary transition-all duration-300 ease-out"
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}