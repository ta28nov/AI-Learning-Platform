import React, { forwardRef, useId } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import './Input.css'

/**
 * Editorial Cinematic Input
 *
 * forwardRef API fully preserved — all existing usages continue to work unchanged.
 *
 * @param {string}  props.type        - Input type (text, email, password, ...)
 * @param {string}  props.label       - Field label
 * @param {string}  props.placeholder
 * @param {boolean} props.required
 * @param {boolean} props.disabled
 * @param {string}  props.error       - Validation error message
 * @param {string}  props.helperText  - Helper text (shown when no error)
 * @param {string}  props.size        - 'sm' | 'md' | 'lg'
 * @param {string}  props.className
 * @param {node}    props.startIcon
 * @param {node}    props.endIcon
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
  const shouldReduceMotion = useReducedMotion()

  // useId gives stable SSR-safe IDs; fall back to props.id when caller provides one
  const autoId = useId()
  const inputId = props.id || `input-${autoId}`

  const containerClasses = ['input-container', className].filter(Boolean).join(' ')

  const inputClasses = [
    'input',
    `input-${size}`,
    error && 'input-error',
    disabled && 'input-disabled',
    startIcon && 'input-with-start-icon',
    endIcon && 'input-with-end-icon',
  ].filter(Boolean).join(' ')

  const errorMotion = shouldReduceMotion
    ? {}
    : { initial: { opacity: 0, y: -4 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.18 } }

  return (
    <div className={containerClasses}>
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
          {required && <span className="input-required" aria-hidden="true">*</span>}
        </label>
      )}

      <div className="input-wrapper">
        {startIcon && (
          <div className="input-icon input-start-icon" aria-hidden="true">
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
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
          {...props}
        />

        {endIcon && (
          <div className="input-icon input-end-icon" aria-hidden="true">
            {endIcon}
          </div>
        )}
      </div>

      {error && (
        <motion.div
          id={`${inputId}-error`}
          className="input-error-message"
          role="alert"
          {...errorMotion}
        >
          {error}
        </motion.div>
      )}

      {helperText && !error && (
        <div id={`${inputId}-helper`} className="input-helper-text">
          {helperText}
        </div>
      )}
    </div>
  )
})

Input.displayName = 'Input'

/**
 * Textarea — same editorial treatment, same prop API as before.
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
  const shouldReduceMotion = useReducedMotion()
  const autoId = useId()
  const textareaId = props.id || `textarea-${autoId}`

  const containerClasses = ['input-container', className].filter(Boolean).join(' ')

  const textareaClasses = [
    'input',
    'textarea',
    error && 'input-error',
    disabled && 'input-disabled',
  ].filter(Boolean).join(' ')

  const errorMotion = shouldReduceMotion
    ? {}
    : { initial: { opacity: 0, y: -4 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.18 } }

  return (
    <div className={containerClasses}>
      {label && (
        <label htmlFor={textareaId} className="input-label">
          {label}
          {required && <span className="input-required" aria-hidden="true">*</span>}
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
        aria-invalid={!!error}
        aria-describedby={error ? `${textareaId}-error` : helperText ? `${textareaId}-helper` : undefined}
        {...props}
      />

      {error && (
        <motion.div
          id={`${textareaId}-error`}
          className="input-error-message"
          role="alert"
          {...errorMotion}
        >
          {error}
        </motion.div>
      )}

      {helperText && !error && (
        <div id={`${textareaId}-helper`} className="input-helper-text">
          {helperText}
        </div>
      )}
    </div>
  )
})

Textarea.displayName = 'Textarea'

export default Input
