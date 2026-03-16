import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly analytics va thong ke
 * Student: 2 endpoints, Instructor: 3 endpoints, Admin: 3 endpoints
 */
export const analyticsService = {
  // ========================
  // STUDENT ANALYTICS
  // ========================

  /**
   * Lay thong ke hoc tap chi tiet cua student
   * @returns {Promise} LearningStatsResponse
   */
  async getLearningStats() {
    try {
      const response = await api.get('/analytics/learning-stats')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay bieu do tien do hoc tap theo thoi gian
   * @param {Object} params - { time_range: day|week|month, course_id? }
   * @returns {Promise} ProgressChartResponse
   */
  async getProgressChart(params = {}) {
    try {
      const response = await api.get('/analytics/progress-chart', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  // ========================
  // INSTRUCTOR ANALYTICS
  // ========================

  /**
   * Lay thong ke lop hoc chi tiet (instructor)
   * @param {Object} params - { class_id? }
   * @returns {Promise} InstructorClassStatsResponse
   */
  async getInstructorClassStats(params = {}) {
    try {
      const response = await api.get('/analytics/instructor/classes', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay bieu do tien do hoc vien (instructor)
   * @param {Object} params - { time_range, class_id? }
   * @returns {Promise} InstructorProgressChartResponse
   */
  async getInstructorProgressChart(params = {}) {
    try {
      const response = await api.get('/analytics/instructor/progress-chart', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay phan tich hieu qua quiz (instructor)
   * @returns {Promise} InstructorQuizPerformanceResponse
   */
  async getInstructorQuizPerformance() {
    try {
      const response = await api.get('/analytics/instructor/quiz-performance')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  // ========================
  // ADMIN ANALYTICS
  // ========================

  /**
   * Lay thong ke tang truong nguoi dung
   * @param {Object} params - { time_range: 7d|30d|90d, role_filter? }
   * @returns {Promise} AdminUsersGrowthResponse
   */
  async getUsersGrowth(params = {}) {
    try {
      const response = await api.get('/admin/analytics/users-growth', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay phan tich khoa hoc (admin)
   * @returns {Promise} AdminCourseAnalyticsResponse
   */
  async getCourseAnalytics() {
    try {
      const response = await api.get('/admin/analytics/courses')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay giam sat suc khoe he thong (admin)
   * @returns {Promise} AdminSystemHealthResponse
   */
  async getSystemHealth() {
    try {
      const response = await api.get('/admin/analytics/system-health')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default analyticsService
