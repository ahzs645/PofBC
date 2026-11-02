// Licence plates: British Columbia's plates from PlateForge (vendor/plateforge, see README), family by
// family and era by era, each opening on a viewer that redraws it with any serial. The plates, their
// dates and their sources are PlateForge's; this view is the site's chrome around its embed API
// (vendor/plateforge/docs/embed.md), which lays them out with the same grouping PlateForge's own
// gallery uses.
//
// Two ways in, as the government view has a graph and a timeline: By family lists every design
// family by family and era by era; By year is a timeline of the families on one axis (PlatesTimeline),
// scrubbed or played like the government's, with the plates in use in the chosen year under it.
//
// The place is kept in the address bar (`?view=plates&family=commercial`, `?view=plates&plate=1953`,
// `?view=plates&year=1953`), so a link to a family, a year or one plate opens it there.

import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { BRITISH_COLUMBIA } from 'plateforge/bc'
import { PlateView, plateforgeLink, regionFamilies, regionSections, samplePlate, setupPlates, statusBadge } from 'plateforge'
import { searchFor } from '../site/navigation.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { PlateViewer } from './PlateViewer.jsx'
import { YearTimeline } from './PlatesTimeline.jsx'
import { inUse, lanesOf, spanOf } from './timeline.js'
import './plates.css'

const REGION = BRITISH_COLUMBIA
const FAMILIES = regionFamilies(REGION)
const TOTAL = FAMILIES.reduce((n, family) => n + family.formats.length, 0)
const SPAN = spanOf(REGION.formats)
const familyOf = (format) => FAMILIES.find((family) => family.formats.includes(format))

const MODES = [
  { value: 'family', label: 'By family', title: 'Every design, family by family and era by era' },
  { value: 'year', label: 'By year', title: 'A timeline of the families, and the plates in use in any year' }
]

/** Every design of a family in its timeline's order, with the era it sits in, for stepping. */
const orderOf = (familyId) => regionSections(REGION, { family: familyId })
  .flatMap((section) => section.cards.map((card) => ({ format: card.format, section })))

const read = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const family = FAMILIES.some((f) => f.id === params.get('family')) ? params.get('family') : null
  const plate = REGION.formats.some((f) => f.id === params.get('plate')) ? params.get('plate') : null
  const year = Number(params.get('year'))
  return { family, plate, year: Number.isInteger(year) && year >= SPAN[0] && year <= SPAN[1] ? year : null }
}

const write = ({ family, plate, year }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'plates')
  for (const [key, value] of Object.entries({ family, plate, year })) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  globalThis.history.replaceState(null, '', url)
}

const isPlainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey

/**
 * A thumbnail drawn once it nears the screen: a family can hold eighty plates, each a full SVG
 * scene, and most of the page is below the fold.
 */
const LazyPlate = ({ format }) => {
  const box = useRef(null)
  const [shown, setShown] = useState(() => typeof IntersectionObserver === 'undefined')
  useEffect(() => {
    if (shown || !box.current) return undefined
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) { setShown(true); observer.disconnect() }
    }, { rootMargin: '600px 0px' })
    observer.observe(box.current)
    return () => observer.disconnect()
  }, [shown])
  return (
    <span ref={box} className="plates__thumb">
      {shown && <PlateView plate={samplePlate(REGION, format)} className="plates__art" />}
    </span>
  )
}

/** A design's card: its drawn sample, name, period or era, and any status PlateForge gives it. */
const PlateCard = ({ format, meta, href, onOpen, cardRef }) => (
  <a
    ref={cardRef}
    className="plates__card"
    href={href}
    onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); onOpen() } }}
  >
    <LazyPlate format={format} />
    <span className="plates__card-text">
      <span className="plates__title">{format.label}</span>
      <span className="plates__meta">
        {meta && meta !== format.label && meta}
        {statusBadge(format) && <span className="plates__status">{statusBadge(format)}</span>}
      </span>
    </span>
  </a>
)

const periodText = ([from, to]) => (from === to ? String(from) : `${from}–${to}`)

