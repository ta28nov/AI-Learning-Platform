import React from 'react'
import './Button.css'

/**
 * Component Button co ban voi cac variant khac nhau
 * @param {Object} props - Cac thuoc tinh cua button
 * @param {string} props.variant - Kieu button: 'primary', 'secondary', 'outline', 'ghost', 'danger'
 * @param {string} props.size - Kich thuoc: 'sm', 'md', 'lg'
 * @param {boolean} props.loading - Trang thai dang tai
 * @param {boolean} props.disabled - Vo hieu hoa button
 * @param {string} props.className - CSS class bo sung
 * @param {React.ReactNode} props.children - Noi dung ben trong button
 * @param {Function} props.onClick - Ham xu ly su kien click
 */
const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false, 
  className = '', 
  children, 
  onClick,
  ...props 
}) => {
  // Tao cac class CSS dua tren props
  const buttonClasses = [
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    loading && 'btn-loading',
    disabled && 'btn-disabled',
    className
  ].filter(Boolean).join(' ')

  // Xu ly su kien click
  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault()
      return
    }
    onClick && onClick(e)
  }

  return (
    <button
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <span className="btn-spinner"></span>}
      {children}
    </button>
  )
}

export default Button