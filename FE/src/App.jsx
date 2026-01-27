import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import AppRouter from './AppRouter'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from 'react-hot-toast'

/**
 * Component App chinh - diem dau vao cua ung dung
 * Chua cac Provider va Router
 */
function App() {
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