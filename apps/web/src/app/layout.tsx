import { useState, useEffect } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { navItems } from './nav'
import { Bug, CheckCircle2 } from 'lucide-react'
import { Switch } from '@/components/ui/switch'
import { Button } from '@/components/ui/button'
import { NavigationProgress } from '@/lib/navigation-progress'
import { BackToTop } from '@/components/state/back-to-top'

function getStoredMockMode(): boolean {
  const stored = localStorage.getItem('glyphser-use-mock-api')
  if (stored !== null) {
    return stored === 'true'
  }
  return import.meta.env.VITE_USE_MOCK_API === 'true'
}

function getStoredDarkMode(): boolean {
  const stored = localStorage.getItem('glyphser-settings')
  if (stored) {
    try {
      const settings = JSON.parse(stored)
      return settings.darkMode ?? false
    } catch {
      return false
    }
  }
  return false
}

export default function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [isMockMode, setIsMockMode] = useState(getStoredMockMode)
  const [isDarkMode, setIsDarkMode] = useState(getStoredDarkMode)
  const [showShortcuts, setShowShortcuts] = useState(false)

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement
      ) {
        return
      }

      if (event.key === '?') {
        event.preventDefault()
        setShowShortcuts(true)
        setTimeout(() => setShowShortcuts(false), 3000)
        return
      }

      if (event.key === '/') {
        event.preventDefault()
        navigate('/runs')
      } else if (event.key === 'v' && !event.ctrlKey && !event.metaKey) {
        event.preventDefault()
        navigate('/verify')
      } else if (event.key === 'd' && !event.ctrlKey && !event.metaKey) {
        event.preventDefault()
        navigate('/')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate])

  const currentItem = navItems.find(
    (item) => item.to === location.pathname || 
      (item.to !== '/' && location.pathname.startsWith(item.to)),
  ) ?? navItems[0]

  return (
    <div className="min-h-screen bg-background text-foreground">
      <NavigationProgress />
      <div className="grid min-h-screen md:grid-cols-[260px_1fr]">
        <aside className="border-r bg-muted/30 p-4 flex flex-col hidden md:block">
          <div className="mb-6">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <span className="text-2xl">𝒢⟦·⟧</span>
              Glyphser
            </h1>
            <p className="text-sm text-muted-foreground">
              Verification Console
            </p>
          </div>

          <nav className="space-y-1 flex-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  [
                    'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-accent hover:text-accent-foreground',
                  ].join(' ')
                }
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="mt-4 pt-4 border-t space-y-4">
            <div className="flex items-center justify-between">
              <button
                onClick={() => {
                  const newValue = !isMockMode
                  setIsMockMode(newValue)
                  localStorage.setItem('glyphser-use-mock-api', String(newValue))
                  window.location.reload()
                }}
                className="flex items-center gap-2 text-xs cursor-pointer hover:opacity-80 transition-opacity"
                aria-label={isMockMode ? 'Switch to live API' : 'Switch to mock mode'}
              >
                {isMockMode ? (
                  <>
                    <Bug className="h-4 w-4 text-amber-600" />
                    <span className="text-amber-600 font-medium">Mock Mode</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-green-600 font-medium">Live API</span>
                  </>
                )}
              </button>
              <Switch
                checked={isMockMode}
                onCheckedChange={(checked) => {
                  setIsMockMode(checked)
                  localStorage.setItem('glyphser-use-mock-api', String(checked))
                  window.location.reload()
                }}
                className="data-[state=checked]:bg-amber-500 data-[state=unchecked]:bg-green-600 h-6 w-11"
                aria-label="Toggle mock mode"
              />
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={() => {
                  const checked = !isDarkMode
                  setIsDarkMode(checked)
                  const stored = localStorage.getItem('glyphser-settings')
                  const settings = stored ? JSON.parse(stored) : {}
                  settings.darkMode = checked
                  localStorage.setItem('glyphser-settings', JSON.stringify(settings))
                  if (checked) {
                    document.documentElement.classList.add('dark')
                  } else {
                    document.documentElement.classList.remove('dark')
                  }
                }}
                className="flex items-center gap-2 text-xs cursor-pointer hover:opacity-80 transition-opacity"
                aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                <span className="font-medium">{isDarkMode ? 'Dark Mode' : 'Light Mode'}</span>
              </button>
              <Switch
                checked={isDarkMode}
                onCheckedChange={(checked) => {
                  setIsDarkMode(checked)
                  const stored = localStorage.getItem('glyphser-settings')
                  const settings = stored ? JSON.parse(stored) : {}
                  settings.darkMode = checked
                  localStorage.setItem('glyphser-settings', JSON.stringify(settings))
                  if (checked) {
                    document.documentElement.classList.add('dark')
                  } else {
                    document.documentElement.classList.remove('dark')
                  }
                }}
                className="data-[state=checked]:bg-gray-300 data-[state=unchecked]:bg-gray-600 dark:data-[state=checked]:bg-gray-400 dark:data-[state=unchecked]:bg-gray-400 h-6 w-11"
                aria-label="Toggle dark mode"
              />
            </div>
          </div>
        </aside>

        <div className="flex min-h-screen flex-col">
          <header className="border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium">{currentItem.title}</h2>
                <p className="text-sm text-muted-foreground">
                  {currentItem.description}
                </p>
              </div>
            </div>
          </header>

          <main className="flex-1 p-6">
            <Outlet />
          </main>
        </div>
      </div>

      {showShortcuts && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-background rounded-lg border p-6 shadow-xl space-y-3">
            <h3 className="font-semibold text-lg">Keyboard Shortcuts</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between gap-8"><span>Dashboard</span><kbd className="bg-muted px-2 py-1 rounded">d</kbd></div>
              <div className="flex justify-between gap-8"><span>Verify</span><kbd className="bg-muted px-2 py-1 rounded">v</kbd></div>
              <div className="flex justify-between gap-8"><span>Runs</span><kbd className="bg-muted px-2 py-1 rounded">/</kbd></div>
              <div className="flex justify-between gap-8"><span>Search/Filter</span><kbd className="bg-muted px-2 py-1 rounded">Ctrl+K</kbd></div>
            </div>
            <p className="text-xs text-muted-foreground text-center mt-4">Press any key to close</p>
          </div>
        </div>
      )}

      <BackToTop />
    </div>
  )
}
