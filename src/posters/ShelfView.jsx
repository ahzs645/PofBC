// A shelf of printed pieces, by series: an index of cards, and the interactive viewer over it when
// one is open. Posters and signs are both shelves; each passes its own catalogue.
//
// The place is kept in the address bar (`?view=posters&poster=dont-drop-it&part=credit`, or
// `?view=signs&sign=lookout`), so a link to a part of a piece opens it there, from anywhere on the
// site.

import { useCallback, useEffect, useRef, useState } from 'react'
import { writeHistory } from '../site/browserHistory.js'
import { useCatalogueIndex } from '../site/useCatalogueIndex.js'
import { Modal } from './ui/Modal.jsx'
import { NavigationContext, SiteLink, useNavigate } from '../site/navigation.jsx'
import { PosterViewer } from './PosterViewer.jsx'
import './posters.css'
import './shelfTools.css'
import { Select } from '../site/ui/Select.jsx'
import { holdScroll } from '../site/holdScroll.js'

/**
 * @param {object} props
 * @param {string} props.view        The site view this shelf is (`posters`, `signs`).
 * @param {string} props.param       The address parameter naming the open piece (`poster`, `sign`).
 * @param {string} props.title       The shelf's heading, and the viewer's way back to it.
 * @param {string} [props.intro]     A heading and one line over the shelf; left out, the shelf starts with its series.
 * @param {string} props.noun        What one piece is called (`poster`, `sign`).
 * @param {Array}  props.series      [{ id, title, kind, unlisted? }], in the order shown. An unlisted
 *                                   series is left off the shelf, out of the shelf's stepping order and
 *                                   the filters, but its pieces still open from their address and step
 *                                   among themselves. A piece whose card says `unlisted` is left off
 *                                   the same way, alone.
 * @param {Function} props.itemsOf   A series' piece ids, in order.
 * @param {object} props.items       Each piece's catalogue card, by id.
 * @param {object} props.loaders     Each piece's loader: resolves to its drawing and parts.
 * @param {object} props.thumbnails  Each piece's card image URL.
 * @param {Array}  [props.facets]    [{ key, label }]: card fields the shelf can be filtered by.
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
  const { cards, openCard, closeCard } = useCatalogueIndex(view)
  const shelfRef = useRef(null)
  // How the shelf is laid out, and what it is narrowed to: by series, or every piece in one grid.
  const savedShelf = globalThis.history?.state?.catalogueIndex
  const [layout, setLayout] = useState(() => savedShelf?.view === view ? savedShelf.layout ?? 'series' : 'series')
  const [filters, setFilters] = useState(() => savedShelf?.view === view ? savedShelf.filters ?? {} : {})
  const parentNavigate = useNavigate()
  // The shelf's own series and pieces; an unlisted one is reached only by its address.
  const shelved = (entry) => itemsOf(entry).filter((id) => !items[id].unlisted)
  const listed = series.filter((entry) => !entry.unlisted && shelved(entry).length)
  const order = listed.flatMap(shelved)
  const seriesOf = (id) => series.find((entry) => itemsOf(entry).includes(id)) ?? null
  // The pieces stepped through from one: the shelf's, or an unlisted series' own, among themselves.
  const runOf = (id) => {
    const own = seriesOf(id)
    return own?.unlisted && !items[id]?.unlisted ? shelved(own) : order
  }

  const go = useCallback(({ id, part }, entering = false) => {
    setPlace({ id, part })
    const url = new URL(globalThis.location.href)
    url.searchParams.set('view', view)
    if (id) url.searchParams.set(param, id)
    else url.searchParams.delete(param)
    if (id && part && part !== 'overview') url.searchParams.set('part', part)
    else url.searchParams.delete('part')
    if (!id) { url.searchParams.delete('story'); url.searchParams.delete('3d') }
    if (entering) openCard(url, id, { layout, filters })
    else writeHistory(url, { replace: true })
  }, [openCard, view, param, layout, filters])

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
        const run = runOf(place.id)
        const at = run.indexOf(place.id)
        // A heavy drawing (`prefetch: false` in its card) is left until it is asked for.
        for (const id of at < 0 ? [] : [run[at - 1], run[at + 1]]) if (id && items[id].prefetch !== false) loaders[id]().catch(() => {})
      })
      .catch((error) => { console.error(error); if (!gone) setFailed(true) })
    return () => { gone = true }
  }, [place.id, attempt, loaders]) // eslint-disable-line react-hooks/exhaustive-deps

  // Links to this shelf land here without leaving it; links elsewhere go to the App.
  const navigate = useCallback((params) => {
    if (params.view === view) {
      const id = items[params[param]] ? params[param] : null
      go({ id, part: params.part || 'overview' }, Boolean(id && !place.id))
      if (!params[param]) globalThis.scrollTo?.({ top: 0 })
    } else parentNavigate?.(params)
  }, [go, parentNavigate, view, param, items, place.id])

  const exit = useCallback(() => {
    closeCard(place.id, () => go({ id: null, part: 'overview' }))
  }, [closeCard, go, place.id])

  const meta = place.id ? items[place.id] : null
  // What's on screen: the piece asked for once it has loaded, until then the one before it.
  const shown = meta && module ? items[module.id] : null
  const switching = Boolean(shown && shown.id !== meta.id)
  const run = shown ? runOf(shown.id) : order
  const index = shown ? run.indexOf(shown.id) : -1
  const step = (id) => id && { title: items[id].title, open: () => go({ id, part: 'overview' }) }
  // A piece unlisted alone stands alone: no stepping to the shelf's pieces either side of it.
  const shelf = index < 0 ? null : { list: run.map((id) => ({ id, title: items[id].title })), index, open: (id) => go({ id, part: 'overview' }) }

  // While a piece is open over the shelf, the shelf cannot be tabbed into or read from behind it.
  useEffect(() => {
    const shelfEl = shelfRef.current
    if (!shelfEl) return
    if (place.id) shelfEl.setAttribute('inert', '')
    else shelfEl.removeAttribute('inert')
  }, [place.id])

  // The layout and the filters redraw the shelf below them, often much shorter; the toolbar stays
  // where it is on screen (holdScroll.js), as each filter's own select does.
  const tools = useRef(null)
  const arrange = (next) => {
    if (next !== layout) holdScroll(tools.current)
    setLayout(next)
  }
  const clear = () => {
    holdScroll(tools.current)
    setFilters({})
  }
  const narrowed = Object.values(filters).some(Boolean)
  const matches = (id) => Object.entries(filters).every(([key, value]) => !value || items[id][key] === value)
  const found = order.filter(matches)
  const valuesOf = (key) => [...new Set(order.map((id) => items[id][key]).filter(Boolean))]
  const card = (id) => (
    <SiteLink key={id} to={{ view, [param]: id }} className="posters__card" ref={(element) => { cards.current[id] = element }}>
      <span className="posters__thumb">
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
        {/* Every shelf opens with the same toolbar as the other catalogues (shelfTools.css): the
            layout, any filters, and the count. */}
        <div className="shelf-tools" role="group" aria-label={`Browse the ${title.toLowerCase()}`} ref={tools}>
          <div className="shelf-tools__toggle" role="group" aria-label="Layout">
            <button type="button" aria-pressed={layout === 'series'} onClick={() => arrange('series')}>By series</button>
            <button type="button" aria-pressed={layout === 'all'} onClick={() => arrange('all')}>All pieces</button>
          </div>
          {(facets ?? []).map(({ key, label }) => (
            <label key={key} className="shelf-tools__filter">
              <span>{label}</span>
              <Select keepPlace value={filters[key] ?? ''} onChange={(value) => setFilters((before) => ({ ...before, [key]: value || null }))}>
                <option value="">All</option>
                {valuesOf(key).map((value) => <option key={value} value={value}>{value}</option>)}
              </Select>
            </label>
          ))}
          <p className="shelf-tools__count" role="status">
            {narrowed ? `${found.length} of ${order.length}` : order.length} {found.length === 1 ? noun : `${noun}s`}
            {narrowed && <> · <button type="button" className="shelf-tools__clear" onClick={clear}>Clear filters</button></>}
          </p>
        </div>
        {layout === 'all' || narrowed
          ? (
            <section className="posters__series" aria-label={narrowed ? `Matching ${noun}s` : `All ${noun}s`}>
              {found.length
                ? <div className="posters__grid posters__grid--all">{found.map(card)}</div>
                : <p className="posters__none">No {noun} matches all of those. <button type="button" className="shelf-tools__clear" onClick={clear}>Clear filters</button></p>}
            </section>
          )
          : (
            // Each series is as wide as its pieces need (--n of them), so short series share a row
            // and a shelf of one-piece series is not a column of mostly empty panels.
            <div className="posters__shelf">
              {listed.map((entry) => (
                <section key={entry.id} className="posters__series" style={{ '--n': shelved(entry).length }} aria-labelledby={`series-${entry.id}`}>
                  <header className="posters__series-head">
                    <h3 id={`series-${entry.id}`}>{entry.title}</h3>
                    <p className="posters__kind">{entry.kind}</p>
                  </header>
                  <div className="posters__grid">{shelved(entry).map(card)}</div>
                </section>
              ))}
            </div>
          )}
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
            previous={index < 0 ? null : step(run[index - 1])}
            next={index < 0 ? null : step(run[index + 1])}
            shelf={shelf}
          />
        </div>
      )}
      {meta && (!module || (failed && switching)) && (
        <Modal className="pv pv-loading" aria-label={meta.title} onDismiss={exit}>
          {failed
            ? <p>Could not load {meta.title}. <button type="button" className="pv-ghost" onClick={() => setAttempt((n) => n + 1)}>Retry</button> <button type="button" className="pv-ghost" onClick={exit}>Back to the {title.toLowerCase()}</button></p>
            : <p role="status">Loading {meta.title}…</p>}
        </Modal>
      )}
    </NavigationContext.Provider>
  )
}
