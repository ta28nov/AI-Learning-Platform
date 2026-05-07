import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import Button from '@components/ui/Button'
import { fadeUp, staggerEditorial } from '@/styles/motion'
import './AuthPages.css'

/**
 * ResetPasswordPage — Editorial empty-state stub
 * BE endpoint không tồn tại; stub giữ nguyên — không sửa authService.js
 * Route: /auth/reset-password
 */
const ResetPasswordPage = () => {
  const shouldReduceMotion = useReducedMotion()

  return (
    <div className="auth-stub-page">
      <motion.div
        className="auth-stub-card"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        animate="show"
      >
        <motion.div className="auth-stub-icon" variants={fadeUp} aria-hidden="true">
          <KeyIcon />
        </motion.div>

        <motion.div variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <p className="auth-stub-eyebrow">Đặt lại mật khẩu</p>
          <h1 className="auth-stub-title">Tính năng chưa khả dụng</h1>
          <p className="auth-stub-desc">
            Chức năng đặt lại mật khẩu hiện chưa được backend hỗ trợ.
            Vui lòng quay lại trang đăng nhập.
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

const KeyIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4" />
  </svg>
)

export default ResetPasswordPage
