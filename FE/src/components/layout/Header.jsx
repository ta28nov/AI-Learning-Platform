import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '@stores/authStore'
import GlobalSearchBar from '@components/search/GlobalSearchBar'

/**
 * Dashboard Header — sticky top bar.
 * Receives onMenuClick from DashboardLayout to toggle sidebar via uiStore.
 */
const Header = ({ onMenuClick }) => {
  const { user } = useAuthStore()
  const initial = user?.full_name?.charAt(0)?.toUpperCase() || 'U'

  return (
    <header className="dashboard-header" role="banner">
      {/* Hamburger — shown only on mobile via CSS */}
      <button
        className="sidebar-toggle"
        onClick={onMenuClick}
        aria-label="Mở sidebar"
        aria-expanded="false"
      >
        <MenuIcon />
      </button>

      {/* Global search */}
      <div className="header-content">
        <GlobalSearchBar />
      </div>

      {/* Right actions */}
      <div className="header-actions">
        <motion.div
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.96 }}
          transition={{ type: 'spring', stiffness: 400, damping: 28 }}
        >
          <Link
            to="/dashboard/profile"
            className="profile-link"
            aria-label={`Hồ sơ của ${user?.full_name || 'bạn'}`}
          >
            <div className="user-avatar header-avatar" aria-hidden="true">
              {initial}
            </div>
          </Link>
        </motion.div>
      </div>
    </header>
  )
}

const MenuIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <line x1="3" y1="6" x2="21" y2="6" />
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
)

export default Header
