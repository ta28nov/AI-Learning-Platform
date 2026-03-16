import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly admin (17 endpoints)
 * Users: 7, Courses: 5, Classes: 2, Analytics: 3
 */
export const adminService = {
  // ========================
  // USER MANAGEMENT (7)
  // ========================

  /**
   * Lay danh sach nguoi dung
   * @param {Object} params - { role?, status?, search?, sort_by?, sort_order?, skip?, limit? }
   * @returns {Promise} AdminUserListResponse
   */
  async getUsers(params = {}) {
    try {
      const response = await api.get('/admin/users', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet nguoi dung
   * @param {string} userId - UUID
   * @returns {Promise} AdminUserDetailResponse
   */
  async getUserDetail(userId) {
    try {
      const response = await api.get(`/admin/users/${userId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Tao tai khoan nguoi dung
   * @param {Object} data - { full_name, email, role, password, bio?, avatar? }
   * @returns {Promise} AdminCreateUserResponse
   */
  async createUser(data) {
    try {
      const response = await api.post('/admin/users', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat thong tin nguoi dung
   * @param {string} userId - UUID
   * @param {Object} data - { full_name?, email?, bio?, avatar?, status? }
   * @returns {Promise} AdminUpdateUserResponse
   */
  async updateUser(userId, data) {
    try {
      const response = await api.put(`/admin/users/${userId}`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa nguoi dung
   * @param {string} userId - UUID
   * @returns {Promise} AdminDeleteUserResponse
   */
  async deleteUser(userId) {
    try {
      const response = await api.delete(`/admin/users/${userId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Thay doi vai tro nguoi dung
   * @param {string} userId - UUID
   * @param {string} newRole - student|instructor|admin
   * @returns {Promise} AdminChangeRoleResponse (bao gom impact analysis)
   */
  async changeUserRole(userId, newRole) {
    try {
      const response = await api.put(`/admin/users/${userId}/role`, {
        new_role: newRole
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Reset mat khau nguoi dung
   * @param {string} userId - UUID
   * @param {string} newPassword - Mat khau moi (min 8)
   * @returns {Promise} AdminResetPasswordResponse
   */
  async resetUserPassword(userId, newPassword) {
    try {
      const response = await api.post(`/admin/users/${userId}/reset-password`, {
        new_password: newPassword
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  // ========================
  // COURSE MANAGEMENT (5)
  // ========================

  /**
   * Lay tat ca khoa hoc (admin view)
   * @param {Object} params - { author_id?, course_type?, status?, category?, level?, search?, sort_by?, sort_order?, skip?, limit? }
   * @returns {Promise} AdminCourseListResponse
   */
  async getCourses(params = {}) {
    try {
      const response = await api.get('/admin/courses', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet khoa hoc (admin view)
   * @param {string} courseId - UUID
   * @returns {Promise} AdminCourseDetailResponse
   */
  async getCourseDetail(courseId) {
    try {
      const response = await api.get(`/admin/courses/${courseId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Tao khoa hoc chinh thuc (public)
   * @param {Object} data - AdminCourseCreateRequest
   * @returns {Promise} AdminCourseCreateResponse
   */
  async createCourse(data) {
    try {
      const response = await api.post('/admin/courses', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Cap nhat bat ky khoa hoc nao
   * @param {string} courseId - UUID
   * @param {Object} data - AdminCourseUpdateRequest
   * @returns {Promise} AdminCourseUpdateResponse
   */
  async updateCourse(courseId, data) {
    try {
      const response = await api.put(`/admin/courses/${courseId}`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa khoa hoc (bao gom impact analysis)
   * @param {string} courseId - UUID
   * @returns {Promise} AdminDeleteCourseResponse (bao gom impact)
   */
  async deleteCourse(courseId) {
    try {
      const response = await api.delete(`/admin/courses/${courseId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  // ========================
  // CLASS MONITORING (2)
  // ========================

  /**
   * Lay tat ca lop hoc (admin view)
   * @param {Object} params - { page?, limit?, search?, status?, sort_by?, sort_order? }
   * @returns {Promise} AdminClassListResponse
   */
  async getClasses(params = {}) {
    try {
      const response = await api.get('/admin/classes', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet lop hoc (admin view)
   * @param {string} classId - UUID
   * @returns {Promise} AdminClassDetailResponse
   */
  async getClassDetail(classId) {
    try {
      const response = await api.get(`/admin/classes/${classId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default adminService
