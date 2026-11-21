import { motion } from 'motion/react'

/**
 * A small label that sits beside the pointer. Position in px relative to the parent; `up` and
 * `left` put it above or to the left of the pointer instead of below and to the right.
 */
export const Chip = ({ x, y, up = false, left = false, title, hint }) => (
  <motion.div
    className={`pv-chip${up ? ' pv-chip-up' : ''}${left ? ' pv-chip-left' : ''}`}
    style={{ left: x, top: y }}
    initial={{ opacity: 0, y: 6, scale: 0.96 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    exit={{ opacity: 0, y: 4, scale: 0.98 }}
    transition={{ duration: 0.18 }}
  >
    <span>{title}</span>
    {hint && <small>{hint}</small>}
  </motion.div>
)
