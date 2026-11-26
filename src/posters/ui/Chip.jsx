import { motion } from 'motion/react'

// Cursor movement and the entrance animation share a transform so the label moves as one layer.
const placeChip = (_, transform) => `translate3d(var(--pv-chip-x), var(--pv-chip-y), 0) ${transform}`

/**
 * A small label beside the pointer. Motion values position it without relaying out the stage.
 */
export const Chip = ({ x, y, title, hint }) => (
  <motion.div
    className="pv-chip"
    style={{ '--pv-chip-x': x, '--pv-chip-y': y }}
    transformTemplate={placeChip}
    initial={{ opacity: 0, y: 6, scale: 0.96 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    exit={{ opacity: 0, y: 4, scale: 0.98 }}
    transition={{ duration: 0.18 }}
  >
    <span>{title}</span>
    {hint && <small>{hint}</small>}
  </motion.div>
)
