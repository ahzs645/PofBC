// What a body paid its people, as it disclosed it, in the panel's card style.
//
// Imported employee and executive disclosures are joined to the atlas by scripts/build-salaries.mjs.
// Source, reporting period and disclosure scope accompany each employer/year. Only
// the totals ship with the page (salaryIndex.js); a body's rows, a few hundred kilobytes for the
// largest, are fetched when its panel is opened, and kept for the visit.

import { useEffect, useMemo, useState } from 'react'
import { Card, CardSection, KindIcon } from './PanelCards.jsx'
import * as salaryData from './salaryIndex.js'
import { PUBLIC_SERVICE, salaryKeyOf } from './salaries.js'
import { displayName, personKey } from '../salaries/people.js'
import { DisclosureSummary, SourceLink } from '../salaries/DisclosureEvidence.jsx'
import { expenseLabel } from '../salaries/coverage.js'
import { formatMoney } from '../salaries/money.js'
import { YearPicker } from '../salaries/parts.jsx'
import { hasExpenseAmount } from '../salaries/viewState.js'
import { SiteLink, searchFor, useNavigate } from '../site/navigation.jsx'

const { SALARY_INDEX, SALARY_YEARS, SALARY_SOURCES = {}, SALARY_COVERAGE = {} } = salaryData

const PAGE = 12
const fetched = new Map()

const money = (value) => formatMoney(value, null)
const compact = (value) => (value >= 1e9 ? `$${(value / 1e9).toFixed(2)}B` : value >= 1e6 ? `$${(value / 1e6).toFixed(1)}M` : money(value))

/** The disclosure year nearest the year on screen, among those this body has. */
const nearest = (slugs, year) => {
  const startOf = (slug) => Number(slug.slice(0, 4))
  return [...slugs].sort((a, b) => Math.abs(startOf(a) - year) - Math.abs(startOf(b) - year) || startOf(b) - startOf(a))[0]
}

const load = (slug, key) => {
  const url = `${import.meta.env?.BASE_URL ?? '/'}salaries/${slug}/${key}.json`
  if (!fetched.has(url)) fetched.set(url, fetch(url)
    .then((response) => (response.ok ? response.json() : Promise.reject(new Error(response.status))))
    .catch((error) => { fetched.delete(url); throw error }))
  return fetched.get(url)
}

