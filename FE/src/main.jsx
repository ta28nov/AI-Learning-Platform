import React from 'react'
import ReactDOM from 'react-dom/client'
import { MotionConfig } from 'framer-motion'
import App from './App.jsx'
import './styles/index.css'

// Suppress Framer Motion's "Reduced Motion" console.error in dev.
// This fires when the OS "prefers-reduced-motion: reduce" setting is on.
// It is NOT a real error — the app handles reduced motion via useReducedMotion().
// The message is dev-only and disappears in production builds.
if (import.meta.env.DEV) {
  const _origError = console.error.bind(console)
  console.error = (...args) => {
    if (typeof args[0] === 'string' && args[0].includes('Reduced Motion')) return
    _origError(...args)
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MotionConfig reducedMotion="never">
      <App />
    </MotionConfig>
  </React.StrictMode>,
)