import { motion } from 'motion/react'
import { Modal } from './Modal.jsx'

/** A modal over a blurred backdrop. Escape and a click outside close it. */
export const Dialog = ({ open, onClose, title, children }) => open && (
  <Modal
    className="pv-dialog-backdrop" aria-label={title} onDismiss={onClose}
    onClick={(event) => { if (event.target === event.currentTarget) onClose() }}
  >
    <motion.div
      className="pv-dialog"
      initial={{ opacity: 0, y: 18, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25, ease: [0.2, 0.7, 0.2, 1] }}
    >
      <div className="pv-dialog-head">
        <h2>{title}</h2>
        <button type="button" className="pv-close" aria-label="Close" onClick={onClose}>×</button>
      </div>
      {children}
    </motion.div>
  </Modal>
)
