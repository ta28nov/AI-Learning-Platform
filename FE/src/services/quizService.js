import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly quiz va bai kiem tra
 * Student: GET detail, POST attempt, GET results, POST retake, POST generate-practice
 * Instructor: POST create, GET list, PUT update, DELETE, GET class-results
 */
export const quizService = {
  // ========================
  // STUDENT ENDPOINTS
  // ========================

  /**
   * Lay thong tin chi tiet quiz truoc khi lam bai
   * @param {string} quizId - UUID quiz
   * @returns {Promise} QuizDetailResponse
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
   * Nop bai lam quiz
   * @param {string} quizId - UUID quiz
   * @param {Object} data - { answers: [{question_id, selected_option}], time_spent_minutes }
   * @returns {Promise} QuizAttemptResponse
   */
  async submitAttempt(quizId, data) {
    try {
      const response = await api.post(`/quizzes/${quizId}/attempt`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay ket qua quiz chi tiet (tung cau hoi + giai thich)
   * @param {string} quizId - UUID quiz
   * @returns {Promise} QuizResultsResponse
   */
  async getQuizResults(quizId) {
    try {
      const response = await api.get(`/quizzes/${quizId}/results`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lam lai quiz (AI sinh cau hoi moi tuong tu)
   * @param {string} quizId - UUID quiz
   * @returns {Promise} QuizRetakeResponse - bao gom questions[] moi
   */
  async retakeQuiz(quizId) {
    try {
      const response = await api.post(`/quizzes/${quizId}/retake`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Sinh bai tap luyen tap ca nhan hoa bang AI
   * @param {Object} data - { lesson_id|course_id|topic_prompt, difficulty, question_count, practice_type, focus_skills }
   * @returns {Promise} PracticeExercisesGenerateResponse
   */
  async generatePractice(data) {
    try {
      const response = await api.post('/ai/generate-practice', data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  // ========================
  // INSTRUCTOR ENDPOINTS
  // ========================

  /**
   * Tao quiz moi cho lesson (Instructor)
   * @param {string} lessonId - UUID lesson
   * @param {Object} data - QuizCreateRequest
   * @returns {Promise} QuizCreateResponse
   */
  async createQuiz(lessonId, data) {
    try {
      const response = await api.post(`/lessons/${lessonId}/quizzes`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach quiz (Instructor)
   * @param {Object} params - role, course_id, class_id, search, sort_by, sort_order, skip, limit
   * @returns {Promise} QuizListResponse
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
   * Cap nhat quiz (Instructor)
   * @param {string} quizId - UUID quiz
   * @param {Object} data - QuizUpdateRequest
   * @returns {Promise} QuizUpdateResponse (bao gom has_attempts, warning)
   */
  async updateQuiz(quizId, data) {
    try {
      const response = await api.put(`/quizzes/${quizId}`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa quiz (Instructor, chi khi chua co attempt)
   * @param {string} quizId - UUID quiz
   * @returns {Promise} QuizDeleteResponse
   */
  async deleteQuiz(quizId) {
    try {
      const response = await api.delete(`/quizzes/${quizId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay ket qua quiz cua lop hoc (Instructor)
   * @param {string} quizId - UUID quiz
   * @param {Object} params - class_id
   * @returns {Promise} QuizClassResultsResponse
   */
  async getClassResults(quizId, params = {}) {
    try {
      const response = await api.get(`/quizzes/${quizId}/class-results`, { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default quizService