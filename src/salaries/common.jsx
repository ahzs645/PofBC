// What the salary pages share: loading their files, the card icons, a record as a row, and the place
// (who or what is open) kept in the address bar (viewState.js).

import { useEffect, useState } from 'react'
import { displayName } from './people.js'
import { sourceHref } from './coverage.js'
import { SourceLink } from './DisclosureEvidence.jsx'
import { formatMoney as money } from './money.js'
import { hasExpenseAmount } from './viewState.js'

const BASE = import.meta.env?.BASE_URL ?? '/'
const loaded = new Map()

export const count = (value, one, many) => `${value.toLocaleString('en-CA')} ${value === 1 ? one : many}`
export const wordsOf = (text) => text.trim().toLowerCase().split(/\s+/).filter(Boolean)
export const seenYears = (entry) => entry.counts.map((value, at) => (value > 0 ? at : null)).filter((at) => at !== null)
export const latestYear = (entry) => entry.counts.reduce((best, value, at) => (value ? at : best), 0)
export const toTop = () => globalThis.scrollTo?.({ top: 0 })

export const SalaryPageHeading = ({ id, back, children }) => (
  <div className="salaries__page-heading">
    {back}
    <h2 id={id} className="salaries__heading">{children}</h2>
  </div>
)

/** A gzipped file, decompressed here; or plain JSON, if the server already undid the gzip. */
export const loadJson = (path, { reload = false } = {}) => {
  if (reload) loaded.delete(path)
  if (!loaded.has(path)) {
    const request = fetch(`${BASE}${path}`, { headers: { Accept: 'application/json' }, ...(reload ? { cache: 'reload' } : {}) }).then(async (response) => {
      if (!response.ok) throw new Error(`${response.status}`)
      const bytes = new Uint8Array(await response.arrayBuffer())
      if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
        const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))
        return JSON.parse(await new Response(stream).text())
      }
      return JSON.parse(new TextDecoder().decode(bytes))
    }).catch((error) => { if (loaded.get(path) === request) loaded.delete(path); throw error })
    loaded.set(path, request)
  }
  return loaded.get(path)
}

export const PersonIcon = () => (
  <svg className="salaries__icon" viewBox="0 0 21 22" aria-hidden="true">
    <rect x="4.25" y="8" width="12.5" height="10" rx="2.6" fill="var(--surface)" />
    <rect x="4.25" y="8" width="12.5" height="10" rx="2.6" fill="var(--salaries-ink)" fillOpacity="0.5" />
    <rect x="4.25" y="8" width="12.5" height="10" rx="2.6" fill="none" stroke="var(--salaries-ink)" />
    <circle cx="10.5" cy="8" r="3.75" fill="var(--surface)" />
    <circle cx="10.5" cy="8" r="3.75" fill="var(--salaries-ink)" fillOpacity="0.5" />
    <circle cx="10.5" cy="8" r="3.75" fill="none" stroke="var(--salaries-ink)" />
  </svg>
)

/** A position or an employer: a briefcase, in the same layered style. */
export const RoleIcon = () => (
  <svg className="salaries__icon" viewBox="0 0 21 22" aria-hidden="true">
    {[{ fill: 'var(--surface)' }, { fill: 'var(--salaries-ink)', fillOpacity: 0.5 }, { fill: 'none', stroke: 'var(--salaries-ink)' }].map((layer, at) => (
      <g key={at}>
        <rect x="3.5" y="7.5" width="14" height="10" rx="2.4" {...layer} />
        <path d="M8 7.5V5.6a1.3 1.3 0 0 1 1.3-1.3h2.4A1.3 1.3 0 0 1 13 5.6v1.9" fill="none" stroke={layer.stroke ?? 'none'} />
      </g>
    ))}
  </svg>
)

/**
 * A record as a card, like the other cards: who on the left, the pay and rank on the right, and the
 * expenses and source under the name — the source opening at the record's page where the parser
 * recorded one. The whole card opens the name; the source link sits above that. A disclosed $0
 * expense is shown.
 */
export const RecordRow = ({ rank, name, position, pay, expenses, expenseText, sourceId, sources, pdfPage, onPerson, nameDisclosure }) => {
  const href = sourceHref(sources?.[sourceId], pdfPage)
  const expense = hasExpenseAmount(expenses)
  return (
    <li className={`salaries__card salaries-record-card${name ? '' : ' salaries__card--still'}`}>
      <span className="salaries__lead"><PersonIcon /></span>
      <span className="salaries__text">
        {name !== undefined && (name
          ? <button type="button" className="salaries__name salaries-record-card__open" onClick={() => onPerson(name)}>{displayName(name, nameDisclosure)}</button>
          : <span className="salaries__name" data-missing>Name unavailable</span>)}
        {position && <span className="salaries__line">{position}</span>}
        {(expense || href) && (
          <span className="salaries__line">
            {expense ? `${expenseText} ${money(expenses)}` : ''}
            {expense && href ? ' · ' : ''}
            {sourceId && <SourceLink sourceId={sourceId} sources={sources} pdfPage={pdfPage} />}
          </span>
        )}
      </span>
      <span className="salaries__aside">{money(pay)}{rank != null && <span className="salaries__line">No. {rank}</span>}</span>
    </li>
  )
}

