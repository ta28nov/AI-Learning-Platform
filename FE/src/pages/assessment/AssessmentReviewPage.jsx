import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import assessmentService from '@services/assessmentService'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import StateView from '@components/ui/StateView'
import AILoadingState from '@components/ui/AILoadingState'
import './AssessmentReviewPage.css'

function formatWhen(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('vi-VN')
  } catch {
    return '—'
  }
}

/**
 * Xem lai de bai + dap an da nop (read-only)
 * Route: /dashboard/assessment/:sessionId/review
 */
const AssessmentReviewPage = () => {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const res = await assessmentService.getReview(sessionId)
        setData(res)
      } catch (e) {
        toast.error(e.message || 'Không thể tải bài xem lại')
        setData(null)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [sessionId])

  if (loading) {
    return (
      <AILoadingState
        title="Đang tải bài làm"
        message="Đang đồng bộ đề bài và đáp án bạn đã nộp."
        steps={['Đang xác thực phiên làm bài…', 'Đang nạp câu hỏi…']}
      />
    )
  }

  if (!data || !data.items?.length) {
    return (
      <StateView
        type="empty"
        title="Không có dữ liệu xem lại"
        message="Phiên chưa chấm xong hoặc không có câu trả lời được lưu."
        actionLabel="Về trang đánh giá"
        onAction={() => navigate('/dashboard/assessment')}
      />
    )
  }

  return (
    <div className="assessment-review-page">
      <div className="page-header page-header--hero arv-header">
        <div className="arv-header__top">
          <Button variant="outline" size="sm" onClick={() => navigate(`/dashboard/assessment/${sessionId}/results`)}>
            ← Kết quả phân tích
          </Button>
        </div>
        <h1>Xem lại bài đánh giá</h1>
        <p className="arv-meta">
          <strong>{data.subject}</strong>
          <span className="arv-dot">·</span>
          {data.level}
          <span className="arv-dot">·</span>
          {data.total_questions} câu
          {data.overall_score != null && (
            <>
              <span className="arv-dot">·</span>
              Điểm: <strong>{Math.round(data.overall_score)}</strong>
            </>
          )}
        </p>
        <p className="arv-sub">Hoàn tất chấm: {formatWhen(data.evaluated_at)}</p>
      </div>

      <div className="arv-list">
        {data.items.map((item, idx) => (
          <Card
            key={item.question_id || idx}
            className={`arv-card${item.is_correct === true ? ' arv-card--correct' : ''}${item.is_correct === false ? ' arv-card--incorrect' : ''}`}
          >
            <CardHeader>
              <div className="arv-q-head">
                <span className="arv-q-num">Câu {idx + 1}</span>
                {item.is_correct === true && (
                  <span className="arv-verdict arv-verdict--ok" aria-label="Đúng">
                    ✓ Đúng
                  </span>
                )}
                {item.is_correct === false && (
                  <span className="arv-verdict arv-verdict--bad" aria-label="Sai">
                    ✗ Sai
                  </span>
                )}
                {item.is_correct == null && (
                  <span className="arv-verdict arv-verdict--na">Không có kết quả chấm</span>
                )}
                {item.difficulty && (
                  <span className={`arv-badge arv-badge--${item.difficulty}`}>{item.difficulty}</span>
                )}
                {item.skill_tag && <span className="arv-skill">{item.skill_tag}</span>}
                {item.points != null && <span className="arv-points">{item.points} điểm</span>}
              </div>
            </CardHeader>
            <CardBody>
              <p className="arv-q-text">{item.question_text}</p>

              {item.question_type === 'multiple_choice' && item.options?.length > 0 && (
                <ul className="arv-options-readonly">
                  {item.options.map((opt, oi) => (
                    <li
                      key={oi}
                      className={
                        item.selected_option === oi ? 'arv-opt arv-opt--picked' : 'arv-opt'
                      }
                    >
                      <span className="arv-opt-letter">{String.fromCharCode(65 + oi)}</span>
                      <span>{opt}</span>
                    </li>
                  ))}
                </ul>
              )}

              {item.grading_note && (
                <p className="arv-grade-note">{item.grading_note}</p>
              )}

              <div className="arv-your-answer">
                <span className="arv-label">Đáp án của bạn</span>
                {item.selected_option_text != null && item.selected_option_text !== '' ? (
                  <p className="arv-answer-text">
                    <strong>{String.fromCharCode(65 + (item.selected_option ?? 0))}.</strong>{' '}
                    {item.selected_option_text}
                  </p>
                ) : (
                  <p className="arv-answer-text">{item.answer_content || '(Chưa trả lời)'}</p>
                )}
              </div>

              {item.time_taken_seconds > 0 && (
                <p className="arv-time">Thời gian câu này: ~{item.time_taken_seconds}s</p>
              )}

              {item.correct_answer_hint && (
                <details className="arv-hint">
                  <summary>Gợi ý tham khảo (đáp án)</summary>
                  <p>{item.correct_answer_hint}</p>
                </details>
              )}
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="arv-footer-actions">
        <Button variant="outline" onClick={() => navigate('/dashboard/assessment')}>
          Lịch sử & bài mới
        </Button>
        <Button onClick={() => navigate(`/dashboard/recommendations?session_id=${sessionId}`)}>
          Xem lộ trình học tập
        </Button>
      </div>
    </div>
  )
}

export default AssessmentReviewPage
