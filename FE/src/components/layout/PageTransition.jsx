import React from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import { pageTurn, pageFade } from '@/styles/motion'

/**
 * PageTransition — wraps dashboard Outlet children with cinematic page-turn.
 *
 * Uses the current pathname as AnimatePresence key so every route change
 * triggers the exit/enter cycle. mode="wait" ensures the old page fully exits
 * before the new one enters, preventing layout collisions.
 *
 * Falls back to pageFade when prefers-reduced-motion is set.
 */
const PageTransition = ({ children }) => {
  const location = useLocation()
  const shouldReduceMotion = useReducedMotion()
  const variants = shouldReduceMotion ? pageFade : pageTurn

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        className="page-transition-wrapper"
        variants={variants}
        initial="initial"
        animate="animate"
        exit="exit"
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

export default PageTransition
