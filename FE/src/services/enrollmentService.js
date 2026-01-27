import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly dang ky khoa hoc
 */
export const enrollmentService = {
  /**
   * Dang ky khoa hoc
   * @param {string} courseId - ID khoa hoc
   * @returns {Promise} Thong tin enrollment
   */
  async enrollCourse(courseId) {
    try {
      const response = await api.post('/enrollments', {
        course_id: courseId
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach khoa hoc da dang ky
   * @param {Object} params - Parameters filter
   * @param {string} params.status - Trang thai enrollment
   * @returns {Promise} Danh sach khoa hoc da dang ky
   */
  async getMyCourses(params = {}) {
    try {
      const response = await api.get('/enrollments/my-courses', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong tin chi tiet enrollment
   * @param {string} enrollmentId - ID enrollment
   * @returns {Promise} Thong tin enrollment
   */
  async getEnrollmentDetail(enrollmentId) {
    try {
      const response = await api.get(`/enrollments/${enrollmentId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Kiem tra trang thai dang ky khoa hoc
   * @param {string} courseId - ID khoa hoc
   * @returns {Promise} Trang thai dang ky
   */
  async getEnrollmentStatus(courseId) {
    try {
      const response = await api.get(`/courses/${courseId}/enrollment-status`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Huy dang ky khoa hoc
   * @param {string} enrollmentId - ID enrollment
   * @returns {Promise}
   */
  async cancelEnrollment(enrollmentId) {
    try {
      const response = await api.delete(`/enrollments/${enrollmentId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat tien do hoc tap
   * @param {string} enrollmentId - ID enrollment
   * @param {Object} progressData - Du lieu tien do
   * @returns {Promise}
   */
  async updateProgress(enrollmentId, progressData) {
    try {
      const response = await api.patch(`/enrollments/${enrollmentId}/progress`, progressData)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong ke tien do hoc tap tong quan
   * @returns {Promise} Thong ke tien do
   */
  async getProgressSummary() {
    try {
      const response = await api.get('/enrollments/progress-summary')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default enrollmentService