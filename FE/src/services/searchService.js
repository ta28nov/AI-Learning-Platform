import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly tim kiem
 * Endpoints: GET /search, GET /search/suggestions, GET /search/history, GET /search/analytics
 */
export const searchService = {
  /**
   * Tim kiem toan he thong
   * @param {Object} params - { q (min 2), category?, level?, instructor?, rating?, page?, limit? }
   * @returns {Promise} SearchResponse
   */
  async search(params = {}) {
    try {
      const response = await api.get('/search', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay goi y tim kiem real-time
   * @param {string} query - Tu khoa (min 1 ky tu)
   * @returns {Promise} SearchSuggestionsResponse
   */
  async getSuggestions(query) {
    try {
      const response = await api.get('/search/suggestions', {
        params: { q: query }
      })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay lich su tim kiem
   * @returns {Promise} SearchHistoryResponse
   */
  async getHistory() {
    try {
      const response = await api.get('/search/history')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay thong ke tim kiem (Admin)
   * @returns {Promise} SearchAnalyticsResponse
   */
  async getAnalytics() {
    try {
      const response = await api.get('/search/analytics')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default searchService
