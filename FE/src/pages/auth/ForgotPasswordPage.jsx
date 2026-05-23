import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import authService from '@services/authService'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import { fadeUp, staggerEditorial } from '@/styles/motion'
import './AuthPages.css'

/**
 * ForgotPasswordPage — POST /auth/forgot-password
 * Route: /auth/forgot-password
 */
const ForgotPasswordPage = () => {
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const shouldReduceMotion = useReducedMotion()
  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async ({ email }) => {
    setLoading(true)
    try {
      await authService.forgotPassword(email)
      setSent(true)
      toast.success('Nếu email tồn tại, bạn sẽ nhận hướng dẫn đặt lại mật khẩu.')
    } catch (error) {
      toast.error(error.message || 'Không thể gửi yêu cầu')
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      className="auth-stub-page"
      variants={staggerEditorial}
      initial={shouldReduceMotion ? false : 'hidden'}
      animate="show"
    >
      <div className="auth-stub-card" style={{ maxWidth: 420 }}>
        <p className="auth-stub-eyebrow">Quên mật khẩu</p>
        <h1 className="auth-stub-title">Khôi phục mật khẩu</h1>
        {sent ? (
          <p className="auth-stub-desc">
            Kiểm tra hộp thư (hoặc liên hệ quản trị viên). Trong môi trường dev, token có thể
            trả về từ API khi <code>TESTING=true</code>.
          </p>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="auth-form" noValidate>
            <Input
              type="email"
              label="Email"
              placeholder="Email đã đăng ký"
              error={errors.email?.message}
              {...register('email', {
                required: 'Email là bắt buộc',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Email không hợp lệ',
                },
              })}
            />
            <Button type="submit" loading={loading} style={{ width: '100%' }}>
              Gửi yêu cầu
            </Button>
          </form>
        )}
        <Link to="/auth/login" className="auth-stub-back" style={{ marginTop: '1rem' }}>
          ← Quay lại đăng nhập
        </Link>
      </div>
    </motion.div>
  )
}

export default ForgotPasswordPage
