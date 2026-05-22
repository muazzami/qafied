import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { api } from '../lib/api'
import { useWorkspaceStore } from '../store/workspace'
import type { Workspace } from '../types'

export function WorkspaceSwitcher() {
  const { currentWorkspaceId, setCurrentWorkspaceId } = useWorkspaceStore()

  const { data: workspaces = [], isLoading } = useQuery<Workspace[]>({
    queryKey: ['workspaces'],
    queryFn: async () => (await api.get('/workspaces/')).data,
  })

  useEffect(() => {
    if (!currentWorkspaceId && workspaces.length > 0) {
      setCurrentWorkspaceId(workspaces[0].id)
    }
  }, [workspaces, currentWorkspaceId, setCurrentWorkspaceId])

  if (isLoading) return <div className="text-sm text-muted-foreground">Loading…</div>

  if (workspaces.length === 0) {
    return <div className="text-sm text-muted-foreground">No workspaces yet</div>
  }

  return (
    <select
      className="rounded-md border border-input bg-background px-3 py-2 text-sm"
      value={currentWorkspaceId ?? ''}
      onChange={(e) => setCurrentWorkspaceId(Number(e.target.value))}
    >
      {workspaces.map((w) => (
        <option key={w.id} value={w.id}>
          {w.name}
        </option>
      ))}
    </select>
  )
}
