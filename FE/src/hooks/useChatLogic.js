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
  const sendMessage = useCallback(async (question, contextType = 'general', contextMeta = {}) => {
    if (!question?.trim() || sending) return

    const effectiveCourseId = contextMeta.courseId || courseId
    if (!effectiveCourseId) {
      setMessages(prev => [...prev, {
        role: 'error',
        content: 'Thiếu ngữ cảnh khóa học để gửi câu hỏi.',
        timestamp: new Date().toISOString(),
      }])
      return
    }

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

      const data = await chatService.sendMessage(effectiveCourseId, payload)

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
        follow_up_suggestions: data?.follow_up_suggestions || buildFollowUpSuggestions(question, contextMeta),
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
      const grouped = data?.grouped_by_date || { today: [], yesterday: [], this_week: [], older: [] }
      let list = data?.conversations || []
      if (!list.length && data?.grouped_by_date) {
        list = [
          ...grouped.today.map(c => ({ ...c, _group: 'Hôm nay' })),
          ...grouped.yesterday.map(c => ({ ...c, _group: 'Hôm qua' })),
          ...grouped.this_week.map(c => ({ ...c, _group: 'Tuần này' })),
          ...grouped.older.map(c => ({ ...c, _group: 'Cũ hơn' })),
        ]
      }
      setConversations(list)
      setGroupedHistory(grouped)
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
        related_lessons: m.related_lessons || [],
        follow_up_suggestions: m.follow_up_suggestions || [],
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
      return true
    } catch {
      return false
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
      return true
    } catch {
      return false
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

const buildFollowUpSuggestions = (question, contextMeta = {}) => {
  const lessonTag = contextMeta.lessonTitle || contextMeta.moduleTitle || 'nội dung này'
  const q = (question || '').toLowerCase()
  if (q.includes('vòng lặp') || q.includes('loop')) {
    return [
      `So sánh for và while trong ${lessonTag}`,
      `Cho 3 bài tập vòng lặp tăng dần độ khó ở ${lessonTag}`,
      `Các lỗi thường gặp khi dùng vòng lặp trong bài này`,
    ]
  }
  return [
    `Tóm tắt ý chính của ${lessonTag}`,
    `Cho ví dụ thực tế áp dụng phần này`,
    `Tạo 3 câu hỏi ôn tập nhanh cho ${lessonTag}`,
  ]
}

export default useChatLogic
