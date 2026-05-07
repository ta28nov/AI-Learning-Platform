import React, { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import './Modal.css'

/**
 * Editorial Cinematic Modal — AnimatePresence enter/exit with backdrop blur.
 *
 * Props API fully preserved:
 * @param {boolean}  props.isOpen          - Open/close state
 * @param {func}     props.onClose         - Close handler
 * @param {string}   props.title           - Modal heading
 * @param {string}   props.size            - 'sm' | 'md' | 'lg' | 'xl'
 * @param {boolean}  props.closeOnOverlay  - Close on backdrop click (default: true)
 * @param {boolean}  props.showCloseButton - Show × button (default: true)
 * @param {node}     props.children
 * @param {string}   props.className
 */
const Modal = ({
  isOpen = false,
  onClose,
  title,
  size = 'md',
  closeOnOverlay = true,
  showCloseButton = true,
  children,
  className = '',
  ...props
}) => {
  const shouldReduceMotion = useReducedMotion()
  const closeButtonRef = useRef(null)

  // Esc to close + scroll-lock
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen && onClose) onClose()
    }
    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
      // Auto-focus the close button for keyboard accessibility
      setTimeout(() => closeButtonRef.current?.focus(), 50)
    }
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && closeOnOverlay && onClose) onClose()
  }

  const modalClasses = ['modal-content', `modal-${size}`, className].filter(Boolean).join(' ')

  // Overlay: fade in/out
  const overlayVariants = {
    hidden: { opacity: 0 },
    show:   { opacity: 1, transition: { duration: shouldReduceMotion ? 0 : 0.22 } },
    exit:   { opacity: 0, transition: { duration: shouldReduceMotion ? 0 : 0.18 } },
  }

  // Panel: cinematic slide-up + scale
  const panelVariants = {
    hidden: { opacity: 0, y: shouldReduceMotion ? 0 : 24, scale: shouldReduceMotion ? 1 : 0.97 },
    show:   {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { duration: shouldReduceMotion ? 0 : 0.32, ease: [0.65, 0, 0.35, 1] },
    },
    exit: {
      opacity: 0,
      y: shouldReduceMotion ? 0 : -12,
      scale: shouldReduceMotion ? 1 : 0.98,
      transition: { duration: shouldReduceMotion ? 0 : 0.20, ease: [0.4, 0, 1, 1] },
    },
  }

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="modal-overlay"
          variants={overlayVariants}
          initial="hidden"
          animate="show"
          exit="exit"
          onClick={handleOverlayClick}
          aria-modal="true"
          role="dialog"
          aria-labelledby={title ? 'modal-title' : undefined}
        >
          <motion.div
            className={modalClasses}
            variants={panelVariants}
            initial="hidden"
            animate="show"
            exit="exit"
            {...props}
          >
            {(title || showCloseButton) && (
              <div className="modal-header">
                {title && (
                  <h3 id="modal-title" className="modal-title">{title}</h3>
                )}
                {showCloseButton && (
                  <button
                    ref={closeButtonRef}
                    className="modal-close-button"
                    onClick={onClose}
                    aria-label="Đóng modal"
                  >
                    <CloseIcon />
                  </button>
                )}
              </div>
            )}

            <div className="modal-body">
              {children}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
  )
}

/** ModalHeader */
export const ModalHeader = ({ children, className = '', ...props }) => (
  <div className={`modal-header ${className}`} {...props}>{children}</div>
)

/** ModalBody */
export const ModalBody = ({ children, className = '', ...props }) => (
  <div className={`modal-body ${className}`} {...props}>{children}</div>
)

/** ModalFooter */
export const ModalFooter = ({ children, className = '', ...props }) => (
  <div className={`modal-footer ${className}`} {...props}>{children}</div>
)

const CloseIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

export default Modal
