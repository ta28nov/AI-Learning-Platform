import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly de xuat hoc tap
 * Endpoints: GET /recommendations/from-assessment, GET /recommendations
 */
export const recommendationService = {
  /**
   * Lay de xuat lo trinh hoc tap tu ket qua danh gia
   * @param {string} sessionId - UUID phien danh gia (required by BE)
   * @returns {Promise} AssessmentRecommendationResponse
   */
  async getFromAssessment(sessionId) {
    try {
      const response = await api.get('/recommendations/from-assessment', {
        params: { session_id: sessionId }
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay danh sach de xuat khoa hoc chung
   * @returns {Promise} RecommendationsResponse
   */
  async getRecommendations() {
    try {
      const response = await api.get('/recommendations')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default recommendationService