export const PlatesView = () => {
  const [place, setPlace] = useState(read)
  const [query, setQuery] = useState('')
  const [playing, setPlaying] = useState(false)
  const deferredQuery = useDeferredValue(query)
  const cards = useRef({})
  const mode = place.year === null ? 'family' : 'year'

  useEffect(() => { setupPlates() }, [])

  const go = useCallback((next) => {
    setPlace(next)
    write(next)
  }, [])

  // Playing steps a year at a time to today, from the start again if it is already there.
  const placeRef = useRef(place)
  placeRef.current = place
  useEffect(() => {
    if (!playing) return undefined
    const timer = setInterval(() => {
      const current = placeRef.current
      if (current.year === null || current.year >= SPAN[1]) { setPlaying(false); return }
      go({ ...current, year: current.year + 1 })
    }, 280)
    return () => clearInterval(timer)
  }, [playing, go])
  const play = () => {
    if (playing) { setPlaying(false); return }
    if (place.year >= SPAN[1]) go({ ...place, year: SPAN[0] })
    setPlaying(true)
  }
  const setYear = (year) => { setPlaying(false); go({ ...place, year }) }

  const families = useMemo(() => FAMILIES
    .filter((family) => !place.family || family.id === place.family)
    .map((family) => ({ family, sections: regionSections(REGION, { family: family.id, query: deferredQuery }) }))
    .filter(({ sections }) => sections.some((section) => section.cards.length || section.gap)),
  [place.family, deferredQuery])
  const shown = families.reduce((n, { sections }) => n + sections.reduce((m, s) => m + s.cards.length, 0), 0)

  const open = place.plate ? REGION.formats.find((f) => f.id === place.plate) : null
  const openFamily = open ? familyOf(open) : null
  const order = useMemo(() => (openFamily ? orderOf(openFamily.id) : []), [openFamily])

  // The year timeline: a strip per family, or, with one family chosen, a lane per design.
  const chosen = FAMILIES.find((family) => family.id === place.family)
  const rows = useMemo(() => (chosen
    ? lanesOf(chosen.formats).map((formats, index) => ({ id: `lane-${index}`, label: '', formats }))
    : FAMILIES.map((family) => ({ id: family.id, label: family.label, formats: family.formats }))), [chosen])
  const using = useMemo(() => {
    if (mode !== 'year') return []
    const words = deferredQuery.toLowerCase().split(/\s+/).filter(Boolean)
    return FAMILIES
      .filter((family) => !chosen || family === chosen)
      .map((family) => ({
        family,
        formats: family.formats
          .filter((format) => inUse(format, place.year))
          .filter((format) => words.every((word) => `${format.label} ${format.id} ${family.label}`.toLowerCase().includes(word)))
          .sort((a, b) => a.period[0] - b.period[0] || a.period[1] - b.period[1])
      }))
      .filter(({ formats }) => formats.length)
  }, [mode, chosen, place.year, deferredQuery])
  const usingCount = using.reduce((n, { formats }) => n + formats.length, 0)

  // Back from a plate lands on its card.
  const close = useCallback(() => {
    const id = place.plate
    go({ ...place, plate: null })
    requestAnimationFrame(() => cards.current[id]?.focus())
  }, [go, place])

  useEffect(() => { if (!open) return; globalThis.scrollTo?.({ top: 0 }) }, [open])

  if (open) {
    const at = order.findIndex((entry) => entry.format === open)
    return (
      <PlateViewer
        key={open.id}
        region={REGION}
        format={open}
        family={openFamily}
        section={order[at]?.section}
        position={{ index: at, count: order.length }}
        previous={order[at - 1]?.format ?? null}
        next={order[at + 1]?.format ?? null}
        onOpen={(format) => go({ ...place, plate: format.id })}
        onClose={close}
      />
    )
  }

  return (
    <section className="plates" aria-label="Licence plates">
      <div className="plates__intro">
        <h2>Licence plates <span className="plates__count">{TOTAL}</span></h2>
        {/* Hidden on a phone, where it would push the controls below the fold. */}
        <p className="plates__lede">
          British Columbia’s plates from the leather plates of 1904 to the flag base of today, in {FAMILIES.length} families:
          passenger, commercial, farm, motorcycle, official, municipal and the rest. Each is a research reconstruction
          from <a href={plateforgeLink(REGION)} target="_blank" rel="noreferrer">PlateForge</a>, redrawn as SVG from
          photographs and source notes, and opens to take any serial.
        </p>
        <div className="plates__filters">
          <label className="plates__filter">
            <span>Family</span>
            <select value={place.family ?? ''} onChange={(event) => go({ ...place, family: event.target.value || null, plate: null })}>
              <option value="">All {FAMILIES.length} families</option>
              {FAMILIES.map((family) => <option key={family.id} value={family.id}>{family.label} ({family.formats.length})</option>)}
            </select>
          </label>
          <label className="plates__filter plates__filter--grow">
            <span>Search</span>
            <input type="search" value={query} placeholder="1953, flag, totem, Expo…" onChange={(event) => setQuery(event.target.value)} />
          </label>
          <div className="plates__mode">
            <Segmented
              ariaLabel="Arrange the plates"
              options={MODES}
              value={mode}
              onChange={(next) => { setPlaying(false); go({ ...place, year: next === 'year' ? SPAN[1] : null }) }}
            />
          </div>
        </div>
      </div>

      {mode === 'year' && (
        <>
          <section className="plates__family plates__timeline" aria-label="Timeline">
            <YearTimeline
              rows={rows}
              span={SPAN}
              year={place.year}
              onYear={setYear}
              playing={playing}
              onPlay={play}
              onRow={chosen ? undefined : (id) => go({ ...place, family: id })}
              note={chosen
                ? `${chosen.label}: each bar is one design, across the years it was issued or valid; those in use in ${place.year} are highlighted. Choose “All families” above to see every family again.`
                : `Each bar is a design, across the years it was issued or valid; those in use in ${place.year} are highlighted. Choose a family to see its designs one by one.`}
            />
          </section>
          <section className="plates__family" aria-labelledby="plates-in-use">
            <header className="plates__family-head">
              <h3 id="plates-in-use">In use in {place.year}</h3>
              <span className="plates__count">{usingCount}</span>
              <p>
                {usingCount === 0
                  ? (deferredQuery ? `No plates in use in ${place.year} match “${deferredQuery}”.` : `PlateForge has no ${chosen ? chosen.label.toLowerCase() + ' ' : ''}plates dated to ${place.year}.`)
                  : 'Issued that year, or still valid from an earlier issue: a multi-year base renewed with tabs or decals counts in every year it was on the road.'}
              </p>
            </header>
            {using.map(({ family, formats }) => (
              <section key={family.id} className="plates__era" aria-label={family.label}>
                <div className="plates__era-head">
                  <h4>{family.label}</h4>
                  <span className="plates__count">{formats.length}</span>
                </div>
                <div className="plates__grid">
                  {formats.map((format) => (
                    <PlateCard
                      key={format.id}
                      format={format}
                      meta={periodText(format.period)}
                      href={searchFor({ view: 'plates', family: place.family, year: place.year, plate: format.id })}
                      onOpen={() => { setPlaying(false); go({ ...place, plate: format.id }) }}
                      cardRef={(element) => { cards.current[format.id] = element }}
                    />
                  ))}
                </div>
              </section>
            ))}
          </section>
        </>
      )}

      {mode === 'family' && shown === 0 && <p className="plates__empty" role="status">No plates match “{query}”.</p>}

      {mode === 'family' && families.map(({ family, sections }) => (
        <section key={family.id} className="plates__family" aria-labelledby={`plates-${family.id}`}>
          <header className="plates__family-head">
            <h3 id={`plates-${family.id}`}>
              <a
                href={searchFor({ view: 'plates', family: family.id })}
                onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ ...place, family: family.id, plate: null }) } }}
              >
                {family.label}
              </a>
            </h3>
            <span className="plates__count">{family.formats.length}</span>
            {family.summary && <p>{family.summary}</p>}
          </header>
          {sections.map((section) => (
            <section key={section.id} className="plates__era" aria-label={section.label}>
              <div className="plates__era-head">
                {section.period && <span className="plates__period">{section.period}</span>}
                <h4>{section.label}</h4>
                {section.summary && <p>{section.summary}</p>}
              </div>
              {section.gap ? (
                <p className="plates__gap">
                  Documented, but not reconstructed yet.{' '}
                  {section.gap.sources.map((source, index) => (
                    <span key={source.url}>{index > 0 && ' · '}<a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></span>
                  ))}
                </p>
              ) : (
                <div className="plates__grid">
                  {section.cards.map(({ format, meta }) => (
                    <PlateCard
                      key={format.id}
                      format={format}
                      meta={meta}
                      href={searchFor({ view: 'plates', family: place.family, plate: format.id })}
                      onOpen={() => go({ ...place, plate: format.id })}
                      cardRef={(element) => { cards.current[format.id] = element }}
                    />
                  ))}
                </div>
              )}
            </section>
          ))}
        </section>
      ))}
    </section>
  )
}
