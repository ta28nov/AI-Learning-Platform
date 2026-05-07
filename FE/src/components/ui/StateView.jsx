import React from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { staggerContainer, fadeUp } from '@/styles/motion'
import Button from './Button'
import './StateView.css'

/**
 * Editorial Cinematic StateView — empty / loading / error states.
 *
 * Props API fully preserved (existing usages unchanged):
 * @param {node|string} props.icon        - Icon element or emoji (still works, now rendered via <span>)
 * @param {string}      props.title       - Heading text
 * @param {string}      props.message     - Body message
 * @param {string}      props.actionLabel - CTA label
 * @param {func}        props.onAction    - CTA handler
 *
 * New optional props (additive):
 * @param {'empty'|'error'|'loading'|'info'} props.type - Visual tone (default: 'empty')
 */
const StateView = ({
  icon = null,
  title,
  message,
  actionLabel,
  onAction,
  type = 'empty',
}) => {
  const shouldReduceMotion = useReducedMotion()

  const containerVariants = shouldReduceMotion ? {} : staggerContainer
  const itemVariants      = shouldReduceMotion ? {} : fadeUp

  return (
    <motion.div
      className={`state-view state-view--${type}`}
      variants={containerVariants}
      initial={shouldReduceMotion ? false : 'hidden'}
      animate="show"
    >
      {/* Icon */}
      {icon && (
        <motion.span
          className="state-view__icon"
          variants={itemVariants}
          aria-hidden="true"
        >
          {icon}
        </motion.span>
      )}

      {/* Fallback ornament when no icon passed */}
      {!icon && (
        <motion.span
          className="state-view__ornament"
          variants={itemVariants}
          aria-hidden="true"
        />
      )}

      {/* Title */}
      {title && (
        <motion.h3 className="state-view__title" variants={itemVariants}>
          {title}
        </motion.h3>
      )}

      {/* Message */}
      {message && (
        <motion.p className="state-view__message" variants={itemVariants}>
          {message}
        </motion.p>
      )}

      {/* CTA */}
      {actionLabel && onAction && (
        <motion.div variants={itemVariants}>
          <Button variant="outline" onClick={onAction}>
            {actionLabel}
          </Button>
        </motion.div>
      )}
    </motion.div>
  )
}

export default StateView
