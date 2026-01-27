import React, { createContext, useContext, useReducer, useEffect } from 'react'

/**
 * Theme context va reducer de quan ly dark/light mode
 */

// Initial state
const initialState = {
  theme: 'light', // 'light' hoac 'dark'
  systemTheme: 'light'
}

// Theme actions
const THEME_ACTIONS = {
  SET_THEME: 'SET_THEME',
  SET_SYSTEM_THEME: 'SET_SYSTEM_THEME',
  TOGGLE_THEME: 'TOGGLE_THEME'
}

// Theme reducer
function themeReducer(state, action) {
  switch (action.type) {
    case THEME_ACTIONS.SET_THEME:
      return {
        ...state,
        theme: action.payload
      }
    
    case THEME_ACTIONS.SET_SYSTEM_THEME:
      return {
        ...state,
        systemTheme: action.payload
      }
    
    case THEME_ACTIONS.TOGGLE_THEME:
      return {
        ...state,
        theme: state.theme === 'light' ? 'dark' : 'light'
      }
    
    default:
      return state
  }
}

// Tao context
const ThemeContext = createContext()

/**
 * Theme Provider component
 * @param {Object} props - Props cua component
 * @param {React.ReactNode} props.children - Cac component con
 */
export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState)

  // Khoi tao theme tu localStorage hoac system preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme')
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    
    dispatch({ type: THEME_ACTIONS.SET_SYSTEM_THEME, payload: systemTheme })
    
    if (savedTheme) {
      dispatch({ type: THEME_ACTIONS.SET_THEME, payload: savedTheme })
    } else {
      // Su dung system theme neu chua co setting
      dispatch({ type: THEME_ACTIONS.SET_THEME, payload: systemTheme })
    }
  }, [])

  // Lang nghe thay doi system theme
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = (e) => {
      const systemTheme = e.matches ? 'dark' : 'light'
      dispatch({ type: THEME_ACTIONS.SET_SYSTEM_THEME, payload: systemTheme })
      
      // Neu dang su dung auto theme, cap nhat theme
      const savedTheme = localStorage.getItem('theme')
      if (!savedTheme) {
        dispatch({ type: THEME_ACTIONS.SET_THEME, payload: systemTheme })
      }
    }
    
    mediaQuery.addEventListener('change', handleChange)
    
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  // Cap nhat DOM khi theme thay doi
  useEffect(() => {
    const root = document.documentElement
    
    // Xoa tat ca class theme
    root.classList.remove('light', 'dark')
    
    // Them class theme hien tai
    root.classList.add(state.theme)
    
    // Cap nhat data-theme attribute
    root.setAttribute('data-theme', state.theme)
    
    // Luu vao localStorage
    localStorage.setItem('theme', state.theme)
  }, [state.theme])

  /**
   * Doi theme
   */
  const toggleTheme = () => {
    dispatch({ type: THEME_ACTIONS.TOGGLE_THEME })
  }

  /**
   * Set theme cu the
   * @param {string} theme - Theme moi ('light' hoac 'dark')
   */
  const setTheme = (theme) => {
    if (theme === 'light' || theme === 'dark') {
      dispatch({ type: THEME_ACTIONS.SET_THEME, payload: theme })
    }
  }

  /**
   * Su dung system theme
   */
  const useSystemTheme = () => {
    localStorage.removeItem('theme')
    dispatch({ type: THEME_ACTIONS.SET_THEME, payload: state.systemTheme })
  }

  // Gia tri context
  const contextValue = {
    theme: state.theme,
    systemTheme: state.systemTheme,
    isDark: state.theme === 'dark',
    isLight: state.theme === 'light',
    toggleTheme,
    setTheme,
    useSystemTheme
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  )
}

/**
 * Hook de su dung theme context
 * @returns {Object} Theme context value
 */
export const useTheme = () => {
  const context = useContext(ThemeContext)
  
  if (!context) {
    throw new Error('useTheme phai duoc su dung ben trong ThemeProvider')
  }
  
  return context
}

export default ThemeContext