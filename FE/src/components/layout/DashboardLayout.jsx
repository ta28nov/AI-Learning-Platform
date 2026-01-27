import React, { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import './DashboardLayout.css'

/**
 * Component DashboardLayout - Layout chinh cho cac trang dashboard
 * Chua sidebar navigation va header
 */
const DashboardLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuthStore()
  const location = useLocation()
  const navigate = useNavigate()

  // Xu ly dang xuat
  const handleLogout = async () => {
    try {
      await logout()
      navigate('/auth/login')
    } catch (error) {
      console.error('Loi khi dang xuat:', error)
    }
  }

  // Toggle sidebar tren mobile
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  // Dong sidebar khi click menu item tren mobile
  const closeSidebar = () => {
    setSidebarOpen(false)
  }

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`dashboard-sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-logo">AI Learning</h2>
          <button 
            className="sidebar-close"
            onClick={toggleSidebar}
            aria-label="Dong sidebar"
          >
            <CloseIcon />
          </button>
        </div>

        <nav className="sidebar-nav">
          <SidebarNavItem 
            to="/dashboard" 
            icon={<DashboardIcon />}
            label="Tong quan"
            isActive={location.pathname === '/dashboard'}
            onClick={closeSidebar}
          />
          
          <SidebarNavItem 
            to="/courses" 
            icon={<CoursesIcon />}
            label="Khoa hoc"
            isActive={location.pathname.startsWith('/courses')}
            onClick={closeSidebar}
          />
          
          <SidebarNavItem 
            to="/my-courses" 
            icon={<MyCoursesIcon />}
            label="Khoa hoc cua toi"
            isActive={location.pathname.startsWith('/my-courses')}
            onClick={closeSidebar}
          />
          
          <SidebarNavItem 
            to="/quiz" 
            icon={<QuizIcon />}
            label="Bai kiem tra"
            isActive={location.pathname.startsWith('/quiz')}
            onClick={closeSidebar}
          />
          
          <SidebarNavItem 
            to="/chat" 
            icon={<ChatIcon />}
            label="AI Chat"
            isActive={location.pathname.startsWith('/chat')}
            onClick={closeSidebar}
          />
          
          <SidebarNavItem 
            to="/progress" 
            icon={<ProgressIcon />}
            label="Tien do"
            isActive={location.pathname.startsWith('/progress')}
            onClick={closeSidebar}
          />

          {/* Menu danh cho admin */}
          {user?.role === 'admin' && (
            <>
              <div className="sidebar-divider"></div>
              <SidebarNavItem 
                to="/admin" 
                icon={<AdminIcon />}
                label="Quan tri"
                isActive={location.pathname.startsWith('/admin')}
                onClick={closeSidebar}
              />
            </>
          )}

          {/* Menu danh cho giang vien */}
          {(user?.role === 'instructor' || user?.role === 'admin') && (
            <>
              <div className="sidebar-divider"></div>
              <SidebarNavItem 
                to="/instructor" 
                icon={<InstructorIcon />}
                label="Giang day"
                isActive={location.pathname.startsWith('/instructor')}
                onClick={closeSidebar}
              />
            </>
          )}
        </nav>

        {/* User info va logout */}
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="user-details">
              <div className="user-name">{user?.full_name}</div>
              <div className="user-role">{getRoleDisplayName(user?.role)}</div>
            </div>
          </div>
          <Button variant="ghost" onClick={handleLogout} size="sm">
            Dang xuat
          </Button>
        </div>
      </aside>

      {/* Overlay cho mobile */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={closeSidebar}></div>
      )}

      {/* Main content */}
      <div className="dashboard-main">
        {/* Header */}
        <header className="dashboard-header">
          <button 
            className="sidebar-toggle"
            onClick={toggleSidebar}
            aria-label="Mo sidebar"
          >
            <MenuIcon />
          </button>
          
          <div className="header-content">
            <h1 className="page-title">
              {getPageTitle(location.pathname)}
            </h1>
          </div>

          <div className="header-actions">
            <Link to="/profile" className="profile-link">
              <div className="user-avatar">
                {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="dashboard-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

/**
 * Component SidebarNavItem - Item trong sidebar navigation
 */
const SidebarNavItem = ({ to, icon, label, isActive, onClick }) => {
  return (
    <Link 
      to={to} 
      className={`sidebar-nav-item ${isActive ? 'nav-item-active' : ''}`}
      onClick={onClick}
    >
      <span className="nav-item-icon">{icon}</span>
      <span className="nav-item-label">{label}</span>
    </Link>
  )
}

// Helper functions
const getRoleDisplayName = (role) => {
  const roleNames = {
    student: 'Hoc vien',
    instructor: 'Giang vien', 
    admin: 'Quan tri vien'
  }
  return roleNames[role] || 'Nguoi dung'
}

const getPageTitle = (pathname) => {
  const titles = {
    '/dashboard': 'Tong quan',
    '/courses': 'Khoa hoc',
    '/my-courses': 'Khoa hoc cua toi',
    '/quiz': 'Bai kiem tra',
    '/chat': 'AI Chat',
    '/progress': 'Tien do hoc tap',
    '/admin': 'Quan tri he thong',
    '/instructor': 'Quan ly giang day',
    '/profile': 'Thong tin ca nhan'
  }
  
  // Tim title khop nhat
  for (const [path, title] of Object.entries(titles)) {
    if (pathname.startsWith(path)) {
      return title
    }
  }
  
  return 'AI Learning Platform'
}

// Simple SVG Icons
const MenuIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <line x1="3" y1="12" x2="21" y2="12"></line>
    <line x1="3" y1="18" x2="21" y2="18"></line>
  </svg>
)

const CloseIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
)

const DashboardIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="7" height="9"></rect>
    <rect x="14" y="3" width="7" height="5"></rect>
    <rect x="14" y="12" width="7" height="9"></rect>
    <rect x="3" y="16" width="7" height="5"></rect>
  </svg>
)

const CoursesIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
  </svg>
)

const MyCoursesIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
  </svg>
)

const QuizIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M9 11H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h4l3 3 3-3h4a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2h-4l-3-3-3 3z"></path>
    <path d="M9 7H5a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h4l3 3 3-3h4a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-4l-3-3-3 3z"></path>
  </svg>
)

const ChatIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
)

const ProgressIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M12 6v6l4 2"></path>
  </svg>
)

const AdminIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
    <path d="M2 17l10 5 10-5"></path>
    <path d="M2 12l10 5 10-5"></path>
  </svg>
)

const InstructorIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
    <circle cx="9" cy="7" r="4"></circle>
    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
  </svg>
)

export default DashboardLayout