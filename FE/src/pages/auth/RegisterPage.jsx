import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@stores/authStore'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import Card, { CardHeader, CardBody, CardFooter } from '@components/ui/Card'
import { toast } from 'react-hot-toast'
import './AuthPages.css'

/**
 * Component RegisterPage - Trang dang ky
 */
const RegisterPage = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { register: registerUser } = useAuthStore()

  // React Hook Form
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm()

  // Watch password de validate confirm password
  const password = watch('password')

  // Xu ly submit form
  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await registerUser({
        full_name: data.fullName,
        email: data.email,
        password: data.password
      })
      toast.success('Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.')
      navigate('/auth/verify-email', { 
        state: { email: data.email } 
      })
    } catch (error) {
      toast.error(error.message || 'Đăng ký thất bại!')
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
              <h1>Đăng ký</h1>
              <p>Tạo tài khoản mới để bắt đầu hành trình học tập</p>
            </div>
          </CardHeader>

          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
              <Input
                type="text"
                label="Họ và tên"
                placeholder="Nhập họ và tên đầy đủ"
                error={errors.fullName?.message}
                {...register('fullName', {
                  required: 'Họ và tên là bắt buộc',
                  minLength: {
                    value: 2,
                    message: 'Họ và tên phải có ít nhất 2 ký tự'
                  }
                })}
              />

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
                placeholder="Tạo mật khẩu mạnh"
                error={errors.password?.message}
                {...register('password', {
                  required: 'Mật khẩu là bắt buộc',
                  minLength: {
                    value: 8,
                    message: 'Mật khẩu phải có ít nhất 8 ký tự'
                  }
                })}
              />

              <Input
                type="password"
                label="Xác nhận mật khẩu"
                placeholder="Nhập lại mật khẩu"
                error={errors.confirmPassword?.message}
                {...register('confirmPassword', {
                  required: 'Vui lòng xác nhận mật khẩu',
                  validate: value => 
                    value === password || 'Mật khẩu xác nhận không khớp'
                })}
              />

              <div className="form-terms">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    {...register('acceptTerms', {
                      required: 'Bạn phải đồng ý với điều khoản sử dụng'
                    })}
                  />
                  <span className="checkmark"></span>
                  Tôi đồng ý với{' '}
                  <Link to="/terms" className="terms-link">
                    Điều khoản sử dụng
                  </Link>{' '}
                  và{' '}
                  <Link to="/privacy" className="terms-link">
                    Chính sách bảo mật
                  </Link>
                </label>
                {errors.acceptTerms && (
                  <div className="error-message">
                    {errors.acceptTerms.message}
                  </div>
                )}
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={loading}
                className="auth-submit-btn"
              >
                Đăng ký
              </Button>
            </form>
          </CardBody>

          <CardFooter>
            <div className="auth-footer">
              <p>
                Đã có tài khoản?{' '}
                <Link to="/auth/login" className="auth-link">
                  Đăng nhập ngay
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

export default RegisterPage