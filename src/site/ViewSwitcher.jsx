// The switch between the site's views, as a menu off the page title.
//
// It used to be a row of pills under the heading, which read as a sub-navigation of the generator
// rather than a choice between three things of equal standing. It is now the title's own last
// word — "Province of British Columbia / Generator ▾" — opening a menu that says what each view is,
// after the org-graph site the government view is modelled on. The menu follows the WAI-ARIA menu
// button pattern: arrows move, Home and End jump, Escape closes and returns focus. The views sit
// under four headings, in two columns on a wide screen and a scrolling sheet across a phone's, so
// none falls off the page.

import { useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { preloadView } from './viewLoaders.js'

// The views, under four headings. The menu sets the first three headings down its left column and
// Objects down its right, so the list is in that order: down the left, then the right. "New" marks a
// view for its first week or so, then comes off.
export const VIEW_GROUPS = [
  { id: 'identity', label: 'Logos and identity', column: 1 },
  { id: 'government', label: 'Government', column: 1 },
  { id: 'pay', label: 'Pay', column: 1 },
  { id: 'objects', label: 'Objects', column: 2 }
]

export const VIEWS = [
  { id: 'generator', label: 'Generator', group: 'identity', description: 'A ministry lockup in any of the four identities' },
  { id: 'gallery', label: 'Logos', group: 'identity', description: 'BC Hydro, BC Timber Sales, BC Parks, and the Province’s one-off marks' },
  { id: 'internal', label: 'Departmental Logos', group: 'identity', description: 'Logos of provincial departments and services, including Forests and Travel Industry' },
  { id: 'initiatives', label: 'Initiatives', group: 'identity', description: 'Programs, campaigns and their websites, identities and publications', badge: 'New' },
  { id: 'airports', label: 'Airports', group: 'identity', description: 'British Columbia’s airports, aviation facilities and their published artwork' },
  { id: 'arms', label: 'Coats of Arms', group: 'identity', description: 'The Province’s arms and its dated drawings, and the arms of public bodies and universities' },
  { id: 'guides', label: 'Visual Guides', group: 'identity', description: 'Identity manuals, rebuilt page by page' },
  { id: 'stationery', label: 'Stationery', group: 'identity', description: 'The 1977 calling card, letterhead and envelope, filled in' },
  { id: 'government', label: 'Government', group: 'government', description: 'The Province’s structure, back to 1871' },
  { id: 'parties', label: 'Political Parties', group: 'government', description: 'Provincial parties’ logos over time, with their formations and renamings', badge: 'New' },
  { id: 'school-districts', label: 'School Districts', group: 'government', description: 'District histories, predecessor connections, original logos and salary records', badge: 'New' },
  { id: 'health-map', label: 'Health Maps', group: 'government', description: 'Historical health areas and their modern boundary comparisons' },
  { id: 'salaries', label: 'Salaries', group: 'pay', description: 'Public-sector pay by name, followed across the years' },
  { id: 'posters', label: 'Posters', group: 'objects', description: 'Posters by series, every part clickable for its history' },
  { id: 'signs', label: 'Signs', group: 'objects', description: 'Signs by series, every part clickable for its history' },
  { id: 'cards', label: 'Cards', group: 'objects', description: 'Printed cards by series, every part clickable for its history' },
  { id: 'certificates', label: 'Certificates', group: 'objects', description: 'Historical certificates and a guilloché border generator' },
  { id: 'stickers', label: 'Stickers', group: 'objects', description: 'BC Parks outreach artwork and the stickers that carried it' },
  { id: 'pins', label: 'Pins', group: 'objects', description: 'Pins and buttons by series, every part clickable for its history' },
  { id: 'patches', label: 'Patches', group: 'objects', description: 'Patches by organization, sewn as embroidery' },
  { id: 'badges', label: 'Badges', group: 'objects', description: 'Metal badges by organization' },
  { id: 'paper-models', label: 'Paper Models', group: 'objects', description: 'Fold-up models to print, folded step by step in PackCAD', badge: 'New' },
  { id: 'plates', label: 'Licence Plates', group: 'objects', description: 'B.C. licence plates since 1904, by family and era, from PlateForge' }
]

// Each view's column in the wide menu, for the left and right arrows.
const columnOf = (entry) => VIEW_GROUPS.find((group) => group.id === entry.group).column

// Views that open from a link but aren't offered in the menu yet. The title still names them.
export const HIDDEN_VIEWS = []

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
/**
 * `compact` draws the trigger as "…" where a breadcrumb has no room for the view's name; it still
 * opens the menu, and is still named for the view it is on.
 */
export const ViewSwitcher = ({ view, onChange, className = '', compact = false }) => {
  const [open, setOpen] = useState(false)
  const root = useRef(null)
  const trigger = useRef(null)
  const menu = useRef(null)
  const items = useRef([])
  const id = useId()
  const current = [...VIEWS, ...HIDDEN_VIEWS].find((entry) => entry.id === view) ?? VIEWS[0]

  // Opening moves focus to the current view's item (the first, on a hidden view), scrolled into the
  // menu's view where it is below a phone's fold; a click elsewhere closes the menu.
  useEffect(() => {
    if (!open) return undefined
    const item = items.current[Math.max(0, VIEWS.indexOf(current))]
    item?.focus({ preventScroll: true })
    item?.scrollIntoView?.({ block: 'nearest' })
    const away = (event) => { if (!root.current?.contains(event.target)) setOpen(false) }
    // A phone's toolbar showing or hiding changes only the height; a turn or a resized window
    // changes the width, and with it where the menu belongs.
    const width = document.documentElement.clientWidth
    const resize = () => { if (document.documentElement.clientWidth !== width) setOpen(false) }
    document.addEventListener('pointerdown', away)
    globalThis.addEventListener('resize', resize)
    return () => {
      document.removeEventListener('pointerdown', away)
      globalThis.removeEventListener('resize', resize)
    }
  }, [open, current])

  // The menu is placed before it is painted. Wide, it hangs from the trigger in two columns, moved
  // back in from the right edge where it would run off it. Narrow (a phone), it is a sheet across the
  // screen under the trigger (site.css). Either way it is no taller than the room below the trigger,
  // and scrolls within that, so the last views are never out of reach below the fold.
  useLayoutEffect(() => {
    if (!open || !menu.current || !trigger.current) return
    const edge = 16
    const element = menu.current
    const below = trigger.current.getBoundingClientRect().bottom + 8
    element.style.setProperty('--menu-top', `${below}px`)
    element.style.setProperty('--menu-room', `${Math.max(240, document.documentElement.clientHeight - below - edge)}px`)
    if (getComputedStyle(element).position !== 'absolute') return
    element.style.left = ''
    const box = element.getBoundingClientRect()
    const over = box.right - (document.documentElement.clientWidth - edge)
    if (over > 0) element.style.left = `${parseFloat(getComputedStyle(element).left) - Math.min(over, box.left - edge)}px`
  }, [open])

  const close = () => { setOpen(false); trigger.current?.focus() }
  const choose = (next) => { setOpen(false); if (next !== view) onChange(next) }

  // Up and down go through the views in order; where they sit in two columns, left and right cross
  // between them.
  const onMenuKey = (event) => {
    event.stopPropagation() // Artwork shortcuts underneath the menu must stay idle.
    const index = items.current.indexOf(document.activeElement)
    const twoColumns = menu.current && getComputedStyle(menu.current).getPropertyValue('--menu-columns').trim() === '2'
    const move = { ArrowDown: 1, ArrowUp: -1 }[event.key]
    if (move !== undefined) {
      event.preventDefault()
      items.current[(index + move + VIEWS.length) % VIEWS.length]?.focus()
    } else if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      // Across to the other column, at the same place down it (its last view, where it is shorter).
      event.preventDefault()
      if (!twoColumns || index < 0) return
      const here = VIEWS.filter((entry) => columnOf(entry) === columnOf(VIEWS[index]))
      const there = VIEWS.filter((entry) => columnOf(entry) !== columnOf(VIEWS[index]))
      const target = there[Math.min(here.indexOf(VIEWS[index]), there.length - 1)]
      items.current[VIEWS.indexOf(target)]?.focus()
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
        aria-label={compact ? current.label : undefined}
        title={compact ? current.label : undefined}
      >
        {compact ? '…' : current.label}
        <Chevron open={open} />
      </button>
      {open && <span className="view-switcher__backdrop" aria-hidden="true" onClick={() => setOpen(false)} />}
      {open && (
        <div ref={menu} id={id} className="view-switcher__menu" role="menu" aria-label="Switch view" onKeyDown={onMenuKey}>
          <div className="view-switcher__columns" role="none">
            {[1, 2].map((column) => (
              <div key={column} className="view-switcher__column" role="none">
                {VIEW_GROUPS.filter((group) => group.column === column).map((group) => (
                  <div key={group.id} className="view-switcher__group" role="group" aria-labelledby={`${id}-${group.id}`}>
                    <div className="view-switcher__heading" id={`${id}-${group.id}`} role="presentation">{group.label}</div>
                    {VIEWS.filter((entry) => entry.group === group.id).map((entry) => {
                      const index = VIEWS.indexOf(entry)
                      return (
                        <button
                          key={entry.id}
                          ref={(element) => { items.current[index] = element }}
                          type="button"
                          role="menuitemradio"
                          aria-checked={entry.id === view}
                          tabIndex={-1}
                          className="view-switcher__item"
                          onPointerEnter={() => preloadView(entry.id)}
                          onFocus={() => { if (entry.id !== view) preloadView(entry.id) }}
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
                      )
                    })}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </span>
  )
}
