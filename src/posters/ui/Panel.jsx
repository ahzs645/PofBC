import { useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'motion/react'

/**
 * A floating glass panel over the stage: from the right on wide screens, as a sheet from the
 * bottom on narrow ones. Contents keyed by `contentKey` swap at once and fade in, so stepping
 * quickly never leaves the panel empty while the old contents leave; the scroll resets.
 */
export const Panel = ({ open, narrow = false, contentKey, onClose, children }) => {
  const ref = useRef(null)
  useEffect(() => { ref.current?.scrollTo({ top: 0 }) }, [contentKey])

  return (
    <AnimatePresence>
      {open && (
        <motion.aside
          key="panel"
          className="pv-panel"
          ref={ref}
          initial={narrow ? { opacity: 0, y: 60 } : { opacity: 0, x: 48 }}
          animate={{ opacity: 1, x: 0, y: 0 }}
          exit={narrow ? { opacity: 0, y: 60 } : { opacity: 0, x: 48 }}
          transition={{ type: 'spring', stiffness: 260, damping: 30 }}
          onClick={(e) => e.stopPropagation()}
        >
          {onClose && <button type="button" className="pv-panel-close" aria-label="Close" onClick={onClose}>×</button>}
          <motion.div
            key={contentKey}
            className="pv-panel-body"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.28, ease: [0.2, 0.7, 0.2, 1] }}
          >
            {children}
          </motion.div>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
