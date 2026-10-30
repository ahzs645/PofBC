// What the salary pages share: loading their files, the card icons, a record as a row, and the place
// (who or what is open) kept in the address bar (viewState.js).

import { displayName } from './people.js'
import { sourceHref } from './coverage.js'
import { SourceLink } from './DisclosureEvidence.jsx'
import { formatMoney as money } from './money.js'
import { hasExpenseAmount, readSalaryPlace, salaryPlaceUrl } from './viewState.js'

const BASE = import.meta.env?.BASE_URL ?? '/'
const loaded = new Map()

export const count = (value, one, many) => `${value.toLocaleString('en-CA')} ${value === 1 ? one : many}`
export const wordsOf = (text) => text.trim().toLowerCase().split(/\s+/).filter(Boolean)
export const seenYears = (entry) => entry.counts.map((value, at) => (value > 0 ? at : null)).filter((at) => at !== null)
export const latestYear = (entry) => entry.counts.reduce((best, value, at) => (value ? at : best), 0)
export const toTop = () => globalThis.scrollTo?.({ top: 0 })

/** A gzipped file, decompressed here; or plain JSON, if the server already undid the gzip. */
export const loadJson = (path) => {
  if (!loaded.has(path)) {
    loaded.set(path, fetch(`${BASE}${path}`).then(async (response) => {
      if (!response.ok) throw new Error(`${response.status}`)
      const bytes = new Uint8Array(await response.arrayBuffer())
      if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
        const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))
        return JSON.parse(await new Response(stream).text())
      }
      return JSON.parse(new TextDecoder().decode(bytes))
    }).catch((error) => { loaded.delete(path); throw error }))
  }
  return loaded.get(path)
}

export const readPlace = () => readSalaryPlace(globalThis.location?.search ?? '')

export const writePlace = (place) => {
  if (!globalThis.history?.replaceState) return
  globalThis.history.replaceState(null, '', salaryPlaceUrl(globalThis.location.href, place))
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
 * A record as a row: who or what on the left, the pay on the right, and its source under the pay —
 * opening at the record's page where the parser recorded one. A disclosed $0 expense is shown.
 */
export const RecordRow = ({ rank, name, position, pay, expenses, expenseText, sourceId, sources, pdfPage, onPerson, nameDisclosure }) => (
  <li className="salaries-row">
    {rank != null && <span className="salaries-row__rank">{rank}</span>}
    <span className="salaries-row__who">
      {name !== undefined && (name
        ? <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(name)}>{displayName(name, nameDisclosure)}</button>
        : <span className="salaries-row__name salaries__line">Name not given</span>)}
      {position && <span className="salaries__line">{position}</span>}
    </span>
    <span className="salaries-row__pay">
      {money(pay)}
      {(hasExpenseAmount(expenses) || sourceHref(sources?.[sourceId], pdfPage)) && (
        <span className="salaries__line">
          {hasExpenseAmount(expenses) ? `${expenseText} ${money(expenses)}` : ''}
          {hasExpenseAmount(expenses) && sourceHref(sources?.[sourceId], pdfPage) ? ' · ' : ''}
          {sourceId && <SourceLink sourceId={sourceId} sources={sources} pdfPage={pdfPage} />}
        </span>
      )}
    </span>
  </li>
)

/** "Show 80 more", under a list cut short. */
export const More = ({ shown, total, step, onMore, inner = false }) => (total > shown
  ? <button type="button" className={`salaries__more${inner ? ' salaries__more--inner' : ''}`} onClick={onMore}>Show {Math.min(step, total - shown).toLocaleString('en-CA')} more of {total.toLocaleString('en-CA')}</button>
  : null)
