/**
 * Editorial Cinematic motion system.
 *
 * Single source of truth for Framer Motion easings, durations, and reusable
 * variants across the application. Mirrors the CSS motion tokens so the
 * design language stays consistent between CSS animations and JS-driven
 * Framer Motion effects.
 *
 * Usage:
 *   import { fadeUp, staggerContainer, EASE } from '@/styles/motion'
 *   <motion.section variants={staggerContainer} initial="hidden" animate="show">
 *     <motion.h1 variants={fadeUp}>Title</motion.h1>
 *   </motion.section>
 */

// -----------------------------------------------------------------------------
// Easing curves (must match tokens.css --ease-* values)
// -----------------------------------------------------------------------------
export const EASE = Object.freeze({
  standard:  [0.4, 0, 0.2, 1],
  cinematic: [0.65, 0, 0.35, 1],
  stagger:   [0.16, 1, 0.3, 1],
  pageTurn:  [0.83, 0, 0.17, 1],
  outExpo:   [0.19, 1, 0.22, 1],
})

// -----------------------------------------------------------------------------
// Durations in seconds (Framer Motion uses seconds, CSS uses ms)
// -----------------------------------------------------------------------------
export const DURATION = Object.freeze({
  instant:   0.08,
  fast:      0.18,
  normal:    0.32,
  slow:      0.6,
  cinematic: 0.9,
  marquee:   1.4,
})

// -----------------------------------------------------------------------------
// Spring presets
// -----------------------------------------------------------------------------
export const SPRING = Object.freeze({
  soft:   { type: 'spring', stiffness: 180, damping: 22, mass: 0.9 },
  snappy: { type: 'spring', stiffness: 360, damping: 28, mass: 0.7 },
  glass:  { type: 'spring', stiffness: 120, damping: 18, mass: 1.0 },
  punchy: { type: 'spring', stiffness: 520, damping: 30, mass: 0.6 },
})

// -----------------------------------------------------------------------------
// Reduced-motion helper. Components can wrap their variants with this and
// gracefully degrade to instant transitions when the user prefers reduced
// motion. Caller must check `window.matchMedia('(prefers-reduced-motion: reduce)')`.
// -----------------------------------------------------------------------------
export const reducedMotionTransition = { duration: 0 }

// -----------------------------------------------------------------------------
// Atomic variants
// -----------------------------------------------------------------------------

/** Fade + rise from below. Default editorial reveal. */
export const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.normal, ease: EASE.cinematic },
  },
}

/** Fade only - for non-translating elements (overlays, backdrops). */
export const fade = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { duration: DURATION.normal, ease: EASE.standard },
  },
  exit: {
    opacity: 0,
    transition: { duration: DURATION.fast, ease: EASE.standard },
  },
}

/** Drop from above (for top-of-view headings, marquee captions). */
export const fadeDown = {
  hidden: { opacity: 0, y: -24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.normal, ease: EASE.cinematic },
  },
}

/** Slide-in from the leading edge (left in LTR). */
export const slideInLeft = {
  hidden: { opacity: 0, x: -32 },
  show: {
    opacity: 1,
    x: 0,
    transition: { duration: DURATION.normal, ease: EASE.cinematic },
  },
}

/** Slide-in from the trailing edge (right in LTR). */
export const slideInRight = {
  hidden: { opacity: 0, x: 32 },
  show: {
    opacity: 1,
    x: 0,
    transition: { duration: DURATION.normal, ease: EASE.cinematic },
  },
}

/** Scale-up reveal (for cards / modals). */
export const scaleIn = {
  hidden: { opacity: 0, scale: 0.96 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: DURATION.normal, ease: EASE.cinematic },
  },
}

// -----------------------------------------------------------------------------
// Stagger containers
// -----------------------------------------------------------------------------

/** Standard staggered reveal container - children inherit their own variants. */
export const staggerContainer = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.06,
    },
  },
}

/** Slower stagger for editorial section reveals. */
export const staggerEditorial = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.14,
      delayChildren: 0.12,
    },
  },
}

/** Tight stagger for list items (table rows, search results). */
export const staggerTight = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.04,
      delayChildren: 0.02,
    },
  },
}

// -----------------------------------------------------------------------------
// Page transitions (cinematic page-turn between routes)
// -----------------------------------------------------------------------------

/** Editorial page-turn: gentle rotateY plus paper-slide. */
export const pageTurn = {
  initial: {
    opacity: 0,
    rotateY: -8,
    y: 12,
    transformPerspective: 1600,
  },
  animate: {
    opacity: 1,
    rotateY: 0,
    y: 0,
    transition: { duration: DURATION.slow, ease: EASE.pageTurn },
  },
  exit: {
    opacity: 0,
    rotateY: 6,
    y: -8,
    transition: { duration: DURATION.fast, ease: EASE.pageTurn },
  },
}

/** Soft page fade for utility routes (auth, error). */
export const pageFade = {
  initial: { opacity: 0, y: 8 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.normal, ease: EASE.cinematic },
  },
  exit: {
    opacity: 0,
    y: -4,
    transition: { duration: DURATION.fast, ease: EASE.standard },
  },
}

// -----------------------------------------------------------------------------
// Hover / interaction
// -----------------------------------------------------------------------------

/** Magnetic hover for primary CTAs. Use on Framer Motion's whileHover. */
export const magneticHover = {
  scale: 1.02,
  y: -2,
  transition: SPRING.snappy,
}

/** Tap feedback - subtle compress. */
export const magneticTap = {
  scale: 0.98,
  y: 0,
  transition: SPRING.punchy,
}

/** Card lift with faux-3D tilt forward. Pair with `transform-style: preserve-3d`. */
export const cardLift = {
  rotateX: -2,
  rotateY: 2,
  y: -6,
  transition: SPRING.glass,
}

// -----------------------------------------------------------------------------
// Scroll-driven helpers
// -----------------------------------------------------------------------------

/**
 * Build a `whileInView` prop set with editorial defaults. Use to opt a
 * component into "reveal on scroll" without re-typing the same options.
 *
 *   <motion.div {...inView()} variants={fadeUp}>...</motion.div>
 */
export const inView = ({ amount = 0.35, once = true } = {}) => ({
  initial: 'hidden',
  whileInView: 'show',
  viewport: { amount, once },
})

const motionPresets = {
  EASE,
  DURATION,
  SPRING,
  fade,
  fadeUp,
  fadeDown,
  slideInLeft,
  slideInRight,
  scaleIn,
  staggerContainer,
  staggerEditorial,
  staggerTight,
  pageTurn,
  pageFade,
  magneticHover,
  magneticTap,
  cardLift,
  inView,
  reducedMotionTransition,
}

export default motionPresets
