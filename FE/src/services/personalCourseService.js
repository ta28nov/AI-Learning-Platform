import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly khoa hoc ca nhan
 * Endpoints: POST from-prompt, POST personal, GET my-personal,
 *            PUT personal/{id}, DELETE personal/{id}
 */
export const personalCourseService = {
  /**
   * Tao khoa hoc tu AI prompt
   * @param {Object} data - { prompt (20-1000 chars), level, duration_weeks, language }
   * @returns {Promise} Course draft duoc tao
   */
  async createFromPrompt(data) {
    try {
      const response = await api.post('/courses/from-prompt', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Tao khoa hoc thu cong
   * @param {Object} data - { title, description, category, level, thumbnail_url?, language? }
   * @returns {Promise} Course draft duoc tao
   */
  async createManual(data) {
    try {
      const response = await api.post('/courses/personal', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach khoa hoc ca nhan
   * @param {Object} params - status (draft|published|archived), skip, limit
   * @returns {Promise} Danh sach khoa hoc ca nhan
   */
  async getMyPersonalCourses(params = {}) {
    try {
      const response = await api.get('/courses/my-personal', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat khoa hoc ca nhan (modules, lessons, noi dung)
   * @param {string} courseId - UUID khoa hoc
   * @param {Object} data - Noi dung cap nhat (nested modules/lessons)
   * @returns {Promise}
   */
  async updateCourse(courseId, data) {
    try {
      const response = await api.put(`/courses/personal/${courseId}`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa khoa hoc ca nhan (vinh vien, chi owner)
   * @param {string} courseId - UUID khoa hoc
   * @returns {Promise} { title, deleted_at }
   */
  async deleteCourse(courseId) {
    try {
      const response = await api.delete(`/courses/personal/${courseId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default personalCourseService
