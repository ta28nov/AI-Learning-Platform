import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly de xuat hoc tap
 * Endpoints: GET /recommendations/from-assessment, GET /recommendations
 */
export const recommendationService = {
  /**
   * Lay de xuat lo trinh hoc tap tu ket qua danh gia
   * @returns {Promise} RecommendationsFromAssessmentResponse
   */
  async getFromAssessment() {
    try {
      const response = await api.get('/recommendations/from-assessment')
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
