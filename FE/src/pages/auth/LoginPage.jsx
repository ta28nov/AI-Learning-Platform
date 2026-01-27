import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import Card, { CardHeader, CardBody, CardFooter } from '@components/ui/Card'
import { toast } from 'react-hot-toast'
import './AuthPages.css'

/**
 * Component LoginPage - Trang dang nhap
 */
const LoginPage = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuthStore()

  // Lay duong dan redirect sau khi dang nhap
  const from = location.state?.from || '/dashboard'

  // React Hook Form
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm()

  // Xu ly submit form
  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await login(data.email, data.password)
      toast.success('Đăng nhập thành công!')
      navigate(from, { replace: true })
    } catch (error) {
      toast.error(error.message || 'Đăng nhập thất bại!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <Card className="auth-card">
          <CardHeader>
            <div className="auth-header">
              <h1>Đăng nhập</h1>
              <p>Chào mừng bạn quay trở lại AI Learning Platform</p>
            </div>
          </CardHeader>

          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
              <Input
                type="email"
                label="Email"
                placeholder="Nhập địa chỉ email của bạn"
                error={errors.email?.message}
                {...register('email', {
                  required: 'Email là bắt buộc',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email không hợp lệ'
                  }
                })}
              />

              <Input
                type="password"
                label="Mật khẩu"
                placeholder="Nhập mật khẩu của bạn"
                error={errors.password?.message}
                {...register('password', {
                  required: 'Mật khẩu là bắt buộc'
                })}
              />

              <div className="forgot-password">
                <Link to="/auth/forgot-password">
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
            </form>
          </CardBody>

          <CardFooter>
            <div className="auth-footer">
              <p>
                Chưa có tài khoản?{' '}
                <Link to="/auth/register" className="auth-link">
                  Đăng ký ngay
                </Link>
              </p>
            </div>
          </CardFooter>
        </Card>

        <div className="auth-back-home">
          <Link to="/">
            ← Quay về trang chủ
          </Link>
        </div>
      </div>
    </div>
  )
}

export default LoginPage