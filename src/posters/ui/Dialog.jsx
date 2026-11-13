import { useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'motion/react'

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])'

/**
 * A modal over a blurred backdrop. Escape and a click outside close it. Focus moves into it when it
 * opens, Tab stays inside it while it is open, and focus goes back to where it was when it closes.
 */
export const Dialog = ({ open, onClose, title, children }) => {
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return undefined
    const before = document.activeElement
    // The dialog is mounted by now; its entrance animation does not delay focus.
    ref.current?.focus()
    const onKey = (e) => {
      if (e.key === 'Escape') { onClose(); return }
      if (e.key !== 'Tab' || !ref.current) return
      const stops = [...ref.current.querySelectorAll(FOCUSABLE)].filter((el) => el.offsetParent !== null)
      if (!stops.length) { e.preventDefault(); return }
      const first = stops[0]
      const last = stops.at(-1)
      const inside = ref.current.contains(document.activeElement)
      if (e.shiftKey && (!inside || document.activeElement === first || document.activeElement === ref.current)) { e.preventDefault(); last.focus() }
      else if (!e.shiftKey && (!inside || document.activeElement === last)) { e.preventDefault(); first.focus() }
    }
    addEventListener('keydown', onKey)
    return () => {
      removeEventListener('keydown', onKey)
      if (before instanceof HTMLElement && before.isConnected) before.focus()
    }
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="pv-dialog-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
          <motion.div
            ref={ref}
            className="pv-dialog"
            role="dialog"
            aria-modal="true"
            aria-label={title}
            tabIndex={-1}
            initial={{ opacity: 0, y: 18, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.98 }}
            transition={{ duration: 0.25, ease: [0.2, 0.7, 0.2, 1] }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="pv-dialog-head">
              <h2>{title}</h2>
              <button type="button" className="pv-close" aria-label="Close" onClick={onClose}>×</button>
            </div>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
