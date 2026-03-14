import { NavLink, Outlet } from 'react-router-dom'
import { navItems } from './nav'

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen md:grid-cols-[260px_1fr]">
        <aside className="border-r bg-muted/30 p-4">
          <div className="mb-6">
            <h1 className="text-xl font-semibold">Glyphser</h1>
            <p className="text-sm text-muted-foreground">
              Verification Console
            </p>
          </div>

          <nav className="space-y-1">
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
        </aside>

        <div className="flex min-h-screen flex-col">
          <header className="border-b px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium">Console</h2>
                <p className="text-sm text-muted-foreground">
                  Deterministic execution and verification
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
