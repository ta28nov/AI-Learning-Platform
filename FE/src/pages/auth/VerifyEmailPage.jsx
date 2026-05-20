import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import authService from '@services/authService'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import StateView from '@components/ui/StateView'
import { fadeUp, staggerEditorial } from '@/styles/motion'
import './AuthPages.css'

/**
 * VerifyEmailPage — POST /auth/verify-email?token=... · POST /auth/resend-verification
 * Route: /auth/verify-email
 */
const VerifyEmailPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()
  const token = searchParams.get('token') || ''

  const [phase, setPhase] = useState(token ? 'verifying' : 'form')
  const [verifyError, setVerifyError] = useState('')
  const [resendLoading, setResendLoading] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm()

  useEffect(() => {
    if (!token) return
    let cancelled = false
    const run = async () => {
      try {
        await authService.verifyEmail(token)
        if (!cancelled) setPhase('success')
      } catch (err) {
        if (!cancelled) {
          setVerifyError(err?.message || 'Token không hợp lệ hoặc đã hết hạn')
          setPhase('error')
        }
      }
    }
    run()
    return () => { cancelled = true }
  }, [token])

  const onResend = async ({ email }) => {
    setResendLoading(true)
    try {
      await authService.resendVerificationEmail(email)
      toast.success('Nếu email hợp lệ, bạn sẽ nhận link xác thực (kiểm tra hộp thư).')
    } catch (err) {
      toast.error(err?.message || 'Không thể gửi lại email xác thực')
    } finally {
      setResendLoading(false)
    }
  }

  return (
    <div className="auth-stub-page">
      <motion.div
        className="auth-stub-card"
        variants={staggerEditorial}
        initial={shouldReduceMotion ? false : 'hidden'}
        animate="show"
        style={{ maxWidth: 440 }}
      >
        <motion.div className="auth-stub-icon" variants={fadeUp} aria-hidden="true">
          <MailIcon />
        </motion.div>

        <motion.div variants={fadeUp} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <p className="auth-stub-eyebrow">Xác thực email</p>
          <h1 className="auth-stub-title">
            {phase === 'success' ? 'Email đã xác thực' : 'Xác nhận tài khoản'}
          </h1>
        </motion.div>

        {phase === 'verifying' && (
          <StateView type="loading" message="Đang xác thực email…" />
        )}

        {phase === 'success' && (
          <motion.div variants={fadeUp}>
            <p className="auth-stub-desc">
              Tài khoản của bạn đã được xác thực. Bạn có thể đăng nhập và bắt đầu học.
            </p>
            <div className="auth-stub-actions">
              <Button onClick={() => navigate('/auth/login', { replace: true })}>
                Đăng nhập
              </Button>
            </div>
          </motion.div>
        )}

        {phase === 'error' && (
          <motion.div variants={fadeUp}>
            <StateView type="error" title="Không xác thực được" message={verifyError} />
            <p className="auth-stub-desc" style={{ marginTop: '1rem' }}>
              Yêu cầu gửi lại link bên dưới.
            </p>
          </motion.div>
        )}

        {(phase === 'form' || phase === 'error') && (
          <motion.form
            variants={fadeUp}
            className="auth-form"
            onSubmit={handleSubmit(onResend)}
            noValidate
          >
            <p className="auth-stub-desc">
              {token
                ? 'Link có thể đã hết hạn. Nhập email để nhận link mới.'
                : 'Nhập email đã đăng ký để nhận link xác thực.'}
            </p>
            <Input
              type="email"
              label="Email"
              placeholder="email@example.com"
              error={errors.email?.message}
              {...register('email', {
                required: 'Nhập email',
                pattern: {
                  value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: 'Email không hợp lệ',
                },
              })}
            />
            <Button type="submit" loading={resendLoading} style={{ width: '100%' }}>
              Gửi lại link xác thực
            </Button>
          </motion.form>
        )}

        <motion.div className="auth-stub-actions" variants={fadeUp}>
          <Link to="/auth/login" className="auth-stub-back">← Đăng nhập</Link>
          <Link to="/" className="auth-stub-back">Trang chủ</Link>
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
