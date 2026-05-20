import { useState } from 'react'
import chatService from '@services/chatService'
import Button from '@components/ui/Button'
import './QuizWrongAnswerExplainer.css'

/**
 * AI giải thích câu sai — dùng POST /chat/course/{courseId} với dữ liệu kết quả quiz thật.
 */
const QuizWrongAnswerExplainer = ({ courseId, quizTitle, wrongItems = [] }) => {
  const [loading, setLoading] = useState(false)
  const [explanation, setExplanation] = useState('')
  const [error, setError] = useState('')

  if (!courseId || wrongItems.length === 0) return null

  const buildPrompt = () => {
    const lines = wrongItems.map((item, idx) => {
      const q = item.question_content || item.question_text || `Câu ${idx + 1}`
      return [
        `${idx + 1}. ${q}`,
        `   Đáp án của tôi: ${item.student_answer || '(trống)'}`,
        `   Đáp án đúng: ${item.correct_answer || '—'}`,
        item.explanation ? `   Ghi chú có sẵn: ${item.explanation}` : null,
      ].filter(Boolean).join('\n')
    }).join('\n\n')

    return (
      `Tôi vừa làm quiz «${quizTitle || 'này'}» và trả lời sai ${wrongItems.length} câu. `
      + `Hãy giải thích ngắn gọn từng câu sai (tại sao đáp án đúng, lỗi thường gặp), `
      + `không chỉ đọc lại đáp án. Dùng tiếng Việt, bullet rõ ràng:\n\n${lines}`
    )
  }

  const handleExplain = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await chatService.sendMessage(courseId, {
        question: buildPrompt(),
        context_type: 'general',
      })
      setExplanation(data?.answer || data?.ai_response || 'Không nhận được phản hồi từ AI.')
    } catch (err) {
      setError(err?.message || 'Không thể kết nối AI. Vui lòng thử lại.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="quiz-wrong-ai">
      <div className="quiz-wrong-ai__head">
        <h3 className="quiz-wrong-ai__title">Giải thích câu sai ({wrongItems.length})</h3>
        <Button variant="outline" size="sm" loading={loading} onClick={handleExplain} disabled={loading}>
          Giải thích bằng AI
        </Button>
      </div>
      {error && <p className="quiz-wrong-ai__error">{error}</p>}
      {explanation && (
        <div className="quiz-wrong-ai__body">
          {explanation.split('\n').map((line, i) => (
            <p key={i}>{line || '\u00A0'}</p>
          ))}
        </div>
      )}
    </div>
  )
}

export default QuizWrongAnswerExplainer
