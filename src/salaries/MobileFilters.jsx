import { useEffect, useId, useRef, useState } from 'react'
import { PeriodRange, rangeLabel } from './parts.jsx'

/** One search state, visible on every salary page and also in the mobile filter sheet. */
export const SalarySearchField = ({ value, onChange, labelled = false, label = 'Search', placeholder, help: helpText, ariaLabel = 'Search a name, an employer or a position' }) => {
  const id = useId()
  const help = `${id}-help`
  return (
    <div className="salaries__filter-field">
      {labelled && <label htmlFor={id} className="salaries__filter-label">{label}</label>}
      <span className="salaries__field">
        <input
          id={id}
          type="search"
          value={value}
          placeholder={placeholder ?? (labelled ? 'First name, surname, employer or position' : 'Any part of a name, an employer or a position')}
          aria-label={ariaLabel}
          aria-describedby={help}
          onChange={(event) => onChange(event.target.value)}
        />
        <span className="salaries__tip">
          <button type="button" className="salaries__tip-button" aria-label={helpText ? 'How this search works' : 'How names are searched'} aria-describedby={help}>i</button>
          <span role="tooltip" id={help} className="salaries__tip-text">
            {helpText ?? 'Search any part of a name, in any order, such as “Milad” or “Milad Fathi”. Partial words work too. Use a comma for a precise surname-first search, as in “Van der Meer, J”.'}
          </span>
        </span>
      </span>
    </div>
  )
}

export const SalarySectorChips = ({ sectors, employers, value, onChange }) => (
  <div className="salaries__chips" role="group" aria-label="Sector">
    <button type="button" aria-pressed={value === 'all'} onClick={() => onChange('all')}>All sectors</button>
    {sectors.map((name) => (
      <button key={name} type="button" aria-pressed={value === name} onClick={() => onChange(value === name ? 'all' : name)}>
        {name} <span>{employers.filter((entry) => entry.sector === name).length}</span>
      </button>
    ))}
  </div>
)

const focusable = (dialog) => [...dialog.querySelectorAll('button:not(:disabled), input:not(:disabled), select:not(:disabled), a[href], [tabindex="0"]')]
  .filter((node) => node.getClientRects().length && !node.closest('[hidden], [inert]'))

