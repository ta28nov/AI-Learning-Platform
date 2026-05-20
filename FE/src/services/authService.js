
import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly xac thuc nguoi dung
 */
export const authService = {
  /**
   * Dang nhap nguoi dung
   * @param {string} email - Email nguoi dung
   * @param {string} password - Mat khau
   * @returns {Promise} User data va tokens
   */
  async login(email, password, remember_me = false) {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        remember_me
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Dang ky nguoi dung moi
   * @param {Object} userData - Thong tin nguoi dung
   * @param {string} userData.full_name - Ho va ten
   * @param {string} userData.email - Email
   * @param {string} userData.password - Mat khau
   * @returns {Promise} User data
   */
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Dang xuat nguoi dung
   * @returns {Promise}
   */
  async logout() {
    try {
      const response = await api.post('/auth/logout')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong tin nguoi dung hien tai
   * @returns {Promise} User data
   */
  async getCurrentUser() {
    try {
      const response = await api.get('/users/me')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat thong tin nguoi dung
   * @param {Object} userData - Thong tin cap nhat
   * @returns {Promise} Updated user data
   */
  async updateProfile(userData) {
    try {
      const response = await api.patch('/users/me', userData)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Yêu cầu đặt lại mật khẩu — POST /auth/forgot-password
   */
  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password', { email })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Đặt lại mật khẩu — POST /auth/reset-password
   */
  async resetPassword(token, password) {
    try {
      const response = await api.post('/auth/reset-password', {
        token,
        new_password: password,
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /** Xác thực email — POST /auth/verify-email */
  async verifyEmail(token) {
    try {
      const response = await api.post('/auth/verify-email', { token })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /** Gửi lại link xác thực — POST /auth/resend-verification */
  async resendVerificationEmail(email) {
    try {
      const response = await api.post('/auth/resend-verification', { email })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise} New tokens
   */
  async refreshToken(refreshToken) {
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default authService