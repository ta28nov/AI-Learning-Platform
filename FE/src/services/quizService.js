import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly bai kiem tra quiz
 */
export const quizService = {
  /**
   * Sinh bai danh gia nang luc AI
   * @param {Object} assessmentData - Du lieu de yeu cau tao bai kiem tra
   * @param {string} assessmentData.subject - Chu de danh gia
   * @param {string} assessmentData.level - Cap do: 'beginner', 'intermediate', 'advanced'
   * @param {Array} assessmentData.topics - Danh sach chu de cu the
   * @returns {Promise} Thong tin session danh gia
   */
  async generateAssessment(assessmentData) {
    try {
      const response = await api.post('/assessments/generate', assessmentData)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong tin bai danh gia
   * @param {string} sessionId - ID session danh gia
   * @returns {Promise} Noi dung bai kiem tra
   */
  async getAssessment(sessionId) {
    try {
      const response = await api.get(`/assessments/${sessionId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Nop bai danh gia nang luc
   * @param {string} sessionId - ID session danh gia
   * @param {Array} answers - Cac cau tra loi
   * @returns {Promise} Ket qua danh gia
   */
  async submitAssessment(sessionId, answers) {
    try {
      const response = await api.post(`/assessments/${sessionId}/submit`, {
        answers
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay ket qua danh gia
   * @param {string} sessionId - ID session danh gia
   * @returns {Promise} Ket qua chi tiet va phan tich
   */
  async getAssessmentResults(sessionId) {
    try {
      const response = await api.get(`/assessments/${sessionId}/results`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay de xuat lo trinh hoc tap tu ket qua danh gia
   * @returns {Promise} Lo trinh hoc tap ca nhan hoa
   */
  async getRecommendationsFromAssessment() {
    try {
      const response = await api.get('/recommendations/from-assessment')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach quiz thuong
   * @param {Object} params - Parameters filter
   * @returns {Promise} Danh sach quiz
   */
  async getQuizzes(params = {}) {
    try {
      const response = await api.get('/quizzes', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong tin chi tiet quiz
   * @param {string} quizId - ID quiz
   * @returns {Promise} Thong tin quiz
   */
  async getQuizDetail(quizId) {
    try {
      const response = await api.get(`/quizzes/${quizId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Bat dau lam quiz
   * @param {string} quizId - ID quiz
   * @returns {Promise} Session quiz
   */
  async startQuiz(quizId) {
    try {
      const response = await api.post(`/quizzes/${quizId}/start`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Nop bai quiz
   * @param {string} quizId - ID quiz
   * @param {string} sessionId - ID session
   * @param {Array} answers - Cac cau tra loi
   * @returns {Promise} Ket qua quiz
   */
  async submitQuiz(quizId, sessionId, answers) {
    try {
      const response = await api.post(`/quizzes/${quizId}/submit`, {
        session_id: sessionId,
        answers
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay ket qua quiz
   * @param {string} quizId - ID quiz
   * @param {string} sessionId - ID session
   * @returns {Promise} Ket qua chi tiet
   */
  async getQuizResults(quizId, sessionId) {
    try {
      const response = await api.get(`/quizzes/${quizId}/results/${sessionId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay lich su lam quiz
   * @param {Object} params - Parameters filter
   * @returns {Promise} Lich su quiz
   */
  async getQuizHistory(params = {}) {
    try {
      const response = await api.get('/quizzes/history', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default quizService