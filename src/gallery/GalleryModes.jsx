// The gallery's first page, three more ways: every logo at once, today's organizations with their
// newest logo, and a timeline to scrub through the years. Each honours the search's organization
// type, and each says what its dates rest on (galleryModes.js).

import { memo, useDeferredValue, useEffect, useId, useMemo, useRef, useState } from 'react'
import { CollectionCard, Tile } from './GalleryView.jsx'
import { tileArt, onPage } from './tileArt.js'
import {
  GALLERY_MODES, PRESENT_YEAR, allLogosOf, documentedCounts, firstMarkYear, currentMarkOf, logosInYear, organizationStatus
} from './galleryModes.js'

/** The collections a mode shows: the type's sections, each collection once. */
export const modeCollections = (sections) => {
  const seen = new Set()
  return sections.flatMap(({ collections }) => collections).filter(({ id }) => !seen.has(id) && seen.add(id))
}

/** Renders a long list a page at a time, adding the next as its end scrolls into view. */
const useIncremental = (items, step = 96) => {
  const [count, setCount] = useState(step)
  const sentinel = useRef(null)
  useEffect(() => setCount(step), [items, step])
  useEffect(() => {
    const end = sentinel.current
    if (!end || count >= items.length || !globalThis.IntersectionObserver) return undefined
    const watch = new IntersectionObserver(([seen]) => {
      if (seen.isIntersecting) setCount((value) => value + step)
    }, { rootMargin: '800px 0px' })
    watch.observe(end)
    return () => watch.disconnect()
  }, [count, items.length, step])
  const more = count < items.length && (
    <div ref={sentinel} className="gallery__more">
      <button type="button" className="button" onClick={() => setCount((value) => value + step)}>
        Show more <span className="gallery__more-count">({items.length - count} left)</span>
      </button>
    </div>
  )
  return [items.slice(0, count), more]
}

export const GalleryModeSwitch = ({ value, onChange }) => (
  <div className="gallery__modes" role="group" aria-label="Show">
    {GALLERY_MODES.map((mode) => (
      <button key={mode.value} type="button" className="gallery__mode" aria-pressed={value === mode.value}
        title={mode.title} onClick={() => onChange(mode.value)}>
        {mode.label}
      </button>
    ))}
  </div>
)

// ── All logos ─────────────────────────────────────────────────────────────────────────────────────

const SORTS = [
  { value: 'organization', label: 'By organization' },
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' }
]
const byDate = (direction) => (a, b) => (a.from === null) - (b.from === null) || direction * ((a.from ?? 0) - (b.from ?? 0))

