import { useEffect, useRef } from 'react'
import { motion } from 'motion/react'

/**
 * A bar along the bottom of the stage, in three parts: where you are on the left, the steps in the
 * middle, and the way forward on the right. `steps` is [{ id, label }]. With no current step the
 * left shows `hint` and the right a start button; once a step is open they become a count and a
 * pair of arrows. The arrows sit at the bar's edge, so they stay put under the pointer however
 * wide the current step's label is. On touch screens every step keeps its label.
 */
export function Dock({ steps, current, onSelect, onStart, hint, startLabel = 'Start →', coarse = false }) {
  const i = steps.findIndex((s) => s.id === current)
  const open = i >= 0
  const pad = (n) => String(n).padStart(2, '0')
  const row = useRef(null)

  // When the steps overflow (every label shown, on touch), keep the current one in view. Scrolled
  // by hand: scrollIntoView would also move the stage, which hides its overflow but still scrolls.
  useEffect(() => {
    const el = row.current
    const step = el?.querySelector('.pv-current')
    if (!step || el.scrollWidth <= el.clientWidth) return
    el.scrollTo({ left: step.offsetLeft - (el.clientWidth - step.offsetWidth) / 2, behavior: 'smooth' })
  }, [current])

  return (
    <nav className={'pv-dock' + (open ? ' pv-dock-open' : '')} aria-label="Parts">
      <div className="pv-dock-start">
        {open
          ? <span className="pv-dock-count"><b>{pad(i + 1)}</b> / {pad(steps.length)}</span>
          : <span className="pv-dock-hint">{hint}</span>}
      </div>

      <div className="pv-steps" role="tablist" ref={row}>
        {steps.map((s, n) => (
          <motion.button
            key={s.id}
            type="button"
            role="tab"
            layout
            aria-selected={s.id === current}
            aria-label={s.label}
            title={s.label}
            className={'pv-step' + (s.id === current ? ' pv-current' : '')}
            onClick={() => onSelect(s.id)}
            transition={{ type: 'spring', stiffness: 500, damping: 40 }}
          >
            {(s.id === current || coarse) && (
              <motion.span layout="position" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <em>{n + 1}</em> {s.label}
              </motion.span>
            )}
          </motion.button>
        ))}
      </div>

      <div className="pv-dock-end">
        {open
          ? (
            <>
              <button type="button" className="pv-arrow" aria-label="Previous" onClick={() => onSelect(i <= 0 ? null : steps[i - 1].id)}>←</button>
              <button type="button" className="pv-arrow" aria-label="Next" onClick={() => onSelect(i >= steps.length - 1 ? null : steps[i + 1].id)}>→</button>
            </>
          )
          : <button type="button" className="pv-ghost pv-solid pv-dock-go" onClick={() => (onStart ? onStart() : onSelect(steps[0].id))}>{startLabel}</button>}
      </div>
    </nav>
  )
}
