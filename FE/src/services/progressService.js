import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly tien do hoc tap
 * Endpoints: GET /progress/course/{course_id}
 */
export const progressService = {
  /**
   * Lay tien do hoc tap chi tiet cua khoa hoc
   * @param {string} courseId - UUID khoa hoc
   * @returns {Promise} ProgressCourseResponse
   */
  async getCourseProgress(courseId) {
    try {
      const response = await api.get(`/progress/course/${courseId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default progressService
