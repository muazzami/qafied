import { create } from 'zustand'

interface WorkspaceState {
  currentWorkspaceId: number | null
  setCurrentWorkspaceId: (id: number | null) => void
}

const STORAGE_KEY = 'currentWorkspaceId'

const stored = localStorage.getItem(STORAGE_KEY)

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  currentWorkspaceId: stored ? Number(stored) : null,
  setCurrentWorkspaceId: (id) => {
    if (id === null) localStorage.removeItem(STORAGE_KEY)
    else localStorage.setItem(STORAGE_KEY, String(id))
    set({ currentWorkspaceId: id })
  },
}))
