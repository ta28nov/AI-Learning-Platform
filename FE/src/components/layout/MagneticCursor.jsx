import React, { useEffect, useState } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'
import './MagneticCursor.css'

/**
 * MagneticCursor — editorial custom cursor overlay.
 *
 * Renders only on pointer:fine devices (mouse / trackpad).
 * Hidden automatically on touch screens.
 *
 * Design: a small ink dot (cursor position) + a larger gold ring that
 * spring-follows with a soft delay, giving a trailing depth effect.
 *
 * The component also listens for "magnetic" elements (data-magnetic) and
 * enlarges the ring when hovering over interactive elements.
 */
const MagneticCursor = () => {
  const [isPointerFine, setIsPointerFine] = useState(false)
  const [isHoveringInteractive, setIsHoveringInteractive] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  // Raw position (snaps immediately to cursor)
  const dotX = useMotionValue(-100)
  const dotY = useMotionValue(-100)

  // Spring-lagged ring position
  const springConfig = { stiffness: 120, damping: 20, mass: 0.8 }
  const ringX = useSpring(dotX, springConfig)
  const ringY = useSpring(dotY, springConfig)

  useEffect(() => {
    // Only activate for mouse/trackpad users
    const mq = window.matchMedia('(pointer: fine)')
    if (!mq.matches) return
    setIsPointerFine(true)

    const move = (e) => {
      dotX.set(e.clientX)
      dotY.set(e.clientY)
      if (!isVisible) setIsVisible(true)
    }

    const enter = () => setIsVisible(true)
    const leave = () => setIsVisible(false)

    const handleInteractiveEnter = () => setIsHoveringInteractive(true)
    const handleInteractiveLeave = () => setIsHoveringInteractive(false)

    document.addEventListener('mousemove', move)
    document.addEventListener('mouseenter', enter)
    document.addEventListener('mouseleave', leave)

    // Enlarge ring when hovering buttons, links, interactive elements
    const interactiveSelector = 'a, button, [role="button"], input, textarea, select, [tabindex]'
    const addInteractiveListeners = () => {
      document.querySelectorAll(interactiveSelector).forEach((el) => {
        el.addEventListener('mouseenter', handleInteractiveEnter)
        el.addEventListener('mouseleave', handleInteractiveLeave)
      })
    }

    addInteractiveListeners()

    // Re-attach on DOM changes (for dynamically rendered elements)
    const observer = new MutationObserver(addInteractiveListeners)
    observer.observe(document.body, { childList: true, subtree: true })

    return () => {
      document.removeEventListener('mousemove', move)
      document.removeEventListener('mouseenter', enter)
      document.removeEventListener('mouseleave', leave)
      observer.disconnect()
    }
  }, [])

  if (!isPointerFine) return null

  return (
    <>
      {/* Dot — snaps to cursor */}
      <motion.div
        className="cursor-dot"
        style={{ x: dotX, y: dotY }}
        animate={{ opacity: isVisible ? 1 : 0, scale: isHoveringInteractive ? 0 : 1 }}
        transition={{ duration: 0.15 }}
      />

      {/* Ring — spring-follows */}
      <motion.div
        className="cursor-ring"
        style={{ x: ringX, y: ringY }}
        animate={{
          opacity: isVisible ? 1 : 0,
          scale: isHoveringInteractive ? 1.6 : 1,
        }}
        transition={{ duration: 0.2 }}
      />
    </>
  )
}

export default MagneticCursor
