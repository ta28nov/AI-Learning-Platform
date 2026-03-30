import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import useChatLogic from '@hooks/useChatLogic'
import './ChatWidget.css'

/**
 * ChatWidget — Floating AI chat button trong LessonPage
 * Vị trí 2 trong Dual-UI architecture (xem FE_CODING_RULES.md Flow 5)
 *
 * - Hiển thị: FAB button góc phải màn hình
 * - Click → Drawer trượt ra, không fullscreen
 * - KHÔNG hiện sidebar lịch sử (tiết kiệm diện tích)
 * - context_type tự động = 'lesson' vì đặt trong LessonPage
 * - Dùng chung useChatLogic hook với ChatPage
 *
 * Usage: <ChatWidget /> — tự lấy courseId từ URL params
 */
const ChatWidget = () => {
  const { courseId } = useParams()
  const [isOpen, setIsOpen] = useState(false)
  const [inputText, setInputText] = useState('')
  const messagesEndRef = useRef(null)

  // Dung chung hook logic voi ChatPage
  const { messages, sending, sendMessage } = useChatLogic(courseId)

  // Auto scroll khi co tin moi
  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  const handleSend = async () => {
    const text = inputText.trim()
    if (!text || sending) return
    setInputText('')
    // context_type = 'lesson' vi widget dat trong LessonPage
    await sendMessage(text, 'lesson')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      {/* FAB button */}
      <button
        id="chat-widget-fab"
        className={`chat-widget__fab ${isOpen ? 'chat-widget__fab--active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Đóng AI trợ giảng' : 'Mở AI trợ giảng'}
        title="AI Trợ giảng"
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Drawer */}
      <div className={`chat-widget__drawer ${isOpen ? 'chat-widget__drawer--open' : ''}`}
        role="dialog"
        aria-label="AI Trợ giảng"
        aria-hidden={!isOpen}
      >
        {/* Header drawer */}
        <div className="chat-widget__header">
          <div className="chat-widget__header-info">
            <span className="chat-widget__avatar">🤖</span>
            <div>
              <div className="chat-widget__title">AI Trợ giảng</div>
              <div className="chat-widget__subtitle">Hỏi nhanh về bài học</div>
            </div>
          </div>
          <button
            className="chat-widget__close"
            onClick={() => setIsOpen(false)}
            aria-label="Đóng"
          >
            ✕
          </button>
        </div>

        {/* Messages list */}
        <div className="chat-widget__messages">
          {messages.length === 0 && (
            <div className="chat-widget__empty">
              <p>Xin chào! Tôi có thể giúp bạn giải đáp thắc mắc về bài học này.</p>
              <p className="chat-widget__example">Ví dụ: "Giải thích khái niệm này cho tôi" hoặc "Cho ví dụ thực tế"</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-widget__msg chat-widget__msg--${msg.role}`}>
              {/* User bubble */}
              {msg.role === 'user' && (
                <div className="chat-widget__bubble chat-widget__bubble--user">
                  {msg.content}
                </div>
              )}

              {/* AI bubble — answer la markdown, hien thi don gian */}
              {msg.role === 'assistant' && (
                <div className="chat-widget__bubble chat-widget__bubble--ai">
                  <div className="chat-widget__answer">{msg.content}</div>

                  {/* Related lessons */}
                  {msg.related_lessons && msg.related_lessons.length > 0 && (
                    <div className="chat-widget__related">
                      <span className="chat-widget__related-label">Xem thêm:</span>
                      {msg.related_lessons.slice(0, 2).map((lesson, i) => (
                        <a
                          key={i}
                          href={lesson.url}
                          className="chat-widget__related-link"
                          target="_self"
                        >
                          📝 {lesson.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Error bubble */}
              {msg.role === 'error' && (
                <div className="chat-widget__bubble chat-widget__bubble--error">
                  {msg.content}
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator khi dang gui */}
          {sending && (
            <div className="chat-widget__msg chat-widget__msg--assistant">
              <div className="chat-widget__bubble chat-widget__bubble--ai">
                <div className="chat-widget__typing">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="chat-widget__input-area">
          <textarea
            className="chat-widget__textarea"
            placeholder="Nhập câu hỏi... (Enter để gửi)"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={sending}
            rows={2}
            aria-label="Nhập câu hỏi"
          />
          <button
            className="chat-widget__send"
            onClick={handleSend}
            disabled={!inputText.trim() || sending}
            aria-label="Gửi câu hỏi"
          >
            {sending ? '⏳' : '➤'}
          </button>
        </div>
      </div>

      {/* Overlay mờ khi drawer mở (mobile) */}
      {isOpen && (
        <div
          className="chat-widget__overlay"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}
    </>
  )
}

export default ChatWidget
