import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly dashboard (3 roles)
 * Endpoints: GET /dashboard/student, GET /dashboard/instructor, GET /dashboard/admin
 */
export const dashboardService = {
  /**
   * Lay dashboard tong quan hoc vien
   * @returns {Promise} StudentDashboardResponse
   */
  async getStudentDashboard() {
    try {
      const response = await api.get('/dashboard/student')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay dashboard tong quan giang vien
   * @returns {Promise} InstructorDashboardResponse
   */
  async getInstructorDashboard() {
    try {
      const response = await api.get('/dashboard/instructor')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay dashboard tong quan admin
   * @returns {Promise} AdminSystemDashboardResponse
   */
  async getAdminDashboard() {
    try {
      const response = await api.get('/dashboard/admin')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default dashboardService
