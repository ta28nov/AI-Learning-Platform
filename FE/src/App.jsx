import React, { useEffect } from 'react'
import { BrowserRouter } from 'react-router-dom'
import AppRouter from './AppRouter'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from 'react-hot-toast'
import toast from 'react-hot-toast'

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

  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="app">
          {/* Router chinh cua ung dung */}
          <AppRouter />
          
          {/* Toast notifications */}
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)'
              }
            }}
          />
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App