import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly khoa hoc
 */
export const courseService = {
  /**
   * Lay danh sach khoa hoc cong khai
   * @param {Object} params - Parameters tim kiem
   * @param {number} params.page - Trang hien tai
   * @param {number} params.limit - So luong item moi trang
   * @param {string} params.search - Tu khoa tim kiem
   * @param {string} params.category - Danh muc
   * @param {string} params.level - Cap do
   * @returns {Promise} Danh sach khoa hoc
   */
  async getPublicCourses(params = {}) {
    try {
      const response = await api.get('/courses/public', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Tim kiem khoa hoc
   * @param {Object} params - Parameters tim kiem
   * @returns {Promise} Ket qua tim kiem
   */
  async searchCourses(params = {}) {
    try {
      const response = await api.get('/courses/search', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong tin chi tiet khoa hoc
   * @param {string} courseId - ID khoa hoc
   * @returns {Promise} Thong tin khoa hoc
   */
  async getCourseDetail(courseId) {
    try {
      const response = await api.get(`/courses/${courseId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong tin module
   * @param {string} courseId - ID khoa hoc
   * @param {string} moduleId - ID module
   * @returns {Promise} Thong tin module
   */
  async getModule(courseId, moduleId) {
    try {
      const response = await api.get(`/courses/${courseId}/modules/${moduleId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay noi dung bai hoc
   * @param {string} courseId - ID khoa hoc
   * @param {string} lessonId - ID bai hoc
   * @returns {Promise} Noi dung bai hoc
   */
  async getLesson(courseId, lessonId) {
    try {
      const response = await api.get(`/courses/${courseId}/lessons/${lessonId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Danh dau bai hoc da hoan thanh
   * @param {string} courseId - ID khoa hoc
   * @param {string} lessonId - ID bai hoc
   * @returns {Promise}
   */
  async markLessonComplete(courseId, lessonId) {
    try {
      const response = await api.post(`/courses/${courseId}/lessons/${lessonId}/complete`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay tien do hoc tap cua khoa hoc
   * @param {string} courseId - ID khoa hoc
   * @returns {Promise} Tien do hoc tap
   */
  async getCourseProgress(courseId) {
    try {
      const response = await api.get(`/courses/${courseId}/progress`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Danh gia khoa hoc
   * @param {string} courseId - ID khoa hoc
   * @param {Object} ratingData - Du lieu danh gia
   * @param {number} ratingData.rating - Diem danh gia (1-5)
   * @param {string} ratingData.review - Nhan xet
   * @returns {Promise}
   */
  async rateCourse(courseId, ratingData) {
    try {
      const response = await api.post(`/courses/${courseId}/rating`, ratingData)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach danh gia khoa hoc
   * @param {string} courseId - ID khoa hoc
   * @param {Object} params - Parameters phan trang
   * @returns {Promise} Danh sach danh gia
   */
  async getCourseRatings(courseId, params = {}) {
    try {
      const response = await api.get(`/courses/${courseId}/ratings`, { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default courseService