import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly lop hoc
 * Instructor: create, list, detail, update, delete, students, student detail, remove student, progress
 * Student: join
 */
export const classService = {
  // ========================
  // INSTRUCTOR ENDPOINTS
  // ========================

  /**
   * Tao lop hoc moi
   * @param {Object} data - { name, description, course_id, start_date, end_date, max_students }
   * @returns {Promise} ClassCreateResponse - bao gom invite_code tu dong
   */
  async createClass(data) {
    try {
      const response = await api.post('/classes', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach lop hoc cua instructor
   * @returns {Promise} ClassListResponse
   */
  async getMyClasses() {
    try {
      const response = await api.get('/classes/my-classes')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet lop hoc
   * @param {string} classId - UUID lop hoc
   * @returns {Promise} ClassDetailResponse
   */
  async getClassDetail(classId) {
    try {
      const response = await api.get(`/classes/${classId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat thong tin lop hoc
   * @param {string} classId - UUID lop hoc
   * @param {Object} data - { name?, description?, max_students?, end_date? }
   * @returns {Promise} ClassUpdateResponse
   */
  async updateClass(classId, data) {
    try {
      const response = await api.put(`/classes/${classId}`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa lop hoc (chi khi chua co hoc vien hoac da completed)
   * @param {string} classId - UUID lop hoc
   * @returns {Promise} ClassDeleteResponse
   */
  async deleteClass(classId) {
    try {
      const response = await api.delete(`/classes/${classId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach hoc vien trong lop
   * @param {string} classId - UUID lop hoc
   * @param {Object} params - skip, limit
   * @returns {Promise} ClassStudentListResponse
   */
  async getStudents(classId, params = {}) {
    try {
      const response = await api.get(`/classes/${classId}/students`, { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet hoc vien trong lop
   * @param {string} classId - UUID lop hoc
   * @param {string} studentId - UUID hoc vien
   * @returns {Promise} ClassStudentDetailResponse
   */
  async getStudentDetail(classId, studentId) {
    try {
      const response = await api.get(`/classes/${classId}/students/${studentId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa hoc vien khoi lop (giu lai du lieu tien do)
   * @param {string} classId - UUID lop hoc
   * @param {string} studentId - UUID hoc vien
   * @returns {Promise}
   */
  async removeStudent(classId, studentId) {
    try {
      const response = await api.delete(`/classes/${classId}/students/${studentId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay tien do tong the cua lop hoc
   * @param {string} classId - UUID lop hoc
   * @returns {Promise} ClassProgressResponse
   */
  async getClassProgress(classId) {
    try {
      const response = await api.get(`/classes/${classId}/progress`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  // ========================
  // STUDENT ENDPOINT
  // ========================

  /**
   * Student tham gia lop hoc bang ma moi
   * @param {string} inviteCode - Ma moi 6-8 ky tu
   * @returns {Promise} ClassJoinResponse - bao gom course_id, enrollment_id
   */
  async joinClass(inviteCode) {
    try {
      const response = await api.post('/classes/join', {
        invite_code: inviteCode
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default classService
