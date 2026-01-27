import React, { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'
import Card, { CardHeader, CardBody, CardFooter } from '@components/ui/Card'
import { toast } from 'react-hot-toast'
import './AuthPages.css'

/**
 * Component ResetPasswordPage - Trang đặt lại mật khẩu
 */
const ResetPasswordPage = () => {
  const [loading, setLoading] = useState(false)
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  // React Hook Form
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm()

  const watchPassword = watch('password')

  // Xu ly submit form
  const onSubmit = async (data) => {
    setLoading(true)
    try {
      if (!token) {
        throw new Error('Token không hợp lệ')
      }

      // Goi API reset password
      // await authService.resetPassword({
      //   token,
      //   password: data.password
      // })
      
      // Gia lap API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      toast.success('Đặt lại mật khẩu thành công!')
      navigate('/auth/login')
    } catch (error) {
      toast.error(error.message || 'Có lỗi xảy ra, vui lòng thử lại!')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <Card className="auth-card">
            <CardHeader>
              <div className="auth-header">
                <div className="error-icon">
                  <i className="fas fa-exclamation-triangle"></i>
                </div>
                <h1>Token không hợp lệ</h1>
                <p>Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn</p>
              </div>
            </CardHeader>
            <CardFooter>
              <div className="auth-footer">
                <Link to="/auth/forgot-password" className="text-link">
                  Yêu cầu đặt lại mật khẩu mới
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
              <div className="auth-icon">
                <i className="fas fa-key"></i>
              </div>
              <h1>Đặt lại mật khẩu</h1>
              <p>Nhập mật khẩu mới cho tài khoản của bạn</p>
            </div>
          </CardHeader>

          <CardBody>
            <form onSubmit={handleSubmit(onSubmit)} className="auth-form">
              <div className="form-group">
                <Input
                  type="password"
                  placeholder="Mật khẩu mới"
                  {...register('password', {
                    required: 'Vui lòng nhập mật khẩu',
                    minLength: {
                      value: 6,
                      message: 'Mật khẩu phải có ít nhất 6 ký tự'
                    },
                    pattern: {
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                      message: 'Mật khẩu phải có ít nhất 1 chữ hoa, 1 chữ thường và 1 số'
                    }
                  })}
                  error={errors.password?.message}
                />
              </div>

              <div className="form-group">
                <Input
                  type="password"
                  placeholder="Xác nhận mật khẩu mới"
                  {...register('confirmPassword', {
                    required: 'Vui lòng xác nhận mật khẩu',
                    validate: value =>
                      value === watchPassword || 'Mật khẩu xác nhận không khớp'
                  })}
                  error={errors.confirmPassword?.message}
                />
              </div>

              <Button
                type="submit"
                loading={loading}
                disabled={loading}
                className="auth-submit-btn"
              >
                {loading ? 'Đang cập nhật...' : 'Đặt lại mật khẩu'}
              </Button>
            </form>
          </CardBody>

          <CardFooter>
            <div className="auth-footer">
              <p>
                Nhớ mật khẩu?{' '}
                <Link to="/auth/login" className="text-link">
                  Đăng nhập
                </Link>
              </p>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

export default ResetPasswordPage