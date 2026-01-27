import React, { forwardRef } from 'react'
import './Input.css'

/**
 * Component Input co ban voi cac tinh nang validation
 * @param {Object} props - Cac thuoc tinh cua input
 * @param {string} props.type - Kieu input: 'text', 'email', 'password', 'number', etc.
 * @param {string} props.label - Nhan cua input
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.required - Co bat buoc khong
 * @param {boolean} props.disabled - Vo hieu hoa input
 * @param {string} props.error - Thong bao loi
 * @param {string} props.helperText - Text huong dan
 * @param {string} props.size - Kich thuoc: 'sm', 'md', 'lg'
 * @param {string} props.className - CSS class bo sung
 * @param {React.ReactNode} props.startIcon - Icon o dau input
 * @param {React.ReactNode} props.endIcon - Icon o cuoi input
 */
const Input = forwardRef(({ 
  type = 'text',
  label,
  placeholder,
  required = false,
  disabled = false,
  error,
  helperText,
  size = 'md',
  className = '',
  startIcon,
  endIcon,
  ...props 
}, ref) => {
  // Tao cac class CSS dua tren props
  const containerClasses = [
    'input-container',
    className
  ].filter(Boolean).join(' ')

  const inputClasses = [
    'input',
    `input-${size}`,
    error && 'input-error',
    disabled && 'input-disabled',
    startIcon && 'input-with-start-icon',
    endIcon && 'input-with-end-icon'
  ].filter(Boolean).join(' ')

  const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div className={containerClasses}>
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
          {required && <span className="input-required">*</span>}
        </label>
      )}
      
      <div className="input-wrapper">
        {startIcon && (
          <div className="input-icon input-start-icon">
            {startIcon}
          </div>
        )}
        
        <input
          ref={ref}
          id={inputId}
          type={type}
          className={inputClasses}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          {...props}
        />
        
        {endIcon && (
          <div className="input-icon input-end-icon">
            {endIcon}
          </div>
        )}
      </div>
      
      {error && (
        <div className="input-error-message">
          {error}
        </div>
      )}
      
      {helperText && !error && (
        <div className="input-helper-text">
          {helperText}
        </div>
      )}
    </div>
  )
})

Input.displayName = 'Input'

/**
 * Component Textarea de nhap text nhieu dong
 */
export const Textarea = forwardRef(({ 
  label,
  placeholder,
  required = false,
  disabled = false,
  error,
  helperText,
  rows = 4,
  className = '',
  ...props 
}, ref) => {
  const containerClasses = [
    'input-container',
    className
  ].filter(Boolean).join(' ')

  const textareaClasses = [
    'input',
    'textarea',
    error && 'input-error',
    disabled && 'input-disabled'
  ].filter(Boolean).join(' ')

  const textareaId = props.id || `textarea-${Math.random().toString(36).substr(2, 9)}`

  return (
    <div className={containerClasses}>
      {label && (
        <label htmlFor={textareaId} className="input-label">
          {label}
          {required && <span className="input-required">*</span>}
        </label>
      )}
      
      <textarea
        ref={ref}
        id={textareaId}
        className={textareaClasses}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        rows={rows}
        {...props}
      />
      
      {error && (
        <div className="input-error-message">
          {error}
        </div>
      )}
      
      {helperText && !error && (
        <div className="input-helper-text">
          {helperText}
        </div>
      )}
    </div>
  )
})

Textarea.displayName = 'Textarea'

export default Input