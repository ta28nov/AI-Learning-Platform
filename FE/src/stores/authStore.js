import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import authService from '@services/authService'

/**
 * Zustand store cho quan ly xac thuc nguoi dung
 */
export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      /**
       * Dang nhap nguoi dung
       * @param {string} email - Email nguoi dung
       * @param {string} password - Mat khau
       */
      login: async (email, password) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await authService.login(email, password)
          const { user, access_token, refresh_token } = response
          
          // Luu tokens vao localStorage
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })
          
          return response
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message
          })
          throw error
        }
      },

      /**
       * Dang ky nguoi dung moi
       * @param {Object} userData - Thong tin nguoi dung
       */
      register: async (userData) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await authService.register(userData)
          
          set({
            isLoading: false,
            error: null
          })
          
          return response
        } catch (error) {
          set({
            isLoading: false,
            error: error.message
          })
          throw error
        }
      },

      /**
       * Dang xuat nguoi dung
       */
      logout: async () => {
        set({ isLoading: true })
        
        try {
          await authService.logout()
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          // Xoa tokens khoi localStorage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          })
        }
      },

      /**
       * Lay thong tin nguoi dung hien tai
       */
      getCurrentUser: async () => {
        set({ isLoading: true, error: null })
        
        try {
          const user = await authService.getCurrentUser()
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })
          
          return user
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message
          })
          throw error
        }
      },

      /**
       * Cap nhat thong tin nguoi dung
       * @param {Object} userData - Thong tin cap nhat
       */
      updateProfile: async (userData) => {
        set({ isLoading: true, error: null })
        
        try {
          const updatedUser = await authService.updateProfile(userData)
          
          set({
            user: updatedUser,
            isLoading: false,
            error: null
          })
          
          return updatedUser
        } catch (error) {
          set({
            isLoading: false,
            error: error.message
          })
          throw error
        }
      },

      /**
       * Kiem tra va khoi phuc trang thai tu localStorage
       */
      initializeAuth: async () => {
        const token = localStorage.getItem('access_token')
        
        if (token) {
          try {
            await get().getCurrentUser()
          } catch (error) {
            // Token het han hoac khong hop le, xoa va reset state
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: null
            })
          }
        }
      },

      /**
       * Xoa loi
       */
      clearError: () => {
        set({ error: null })
      },

      /**
       * Reset store
       */
      reset: () => {
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        })
      }
    }),
    {
      name: 'auth-storage', // Ten key trong localStorage
      partialize: (state) => ({
        // Chi luu cac field can thiet
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)