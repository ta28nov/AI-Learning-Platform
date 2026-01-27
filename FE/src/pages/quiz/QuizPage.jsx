import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'

/**
 * Component QuizPage - Trang danh sách quiz
 */
const QuizPage = () => {
  return (
    <div className="quiz-page">
      <div className="page-header">
        <h1>Bài Quiz</h1>
        <p>Thực hành với các bài quiz</p>
      </div>

      <div className="quiz-content">
        <div className="quiz-grid">
          <Card>
            <CardHeader>
              <h3>Quiz cơ bản</h3>
            </CardHeader>
            <CardBody>
              <p>Bài quiz kiểm tra kiến thức cơ bản</p>
              <div className="quiz-info">
                <span>10 câu hỏi</span>
                <span>15 phút</span>
              </div>
              <Button>Bắt đầu làm</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h3>Quiz nâng cao</h3>
            </CardHeader>
            <CardBody>
              <p>Bài quiz kiểm tra kiến thức nâng cao</p>
              <div className="quiz-info">
                <span>20 câu hỏi</span>
                <span>30 phút</span>
              </div>
              <Button>Bắt đầu làm</Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default QuizPage