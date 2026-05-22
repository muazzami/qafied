import { Button } from '../components/ui/button'
import { WorkspaceSwitcher } from '../components/WorkspaceSwitcher'
import { useAuthStore } from '../store/auth'

export default function Dashboard() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold tracking-tight text-gray-900">Qafied</h1>
            <WorkspaceSwitcher />
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={logout}>
              Sign out
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <h2 className="text-xl font-semibold text-gray-900">Welcome back</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Add a website to start collecting visual feedback.
        </p>
      </main>
    </div>
  )
}
