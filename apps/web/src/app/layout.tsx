import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { navItems } from './nav'
import { Bug, CheckCircle2 } from 'lucide-react'

const isMockMode = import.meta.env.VITE_USE_MOCK_API === 'true'

export default function AppLayout() {
  const location = useLocation()
  const currentItem = navItems.find(
    (item) => item.to === location.pathname || 
      (item.to !== '/' && location.pathname.startsWith(item.to)),
  ) ?? navItems[0]

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen md:grid-cols-[260px_1fr]">
        <aside className="border-r bg-muted/30 p-4 flex flex-col">
          <div className="mb-6">
            <h1 className="text-xl font-semibold">Glyphser</h1>
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

          <div className="mt-4 pt-4 border-t">
            {isMockMode ? (
              <div className="flex items-center gap-2 text-xs text-amber-600">
                <Bug className="h-3 w-3" />
                <span>Mock Mode</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-xs text-green-600">
                <CheckCircle2 className="h-3 w-3" />
                <span>Live API</span>
              </div>
            )}
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
    </div>
  )
}