export const Salaries = ({ node, year }) => {
  const navigate = useNavigate()
  const key = salaryKeyOf(node)
  const years = key ? SALARY_YEARS.filter(({ slug }) => SALARY_INDEX[key]?.[slug]) : []
  // Every collection year, so the picker shows the gaps too; choosing one without records says so.
  const counts = SALARY_YEARS.map(({ slug }) => (key ? SALARY_INDEX[key]?.[slug]?.count ?? 0 : 0))
  const [slug, setSlug] = useState(() => (years.length ? nearest(years.map((each) => each.slug), year) : null))
  const [state, setState] = useState({ status: 'idle', rows: [] })
  const [query, setQuery] = useState('')
  const [shown, setShown] = useState(PAGE)
  const [loadVersion, setLoadVersion] = useState(0)
  const selectedSlug = SALARY_YEARS.some((each) => each.slug === slug) ? slug : nearest(years.map((each) => each.slug), year)
  const totals = key ? SALARY_INDEX[key]?.[selectedSlug] : null

  useEffect(() => {
    setSlug(nearest(years.map((each) => each.slug), year) ?? null)
    setShown(PAGE)
  }, [key, year])

  useEffect(() => { setQuery('') }, [key])

  useEffect(() => {
    if (!key || !selectedSlug || !totals) return undefined
    let live = true
    setState({ status: 'loading', rows: [] })
    load(selectedSlug, key).then(
      (data) => live && setState({ status: 'ready', rows: data.rows, agencies: data.agencies }),
      () => live && setState({ status: 'failed', rows: [] })
    )
    return () => { live = false }
  }, [key, selectedSlug, loadVersion, totals])

  const matches = useMemo(() => {
    const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean)
    if (!words.length) return state.rows
    return state.rows.filter(([name, position]) => {
      const text = `${name ?? ''} ${position ?? ''}`.toLowerCase()
      return words.every((word) => text.includes(word))
    })
  }, [state.rows, query])

  if (!key || !years.length) return null
  const label = SALARY_YEARS.find((each) => each.slug === selectedSlug)?.label
  const selectedIndex = SALARY_YEARS.findIndex((each) => each.slug === selectedSlug)
  const coverage = SALARY_COVERAGE[key]?.[selectedIndex]
  // A source shown once in the summary is not repeated on every card.
  const oneSource = new Set(state.rows.map((row) => row[4])).size <= 1
  const personLink = (name) => ({ view: 'salaries', q: name, person: personKey(name) })
  const follow = (name) => (navigate ? navigate(personLink(name)) : globalThis.location.assign(searchFor(personLink(name))))

  return (
    <section className="gov-card gov-salaries" aria-labelledby={`salaries-${node.id}`}>
      <div className="gov-salaries__head">
        <h2 id={`salaries-${node.id}`} className="gov-card__heading">Salaries</h2>
        <SiteLink className="gov-salaries__open" to={{ view: 'salaries', employer: key, 'employer-year': label }}>All years in Salaries →</SiteLink>
      </div>
      <p className="gov-muted gov-salaries__about">
        {key === PUBLIC_SERVICE
          ? 'The Province discloses its public service as one employer, so every ministry shows the same records.'
          : `Disclosed pay for ${node.shortName ?? node.name}${totals?.agencies?.length ? `, filed as “${totals.agencies.join('”, “')}”` : ''}.`}
      </p>
      <YearPicker years={SALARY_YEARS.map((each) => each.label)} counts={counts} coverage={SALARY_COVERAGE[key]} value={selectedIndex} onChange={(at) => { setSlug(SALARY_YEARS[at].slug); setShown(PAGE) }} />
      {!totals && <>
        <p className="gov-muted gov-salaries__about">No records have been imported for {label}. That does not mean no one was employed or paid.</p>
        {coverage && <DisclosureSummary coverage={coverage} sources={SALARY_SOURCES} className="gov-salaries__disclosure" />}
      </>}
      {totals && (
        <>
          <dl className="gov-tiles">
            <div><dt>Records</dt><dd>{totals.count.toLocaleString('en-CA')}</dd></div>
            <div><dt>Disclosed total</dt><dd>{compact(totals.total)}</dd></div>
            <div><dt>Median</dt><dd>{money(totals.median)}</dd></div>
          </dl>
          <DisclosureSummary
            coverage={{ ...coverage, status: 'available', ...totals }}
            sources={SALARY_SOURCES}
            className="gov-salaries__disclosure"
            more={<p>Figures are the records’ remuneration or compensation for the reporting period. Record counts are not verified headcounts, and the disclosed total is not necessarily the employer’s full payroll.</p>}
          />
          <input
            type="search"
            className="gov-salaries__search"
            placeholder="Search a name or a position"
            aria-label={`Search ${label} salaries`}
            value={query}
            onChange={(event) => { setQuery(event.target.value); setShown(PAGE) }}
          />
          {state.status === 'loading' && <p className="gov-muted" role="status">Loading {label}…</p>}
          {state.status === 'failed' && <p className="gov-muted" role="alert">The {label} records could not be loaded. <button type="button" onClick={() => setLoadVersion((value) => value + 1)}>Retry</button></p>}
          {state.status === 'ready' && (
            <CardSection
              title={query ? 'Matching' : 'Highest paid'}
              meta={`${matches.length.toLocaleString('en-CA')} ${matches.length === 1 ? 'record' : 'records'} · ${label}`}
              footer={matches.length > shown && (
                <button type="button" className="gov-show-more gov-cards__more" onClick={() => setShown((count) => count + PAGE * 2)}>
                  Show {Math.min(PAGE * 2, matches.length - shown)} more
                </button>
              )}
            >
              {matches.length === 0 && <p className="gov-muted">No imported records match “{query.trim()}”. Try a surname or position.</p>}
              {matches.slice(0, shown).map(([name, position, pay, expenses, sourceId, pdfPage], index) => (
                <div key={`${name}-${position}-${index}`} className="gov-salaries__record">
                <Card
                  icon={<KindIcon person branch={node.branch ?? 'executive'} />}
                  title={displayName(name, SALARY_SOURCES[sourceId]?.nameDisclosure) ?? 'Name not given'}
                  lines={[position, hasExpenseAmount(expenses) ? `${expenseLabel(sourceId, SALARY_SOURCES)} ${money(expenses)}` : null, !oneSource && sourceId ? SALARY_SOURCES[sourceId]?.title : null]}
                  aside={money(pay)}
                  onClick={name ? () => follow(name) : undefined}
                />
                {pdfPage && <p className="salaries__source"><SourceLink sourceId={sourceId} sources={SALARY_SOURCES} pdfPage={pdfPage} /></p>}
                </div>
              ))}
            </CardSection>
          )}
        </>
      )}
    </section>
  )
}
