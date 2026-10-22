// What a body paid its people, as it disclosed it, in the panel's card style.
//
// The rows are each employer's own disclosure of pay over $75,000 (and every elected official),
// compiled in the pssdb files and joined to the atlas's bodies by scripts/build-salaries.mjs. Only
// the totals ship with the page (salaryIndex.js); a body's rows, a few hundred kilobytes for the
// largest, are fetched when its panel is opened, and kept for the visit.

import { useEffect, useMemo, useState } from 'react'
import { Card, CardSection, KindIcon } from './PanelCards.jsx'
import { SALARY_INDEX, SALARY_YEARS } from './salaryIndex.js'
import { PUBLIC_SERVICE, salaryKeyOf } from './salaries.js'
import { personKey } from '../salaries/people.js'

const PAGE = 12
const fetched = new Map()

const money = (value) => (value === null || value === undefined ? null : `$${Math.round(value).toLocaleString('en-CA')}`)
const compact = (value) => (value >= 1e9 ? `$${(value / 1e9).toFixed(2)}B` : value >= 1e6 ? `$${(value / 1e6).toFixed(1)}M` : money(value))

/** Opens the salary search on a person, to follow their name through the other years. */
const followPerson = (name) => {
  const url = new URL(globalThis.location.href)
  for (const key of [...url.searchParams.keys()]) url.searchParams.delete(key)
  url.searchParams.set('view', 'salaries')
  url.searchParams.set('q', name)
  url.searchParams.set('person', personKey(name))
  globalThis.location.assign(url)
}

/** The disclosure year nearest the year on screen, among those this body has. */
const nearest = (slugs, year) => {
  const startOf = (slug) => Number(slug.slice(0, 4))
  return [...slugs].sort((a, b) => Math.abs(startOf(a) - year) - Math.abs(startOf(b) - year) || startOf(b) - startOf(a))[0]
}

const load = (slug, key) => {
  const url = `${import.meta.env?.BASE_URL ?? '/'}salaries/${slug}/${key}.json`
  if (!fetched.has(url)) fetched.set(url, fetch(url).then((response) => (response.ok ? response.json() : Promise.reject(new Error(response.status)))))
  return fetched.get(url)
}

export const Salaries = ({ node, year }) => {
  const key = salaryKeyOf(node)
  const years = key ? SALARY_YEARS.filter(({ slug }) => SALARY_INDEX[key]?.[slug]) : []
  const [slug, setSlug] = useState(() => (years.length ? nearest(years.map((each) => each.slug), year) : null))
  const [state, setState] = useState({ status: 'idle', rows: [] })
  const [query, setQuery] = useState('')
  const [shown, setShown] = useState(PAGE)

  useEffect(() => {
    if (!key || !slug) return undefined
    let live = true
    setState({ status: 'loading', rows: [] })
    load(slug, key).then(
      (data) => live && setState({ status: 'ready', rows: data.rows, agencies: data.agencies }),
      () => live && setState({ status: 'failed', rows: [] })
    )
    return () => { live = false }
  }, [key, slug])

  const matches = useMemo(() => {
    const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean)
    if (!words.length) return state.rows
    return state.rows.filter(([name, position]) => {
      const text = `${name ?? ''} ${position ?? ''}`.toLowerCase()
      return words.every((word) => text.includes(word))
    })
  }, [state.rows, query])

  if (!key || !years.length) return null
  const totals = SALARY_INDEX[key][slug]
  const label = years.find((each) => each.slug === slug)?.label

  return (
    <section className="gov-card gov-salaries" aria-labelledby={`salaries-${node.id}`}>
      <h2 id={`salaries-${node.id}`} className="gov-card__heading">Salaries</h2>
      <p className="gov-muted gov-salaries__about">
        {key === PUBLIC_SERVICE
          ? 'The Province discloses its public service as one employer, so these are everyone it paid over $75,000 in any ministry: the disclosure does not say which.'
          : `What ${node.shortName ?? node.name} disclosed it paid each person over $75,000${totals.agencies?.length ? `, as “${totals.agencies.join('”, “')}”` : ''}.`}
      </p>
      {years.length > 1 && (
        <div className="gov-salaries__years" role="group" aria-label="Disclosure year">
          {years.map((each) => (
            <button key={each.slug} type="button" aria-pressed={each.slug === slug} onClick={() => { setSlug(each.slug); setShown(PAGE) }}>{each.label}</button>
          ))}
        </div>
      )}
      <dl className="gov-tiles">
        <div><dt>People</dt><dd>{totals.count.toLocaleString('en-CA')}</dd></div>
        <div><dt>Total paid</dt><dd>{compact(totals.total)}</dd></div>
        <div><dt>Median</dt><dd>{money(totals.median)}</dd></div>
      </dl>
      <input
        type="search"
        className="gov-salaries__search"
        placeholder="Search a name or a position"
        aria-label={`Search ${label} salaries`}
        value={query}
        onChange={(event) => { setQuery(event.target.value); setShown(PAGE) }}
      />
      {state.status === 'loading' && <p className="gov-muted">Loading {label}…</p>}
      {state.status === 'failed' && <p className="gov-muted">The {label} disclosure could not be loaded.</p>}
      {state.status === 'ready' && (
        <CardSection
          title={query ? 'Matching' : 'Highest paid'}
          meta={`${matches.length.toLocaleString('en-CA')} ${matches.length === 1 ? 'person' : 'people'} · ${label}`}
          footer={matches.length > shown && (
            <button type="button" className="gov-show-more gov-cards__more" onClick={() => setShown((count) => count + PAGE * 2)}>
              Show {Math.min(PAGE * 2, matches.length - shown)} more
            </button>
          )}
        >
          {matches.slice(0, shown).map(([name, position, pay, expenses, department], index) => (
            <Card
              key={`${name}-${position}-${index}`}
              icon={<KindIcon person branch={node.branch ?? 'executive'} />}
              title={name ?? 'Name not given'}
              lines={[[position, department].filter(Boolean).join(' · ') || null, expenses ? `Expenses ${money(expenses)}` : null]}
              aside={money(pay)}
              onClick={name ? () => followPerson(name) : undefined}
            />
          ))}
        </CardSection>
      )}
      <p className="gov-muted gov-salaries__source">
        Disclosed by each employer under the Financial Information Act; compiled in the pssdb public-sector salary files.
        Pay is the year’s remuneration, not a salary rate.
      </p>
    </section>
  )
}
