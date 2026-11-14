// A shelf of printed pieces, by series: an index of cards, and the interactive viewer over it when
// one is open. Posters and signs are both shelves; each passes its own catalogue.
//
// The place is kept in the address bar (`?view=posters&poster=dont-drop-it&part=credit`, or
// `?view=signs&sign=lookout`), so a link to a part of a piece opens it there, from anywhere on the
// site.

import { useCallback, useEffect, useRef, useState } from 'react'
import { NavigationContext, SiteLink, useNavigate } from '../site/navigation.jsx'
import { PosterViewer } from './PosterViewer.jsx'
import './posters.css'

/**
 * @param {object} props
 * @param {string} props.view        The site view this shelf is (`posters`, `signs`).
 * @param {string} props.param       The address parameter naming the open piece (`poster`, `sign`).
 * @param {string} props.title       The shelf's heading, and the viewer's way back to it.
 * @param {string} [props.intro]     A heading and one line over the shelf; left out, the shelf starts with its series.
 * @param {string} props.noun        What one piece is called (`poster`, `sign`).
 * @param {Array}  props.series      [{ id, title, kind, unlisted? }], in the order shown. An unlisted
 *                                   series is left off the shelf, out of the stepping order and the
 *                                   filters, but its pieces still open from their address.
 * @param {Function} props.itemsOf   A series' piece ids, in order.
 * @param {object} props.items       Each piece's catalogue card, by id.
 * @param {object} props.loaders     Each piece's loader: resolves to its drawing and parts.
 * @param {object} props.thumbnails  Each piece's card image URL.
 * @param {Array}  [props.facets]    [{ key, label }]: card fields the shelf can be filtered by. Given
 *                                   them, the shelf also offers every piece in one grid.
 */
