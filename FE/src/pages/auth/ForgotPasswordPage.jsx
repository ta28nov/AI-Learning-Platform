import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import Card, { CardHeader, CardBody, CardFooter } from '@components/ui/Card'
import { toast } from 'react-hot-toast'
import './AuthPages.css'

/**
 * Component ForgotPasswordPage - Trang quen mat khau
 */
const ForgotPasswordPage = () => {
  const [loading, setLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)

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
      // Goi API forgot password
      // await authService.forgotPassword(data.email)
      
      // Gia lap API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setEmailSent(true)
      toast.success('Email khôi phục mật khẩu đã được gửi!')
    } catch (error) {
      toast.error(error.message || 'Có lỗi xảy ra, vui lòng thử lại!')
    } finally {
      setLoading(false)
    }
  }

  if (emailSent) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <Card className="auth-card">
            <CardHeader>
              <div className="auth-header">
                <div className="success-icon">
                  <CheckIcon />
                </div>
                <h1>Email đã được gửi</h1>
                <p>Chúng tôi đã gửi hướng dẫn khôi phục mật khẩu đến email của bạn</p>
              </div>
            </CardHeader>

            <CardBody>
              <div className="email-sent-content">
                <p>
                  Vui lòng kiểm tra hộp thư đến và làm theo hướng dẫn để đặt lại mật khẩu.
                  Nếu không thấy email, hãy kiểm tra thư mục spam.
                </p>
                <div className="resend-info">
                  <p>Chưa nhận được email?</p>
                  <Button 
                    variant="ghost" 
                    onClick={() => setEmailSent(false)}
                  >
                    Gửi lại
                  </Button>
                </div>
              </div>
            </CardBody>

            <CardFooter>
              <div className="auth-footer">
                <Link to="/auth/login" className="auth-link">
                  ← Quay lại đăng nhập
                </Link>
              </div>
            </CardFooter>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <Card className="auth-card">
          <CardHeader>
            <div className="auth-header">
              <h1>Quên mật khẩu</h1>
              <p>Nhập email của bạn để nhận hướng dẫn khôi phục mật khẩu</p>
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

              <Button
                type="submit"
                variant="primary"
                size="lg"
                loading={loading}
                className="auth-submit-btn"
              >
                Gửi email khôi phục
              </Button>
            </form>
          </CardBody>

          <CardFooter>
            <div className="auth-footer">
              <p>
                Nhớ lại mật khẩu?{' '}
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

// Success Icon
const CheckIcon = () => (
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" fill="var(--success)" stroke="var(--success)"></circle>
    <path d="M9 12l2 2 4-4" stroke="white" strokeWidth="2"></path>
  </svg>
)

export default ForgotPasswordPage