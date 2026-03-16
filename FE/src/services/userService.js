import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly thong tin nguoi dung (tach khoi authService)
 * Endpoints: GET /users/me, PATCH /users/me
 */
export const userService = {
  /**
   * Lay thong tin nguoi dung hien tai
   * @returns {Promise} UserProfileResponse
   */
  async getProfile() {
    try {
      const response = await api.get('/users/me')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat thong tin nguoi dung
   * @param {Object} data - { full_name?, avatar_url?, bio?, contact_info?, learning_preferences? }
   * @returns {Promise} UserProfileUpdateResponse
   */
  async updateProfile(data) {
    try {
      const response = await api.patch('/users/me', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default userService
