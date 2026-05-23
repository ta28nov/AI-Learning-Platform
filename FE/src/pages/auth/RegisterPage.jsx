import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion, useReducedMotion } from 'framer-motion'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import toast from 'react-hot-toast'
import { staggerEditorial, fadeUp, fadeDown } from '@/styles/motion'
import { AuthInkPanel } from './LoginPage'
import SocialAuthButtons from '@components/auth/SocialAuthButtons'
import './AuthPages.css'

/* =============================================================================
   REGISTER PAGE — Split-screen Editorial
   LEFT: ink panel with pull-quote  |  RIGHT: form (all logic preserved)
   ============================================================================= */
const RegisterPage = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { register: registerUser } = useAuthStore()
  const shouldReduceMotion = useReducedMotion()

  const { register, handleSubmit, watch, formState: { errors } } = useForm()

  // Watch password for confirm-password validation — unchanged
  const password = watch('password')

  // Submit logic — unchanged
  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await registerUser({
        full_name: data.fullName,
        email: data.email,
        password: data.password,
      })
      toast.success('Đăng ký thành công! Vui lòng đăng nhập.')
      navigate('/auth/login', { state: { email: data.email } })
    } catch (error) {
      toast.error(error.message || 'Đăng ký thất bại!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-split auth-split--register">
      {/* ── LEFT: Editorial ink panel ── */}
      <AuthInkPanel
        shouldReduceMotion={shouldReduceMotion}
        quote="Hành trình vạn dặm bắt đầu từ một bước chân. Bước chân đầu tiên của bạn bắt đầu hôm nay."
        attribution="Lão Tử"
        tag="Tạo tài khoản"
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
            <h1 className="auth-form-title">Đăng ký</h1>
            <p className="auth-form-subtitle">
              Tạo tài khoản mới để bắt đầu hành trình học tập
            </p>
          </motion.div>

          <motion.div variants={fadeUp}>
            <SocialAuthButtons mode="register" />
          </motion.div>

          {/* Form — react-hook-form logic unchanged */}
          <motion.form
            className="auth-form"
            onSubmit={handleSubmit(onSubmit)}
            variants={fadeUp}
            noValidate
          >
            <Input
              type="text"
              label="Họ và tên"
              placeholder="Nhập họ và tên đầy đủ (ít nhất 2 từ)"
              error={errors.fullName?.message}
              autoComplete="name"
              {...register('fullName', {
                required: 'Họ và tên là bắt buộc',
                validate: (v) => {
                  const words = v.trim().split(/\s+/).filter(Boolean)
                  if (words.length < 2) return 'Vui lòng nhập đầy đủ họ và tên (ít nhất 2 từ)'
                  return true
                },
              })}
            />

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
              placeholder="Tạo mật khẩu mạnh (≥ 8 ký tự, chữ hoa, số)"
              error={errors.password?.message}
              autoComplete="new-password"
              {...register('password', {
                required: 'Mật khẩu là bắt buộc',
                minLength: { value: 8, message: 'Mật khẩu phải có ít nhất 8 ký tự' },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?])/,
                  message: 'Mật khẩu cần có chữ hoa, chữ thường, số và ký tự đặc biệt',
                },
              })}
            />

            <Input
              type="password"
              label="Xác nhận mật khẩu"
              placeholder="Nhập lại mật khẩu"
              error={errors.confirmPassword?.message}
              autoComplete="new-password"
              {...register('confirmPassword', {
                required: 'Vui lòng xác nhận mật khẩu',
                validate: (value) => value === password || 'Mật khẩu xác nhận không khớp',
              })}
            />

            {/* Terms checkbox */}
            <div className="auth-form-terms">
              <label className="auth-checkbox-label">
                <input
                  type="checkbox"
                  className="auth-checkbox-input"
                  {...register('acceptTerms', {
                    required: 'Bạn phải đồng ý với điều khoản sử dụng',
                  })}
                />
                <span className="auth-checkmark" aria-hidden="true" />
                <span>
                  Tôi đồng ý với{' '}
                  <Link to="/terms" className="auth-text-link">Điều khoản sử dụng</Link>
                  {' '}và{' '}
                  <Link to="/privacy" className="auth-text-link">Chính sách bảo mật</Link>
                </span>
              </label>
              {errors.acceptTerms && (
                <p className="auth-field-error" role="alert">{errors.acceptTerms.message}</p>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="auth-submit-btn"
            >
              Tạo tài khoản
            </Button>
          </motion.form>

          {/* Switch to login */}
          <motion.p className="auth-switch-text" variants={fadeUp}>
            Đã có tài khoản?{' '}
            <Link to="/auth/login" className="auth-text-link auth-text-link--bold">
              Đăng nhập ngay
            </Link>
          </motion.p>
        </motion.div>
      </div>
    </div>
  )
}

const BackArrowIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="m15 18-6-6 6-6" />
  </svg>
)

export default RegisterPage
