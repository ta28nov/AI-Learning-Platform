import React from 'react'
import { useParams } from 'react-router-dom'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component QuizDetailPage - Trang chi tiết quiz
 */
const QuizDetailPage = () => {
  const { quizId } = useParams()

  return (
    <div className="quiz-detail-page">
      <div className="page-header">
        <h1>Chi tiết Quiz</h1>
        <p>Quiz ID: {quizId}</p>
      </div>

      <div className="quiz-detail-content">
        <Card>
          <CardHeader>
            <h3>Thông tin Quiz</h3>
          </CardHeader>
          <CardBody>
            <div className="quiz-info">
              <div className="info-item">
                <label>Tên quiz:</label>
                <span>Đang tải...</span>
              </div>
              <div className="info-item">
                <label>Số câu hỏi:</label>
                <span>Đang tải...</span>
              </div>
              <div className="info-item">
                <label>Thời gian:</label>
                <span>Đang tải...</span>
              </div>
            </div>
            <div className="quiz-actions">
              <Button>Bắt đầu làm bài</Button>
              <Button variant="outline">Xem kết quả cũ</Button>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h3>Hướng dẫn</h3>
          </CardHeader>
          <CardBody>
            <ul>
              <li>Đọc kỹ câu hỏi trước khi trả lời</li>
              <li>Chọn đáp án đúng nhất</li>
              <li>Có thể quay lại câu hỏi trước đó</li>
              <li>Nhấn "Nộp bài" khi hoàn thành</li>
            </ul>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default QuizDetailPage