import { useState, useEffect, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import chatService from '@services/chatService'
import Button from '@components/ui/Button'
import './ChatPage.css'

/**
 * ChatPage - Trang chat với AI trợ giảng
 * Route: /dashboard/chat
 * API: POST /chat/course/{courseId} (gửi tin nhắn)
 *      GET /chat/history (lịch sử hội thoại)
 *      GET /chat/conversations/{id} (chi tiết hội thoại)
 *      DELETE /chat/conversations (xóa tất cả)
 *      DELETE /chat/history/{id} (xóa 1 hội thoại)
 * Giao diện: sidebar danh sách hội thoại + khu vực chat chính
 */
const ChatPage = () => {
  // === STATE ===
  const [conversations, setConversations] = useState([])
  const [activeConversation, setActiveConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [sending, setSending] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [loadingMessages, setLoadingMessages] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Ref để auto-scroll xuống cuối khi có tin nhắn mới
  const messagesEndRef = useRef(null)

  // Cuộn xuống cuối danh sách tin nhắn
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Lấy lịch sử hội thoại khi mount
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoadingHistory(true)
        const data = await chatService.getHistory()
        // API co the tra ve conversations[] hoac grouped_by_date{today[], yesterday[], this_week[], older[]}
        let convList = data?.conversations || []
        // Neu BE tra grouped_by_date, flatten thanh list
        if (data?.grouped_by_date && convList.length === 0) {
          const groups = data.grouped_by_date
          const flatten = []
          if (groups.today?.length) flatten.push(...groups.today.map(c => ({ ...c, _group: 'Hôm nay' })))
          if (groups.yesterday?.length) flatten.push(...groups.yesterday.map(c => ({ ...c, _group: 'Hôm qua' })))
          if (groups.this_week?.length) flatten.push(...groups.this_week.map(c => ({ ...c, _group: 'Tuần này' })))
          if (groups.older?.length) flatten.push(...groups.older.map(c => ({ ...c, _group: 'Cũ hơn' })))
          convList = flatten
        }
        setConversations(convList)
      } catch (error) {
        toast.error('Không thể tải lịch sử hội thoại')
      } finally {
        setLoadingHistory(false)
      }
    }
    fetchHistory()
  }, [])

  // Lấy chi tiết hội thoại khi chọn conversation
  const selectConversation = async (conversationId) => {
    if (activeConversation === conversationId) return
    try {
      setLoadingMessages(true)
      setActiveConversation(conversationId)
      setSidebarOpen(false) // Đóng sidebar trên mobile
      const data = await chatService.getConversation(conversationId)
      setMessages(data?.messages || [])
      // Cuộn xuống sau khi render
      setTimeout(scrollToBottom, 100)
    } catch (error) {
      toast.error('Không thể tải nội dung hội thoại')
    } finally {
      setLoadingMessages(false)
    }
  }

  // Gửi tin nhắn mới
  const handleSend = async () => {
    const question = inputText.trim()
    if (!question || sending) return

    // Thêm tin nhắn user vào danh sách ngay lập tức (optimistic update)
    const userMessage = {
      message_id: `temp-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setSending(true)
    setTimeout(scrollToBottom, 50)

    try {
      // Gửi API — cần course_id. Nếu đang trong hội thoại, lấy từ conversation
      // Nếu là hội thoại mới, dùng context_type: 'general'
      const currentConv = conversations.find(c => c.conversation_id === activeConversation)
      const courseId = currentConv?.course_id || 'general'

      const data = await chatService.sendMessage(courseId, {
        question,
        conversation_id: activeConversation || undefined,
        context_type: 'general'
      })

      // Thêm tin nhắn AI vào danh sách
      const aiMessage = {
        message_id: data?.message_id || `ai-${Date.now()}`,
        role: 'assistant',
        content: data?.answer || 'Xin lỗi, tôi không thể trả lời lúc này.',
        timestamp: new Date().toISOString(),
        sources: data?.sources || []
      }
      setMessages(prev => [...prev, aiMessage])

      // Cập nhật conversation_id nếu là hội thoại mới
      if (!activeConversation && data?.conversation_id) {
        setActiveConversation(data.conversation_id)
        // Thêm hội thoại mới vào sidebar
        setConversations(prev => [{
          conversation_id: data.conversation_id,
          topic_summary: question.substring(0, 50),
          message_count: 2,
          last_message_preview: (data.answer || '').substring(0, 100),
          last_updated: new Date().toISOString()
        }, ...prev])
      }

      setTimeout(scrollToBottom, 50)
    } catch (error) {
      toast.error('Không thể gửi tin nhắn')
      // Xóa tin nhắn user đã thêm optimistic
      setMessages(prev => prev.filter(m => m.message_id !== userMessage.message_id))
    } finally {
      setSending(false)
    }
  }

  // Tạo hội thoại mới
  const startNewChat = () => {
    setActiveConversation(null)
    setMessages([])
    setSidebarOpen(false)
  }

  // Xóa một hội thoại
  const deleteConversation = async (conversationId, e) => {
    e.stopPropagation()
    if (!window.confirm('Bạn có chắc muốn xóa hội thoại này?')) return
    try {
      await chatService.deleteConversation(conversationId)
      setConversations(prev => prev.filter(c => c.conversation_id !== conversationId))
      if (activeConversation === conversationId) {
        setActiveConversation(null)
        setMessages([])
      }
      toast.success('Đã xóa hội thoại')
    } catch (error) {
      toast.error('Không thể xóa hội thoại')
    }
  }

  // Xóa tất cả hội thoại
  const deleteAllConversations = async () => {
    if (!window.confirm('Bạn có chắc muốn xóa TẤT CẢ hội thoại?')) return
    try {
      await chatService.deleteAllConversations()
      setConversations([])
      setActiveConversation(null)
      setMessages([])
      toast.success('Đã xóa tất cả hội thoại')
    } catch (error) {
      toast.error('Không thể xóa hội thoại')
    }
  }

  // Nhấn Enter để gửi
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const fadeUp = { hidden: { opacity: 0, y: 15 }, visible: { opacity: 1, y: 0 } }

  return (
    <div className="chat-page">
      {/* Overlay (mobile sidebar) */}
      {sidebarOpen && (
        <div className="chat-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar - danh sách hội thoại */}
      <aside className={`chat-sidebar ${sidebarOpen ? 'chat-sidebar--open' : ''}`}>
        <div className="chat-sidebar__header">
          <h3 className="chat-sidebar__title">Hội thoại</h3>
          <Button variant="primary" size="sm" onClick={startNewChat}>
            + Mới
          </Button>
        </div>

        {loadingHistory ? (
          <div className="chat-sidebar__loading">
            {[1, 2, 3].map(i => <div key={i} className="chat-sidebar__skeleton" />)}
          </div>
        ) : conversations.length > 0 ? (
          <div className="chat-sidebar__list">
            {conversations.map((conv, idx) => (
              <React.Fragment key={conv.conversation_id}>
                {/* Hien thi label nhom ngay neu co grouped_by_date */}
                {conv._group && (idx === 0 || conversations[idx - 1]?._group !== conv._group) && (
                  <div className="chat-sidebar__group-label">{conv._group}</div>
                )}
                <div
                  className={`chat-conv ${activeConversation === conv.conversation_id ? 'chat-conv--active' : ''}`}
                  onClick={() => selectConversation(conv.conversation_id)}
                >
                  <div className="chat-conv__info">
                    <span className="chat-conv__title">
                      {conv.topic_summary || conv.course_title || 'Hội thoại'}
                    </span>
                    <span className="chat-conv__preview">
                      {conv.last_message_preview || `${conv.message_count || 0} tin nhắn`}
                    </span>
                  </div>
                  <button
                    className="chat-conv__delete"
                    onClick={(e) => deleteConversation(conv.conversation_id, e)}
                    title="Xóa hội thoại"
                  >
                    ×
                  </button>
                </div>
              </React.Fragment>
            ))}
          </div>
        ) : (
          <div className="chat-sidebar__empty">
            <p>Chưa có hội thoại nào</p>
          </div>
        )}

        {conversations.length > 0 && (
          <button className="chat-sidebar__clear" onClick={deleteAllConversations}>
            Xóa tất cả
          </button>
        )}
      </aside>

      {/* Khu vực chat chính */}
      <main className="chat-main">
        {/* Header mobile */}
        <div className="chat-main__header">
          <button className="chat-main__menu-btn" onClick={() => setSidebarOpen(true)}>
            ☰
          </button>
          <span className="chat-main__header-title">AI Trợ giảng</span>
        </div>

        {/* Vùng tin nhắn */}
        <div className="chat-messages">
          {messages.length === 0 && !loadingMessages && (
            <div className="chat-welcome">
              <span className="chat-welcome__icon">🤖</span>
              <h2 className="chat-welcome__title">Xin chào!</h2>
              <p className="chat-welcome__desc">
                Tôi là AI trợ giảng. Hãy hỏi tôi bất cứ điều gì về khóa học của bạn.
              </p>
              <div className="chat-welcome__suggestions">
                <button onClick={() => setInputText('Giải thích khái niệm cơ bản')}>
                  Giải thích khái niệm cơ bản
                </button>
                <button onClick={() => setInputText('Tóm tắt bài học')}>
                  Tóm tắt bài học
                </button>
                <button onClick={() => setInputText('Cho tôi ví dụ thực tế')}>
                  Cho tôi ví dụ thực tế
                </button>
              </div>
            </div>
          )}

          {loadingMessages && (
            <div className="chat-loading">Đang tải tin nhắn...</div>
          )}

          {messages.map((msg) => (
            <motion.div
              key={msg.message_id}
              className={`chat-msg ${msg.role === 'user' ? 'chat-msg--user' : 'chat-msg--ai'}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="chat-msg__avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="chat-msg__content">
                <div className="chat-msg__text">{msg.content}</div>
                {/* Nguồn tham khảo (nếu có) */}
                {msg.sources?.length > 0 && (
                  <div className="chat-msg__sources">
                    <span className="chat-msg__sources-label">Nguồn tham khảo:</span>
                    {msg.sources.map((src, i) => (
                      <span key={i} className="chat-msg__source">{src.title}</span>
                    ))}
                  </div>
                )}
                {/* Bài học liên quan (nếu có) */}
                {msg.related_lessons?.length > 0 && (
                  <div className="chat-msg__related">
                    <span className="chat-msg__related-label">Bài học liên quan:</span>
                    {msg.related_lessons.map((lesson, i) => (
                      <span key={i} className="chat-msg__related-item">
                        📖 {lesson.title || lesson.lesson_title}
                      </span>
                    ))}
                  </div>
                )}
                {msg.timestamp && (
                  <span className="chat-msg__time">
                    {new Date(msg.timestamp).toLocaleTimeString('vi-VN', {
                      hour: '2-digit', minute: '2-digit'
                    })}
                  </span>
                )}
              </div>
            </motion.div>
          ))}

          {/* Hiệu ứng "Đang suy nghĩ..." */}
          {sending && (
            <div className="chat-msg chat-msg--ai">
              <div className="chat-msg__avatar">🤖</div>
              <div className="chat-msg__content">
                <div className="chat-msg__typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Thanh nhập tin nhắn */}
        <div className="chat-input">
          <textarea
            className="chat-input__textarea"
            placeholder="Nhập câu hỏi của bạn..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={sending}
          />
          <Button
            variant="primary"
            size="sm"
            onClick={handleSend}
            disabled={!inputText.trim() || sending}
            loading={sending}
          >
            Gửi
          </Button>
        </div>
      </main>
    </div>
  )
}

export default ChatPage