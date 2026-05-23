import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { motion, useReducedMotion } from 'framer-motion'
import toast from 'react-hot-toast'
import authService from '@services/authService'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import { staggerEditorial } from '@/styles/motion'
import './AuthPages.css'

/**
 * ResetPasswordPage — POST /auth/reset-password?token=...
 * Route: /auth/reset-password
 */
const ResetPasswordPage = () => {
  const [loading, setLoading] = useState(false)
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const shouldReduceMotion = useReducedMotion()
  const token = searchParams.get('token') || ''

  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async ({ password }) => {
    if (!token) {
      toast.error('Thiếu token đặt lại mật khẩu')
      return
    }
    setLoading(true)
    try {
      await authService.resetPassword(token, password)
      toast.success('Đặt lại mật khẩu thành công!')
      navigate('/auth/login', { replace: true })
    } catch (error) {
      toast.error(error.message || 'Không thể đặt lại mật khẩu')
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
      <motion.div className="auth-stub-card" style={{ maxWidth: 420 }}>
        <p className="auth-stub-eyebrow">Đặt lại mật khẩu</p>
        <h1 className="auth-stub-title">Mật khẩu mới</h1>
        {!token ? (
          <p className="auth-stub-desc">Link không hợp lệ. Yêu cầu quên mật khẩu lại.</p>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="auth-form" noValidate>
            <Input
              type="password"
              label="Mật khẩu mới"
              placeholder="≥ 8 ký tự, chữ hoa, số, ký tự đặc biệt"
              error={errors.password?.message}
              {...register('password', {
                required: 'Mật khẩu là bắt buộc',
                minLength: { value: 8, message: 'Tối thiểu 8 ký tự' },
              })}
            />
            <Button type="submit" loading={loading} style={{ width: '100%' }}>
              Đặt lại mật khẩu
            </Button>
          </form>
        )}
        <Link to="/auth/login" className="auth-stub-back" style={{ marginTop: '1rem' }}>
          ← Đăng nhập
        </Link>
      </motion.div>
    </motion.div>
  )
}

export default ResetPasswordPage
