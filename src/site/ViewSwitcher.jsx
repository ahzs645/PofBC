// The switch between the site's views, as a menu off the page title.
//
// It used to be a row of pills under the heading, which read as a sub-navigation of the generator
// rather than a choice between three things of equal standing. It is now the title's own last
// word — "Province of British Columbia / Generator ▾" — opening a menu that says what each view is,
// after the org-graph site the government view is modelled on. The menu follows the WAI-ARIA menu
// button pattern: arrows move, Home and End jump, Escape closes and returns focus.

import { useEffect, useId, useRef, useState } from 'react'

export const VIEWS = [
  { id: 'generator', label: 'Generator', description: 'A ministry lockup in any of the four identities' },
  { id: 'gallery', label: 'Logos', description: 'BC Hydro, BC Timber Sales, BC Parks, and the Province’s one-off marks' },
  { id: 'government', label: 'Government', description: 'The Province’s structure, back to 1871', badge: 'New' }
]

const Check = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
    <path d="M2.5 7.5l3 3 6-7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const Chevron = ({ open }) => (
  <svg width="10" height="10" viewBox="0 0 18 10" fill="none" aria-hidden="true" style={{ transform: open ? 'rotate(180deg)' : undefined }}>
    <path d="M1.64 0.74 0.74 1.64 8.55 9.45 9 9.88 9.45 9.45 17.26 1.64 16.36 0.74 9 8.1 1.64 0.74Z" fill="currentColor" />
  </svg>
)

/**
 * @param {object} props
 * @param {string} props.view                 The view on screen.
 * @param {(view: string) => void} props.onChange
 * @param {string} [props.className]
 */
export const ViewSwitcher = ({ view, onChange, className = '' }) => {
  const [open, setOpen] = useState(false)
  const root = useRef(null)
  const trigger = useRef(null)
  const items = useRef([])
  const id = useId()
  const current = VIEWS.find((entry) => entry.id === view) ?? VIEWS[0]

  // Opening moves focus to the current view's item; a click elsewhere closes the menu.
  useEffect(() => {
    if (!open) return undefined
    items.current[VIEWS.indexOf(current)]?.focus()
    const away = (event) => { if (!root.current?.contains(event.target)) setOpen(false) }
    document.addEventListener('pointerdown', away)
    return () => document.removeEventListener('pointerdown', away)
  }, [open, current])

  const close = () => { setOpen(false); trigger.current?.focus() }
  const choose = (next) => { setOpen(false); if (next !== view) onChange(next) }

  const onMenuKey = (event) => {
    const index = items.current.indexOf(document.activeElement)
    const move = { ArrowDown: 1, ArrowUp: -1 }[event.key]
    if (move) {
      event.preventDefault()
      items.current[(index + move + VIEWS.length) % VIEWS.length]?.focus()
    } else if (event.key === 'Home' || event.key === 'End') {
      event.preventDefault()
      items.current[event.key === 'Home' ? 0 : VIEWS.length - 1]?.focus()
    } else if (event.key === 'Escape' || event.key === 'Tab') {
      if (event.key === 'Escape') event.preventDefault()
      close()
    }
  }

  return (
    <span className={`view-switcher ${className}`} ref={root}>
      <button
        ref={trigger}
        type="button"
        className="view-switcher__trigger"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={open ? id : undefined}
        onClick={() => setOpen((value) => !value)}
        onKeyDown={(event) => { if (event.key === 'ArrowDown') { event.preventDefault(); setOpen(true) } }}
      >
        {current.label}
        <Chevron open={open} />
      </button>
      {open && (
        <div id={id} className="view-switcher__menu" role="menu" aria-label="Switch view" onKeyDown={onMenuKey}>
          <div className="view-switcher__heading" aria-hidden="true">Switch view</div>
          {VIEWS.map((entry, index) => (
            <button
              key={entry.id}
              ref={(element) => { items.current[index] = element }}
              type="button"
              role="menuitemradio"
              aria-checked={entry.id === view}
              tabIndex={-1}
              className="view-switcher__item"
              onClick={() => choose(entry.id)}
            >
              <span className="view-switcher__text">
                <span className="view-switcher__label">
                  {entry.label}
                  {entry.badge && <span className="view-switcher__badge">{entry.badge}</span>}
                </span>
                <span className="view-switcher__description">{entry.description}</span>
              </span>
              <span className="view-switcher__check">{entry.id === view && <Check />}</span>
            </button>
          ))}
        </div>
      )}
    </span>
  )
}
