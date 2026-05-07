import React, { useEffect } from 'react'
import { BrowserRouter, useLocation } from 'react-router-dom'
import AppRouter from './AppRouter'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from 'react-hot-toast'
import toast from 'react-hot-toast'
import ErrorBoundary from '@components/system/ErrorBoundary'
import appLogger from '@utils/logger'
import MagneticCursor from '@components/layout/MagneticCursor'
import Footer from '@components/layout/Footer'

/**
 * Component App chinh - diem dau vao cua ung dung
 * Chua cac Provider va Router
 */
function App() {
  // Lắng nghe sự kiện session hết hạn từ api.js interceptor
  useEffect(() => {
    const handleSessionExpired = () => {
      toast.error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', {
        duration: 5000,
        id: 'session-expired' // tránh duplicate toast
      })
    }
    window.addEventListener('auth:session-expired', handleSessionExpired)
    return () => window.removeEventListener('auth:session-expired', handleSessionExpired)
  }, [])

  useEffect(() => {
    const handleWindowError = (event) => {
      appLogger.error(event?.error || new Error(event?.message || 'Runtime error'), {
        source: 'window.error'
      })
    }
    const handleUnhandledRejection = (event) => {
      appLogger.error(event?.reason || new Error('Unhandled promise rejection'), {
        source: 'window.unhandledrejection'
      })
    }
    window.addEventListener('error', handleWindowError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)
    return () => {
      window.removeEventListener('error', handleWindowError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [])

  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </ThemeProvider>
  )
}

/**
 * AppShell — inner component so it can use Router hooks (useLocation).
 * Renders Footer only on public routes (outside /dashboard/*).
 */
function AppShell() {
  const location = useLocation()
  const { pathname } = location
  const isDashboard = pathname.startsWith('/dashboard')
  // Landing page has its own rich footer — only show generic Footer on auth/error routes
  const showGenericFooter = !isDashboard && pathname !== '/'

  return (
    <div className="app">
      <ErrorBoundary>
        <AppRouter />
      </ErrorBoundary>

      {/* Generic editorial footer — auth & error pages only (landing has its own) */}
      {showGenericFooter && <Footer />}

      {/* Custom cursor — pointer:fine devices only (handled inside component) */}
      <MagneticCursor />

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
          },
        }}
      />
    </div>
  )
}

export default App