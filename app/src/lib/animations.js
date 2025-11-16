/**
 * Framer Motion animation presets for EpiHelix
 */

export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.24 },
}

export const slideUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
  transition: { duration: 0.24, ease: [0.22, 0.9, 0.32, 1] },
}

export const slideDown = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.24, ease: [0.22, 0.9, 0.32, 1] },
}

export const scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
  transition: { duration: 0.24, ease: [0.22, 0.9, 0.32, 1] },
}

export const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.05,
    },
  },
}

export const listItem = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.12 },
}

// Easing
export const easeOut = [0.22, 0.9, 0.32, 1]
