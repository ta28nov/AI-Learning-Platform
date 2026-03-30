import { useState, useCallback, useRef } from 'react'
import chatService from '@services/chatService'

/**
 * useChatLogic — Custom hook dùng chung cho ChatPage VÀ ChatWidget
 * Theo Dual-UI architecture: một logic, hai giao diện
 *
 * Request: POST /chat/course/{courseId}
 *   body: { question, conversation_id?, context_type? }
 * Response: { conversation_id, message_id, question, answer(markdown),
 *             sources[]{type,title,excerpt}, related_lessons[]{lesson_id,title,url} }
 *
 * History: GET /chat/history
 *   Response: { conversations[], grouped_by_date{today[], yesterday[], this_week[], older[]} }
 */
const useChatLogic = (courseId) => {
  const [messages, setMessages] = useState([])      // Messages trong conversation hien tai
  const [conversations, setConversations] = useState([]) // Lich su tat ca conversations
  const [groupedHistory, setGroupedHistory] = useState({ today: [], yesterday: [], this_week: [], older: [] })
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const abortRef = useRef(null)

  // Gui tin nhan, nhan phan hoi AI
  // question: string, context_type: 'lesson'|'module'|'general'
  const sendMessage = useCallback(async (question, contextType = 'general') => {
    if (!question?.trim() || !courseId || sending) return

    const userMsg = { role: 'user', content: question.trim(), timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setSending(true)

    try {
      const payload = {
        question: question.trim(),
        context_type: contextType,
        // Tiep tuc conversation cu neu co (BE dung de luu lich su lien tuc)
        ...(currentConversationId ? { conversation_id: currentConversationId } : {})
      }

      const data = await chatService.sendMessage(courseId, payload)

      // Cap nhat conversation_id tu response dau tien
      if (data?.conversation_id && !currentConversationId) {
        setCurrentConversationId(data.conversation_id)
      }

      // Them AI bubble vao messages
      const aiMsg = {
        role: 'assistant',
        content: data?.answer || '',          // Markdown text
        sources: data?.sources || [],          // [{ type, title, excerpt }]
        related_lessons: data?.related_lessons || [], // [{ lesson_id, title, url }]
        message_id: data?.message_id,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, aiMsg])

    } catch (error) {
      // Them error message vao list
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Không thể kết nối với AI. Vui lòng thử lại.',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setSending(false)
    }
  }, [courseId, currentConversationId, sending])

  // Tai lich su tat ca conversations (sidebar ChatPage)
  // Response: { conversations[], grouped_by_date{today[], yesterday[], this_week[], older[]} }
  const loadHistory = useCallback(async () => {
    setLoadingHistory(true)
    try {
      const data = await chatService.getHistory()
      setConversations(data?.conversations || [])
      setGroupedHistory(data?.grouped_by_date || { today: [], yesterday: [], this_week: [], older: [] })
    } catch {
      setConversations([])
    } finally {
      setLoadingHistory(false)
    }
  }, [])

  // Tai messages cua mot conversation cu (khi click vao sidebar)
  // Response: { course, messages[]{message_id, role, content, timestamp, sources[]} }
  const loadConversation = useCallback(async (conversationId) => {
    try {
      const data = await chatService.getConversation(conversationId)
      setCurrentConversationId(conversationId)
      // Map ve format noi bo
      const mapped = (data?.messages || []).map(m => ({
        role: m.role,             // 'user' | 'assistant'
        content: m.content,       // markdown
        sources: m.sources || [],
        message_id: m.message_id,
        timestamp: m.timestamp
      }))
      setMessages(mapped)
    } catch {
      // Giu nguyen state neu loi
    }
  }, [])

  // Xoa mot conversation
  const deleteConversation = useCallback(async (conversationId) => {
    try {
      await chatService.deleteConversation(conversationId)
      setConversations(prev => prev.filter(c => c.conversation_id !== conversationId))
      // Reset neu dang xem conversation nay
      if (currentConversationId === conversationId) {
        setMessages([])
        setCurrentConversationId(null)
      }
    } catch {
      // Bo qua loi
    }
  }, [currentConversationId])

  // Xoa tat ca conversations
  const deleteAllConversations = useCallback(async () => {
    try {
      await chatService.deleteAllConversations()
      setConversations([])
      setGroupedHistory({ today: [], yesterday: [], this_week: [], older: [] })
      setMessages([])
      setCurrentConversationId(null)
    } catch {
      // Bo qua loi
    }
  }, [])

  // Bat dau conversation moi (reset state)
  const startNewConversation = useCallback(() => {
    setMessages([])
    setCurrentConversationId(null)
  }, [])

  return {
    // State
    messages,
    conversations,
    groupedHistory,
    currentConversationId,
    sending,
    loadingHistory,
    // Actions
    sendMessage,
    loadHistory,
    loadConversation,
    deleteConversation,
    deleteAllConversations,
    startNewConversation
  }
}

export default useChatLogic
