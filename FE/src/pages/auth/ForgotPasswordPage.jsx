import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import Button from '@components/ui/Button'
import { fadeUp, staggerEditorial } from '@/styles/motion'
import './AuthPages.css'

/**
 * ForgotPasswordPage — Editorial empty-state stub
 * BE endpoint không tồn tại; logic "throw" vẫn nằm trong authService.js (không sửa)
 * Route: /auth/forgot-password
 */
const ForgotPasswordPage = () => {
  const shouldReduceMotion = useReducedMotion()

  return (
    <div className="auth-stub-page">
      <motion.div
        className="auth-stub-card"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        animate="show"
      >
        {/* Icon */}
        <motion.div className="auth-stub-icon" variants={fadeUp} aria-hidden="true">
          <LockIcon />
        </motion.div>

        <motion.div variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <p className="auth-stub-eyebrow">Quên mật khẩu</p>
          <h1 className="auth-stub-title">Tính năng chưa khả dụng</h1>
          <p className="auth-stub-desc">
            Chức năng quên mật khẩu hiện chưa được backend hỗ trợ.
            Vui lòng đăng nhập bằng tài khoản demo hoặc liên hệ quản trị viên.
          </p>
        </motion.div>

        <motion.div className="auth-stub-actions" variants={fadeUp}>
          <Link to="/auth/login">
            <Button variant="primary">Quay lại đăng nhập</Button>
          </Link>
          <Link to="/" className="auth-stub-back">← Trang chủ</Link>
        </motion.div>
      </motion.div>
    </div>
  )
}

const LockIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </svg>
)

export default ForgotPasswordPage
