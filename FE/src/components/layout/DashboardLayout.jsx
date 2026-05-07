import React from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import { useUiStore } from '@stores/uiStore'
import Sidebar from './Sidebar'
import Header from './Header'
import MobileDrawer from './MobileDrawer'
import PageTransition from './PageTransition'
import './DashboardLayout.css'

/**
 * DashboardLayout — shell for all authenticated /dashboard/* routes.
 *
 * Architecture (Phase 3 refactor):
 *   DashboardLayout (orchestrator)
 *     ├── Sidebar          (desktop fixed sidebar + mobile slide-in)
 *     ├── MobileDrawer     (backdrop overlay for mobile)
 *     └── .dashboard-main
 *           ├── Header     (sticky top bar)
 *           └── PageTransition → <Outlet /> (cinematic page-turn)
 *
 * uiStore replaces local useState for sidebarOpen — single source of truth.
 * AppRouter.jsx import path is unchanged; this component is still the default export.
 */
const DashboardLayout = () => {
  const navigate = useNavigate()
  const { logout } = useAuthStore()
  const { sidebarOpen, setSidebarOpen, toggleSidebar } = useUiStore()

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/auth/login')
    } catch {
      // Logout errors are non-critical; navigate regardless
      navigate('/auth/login')
    }
  }

  return (
    <div className="dashboard-layout">
      {/* Sidebar — always in DOM; CSS controls visibility on mobile */}
      <Sidebar onLogout={handleLogout} />

      {/* Mobile backdrop overlay — AnimatePresence-animated */}
      <MobileDrawer
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main panel */}
      <div className="dashboard-main">
        <Header onMenuClick={toggleSidebar} />

        <main className="dashboard-content" id="main-content" tabIndex={-1}>
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
