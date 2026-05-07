import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion, useReducedMotion } from 'framer-motion'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import { toast } from 'react-hot-toast'
import { staggerEditorial, fadeUp, fadeDown } from '@/styles/motion'
import './AuthPages.css'

/* =============================================================================
   LOGIN PAGE — Split-screen Editorial
   LEFT: ink panel with pull-quote  |  RIGHT: form (all logic preserved)
   ============================================================================= */
const LoginPage = () => {
  const [loading, setLoading] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuthStore()
  const shouldReduceMotion = useReducedMotion()

  // Redirect destination after login — preserved exactly
  const from = location.state?.from || '/dashboard'

  const { register, handleSubmit, formState: { errors } } = useForm()

  // Submit logic — unchanged
  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await login(data.email, data.password, rememberMe)
      toast.success('Đăng nhập thành công!')
      navigate(from, { replace: true })
    } catch (error) {
      toast.error(error.message || 'Đăng nhập thất bại!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-split">
      {/* ── LEFT: Editorial ink panel ── */}
      <AuthInkPanel
        shouldReduceMotion={shouldReduceMotion}
        quote="Đầu tư vào tri thức luôn cho lãi suất tốt nhất."
        attribution="Benjamin Franklin"
        tag="Chào mừng trở lại"
      />

      {/* ── RIGHT: Form panel ── */}
      <div className="auth-split__form-side">
        <motion.div
          className="auth-split__form-wrap"
          variants={staggerEditorial}
          initial={shouldReduceMotion ? false : 'hidden'}
          animate="show"
        >
          {/* Back link */}
          <motion.div variants={fadeDown}>
            <Link to="/" className="auth-back-link">
              <BackArrowIcon /> Trang chủ
            </Link>
          </motion.div>

          {/* Header */}
          <motion.div className="auth-form-header" variants={fadeUp}>
            <p className="auth-form-eyebrow">Nền tảng học tập AI</p>
            <h1 className="auth-form-title">Đăng nhập</h1>
            <p className="auth-form-subtitle">
              Chào mừng bạn quay trở lại AI Learning Platform
            </p>
          </motion.div>

          {/* Form — react-hook-form logic unchanged */}
          <motion.form
            className="auth-form"
            onSubmit={handleSubmit(onSubmit)}
            variants={fadeUp}
            noValidate
          >
            <Input
              type="email"
              label="Email"
              placeholder="Nhập địa chỉ email của bạn"
              error={errors.email?.message}
              autoComplete="email"
              {...register('email', {
                required: 'Email là bắt buộc',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Email không hợp lệ',
                },
              })}
            />

            <Input
              type="password"
              label="Mật khẩu"
              placeholder="Nhập mật khẩu của bạn"
              error={errors.password?.message}
              autoComplete="current-password"
              {...register('password', {
                required: 'Mật khẩu là bắt buộc',
              })}
            />

            {/* Remember me + forgot password row */}
            <div className="auth-form-row">
              <label className="auth-checkbox-label">
                <input
                  type="checkbox"
                  className="auth-checkbox-input"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span className="auth-checkmark" aria-hidden="true" />
                Ghi nhớ đăng nhập
              </label>
              <Link to="/auth/forgot-password" className="auth-text-link">
                Quên mật khẩu?
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="auth-submit-btn"
            >
              Đăng nhập
            </Button>
          </motion.form>

          {/* Switch to register */}
          <motion.p className="auth-switch-text" variants={fadeUp}>
            Chưa có tài khoản?{' '}
            <Link to="/auth/register" className="auth-text-link auth-text-link--bold">
              Đăng ký ngay
            </Link>
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}

/* =============================================================================
   SHARED: Editorial ink left panel
   ============================================================================= */
export const AuthInkPanel = ({ shouldReduceMotion, quote, attribution, tag }) => (
  <div className="auth-split__ink-side" aria-hidden="true">
    <motion.div
      className="auth-split__ink-content"
      variants={staggerEditorial}
      initial={shouldReduceMotion ? false : 'hidden'}
      animate="show"
    >
      {/* Brand mark */}
      <motion.div className="auth-ink-brand" variants={fadeDown}>
        <span className="auth-ink-mark">◆</span>
        <span className="auth-ink-logo-text">AI Learning</span>
      </motion.div>

      {/* Ornamental divider */}
      <motion.div className="auth-ink-ornament" variants={fadeUp} aria-hidden="true">
        <span className="auth-ink-ornament-line" />
        <span className="auth-ink-ornament-char">{tag}</span>
        <span className="auth-ink-ornament-line" />
      </motion.div>

      {/* Pull-quote */}
      <motion.blockquote className="auth-ink-quote" variants={fadeUp}>
        <span className="auth-ink-quote-mark" aria-hidden="true">"</span>
        {quote}
      </motion.blockquote>

      {/* Attribution */}
      <motion.footer className="auth-ink-attribution" variants={fadeUp}>
        — {attribution}
      </motion.footer>

      {/* Bottom decorative numerals */}
      <motion.div className="auth-ink-deco" variants={fadeDown} aria-hidden="true">
        <span>01</span>
        <span className="auth-ink-deco-line" />
        <span>Học để tiến bộ</span>
      </motion.div>
    </motion.div>
  </div>
)

/* =============================================================================
   ICONS
   ============================================================================= */
const BackArrowIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="m15 18-6-6 6-6" />
  </svg>
)

export default LoginPage
