// Licence plates: British Columbia's plates from PlateForge (vendor/plateforge, see README), family by
// family and era by era, each opening on a viewer that redraws it with any serial. The plates, their
// dates and their sources are PlateForge's; this view is the site's chrome around its embed API
// (vendor/plateforge/docs/embed.md), which lays them out with the same grouping PlateForge's own
// gallery uses.
//
// The place is kept in the address bar (`?view=plates&family=commercial`, `?view=plates&plate=1953`),
// so a link to a family or to one plate opens it there.

import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { BRITISH_COLUMBIA } from 'plateforge/bc'
import { PlateView, plateforgeLink, regionFamilies, regionSections, samplePlate, setupPlates, statusBadge } from 'plateforge'
import { searchFor } from '../site/navigation.jsx'
import { PlateViewer } from './PlateViewer.jsx'
import './plates.css'

const REGION = BRITISH_COLUMBIA
const FAMILIES = regionFamilies(REGION)
const TOTAL = FAMILIES.reduce((n, family) => n + family.formats.length, 0)

/** Every design of a family in its timeline's order, with the era it sits in, for stepping. */
const orderOf = (familyId) => regionSections(REGION, { family: familyId })
  .flatMap((section) => section.cards.map((card) => ({ format: card.format, section })))

const read = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const family = FAMILIES.some((f) => f.id === params.get('family')) ? params.get('family') : null
  const plate = REGION.formats.some((f) => f.id === params.get('plate')) ? params.get('plate') : null
  return { family, plate }
}

const write = ({ family, plate }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'plates')
  for (const [key, value] of Object.entries({ family, plate })) {
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

export const PlatesView = () => {
  const [place, setPlace] = useState(read)
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const cards = useRef({})

  useEffect(() => { setupPlates() }, [])

  const go = useCallback((next) => {
    setPlace(next)
    write(next)
  }, [])

  const families = useMemo(() => FAMILIES
    .filter((family) => !place.family || family.id === place.family)
    .map((family) => ({ family, sections: regionSections(REGION, { family: family.id, query: deferredQuery }) }))
    .filter(({ sections }) => sections.some((section) => section.cards.length || section.gap)),
  [place.family, deferredQuery])
  const shown = families.reduce((n, { sections }) => n + sections.reduce((m, s) => m + s.cards.length, 0), 0)

  const open = place.plate ? REGION.formats.find((f) => f.id === place.plate) : null
  const openFamily = open ? FAMILIES.find((f) => f.formats.includes(open)) : null
  const order = useMemo(() => (openFamily ? orderOf(openFamily.id) : []), [openFamily])

  // Back from a plate lands on its card.
  const close = useCallback(() => {
    const id = place.plate
    go({ family: place.family, plate: null })
    requestAnimationFrame(() => cards.current[id]?.focus())
  }, [go, place.family, place.plate])

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
        onOpen={(format) => go({ family: place.family, plate: format.id })}
        onClose={close}
      />
    )
  }

  return (
    <section className="plates" aria-label="Licence plates">
      <div className="plates__intro">
        <h2>Licence plates <span className="plates__count">{TOTAL}</span></h2>
        <p>
          British Columbia’s plates from the leather plates of 1904 to the flag base of today, in {FAMILIES.length} families:
          passenger, commercial, farm, motorcycle, official, municipal and the rest. Each is a research reconstruction
          from <a href={plateforgeLink(REGION)} target="_blank" rel="noreferrer">PlateForge</a>, redrawn as SVG from
          photographs and source notes, and opens to take any serial.
        </p>
        <div className="plates__filters">
          <label className="plates__filter">
            <span>Family</span>
            <select value={place.family ?? ''} onChange={(event) => go({ family: event.target.value || null, plate: null })}>
              <option value="">All {FAMILIES.length} families</option>
              {FAMILIES.map((family) => <option key={family.id} value={family.id}>{family.label} ({family.formats.length})</option>)}
            </select>
          </label>
          <label className="plates__filter plates__filter--grow">
            <span>Search</span>
            <input type="search" value={query} placeholder="1953, flag, totem, Expo…" onChange={(event) => setQuery(event.target.value)} />
          </label>
        </div>
      </div>

      {shown === 0 && <p className="plates__empty" role="status">No plates match “{query}”.</p>}

      {families.map(({ family, sections }) => (
        <section key={family.id} className="plates__family" aria-labelledby={`plates-${family.id}`}>
          <header className="plates__family-head">
            <h3 id={`plates-${family.id}`}>
              <a
                href={searchFor({ view: 'plates', family: family.id })}
                onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ family: family.id, plate: null }) } }}
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
                    <a
                      key={format.id}
                      ref={(element) => { cards.current[format.id] = element }}
                      className="plates__card"
                      href={searchFor({ view: 'plates', family: place.family, plate: format.id })}
                      onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ family: place.family, plate: format.id }) } }}
                    >
                      <LazyPlate format={format} />
                      <span className="plates__card-text">
                        <span className="plates__title">{format.label}</span>
                        <span className="plates__meta">
                          {meta !== format.label && meta}
                          {statusBadge(format) && <span className="plates__status">{statusBadge(format)}</span>}
                        </span>
                      </span>
                    </a>
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
