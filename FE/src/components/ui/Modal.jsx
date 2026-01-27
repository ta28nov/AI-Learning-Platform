import React, { useEffect } from 'react'
import { createPortal } from 'react-dom'
import './Modal.css'

/**
 * Component Modal de hien thi dialog popup
 * @param {Object} props - Cac thuoc tinh cua modal
 * @param {boolean} props.isOpen - Trang thai mo/dong modal
 * @param {Function} props.onClose - Ham xu ly dong modal
 * @param {string} props.title - Tieu de modal
 * @param {string} props.size - Kich thuoc modal: 'sm', 'md', 'lg', 'xl'
 * @param {boolean} props.closeOnOverlay - Dong modal khi click overlay
 * @param {boolean} props.showCloseButton - Hien thi nut dong
 * @param {React.ReactNode} props.children - Noi dung modal
 * @param {string} props.className - CSS class bo sung
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
  // Xu ly dong modal bang phim Esc
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen && onClose) {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Vo hieu hoa scroll tren body
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  // Xu ly click overlay
  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && closeOnOverlay && onClose) {
      onClose()
    }
  }

  // Khong render gi neu modal dong
  if (!isOpen) {
    return null
  }

  // Tao cac class CSS dua tren props
  const modalClasses = [
    'modal-content',
    `modal-${size}`,
    className
  ].filter(Boolean).join(' ')

  const modalContent = (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className={modalClasses} {...props}>
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && <h3 className="modal-title">{title}</h3>}
            {showCloseButton && (
              <button 
                className="modal-close-button"
                onClick={onClose}
                aria-label="Dong modal"
              >
                <CloseIcon />
              </button>
            )}
          </div>
        )}
        
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  )

  // Su dung portal de render modal ngoai DOM tree
  return createPortal(modalContent, document.body)
}

/**
 * Component ModalHeader
 */
export const ModalHeader = ({ children, className = '', ...props }) => {
  return (
    <div className={`modal-header ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Component ModalBody
 */
export const ModalBody = ({ children, className = '', ...props }) => {
  return (
    <div className={`modal-body ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Component ModalFooter
 */
export const ModalFooter = ({ children, className = '', ...props }) => {
  return (
    <div className={`modal-footer ${className}`} {...props}>
      {children}
    </div>
  )
}

// Icon dong modal don gian
const CloseIcon = () => (
  <svg 
    width="20" 
    height="20" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2"
  >
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
)

export default Modal