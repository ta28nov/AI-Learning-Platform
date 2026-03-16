import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly dang ky khoa hoc
 * Endpoints: POST /enrollments, GET /enrollments/my-courses,
 *            GET /enrollments/{id}, DELETE /enrollments/{id}
 */
export const enrollmentService = {
  /**
   * Dang ky khoa hoc
   * @param {string} courseId - UUID khoa hoc
   * @returns {Promise} EnrollmentCreateResponse
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
   * @param {Object} params - status (in-progress|completed|cancelled), skip, limit
   * @returns {Promise} EnrollmentListResponse
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
   * Lay chi tiet enrollment
   * @param {string} enrollmentId - UUID enrollment
   * @returns {Promise} EnrollmentDetailResponse
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
   * Huy dang ky khoa hoc
   * @param {string} enrollmentId - UUID enrollment
   * @returns {Promise} EnrollmentCancelResponse
   */
  async cancelEnrollment(enrollmentId) {
    try {
      const response = await api.delete(`/enrollments/${enrollmentId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default enrollmentService