import { create } from 'zustand'

/**
 * Zustand store cho trang thai UI chung
 * Sidebar, theme, global loading, modal state
 */
export const useUiStore = create((set) => ({
  // Sidebar state
  sidebarOpen: true,
  sidebarCollapsed: false,

  // Global loading overlay
  globalLoading: false,

  // Toggle sidebar (mobile)
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Collapse sidebar (desktop - chi hien icon)
  toggleSidebarCollapse: () => set((state) => ({ 
    sidebarCollapsed: !state.sidebarCollapsed 
  })),

  // Global loading
  setGlobalLoading: (loading) => set({ globalLoading: loading }),

  // Reset
  reset: () => set({
    sidebarOpen: true,
    sidebarCollapsed: false,
    globalLoading: false
  })
}))

export default useUiStore