export const AllLogos = ({ sections, theme, onOpenMark }) => {
  const [sort, setSort] = useState('organization')
  const logos = useMemo(() => {
    const all = allLogosOf(modeCollections(sections))
    return sort === 'organization' ? all : [...all].sort(byDate(sort === 'newest' ? -1 : 1))
  }, [sections, sort])
  const [shown, more] = useIncremental(logos)
  const undated = logos.filter(({ from }) => from === null).length
  return (
    <section className="gallery__shelf" aria-labelledby="all-logos-heading">
      <div className="gallery__mode-head">
        <h2 id="all-logos-heading" className="gallery__category-title">{logos.length} logos</h2>
        <label className="gallery__sort">
          <span>Order</span>
          <select value={sort} onChange={(event) => setSort(event.target.value)}>
            {SORTS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
      </div>
      {sort !== 'organization' && undated > 0 && (
        <p className="gallery__intro gallery__shelf-intro">{undated} logos have no established date, so they come last.</p>
      )}
      <div className="gallery__tiles gallery__tiles--all">
        {shown.map(({ entry, collection }) => (
          <Tile key={`${collection.id}/${entry.id}`} entry={entry} theme={theme} owner={collection.label}
            onOpen={() => onOpenMark(collection.id, entry)} />
        ))}
      </div>
      {more}
    </section>
  )
}

// ── Current organizations ────────────────────────────────────────────────────────────────────────

export const CurrentOrganizations = ({ sections, theme, onChooseCollection }) => {
  const groups = useMemo(() => sections.map((section) => {
    const rows = section.collections.map((collection) => ({ collection, ...organizationStatus(collection) }))
    return {
      ...section,
      current: rows.filter(({ status }) => status === 'current'),
      unconfirmed: rows.filter(({ status }) => status === 'unconfirmed')
    }
  }), [sections])
  const seen = new Set()
  const unique = (rows) => rows.filter(({ collection }) => !seen.has(collection.id) && seen.add(collection.id))
  const shelves = groups.map((group) => ({ ...group, current: unique(group.current) }))
  const unconfirmed = groups.flatMap((group) => group.unconfirmed).filter(({ collection }) => !seen.has(collection.id) && seen.add(collection.id))
  const total = shelves.reduce((sum, { current }) => sum + current.length, 0)
  const card = ({ collection, reason }) => (
    <CollectionCard key={collection.id} collection={collection} theme={theme} coverEntry={currentMarkOf(collection)}
      onOpen={() => onChooseCollection(collection.id)}>
      <span className="gallery__status" title={reason}>{reason}</span>
    </CollectionCard>
  )
  return (
    <>
      <p className="gallery__intro gallery__mode-intro">
        <strong>{total}</strong> organizations stand today, each shown with its logo in use today where one is dated
        to the present, and otherwise with its collection’s cover. An organization
        counts as current only when its dates run to the present, the identity register or the government atlas
        lists it as current, or it is a local government or school district.
      </p>
      {shelves.filter(({ current }) => current.length).map((section) => (
        <section key={section.value} className="gallery__shelf gallery__category" aria-labelledby={`current-${section.value}`}>
          <div className="gallery__category-head">
            <h2 id={`current-${section.value}`} className="gallery__category-title">{section.label}</h2>
            <span className="gallery__count">{section.current.length}</span>
          </div>
          <div className="gallery__collections">{section.current.map(card)}</div>
        </section>
      ))}
      {unconfirmed.length > 0 && (
        <details className="gallery__shelf gallery__unconfirmed">
          <summary>
            <span className="gallery__category-title">Status not confirmed</span>
            <span className="gallery__note">{unconfirmed.length} organizations with no source here for whether they stand today</span>
          </summary>
          <div className="gallery__collections">{unconfirmed.map(card)}</div>
        </details>
      )}
    </>
  )
}

// ── Timeline ─────────────────────────────────────────────────────────────────────────────────────

const STRIP_HEIGHT = 36

/** A bar for each year: how many organizations have a logo dated to it. Clicking a bar picks it. */
const YearStrip = ({ counts, first, year, onYear }) => {
  const max = Math.max(1, ...counts)
  const width = counts.length
  return (
    <svg className="gallery__strip" viewBox={`0 0 ${width} ${STRIP_HEIGHT}`} preserveAspectRatio="none" aria-hidden="true"
      onClick={(event) => {
        const box = event.currentTarget.getBoundingClientRect()
        onYear(first + Math.min(width - 1, Math.max(0, Math.floor(((event.clientX - box.left) / box.width) * width))))
      }}>
      {counts.map((count, index) => {
        const height = count ? Math.max(2, (count / max) * STRIP_HEIGHT) : 0
        return <rect key={index} x={index + 0.12} width={0.76} y={STRIP_HEIGHT - height} height={height}
          data-active={first + index === year || undefined} />
      })}
    </svg>
  )
}

export const TimelineScrubber = ({ sections, year, onYear }) => {
  const collections = useMemo(() => modeCollections(sections), [sections])
  const first = useMemo(() => Math.min(firstMarkYear(collections), PRESENT_YEAR - 1), [collections])
  const counts = useMemo(() => documentedCounts(collections, first, PRESENT_YEAR), [collections, first])
  const [playing, setPlaying] = useState(false)
  const sliderId = useId()
  const shown = Math.min(PRESENT_YEAR, Math.max(first, year ?? PRESENT_YEAR))
  useEffect(() => {
    if (!playing) return undefined
    if (shown >= PRESENT_YEAR) { setPlaying(false); return undefined }
    const next = setTimeout(() => onYear(shown + 1), 650)
    return () => clearTimeout(next)
  }, [playing, shown, onYear])
  const step = (by) => { setPlaying(false); onYear(Math.min(PRESENT_YEAR, Math.max(first, shown + by))) }
  return (
    <div className="gallery__scrubber">
      <div className="gallery__scrubber-controls">
        <button type="button" className="gallery__scrub-button" aria-label="Previous year" onClick={() => step(-1)} disabled={shown <= first}>
          <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="m10 4-4 4 4 4" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg>
        </button>
        <button type="button" className="gallery__scrub-button gallery__scrub-play" aria-pressed={playing}
          aria-label={playing ? 'Pause' : 'Play through the years'}
          onClick={() => {
            if (!playing && shown >= PRESENT_YEAR) onYear(first)
            setPlaying(!playing)
          }}>
          {playing
            ? <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" /></svg>
            : <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8Z" fill="currentColor" /></svg>}
        </button>
        <button type="button" className="gallery__scrub-button" aria-label="Next year" onClick={() => step(1)} disabled={shown >= PRESENT_YEAR}>
          <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="m6 4 4 4-4 4" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" /></svg>
        </button>
        <label className="gallery__scrub-year" htmlFor={sliderId}><span className="visually-hidden">Year</span>{shown}</label>
      </div>
      <div className="gallery__scrub-track">
        <YearStrip counts={counts} first={first} year={shown} onYear={(value) => { setPlaying(false); onYear(value) }} />
        <input id={sliderId} type="range" min={first} max={PRESENT_YEAR} step={1} value={shown}
          aria-valuetext={`${shown}: ${counts[shown - first]} organizations with a logo dated to it`}
          onChange={(event) => { setPlaying(false); onYear(Number(event.target.value)) }} />
        <div className="gallery__scrub-ends" aria-hidden="true"><span>{first}</span><span>{PRESENT_YEAR}</span></div>
      </div>
    </div>
  )
}

const TimelineCard = memo(({ row, year, theme, onOpenMark }) => {
  const { collection, marks, documented } = row
  const [mark] = marks
  const span = mark.from === mark.to ? `${mark.from}` : mark.open ? `${mark.from}–present` : `${mark.from}–${mark.to}`
  return (
    <button type="button" className="gallery__pick gallery__pick--tile gallery__year-card" data-carried={!documented || undefined}
      onClick={() => onOpenMark(collection.id, mark.entry)} aria-label={`Open ${mark.entry.label}, ${collection.label}`}>
      <span className="gallery__art" data-ground={onPage(mark.entry, theme) ? 'page' : 'own'}
        // Built by this project's own renderers; every value is escaped where written.
        dangerouslySetInnerHTML={{ __html: tileArt(mark.entry, theme) }} />
      <span className="gallery__owner">{collection.label}</span>
      <span className="gallery__label">{mark.entry.label}</span>
      <span className="gallery__note">
        {documented ? `Dated ${span}` : `Last dated ${span}; ${collection.label} still stood in ${year}`}
        {marks.length > 1 && ` · +${marks.length - 1} more dated to ${year}`}
      </span>
    </button>
  )
})
TimelineCard.displayName = 'TimelineCard'

export const GalleryTimeline = ({ sections, year, theme, onOpenMark }) => {
  const collections = useMemo(() => modeCollections(sections), [sections])
  const [documentedOnly, setDocumentedOnly] = useState(false)
  // Dragging the slider redraws the cards a beat behind it, so the handle never waits on them.
  const shown = useDeferredValue(year ?? PRESENT_YEAR)
  const rows = useMemo(() => logosInYear(collections, shown, { documentedOnly })
    .sort((a, b) => (b.documented - a.documented) || (b.marks[0].from - a.marks[0].from) || a.collection.label.localeCompare(b.collection.label)),
  [collections, shown, documentedOnly])
  const [cards, more] = useIncremental(rows, 60)
  const documented = rows.filter((row) => row.documented).length
  const undated = useMemo(() => allLogosOf(collections).filter(({ from }) => from === null).length, [collections])
  return (
    <section className="gallery__shelf" aria-labelledby="timeline-heading" aria-busy={shown !== (year ?? PRESENT_YEAR) || undefined}>
      <div className="gallery__mode-head">
        <h2 id="timeline-heading" className="gallery__category-title" aria-live="polite">
          {shown}: {rows.length} {rows.length === 1 ? 'organization' : 'organizations'}
        </h2>
        <label className="gallery__check">
          <input type="checkbox" checked={documentedOnly} onChange={(event) => setDocumentedOnly(event.target.checked)} />
          Only logos dated to this year
        </label>
      </div>
      <p className="gallery__intro gallery__shelf-intro">
        {documented} with a logo dated to {shown}
        {!documentedOnly && rows.length > documented && `, ${rows.length - documented} with their last dated logo, carried forward while the organization is known to stand`}.
        {' '}{undated} logos have no established date and are not placed.
      </p>
      {rows.length === 0
        ? <p className="gallery__intro" role="status">No logo in this selection is dated to {shown}.</p>
        : (
          <div className="gallery__tiles gallery__tiles--all">
            {cards.map((row) => <TimelineCard key={row.collection.id} row={row} year={shown} theme={theme} onOpenMark={onOpenMark} />)}
          </div>
          )}
      {more}
    </section>
  )
}
