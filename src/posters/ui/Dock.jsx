import { motion } from 'motion/react'

/**
 * A stepper pill at the bottom of the stage. `steps` is [{ id, label }]. With no current step it
 * shows `hint` and a start button instead; on touch screens every step keeps its label.
 */
export function Dock({ steps, current, onSelect, onStart, hint, startLabel = 'Start →', coarse = false }) {
  const i = steps.findIndex((s) => s.id === current)
  const open = i >= 0

  if (!open && !coarse) {
    return (
      <motion.div className="pv-dock pv-hint" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8, duration: 0.6 }}>
        <span>{hint}</span>
        <button type="button" className="pv-ghost" onClick={() => (onStart ? onStart() : onSelect(steps[0].id))}>{startLabel}</button>
      </motion.div>
    )
  }

  return (
    <motion.div className="pv-dock" layout initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <button type="button" className="pv-arrow" aria-label="Previous" onClick={() => onSelect(i <= 0 ? null : steps[i - 1].id)}>←</button>
      <div className="pv-steps" role="tablist">
        {steps.map((s, n) => (
          <motion.button
            key={s.id}
            type="button"
            role="tab"
            layout
            aria-selected={s.id === current}
            aria-label={s.label}
            className={'pv-step' + (s.id === current ? ' pv-current' : '')}
            onClick={() => onSelect(s.id)}
            transition={{ type: 'spring', stiffness: 400, damping: 32 }}
          >
            {(s.id === current || coarse) && (
              <motion.span layout="position" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <em>{n + 1}</em> {s.label}
              </motion.span>
            )}
          </motion.button>
        ))}
      </div>
      <button type="button" className="pv-arrow" aria-label="Next" onClick={() => onSelect(i >= steps.length - 1 ? null : steps[i + 1].id)}>→</button>
    </motion.div>
  )
}
