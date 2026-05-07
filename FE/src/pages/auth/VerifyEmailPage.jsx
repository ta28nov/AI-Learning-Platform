import { Link, useNavigate } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import Button from '@components/ui/Button'
import { fadeUp, staggerEditorial } from '@/styles/motion'
import './AuthPages.css'

/**
 * VerifyEmailPage — Editorial empty-state stub
 * BE endpoint không tồn tại; stub giữ nguyên — không sửa authService.js
 * Route: /auth/verify-email
 */
const VerifyEmailPage = () => {
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()

  // Preserved original navigation handler
  const handleGoToLogin = () => navigate('/auth/login')

  return (
    <div className="auth-stub-page">
      <motion.div
        className="auth-stub-card"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        animate="show"
      >
        <motion.div className="auth-stub-icon" variants={fadeUp} aria-hidden="true">
          <MailIcon />
        </motion.div>

        <motion.div variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <p className="auth-stub-eyebrow">Xác thực email</p>
          <h1 className="auth-stub-title">Tính năng chưa khả dụng</h1>
          <p className="auth-stub-desc">
            Chức năng xác thực email chưa được backend hỗ trợ trong phiên bản hiện tại.
            Bạn có thể tiếp tục sử dụng nền tảng bằng cách đăng nhập.
          </p>
        </motion.div>

        <motion.div className="auth-stub-actions" variants={fadeUp}>
          <Button variant="primary" onClick={handleGoToLogin}>
            Quay lại đăng nhập
          </Button>
          <Link to="/" className="auth-stub-back">← Trang chủ</Link>
        </motion.div>
      </motion.div>
    </div>
  )
}

const MailIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2" />
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
  </svg>
)

export default VerifyEmailPage
