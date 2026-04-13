import api, { handleApiResponse, handleApiError, AI_TIMEOUT } from './api'

/**
 * Service xu ly danh gia nang luc AI
 * Endpoints: POST /assessments/generate, POST /assessments/{id}/submit, GET /assessments/{id}/results
 */
export const assessmentService = {
  /**
   * Sinh bai danh gia nang luc
   * @param {Object} data - { category, subject, level, focus_areas[] }
   * @returns {Promise} AssessmentGenerateResponse
   */
  async generate(data) {
    try {
      const response = await api.post('/assessments/generate', data, { timeout: AI_TIMEOUT })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Nop bai danh gia
   * @param {string} sessionId - UUID session
   * @param {Object} data - { answers[], total_time_seconds, submitted_at }
   * @returns {Promise} { session_id, message }
   */
  async submit(sessionId, data) {
    try {
      // BE yeu cau submitted_at (datetime ISO 8601) - tu dong them neu thieu
      const payload = {
        ...data,
        submitted_at: data.submitted_at || new Date().toISOString()
      }
      const response = await api.post(`/assessments/${sessionId}/submit`, payload)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay ket qua danh gia chi tiet
   * @param {string} sessionId - UUID session
   * @returns {Promise} AssessmentResultsResponse
   */
  async getResults(sessionId) {
    try {
      const response = await api.get(`/assessments/${sessionId}/results`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default assessmentService