export const ShelfView = ({ view, param, title, intro, noun, series, itemsOf, items, loaders, thumbnails, facets }) => {
  const read = () => {
    const params = new URLSearchParams(globalThis.location?.search ?? '')
    const id = items[params.get(param)] ? params.get(param) : null
    return { id, part: id ? params.get('part') || 'overview' : 'overview' }
  }
  const [place, setPlace] = useState(read)
  const [module, setModule] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const cards = useRef({})
  const shelfRef = useRef(null)
  // How the shelf is laid out, and what it is narrowed to: by series, or every piece in one grid.
  const [layout, setLayout] = useState('series')
  const [filters, setFilters] = useState({})
  const parentNavigate = useNavigate()
  // The shelf's own series; an unlisted one is reached only by its address.
  const listed = series.filter((entry) => !entry.unlisted)
  const order = listed.flatMap(itemsOf)
  const seriesOf = (id) => series.find((entry) => itemsOf(entry).includes(id)) ?? null

  const go = useCallback(({ id, part }) => {
    setPlace({ id, part })
    if (!globalThis.history?.replaceState) return
    const url = new URL(globalThis.location.href)
    url.searchParams.set('view', view)
    if (id) url.searchParams.set(param, id)
    else url.searchParams.delete(param)
    if (id && part && part !== 'overview') url.searchParams.set('part', part)
    else url.searchParams.delete('part')
    if (!id) url.searchParams.delete('story')
    globalThis.history.replaceState(null, '', url)
  }, [view, param])

  // Load the open piece's drawing; keep it while only the part changes. Moving from one piece to
  // another keeps the last one on screen until the next is ready, so the switch doesn't flash a
  // loading screen; its neighbours are then fetched ahead, so stepping on is quick.
  useEffect(() => {
    if (!place.id) { setModule(null); return undefined }
    let gone = false
    setFailed(false)
    loaders[place.id]()
      .then((loaded) => {
        if (gone) return
        setModule({ id: place.id, ...loaded })
        const at = order.indexOf(place.id)
        // A heavy drawing (`prefetch: false` in its card) is left until it is asked for.
        for (const id of [order[at - 1], order[at + 1]]) if (id && items[id].prefetch !== false) loaders[id]().catch(() => {})
      })
      .catch((error) => { console.error(error); if (!gone) setFailed(true) })
    return () => { gone = true }
  }, [place.id, attempt, loaders]) // eslint-disable-line react-hooks/exhaustive-deps

  // Links to this shelf land here without leaving it; links elsewhere go to the App.
  const navigate = useCallback((params) => {
    if (params.view === view) {
      go({ id: items[params[param]] ? params[param] : null, part: params.part || 'overview' })
      if (!params[param]) globalThis.scrollTo?.({ top: 0 })
    } else parentNavigate?.(params)
  }, [go, parentNavigate, view, param, items])

  const exit = useCallback(() => {
    const id = place.id
    go({ id: null, part: 'overview' })
    requestAnimationFrame(() => cards.current[id]?.focus())
  }, [go, place.id])

  const meta = place.id ? items[place.id] : null
  // What's on screen: the piece asked for once it has loaded, until then the one before it.
  const shown = meta && module ? items[module.id] : null
  const switching = Boolean(shown && shown.id !== meta.id)
  const index = shown ? order.indexOf(shown.id) : -1
  const step = (id) => id && { title: items[id].title, open: () => go({ id, part: 'overview' }) }
  // An unlisted piece stands alone: no stepping to the shelf's pieces either side of it.
  const shelf = index < 0 ? null : { list: order.map((id) => ({ id, title: items[id].title })), index, open: (id) => go({ id, part: 'overview' }) }

  // While a piece is open over the shelf, the shelf cannot be tabbed into or read from behind it.
  useEffect(() => {
    const shelfEl = shelfRef.current
    if (!shelfEl) return
    if (place.id) shelfEl.setAttribute('inert', '')
    else shelfEl.removeAttribute('inert')
  }, [place.id])

  const narrowed = Object.values(filters).some(Boolean)
  const matches = (id) => Object.entries(filters).every(([key, value]) => !value || items[id][key] === value)
  const found = order.filter(matches)
  const valuesOf = (key) => [...new Set(order.map((id) => items[id][key]).filter(Boolean))]
  const card = (id) => (
    <SiteLink key={id} to={{ view, [param]: id }} className="posters__card" ref={(element) => { cards.current[id] = element }}>
      <span className="posters__thumb" style={{ background: items[id].background ?? undefined }}>
        <img src={thumbnails[id]} alt="" loading="lazy" />
      </span>
      <span className="posters__card-text">
        <span className="posters__title">{items[id].title}</span>
        {items[id].blurb && <span className="posters__blurb">{items[id].blurb}</span>}
        <span className="posters__dated">{[items[id].format, items[id].when].filter(Boolean).join(' · ')}</span>
      </span>
    </SiteLink>
  )

  return (
    <NavigationContext.Provider value={navigate}>
      <section className="posters" aria-label={title} ref={shelfRef}>
        {intro && (
          <div className="posters__intro">
            <h2>{title}</h2>
            <p>{intro}</p>
          </div>
        )}
        {facets && (
          <div className="posters__tools" role="group" aria-label={`Browse the ${title.toLowerCase()}`}>
            <div className="posters__layout" role="group" aria-label="Layout">
              <button type="button" aria-pressed={layout === 'series'} onClick={() => setLayout('series')}>By series</button>
              <button type="button" aria-pressed={layout === 'all'} onClick={() => setLayout('all')}>All pieces</button>
            </div>
            {facets.map(({ key, label }) => (
              <label key={key} className="posters__filter">
                <span>{label}</span>
                <select value={filters[key] ?? ''} onChange={(event) => setFilters((before) => ({ ...before, [key]: event.target.value || null }))}>
                  <option value="">All</option>
                  {valuesOf(key).map((value) => <option key={value} value={value}>{value}</option>)}
                </select>
              </label>
            ))}
            <p className="posters__count" role="status">
              {narrowed ? `${found.length} of ${order.length}` : order.length} {found.length === 1 && narrowed ? noun : `${noun}s`}
              {narrowed && <> · <button type="button" className="posters__clear" onClick={() => setFilters({})}>Clear filters</button></>}
            </p>
          </div>
        )}
        {layout === 'all' || narrowed
          ? (
            <section className="posters__series" aria-label={narrowed ? `Matching ${noun}s` : `All ${noun}s`}>
              {found.length
                ? <div className="posters__grid posters__grid--all">{found.map(card)}</div>
                : <p className="posters__none">No {noun} matches all of those. <button type="button" className="posters__clear" onClick={() => setFilters({})}>Clear filters</button></p>}
            </section>
          )
          : listed.map((entry) => (
            <section key={entry.id} className="posters__series" aria-labelledby={`series-${entry.id}`}>
              <header className="posters__series-head">
                <h3 id={`series-${entry.id}`}>{entry.title}</h3>
                <p className="posters__kind">{entry.kind}</p>
              </header>
              <div className="posters__grid">{itemsOf(entry).map(card)}</div>
            </section>
          ))}
      </section>

      {shown && (
        <div className={switching ? 'pv-switching' : undefined} aria-busy={switching}>
          <PosterViewer
            key={shown.id}
            meta={shown}
            series={seriesOf(shown.id)}
            module={module}
            part={switching ? 'overview' : place.part}
            onPart={(part) => go({ id: shown.id, part })}
            onExit={exit}
            backLabel={title}
            noun={noun}
            previous={index < 0 ? null : step(order[index - 1])}
            next={index < 0 ? null : step(order[index + 1])}
            shelf={shelf}
          />
        </div>
      )}
      {meta && (!module || (failed && switching)) && (
        <div className="pv pv-loading" role="status">
          {failed
            ? <p>Could not load {meta.title}. <button type="button" className="pv-ghost" onClick={() => setAttempt((n) => n + 1)}>Retry</button> <button type="button" className="pv-ghost" onClick={exit}>Back to the {title.toLowerCase()}</button></p>
            : <p>Loading {meta.title}…</p>}
        </div>
      )}
    </NavigationContext.Provider>
  )
}