/** Mobile filters share the page's live values; closing never resets a filter or its URL. */
export const MobileSalaryFilters = ({ query, onSearch, years, counts, range, onRange, sectors, employers, sector, onSector, showSector = true, showFilters = true }) => {
  const [open, setOpen] = useState(false)
  const id = useId()
  const dialog = useRef(null)
  const title = useRef(null)
  const trigger = useRef(null)
  const active = Number(Boolean(query.trim())) + Number(Boolean(range)) + Number(showSector && sector !== 'all')
  const summary = [query.trim() && `“${query.trim()}”`, rangeLabel(years, range), showSector && (sector === 'all' ? 'All sectors' : sector)].filter(Boolean).join(' · ')

  useEffect(() => {
    if (!open) return undefined
    const node = dialog.current
    const previous = document.activeElement
    const opener = trigger.current
    const rootOverflow = document.documentElement.style.overflow
    const bodyOverflow = document.body.style.overflow
    document.documentElement.style.overflow = 'hidden'
    document.body.style.overflow = 'hidden'
    // Phone keyboards can shrink/pan the visual viewport without changing 100dvh.
    const viewport = globalThis.visualViewport
    const fit = () => {
      if (!viewport) return
      node.style.setProperty('--salaries-sheet-height', `${viewport.height * 0.9}px`)
      node.style.setProperty('--salaries-sheet-bottom', `${Math.max(0, globalThis.innerHeight - viewport.height - viewport.offsetTop)}px`)
    }
    fit()
    viewport?.addEventListener('resize', fit)
    viewport?.addEventListener('scroll', fit)
    globalThis.addEventListener('resize', fit)
    node.showModal()
    // A long form opens at its heading without immediately raising a phone's keyboard.
    title.current?.focus({ preventScroll: true })
    return () => {
      viewport?.removeEventListener('resize', fit)
      viewport?.removeEventListener('scroll', fit)
      globalThis.removeEventListener('resize', fit)
      node.style.removeProperty('--salaries-sheet-height')
      node.style.removeProperty('--salaries-sheet-bottom')
      node.close()
      document.documentElement.style.overflow = rootOverflow
      document.body.style.overflow = bodyOverflow
      // A touch/Safari button activation may leave body as the active element.
      // When rotating into desktop, return to the now-visible search instead.
      const desktopSearch = document.querySelector('.salaries__global-search input[type="search"]')
      const back = opener?.isConnected && opener.getClientRects().length ? opener
        : desktopSearch?.getClientRects().length ? desktopSearch : previous?.isConnected ? previous : null
      back?.focus({ preventScroll: true })
    }
  }, [open])

  useEffect(() => {
    const desktop = globalThis.matchMedia('(min-width: 640px)')
    const resized = () => { if (desktop.matches) setOpen(false) }
    desktop.addEventListener('change', resized)
    return () => desktop.removeEventListener('change', resized)
  }, [])

  useEffect(() => { if (!showFilters) setOpen(false) }, [showFilters])

  const key = (event) => {
    if (event.key !== 'Tab') return
    const controls = focusable(event.currentTarget)
    const first = controls[0]
    const last = controls.at(-1)
    if (!first) { event.preventDefault(); title.current?.focus(); return }
    const current = document.activeElement
    if (event.shiftKey && (current === first || !controls.includes(current))) {
      event.preventDefault(); last.focus()
    } else if (!event.shiftKey && (current === last || !controls.includes(current))) {
      event.preventDefault(); first.focus()
    }
  }

  const backdrop = (event) => {
    if (event.target !== event.currentTarget) return
    const rect = event.currentTarget.getBoundingClientRect()
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) setOpen(false)
  }

  return (
    <>
      <div className="salaries__mobile-filters">
        <SalarySearchField value={query} onChange={onSearch} placeholder="Name or place" />
        {showFilters && <button
          ref={trigger}
          type="button"
          className="salaries__filter-trigger"
          aria-haspopup="dialog"
          aria-controls={id}
          aria-expanded={open}
          aria-label={`Filters${active ? `, ${active} active` : ''}`}
          aria-description={summary}
          onClick={() => setOpen(true)}
        >
          <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="M3 5h14M3 10h14M3 15h14M7 3v4m6 1v4m-6 1v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <span>Filters</span>
          {active > 0 && <span className="salaries__filter-count" aria-hidden="true">{active}</span>}
        </button>}
      </div>
      <dialog
        ref={dialog}
        id={id}
        className="salaries-filter-sheet"
        aria-labelledby={`${id}-title`}
        aria-modal="true"
        onCancel={(event) => { event.preventDefault(); setOpen(false) }}
        onKeyDown={key}
        onClick={backdrop}
      >
          <div className="salaries-filter-sheet__head">
            <h2 ref={title} id={`${id}-title`} tabIndex={-1}>Search and filters</h2>
            <button type="button" className="salaries-filter-sheet__close" aria-label="Close filters" onClick={() => setOpen(false)}>
              <svg width="18" height="18" viewBox="0 0 20 20" aria-hidden="true"><path d="m5 5 10 10M15 5 5 15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>
            </button>
          </div>
        {open && <>
          <div className="salaries-filter-sheet__body">
            <SalarySearchField labelled value={query} onChange={onSearch} />
            <section aria-label="Period" className="salaries__filter-field">
              <h3 className="salaries__filter-label">Period</h3>
              <PeriodRange inline years={years} counts={counts} value={range} onChange={onRange} />
            </section>
            {showSector && <section aria-label="Filter by sector" className="salaries__filter-field">
              <h3 className="salaries__filter-label">Sector</h3>
              <SalarySectorChips sectors={sectors} employers={employers} value={sector} onChange={onSector} />
            </section>}
          </div>
          <div className="salaries-filter-sheet__actions">
            <button type="button" className="salaries__link" disabled={!active} onClick={() => { onSearch(''); onRange(null); if (showSector) onSector('all') }}>Clear filters</button>
            <button type="button" className="salaries__more" onClick={() => setOpen(false)}>Done</button>
          </div>
        </>}
      </dialog>
    </>
  )
}
