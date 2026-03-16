import api, { handleApiResponse, handleApiError } from './api'

/**
 * Service xu ly chat voi AI
 * Endpoints: POST send, GET history, GET conversation detail, DELETE all, DELETE one
 */
export const chatService = {
  /**
   * Gui tin nhan hoi dap AI trong khoa hoc
   * @param {string} courseId - UUID khoa hoc
   * @param {Object} data - { question, conversation_id?, context_type? }
   * @returns {Promise} ChatMessageResponse
   */
  async sendMessage(courseId, data) {
    try {
      const response = await api.post(`/chat/course/${courseId}`, data)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay lich su hoi thoai (grouped by date)
   * @param {Object} params - skip, limit
   * @returns {Promise} ChatHistoryListResponse
   */
  async getHistory(params = {}) {
    try {
      const response = await api.get('/chat/history', { params })
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Lay chi tiet mot cuoc hoi thoai (tat ca messages)
   * @param {string} conversationId - UUID conversation
   * @returns {Promise} ConversationDetailResponse
   */
  async getConversation(conversationId) {
    try {
      const response = await api.get(`/chat/conversations/${conversationId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa tat ca lich su chat
   * @returns {Promise} ChatDeleteAllResponse - { deleted_count, message }
   */
  async deleteAllConversations() {
    try {
      const response = await api.delete('/chat/conversations')
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  },

  /**
   * Xoa mot cuoc hoi thoai cu the
   * @param {string} conversationId - UUID conversation
   * @returns {Promise} ChatDeleteResponse
   */
  async deleteConversation(conversationId) {
    try {
      const response = await api.delete(`/chat/history/${conversationId}`)
      return handleApiResponse(response)
    } catch (error) {
      handleApiError(error)
    }
  }
}

export default chatService
