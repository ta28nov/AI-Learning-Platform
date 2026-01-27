import React, { useState, useEffect } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import Button from '@components/ui/Button'
import Card, { CardHeader, CardBody, CardFooter } from '@components/ui/Card'
import { toast } from 'react-hot-toast'
import './AuthPages.css'

/**
 * Component VerifyEmailPage - Trang xác thực email
 */
const VerifyEmailPage = () => {
  const [loading, setLoading] = useState(true)
  const [verificationStatus, setVerificationStatus] = useState('verifying') // 'verifying', 'success', 'error'
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')
  const email = searchParams.get('email')

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setVerificationStatus('error')
        setLoading(false)
        return
      }

      try {
        // Goi API verify email
        // await authService.verifyEmail(token)
        
        // Gia lap API call
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        setVerificationStatus('success')
        toast.success('Email đã được xác thực thành công!')
      } catch (error) {
        setVerificationStatus('error')
        toast.error(error.message || 'Xác thực email thất bại!')
      } finally {
        setLoading(false)
      }
    }

    verifyEmail()
  }, [token])

  const handleResendVerification = async () => {
    if (!email) {
      toast.error('Không tìm thấy thông tin email')
      return
    }

    setLoading(true)
    try {
      // Goi API resend verification
      // await authService.resendVerification(email)
      
      // Gia lap API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      toast.success('Email xác thực đã được gửi lại!')
    } catch (error) {
      toast.error(error.message || 'Không thể gửi lại email xác thực!')
    } finally {
      setLoading(false)
    }
  }

  const handleGoToLogin = () => {
    navigate('/auth/login')
  }

  if (loading && verificationStatus === 'verifying') {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <Card className="auth-card">
            <CardHeader>
              <div className="auth-header">
                <div className="loading-icon">
                  <i className="fas fa-spinner fa-spin"></i>
                </div>
                <h1>Đang xác thực email...</h1>
                <p>Vui lòng đợi trong giây lát</p>
              </div>
            </CardHeader>
          </Card>
        </div>
      </div>
    )
  }

  if (verificationStatus === 'success') {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <Card className="auth-card">
            <CardHeader>
              <div className="auth-header">
                <div className="success-icon">
                  <i className="fas fa-check-circle"></i>
                </div>
                <h1>Xác thực thành công!</h1>
                <p>Email của bạn đã được xác thực thành công. Bạn có thể đăng nhập ngay bây giờ.</p>
              </div>
            </CardHeader>

            <CardBody>
              <Button
                onClick={handleGoToLogin}
                className="auth-submit-btn"
              >
                Đăng nhập ngay
              </Button>
            </CardBody>

            <CardFooter>
              <div className="auth-footer">
                <p>
                  Cần hỗ trợ?{' '}
                  <Link to="/contact" className="text-link">
                    Liên hệ với chúng tôi
                  </Link>
                </p>
              </div>
            </CardFooter>
          </Card>
        </div>
      </div>
    )
  }

  // verificationStatus === 'error'
  return (
    <div className="auth-page">
      <div className="auth-container">
        <Card className="auth-card">
          <CardHeader>
            <div className="auth-header">
              <div className="error-icon">
                <i className="fas fa-exclamation-triangle"></i>
              </div>
              <h1>Xác thực thất bại</h1>
              <p>
                {!token 
                  ? 'Link xác thực không hợp lệ hoặc đã hết hạn'
                  : 'Không thể xác thực email của bạn. Vui lòng thử lại.'
                }
              </p>
            </div>
          </CardHeader>

          <CardBody>
            <div className="auth-actions">
              {email && (
                <Button
                  onClick={handleResendVerification}
                  loading={loading}
                  disabled={loading}
                  variant="outline"
                  className="auth-action-btn"
                >
                  {loading ? 'Đang gửi...' : 'Gửi lại email xác thực'}
                </Button>
              )}
              
              <Button
                onClick={handleGoToLogin}
                className="auth-submit-btn"
              >
                Quay lại đăng nhập
              </Button>
            </div>
          </CardBody>

          <CardFooter>
            <div className="auth-footer">
              <p>
                Cần hỗ trợ?{' '}
                <Link to="/contact" className="text-link">
                  Liên hệ với chúng tôi
                </Link>
              </p>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}

export default VerifyEmailPage