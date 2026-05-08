import { Fragment, useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'
import enrollmentService from '@services/enrollmentService'
import courseService from '@services/courseService'
import adminService from '@services/adminService'
import useChatLogic from '@hooks/useChatLogic'
import Modal, { ModalFooter } from '@components/ui/Modal'
import AILoadingState from '@components/ui/AILoadingState'
import { useAuthStore } from '@stores/authStore'
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
  const { user } = useAuthStore()
  const {
    messages,
    conversations,
    currentConversationId,
    sending,
    loadingHistory,
    sendMessage,
    loadHistory,
    loadConversation,
    deleteConversation,
    deleteAllConversations,
    startNewConversation,
  } = useChatLogic()

  const [inputText, setInputText] = useState('')
  const [loadingMessages, setLoadingMessages] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeCourseId, setActiveCourseId] = useState(null)
  const [myCourses, setMyCourses] = useState([])
  const [showDeleteAllModal, setShowDeleteAllModal] = useState(false)
  const [deleteConversationId, setDeleteConversationId] = useState(null)

  // Ref để auto-scroll xuống cuối khi có tin nhắn mới
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  useEffect(() => {
    const fetchMyCourses = async () => {
      try {
        if (user?.role === 'student') {
          const data = await enrollmentService.getMyCourses({ limit: 100 })
          setMyCourses(data?.enrollments || data?.data || [])
          return
        }
        if (user?.role === 'admin') {
          const adminCourses = await adminService.getCourses({ skip: 0, limit: 50 })
          const normalizedAdmin = (adminCourses?.data || []).map((c) => ({
            course_id: c.course_id || c.id,
            course_title: c.title,
          }))
          setMyCourses(normalizedAdmin)
          return
        }
        const publicCourses = await courseService.getPublicCourses({ skip: 0, limit: 50 })
        const normalized = (publicCourses?.courses || publicCourses?.data || []).map((c) => ({
          course_id: c.course_id || c.id,
          course_title: c.title,
        }))
        setMyCourses(normalized)
      } catch {
        setMyCourses([])
      }
    }
    fetchMyCourses()
  }, [user?.role])

  const selectConversation = async (conversationId) => {
    if (currentConversationId === conversationId) return
    const selected = conversations.find(c => c.conversation_id === conversationId)
    setActiveCourseId(selected?.course_id || null)
    try {
      setLoadingMessages(true)
      setSidebarOpen(false) // Đóng sidebar trên mobile
      await loadConversation(conversationId)
      setTimeout(scrollToBottom, 100)
    } catch (error) {
      toast.error('Không thể tải nội dung hội thoại')
    } finally {
      setLoadingMessages(false)
    }
  }

  const handleSend = async () => {
    const question = inputText.trim()
    if (!question || sending) return
    setInputText('')
    const fallbackCourse = activeCourseId || conversations.find(c => c.conversation_id === currentConversationId)?.course_id
    if (!fallbackCourse) {
      toast.error('Vui lòng chọn khóa học ở phần nhập tin nhắn để bắt đầu chat.')
      return
    }
    await sendMessage(question, 'general', { courseId: fallbackCourse })
    setTimeout(scrollToBottom, 50)
  }

  const startNewChat = () => {
    startNewConversation()
    setActiveCourseId(null)
    setSidebarOpen(false)
  }

  const handleDeleteConversation = async (conversationId, e) => {
    e.stopPropagation()
    setDeleteConversationId(conversationId)
  }

  const confirmDeleteConversation = async () => {
    if (!deleteConversationId) return
    const ok = await deleteConversation(deleteConversationId)
    setDeleteConversationId(null)
    if (ok) toast.success('Đã xóa hội thoại')
    else toast.error('Không thể xóa hội thoại')
  }

  const handleDeleteAllConversations = async () => {
    setShowDeleteAllModal(true)
  }

  const confirmDeleteAll = async () => {
    const allOk = await deleteAllConversations()
    setShowDeleteAllModal(false)
    if (allOk) toast.success('Đã xóa tất cả hội thoại')
    else toast.error('Không thể xóa hội thoại')
  }

  const courseOptions = myCourses.map((item) => ({
    id: item.course_id || item.id,
    title: item.course_title || item.title || 'Khóa học',
  })).filter((item) => item.id)

  const selectedCourseId = activeCourseId || conversations.find(c => c.conversation_id === currentConversationId)?.course_id || ''
  const handleCourseChange = (value) => {
    setActiveCourseId(value || null)
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
              <Fragment key={conv.conversation_id}>
                {/* Hien thi label nhom ngay neu co grouped_by_date */}
                {conv._group && (idx === 0 || conversations[idx - 1]?._group !== conv._group) && (
                  <div className="chat-sidebar__group-label">{conv._group}</div>
                )}
                <div
                  className={`chat-conv ${currentConversationId === conv.conversation_id ? 'chat-conv--active' : ''}`}
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
                    onClick={(e) => handleDeleteConversation(conv.conversation_id, e)}
                    title="Xóa hội thoại"
                  >
                    ×
                  </button>
                </div>
              </Fragment>
            ))}
          </div>
        ) : (
          <div className="chat-sidebar__empty">
            <p>Chưa có hội thoại nào</p>
          </div>
        )}

        {conversations.length > 0 && (
          <button className="chat-sidebar__clear" onClick={handleDeleteAllConversations}>
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
            <AILoadingState
              compact
              title="Đang tải hội thoại AI"
              message="Hệ thống đang khôi phục ngữ cảnh để phản hồi chính xác."
              steps={[
                'Đang nạp lịch sử hội thoại...',
                'Đang đồng bộ ngữ cảnh khóa học...',
                'Sẵn sàng trao đổi...',
              ]}
            />
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
                {msg.role === 'user' ? 'U' : 'AI'}
              </div>
              <div className="chat-msg__content">
                <div className="chat-msg__text">{msg.content}</div>
                {msg.sources?.length > 0 && (
                  <div className="chat-msg__sources">
                    <span className="chat-msg__sources-label">Nguồn tham khảo:</span>
                    {msg.sources.map((src, i) => (
                      <span key={`${src.title}-${i}`} className="chat-msg__source">{src.title}</span>
                    ))}
                  </div>
                )}
                {msg.related_lessons?.length > 0 && (
                  <div className="chat-msg__related">
                    <span className="chat-msg__related-label">Bài học liên quan:</span>
                    {msg.related_lessons.map((lesson) => (
                      <a key={lesson.lesson_id} className="chat-msg__related-item" href={lesson.url || '#'}>
                        {lesson.title || lesson.lesson_title}
                      </a>
                    ))}
                  </div>
                )}
                {msg.follow_up_suggestions?.length > 0 && (
                  <div className="chat-msg__followup">
                    {msg.follow_up_suggestions.slice(0, 3).map((suggestion) => (
                      <button key={suggestion} onClick={() => setInputText(suggestion)} type="button">
                        {suggestion}
                      </button>
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
              <div className="chat-msg__avatar">AI</div>
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
          <select
            className="chat-input__course-select"
            value={selectedCourseId}
            onChange={(e) => handleCourseChange(e.target.value)}
          >
            <option value="">Chọn khóa học để chat</option>
            {courseOptions.map((course) => (
              <option key={course.id} value={course.id}>{course.title}</option>
            ))}
          </select>
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

      <Modal isOpen={Boolean(deleteConversationId)} onClose={() => setDeleteConversationId(null)} title="Xóa hội thoại" size="sm">
        <p>Bạn có chắc muốn xóa hội thoại này?</p>
        <ModalFooter>
          <Button variant="outline" onClick={() => setDeleteConversationId(null)}>Hủy</Button>
          <Button variant="danger" onClick={confirmDeleteConversation}>Xóa</Button>
        </ModalFooter>
      </Modal>

      <Modal isOpen={showDeleteAllModal} onClose={() => setShowDeleteAllModal(false)} title="Xóa tất cả hội thoại" size="sm">
        <p>Hành động này sẽ xóa toàn bộ lịch sử chat AI.</p>
        <ModalFooter>
          <Button variant="outline" onClick={() => setShowDeleteAllModal(false)}>Hủy</Button>
          <Button variant="danger" onClick={confirmDeleteAll}>Xóa tất cả</Button>
        </ModalFooter>
      </Modal>
    </div>
  )
}

export default ChatPage