import { useEffect, useMemo, useState } from 'react'
import './AILoadingState.css'

const DEFAULT_STEPS = [
  'Đang phân tích dữ liệu...',
  'Đang suy luận bằng AI...',
  'Đang tổng hợp kết quả...',
]

const AILoadingState = ({
  title = 'AI đang xử lý',
  message = 'Tác vụ này có thể mất vài giây.',
  steps = DEFAULT_STEPS,
  compact = false,
}) => {
  const safeSteps = useMemo(
    () => (Array.isArray(steps) && steps.length > 0 ? steps : DEFAULT_STEPS),
    [steps]
  )
  const [stepIndex, setStepIndex] = useState(0)

  useEffect(() => {
    const timer = window.setInterval(() => {
      setStepIndex((prev) => (prev + 1) % safeSteps.length)
    }, 1800)
    return () => window.clearInterval(timer)
  }, [safeSteps.length])

  return (
    <div className={`ai-loading ${compact ? 'ai-loading--compact' : ''}`} role="status" aria-live="polite">
      <div className="ai-loading__pulse" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <h3 className="ai-loading__title">{title}</h3>
      <p className="ai-loading__message">{message}</p>
      <p className="ai-loading__step">{safeSteps[stepIndex]}</p>
      <div className="ai-loading__bar" aria-hidden="true">
        <div className="ai-loading__bar-fill" />
      </div>
    </div>
  )
}

export default AILoadingState
