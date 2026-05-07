import React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useReducedMotion } from 'framer-motion'

/**
 * MobileDrawer — backdrop overlay for mobile sidebar.
 * Rendered outside the sidebar so clicks on the backdrop close it.
 * The actual sidebar sliding is handled by CSS class .sidebar-open.
 *
 * @param {boolean} isOpen   - Whether the sidebar (and thus this overlay) is open
 * @param {func}    onClose  - Close handler
 */
const MobileDrawer = ({ isOpen, onClose }) => {
  const shouldReduceMotion = useReducedMotion()

  const backdropVariants = {
    hidden: { opacity: 0 },
    show:   { opacity: 1, transition: { duration: shouldReduceMotion ? 0 : 0.22 } },
    exit:   { opacity: 0, transition: { duration: shouldReduceMotion ? 0 : 0.18 } },
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="sidebar-overlay"
          variants={backdropVariants}
          initial="hidden"
          animate="show"
          exit="exit"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
    </AnimatePresence>
  )
}

export default MobileDrawer
