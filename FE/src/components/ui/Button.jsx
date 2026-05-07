import React from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { SPRING, magneticHover, magneticTap } from '@/styles/motion'
import './Button.css'

/**
 * Editorial Cinematic Button
 *
 * Props API fully preserved — all existing usages continue to work unchanged.
 *
 * @param {string}  props.variant   - 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
 * @param {string}  props.size      - 'sm' | 'md' | 'lg'
 * @param {boolean} props.loading   - Shows spinner, disables interaction
 * @param {boolean} props.disabled  - Disables interaction
 * @param {string}  props.className - Extra CSS classes
 * @param {node}    props.children  - Button content
 * @param {func}    props.onClick   - Click handler
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
  const shouldReduceMotion = useReducedMotion()

  const buttonClasses = [
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    loading && 'btn-loading',
    disabled && 'btn-disabled',
    className,
  ].filter(Boolean).join(' ')

  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault()
      return
    }
    onClick && onClick(e)
  }

  // Reduced-motion: fall back to bare <button> with CSS transitions only
  if (shouldReduceMotion) {
    return (
      <button
        className={buttonClasses}
        onClick={handleClick}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <span className="btn-spinner" />}
        {children}
      </button>
    )
  }

  const hoverAnim = disabled || loading ? {} : magneticHover
  const tapAnim   = disabled || loading ? {} : magneticTap

  return (
    <motion.button
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      whileHover={hoverAnim}
      whileTap={tapAnim}
      transition={SPRING.snappy}
      {...props}
    >
      {loading && <span className="btn-spinner" />}
      {children}
    </motion.button>
  )
}

/* ---------------------------------------------------------------------------
   Sub-variants (editorial additions — opt-in, do not break existing usage)
   --------------------------------------------------------------------------- */

/**
 * Button.Magnetic — primary action with a strong pull-up and gold shadow on hover.
 * Same props as Button. variant defaults to 'primary'.
 */
Button.Magnetic = function MagneticButton({ className = '', ...props }) {
  return (
    <Button
      variant="primary"
      className={`btn-magnetic ${className}`}
      {...props}
    />
  )
}

/**
 * Button.Ghost — invisible until hovered; ink text, no border.
 * Same props as Button. variant locked to 'ghost'.
 */
Button.Ghost = function GhostButton({ className = '', ...props }) {
  return (
    <Button
      variant="ghost"
      className={`btn-ghost-editorial ${className}`}
      {...props}
    />
  )
}

/**
 * Button.Link — text-only with animated underline; use for inline editorial CTAs.
 * Same props as Button minus size (ignored).
 */
Button.Link = function LinkButton({ className = '', children, ...props }) {
  const shouldReduceMotion = useReducedMotion()
  return (
    <motion.button
      className={`btn btn-link-editorial ${className}`}
      whileHover={shouldReduceMotion ? {} : { x: 2 }}
      whileTap={shouldReduceMotion ? {} : { x: 0 }}
      transition={SPRING.snappy}
      {...props}
    >
      {children}
      <span className="btn-link-underline" aria-hidden="true" />
    </motion.button>
  )
}

export default Button
