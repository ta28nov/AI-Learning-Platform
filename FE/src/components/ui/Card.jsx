import React, { useRef, useCallback } from 'react'
import { motion, useMotionValue, useTransform, useReducedMotion } from 'framer-motion'
import { SPRING, scaleIn } from '@/styles/motion'
import './Card.css'

// Statically create motion variants for both element types to avoid
// generating new component classes on every render.
const MotionDiv    = motion('div')
const MotionButton = motion('button')

/**
 * Editorial Cinematic Card — faux-3D tilt on cursor move.
 *
 * Props API fully preserved:
 * @param {string}   props.className
 * @param {boolean}  props.hover     - Enables hover shadow/border lift
 * @param {boolean}  props.shadow    - Enables base box-shadow
 * @param {string}   props.padding   - 'sm' | 'md' | 'lg'
 * @param {node}     props.children
 * @param {func}     props.onClick   - Renders as <button> when provided
 *
 * New optional props (additive, do not break existing usage):
 * @param {boolean}  props.tilt      - Enables cursor-driven 3D tilt (default: same as hover)
 * @param {boolean}  props.reveal    - Animate in with scaleIn on mount (default: false)
 */
const Card = ({
  className = '',
  hover = false,
  shadow = true,
  padding = 'md',
  children,
  onClick,
  tilt,          // defaults to hover value if not explicitly set
  reveal = false,
  ...props
}) => {
  const shouldReduceMotion = useReducedMotion()
  const enableTilt = (tilt !== undefined ? tilt : hover) && !shouldReduceMotion

  // Mouse-position motion values for the tilt effect
  const cardRef = useRef(null)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  // Map cursor position to subtle rotation: ±6° on each axis
  const rotateX = useTransform(mouseY, [-0.5, 0.5], [6, -6])
  const rotateY = useTransform(mouseX, [-0.5, 0.5], [-6, 6])

  const handleMouseMove = useCallback((e) => {
    if (!enableTilt || !cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    // Normalize to [-0.5, 0.5]
    mouseX.set((e.clientX - rect.left) / rect.width - 0.5)
    mouseY.set((e.clientY - rect.top) / rect.height - 0.5)
  }, [enableTilt, mouseX, mouseY])

  const handleMouseLeave = useCallback(() => {
    if (!enableTilt) return
    // Spring back to neutral
    mouseX.set(0)
    mouseY.set(0)
  }, [enableTilt, mouseX, mouseY])

  const cardClasses = [
    'card',
    shadow && 'card-shadow',
    hover && 'card-hover',
    `card-padding-${padding}`,
    onClick && 'card-clickable',
    enableTilt && 'card-tilt',
    className,
  ].filter(Boolean).join(' ')

  const motionProps = enableTilt
    ? { style: { rotateX, rotateY, transformStyle: 'preserve-3d' }, transition: SPRING.glass }
    : {}

  const revealProps = reveal && !shouldReduceMotion
    ? { variants: scaleIn, initial: 'hidden', animate: 'show' }
    : {}

  const MotionEl = onClick ? MotionButton : MotionDiv

  return (
    <MotionEl
      ref={cardRef}
      className={cardClasses}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      {...motionProps}
      {...revealProps}
      {...props}
    >
      {children}
    </MotionEl>
  )
}

/** CardHeader — phan dau card */
export const CardHeader = ({ className = '', children, ...props }) => (
  <div className={`card-header ${className}`} {...props}>
    {children}
  </div>
)

/** CardBody — phan noi dung chinh */
export const CardBody = ({ className = '', children, ...props }) => (
  <div className={`card-body ${className}`} {...props}>
    {children}
  </div>
)

/** CardFooter — phan cuoi card */
export const CardFooter = ({ className = '', children, ...props }) => (
  <div className={`card-footer ${className}`} {...props}>
    {children}
  </div>
)

export default Card
