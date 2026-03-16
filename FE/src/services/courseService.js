import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly khoa hoc
 * Endpoints: GET /courses/search, GET /courses/public, 
 *            GET /courses/{id}, GET /courses/{id}/enrollment-status
 */
export const courseService = {
  /**
   * Tim kiem khoa hoc
   * @param {Object} params - keyword, category, level, duration_range, sort_by, skip, limit
   * @returns {Promise} CourseSearchResponse
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
   * Lay danh sach khoa hoc cong khai
   * @param {Object} params - skip, limit
   * @returns {Promise} CourseListResponse (alias CourseSearchResponse)
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
   * Lay chi tiet khoa hoc
   * @param {string} courseId - UUID khoa hoc
   * @returns {Promise} CourseDetailResponse
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
   * Kiem tra trang thai enrollment cua user hien tai voi khoa hoc
   * @param {string} courseId - UUID khoa hoc
   * @returns {Promise} CourseEnrollmentStatusResponse
   */
  async getEnrollmentStatus(courseId) {
    try {
      const response = await api.get(`/courses/${courseId}/enrollment-status`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default courseService