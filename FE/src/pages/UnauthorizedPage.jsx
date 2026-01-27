import React from 'react'
import { Link } from 'react-router-dom'
import Button from '@components/ui/Button'
import './ErrorPages.css'

/**
 * Component UnauthorizedPage - Trang khong co quyen truy cap
 */
const UnauthorizedPage = () => {
  return (
    <div className="error-page">
      <div className="error-container">
        <div className="error-content">
          <div className="error-illustration">
            <div className="error-code">403</div>
          </div>
          
          <h1 className="error-title">
            Không có quyền truy cập
          </h1>
          
          <p className="error-description">
            Xin lỗi, bạn không có quyền truy cập vào trang này. 
            Vui lòng liên hệ quản trị viên nếu bạn nghĩ đây là lỗi.
          </p>
          
          <div className="error-actions">
            <Link to="/dashboard">
              <Button variant="primary" size="lg">
                Về dashboard
              </Button>
            </Link>
            <Link to="/">
              <Button variant="outline" size="lg">
                Về trang chủ
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UnauthorizedPage