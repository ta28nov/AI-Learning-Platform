import React from 'react'
import Button from '@components/ui/Button'
import appLogger from '@utils/logger'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    appLogger.error(error, { errorInfo, source: 'ErrorBoundary' })
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="dash-empty" style={{ margin: '2rem' }}>
          <span className="dash-empty__icon">⚠️</span>
          <p className="dash-empty__msg">
            Đã xảy ra lỗi ngoài ý muốn khi hiển thị trang. Vui lòng tải lại.
          </p>
          <Button onClick={this.handleReload}>Tải lại trang</Button>
        </div>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
