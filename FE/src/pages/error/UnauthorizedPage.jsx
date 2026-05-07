import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import Button from '@components/ui/Button'
import './ErrorPages.css'

const LockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
)

/**
 * UnauthorizedPage — Trang 403 không có quyền truy cập
 * Route: /unauthorized
 */
const UnauthorizedPage = () => {
  return (
    <div className="error-page error-page--403">
      <div className="error-page__bg">
        <div className="error-orb error-orb--1" />
        <div className="error-orb error-orb--2" />
      </div>
      <motion.div
        className="error-content"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.65, 0, 0.35, 1] }}
      >
        <div className="error-code">
          <span className="error-code__digit">4</span>
          <span className="error-code__circle error-code__circle--red">
            <LockIcon />
          </span>
          <span className="error-code__digit">3</span>
        </div>
        <h1 className="error-title">Không có quyền truy cập</h1>
        <p className="error-desc">
          Xin lỗi, bạn không có quyền truy cập vào trang này.
          Vui lòng liên hệ quản trị viên nếu bạn nghĩ đây là lỗi.
        </p>
        <div className="error-actions">
          <Link to="/dashboard">
            <Button variant="primary" size="lg">Về Dashboard</Button>
          </Link>
          <Link to="/">
            <Button variant="outline" size="lg">Về trang chủ</Button>
          </Link>
        </div>
      </motion.div>
    </div>
  )
}

export default UnauthorizedPage
