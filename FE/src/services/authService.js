
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
   * Gui email khoi phuc mat khau
   * @param {string} email - Email nguoi dung
   * @returns {Promise}
   * @deprecated [TODO] BE chua implement route POST /auth/forgot-password → se nhan 404
   */
  async forgotPassword(email) {
    throw new Error('Chức năng quên mật khẩu chưa được backend hỗ trợ trong phiên bản hiện tại.')
  },

  /**
   * Dat lai mat khau
   * @param {string} token - Reset token
   * @param {string} password - Mat khau moi
   * @returns {Promise}
   * @deprecated [TODO] BE chua implement route POST /auth/reset-password → se nhan 404
   */
  async resetPassword(token, password) {
    throw new Error('Chức năng đặt lại mật khẩu chưa được backend hỗ trợ trong phiên bản hiện tại.')
  },

  /**
   * Xac thuc email
   * @param {string} token - Verification token
   * @returns {Promise}
   * @deprecated [TODO] BE chua implement route POST /auth/verify-email → se nhan 404
   */
  async verifyEmail(token) {
    throw new Error('Chức năng xác thực email chưa được backend hỗ trợ trong phiên bản hiện tại.')
  },

  /**
   * Gui lai email xac thuc
   * @param {string} email - Email nguoi dung
   * @returns {Promise}
   * @deprecated [TODO] BE chua implement route POST /auth/resend-verification → se nhan 404
   */
  async resendVerificationEmail(email) {
    throw new Error('Chức năng gửi lại email xác thực chưa được backend hỗ trợ trong phiên bản hiện tại.')
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