/**
 * A list in pages: `items` is the page on screen, `pager` the control under it (none for one page).
 * The page returns to the first whenever `reset` changes — a new filter, year or order.
 */
export const usePages = (list, size, reset) => {
  const [state, setState] = useState({ page: 1, reset })
  // Remember every new search/filter key, including while its results are loading. Otherwise
  // revisiting an earlier query can resurrect the page number left under that old key.
  if (state.reset !== reset) setState({ page: 1, reset })
  const page = state.reset === reset ? state.page : 1
  const pages = Math.max(1, Math.ceil(list.length / size))
  const at = Math.min(page, pages)
  const go = (next) => setState({ page: next, reset })
  return {
    items: list.slice((at - 1) * size, at * size),
    pager: pages > 1 ? <Pager page={at} pages={pages} total={list.length} size={size} onPage={go} /> : null
  }
}

/** Whether the screen is a phone's width, kept current as it turns. */
const useNarrow = (query = '(max-width: 480px)') => {
  const [narrow, setNarrow] = useState(() => globalThis.matchMedia?.(query).matches ?? false)
  useEffect(() => {
    const list = globalThis.matchMedia?.(query)
    if (!list) return undefined
    const change = () => setNarrow(list.matches)
    change()
    list.addEventListener('change', change)
    return () => list.removeEventListener('change', change)
  }, [query])
  return narrow
}

/**
 * Numbered pages on one line: the first, the last, and the two either side of the one on screen —
 * one either side on a phone, where five would not fit beside the arrows, and none on the narrowest.
 */
export const Pager = ({ page, pages, total, size, onPage }) => {
  const narrow = useNarrow()
  const narrowest = useNarrow('(max-width: 359px)')
  const reach = narrowest ? 0 : narrow ? 1 : 2
  const shown = [...new Set([1, ...Array.from({ length: reach * 2 + 1 }, (_, at) => page - reach + at), pages])].filter((at) => at >= 1 && at <= pages).sort((a, b) => a - b)
  const turn = (at) => { onPage(at); globalThis.requestAnimationFrame?.(() => globalThis.document?.activeElement?.closest?.('section')?.scrollIntoView?.({ block: 'start' })) }
  return (
    <nav className="salaries-pager" aria-label="Pages">
      <button type="button" disabled={page === 1} onClick={() => turn(page - 1)} aria-label="Previous page">‹</button>
      {shown.map((at, index) => (
        <span key={at} className="salaries-pager__slot">
          {index > 0 && at - shown[index - 1] > 1 && <span className="salaries-pager__gap" aria-hidden="true">…</span>}
          <button type="button" aria-current={at === page ? 'page' : undefined} onClick={() => turn(at)}>{at}</button>
        </span>
      ))}
      <button type="button" disabled={page === pages} onClick={() => turn(page + 1)} aria-label="Next page">›</button>
      <span className="salaries-pager__range">{((page - 1) * size + 1).toLocaleString('en-CA')}–{Math.min(total, page * size).toLocaleString('en-CA')} of {total.toLocaleString('en-CA')}</span>
    </nav>
  )
}

/** `usePages` where a hook cannot go: `children(items)` draws the page on screen. */
export const Paged = ({ list, size, reset, children }) => {
  const { items, pager } = usePages(list, size, reset)
  return <>{children(items)}{pager}</>
}

const CardsIcon = () => (
  <svg className="salaries__layout-icon" viewBox="0 0 16 16" aria-hidden="true">
    <rect x="2" y="2" width="5" height="5" rx="1.2" /><rect x="9" y="2" width="5" height="5" rx="1.2" />
    <rect x="2" y="9" width="5" height="5" rx="1.2" /><rect x="9" y="9" width="5" height="5" rx="1.2" />
  </svg>
)
const TableIcon = () => (
  <svg className="salaries__layout-icon" viewBox="0 0 16 16" aria-hidden="true">
    <rect x="2" y="2.5" width="12" height="2.5" rx="1" /><rect x="2" y="6.75" width="12" height="2.5" rx="1" /><rect x="2" y="11" width="12" height="2.5" rx="1" />
  </svg>
)

/** Cards or a table: the choice offered above every list that has both, as two icons. */
export const LAYOUTS = [
  { value: 'cards', label: <CardsIcon />, ariaLabel: 'Cards', title: 'Cards' },
  { value: 'table', label: <TableIcon />, ariaLabel: 'Table', title: 'Table' }
]
