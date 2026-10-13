// The posters, by series: an index of cards, and the interactive viewer over it when one is open.
//
// The place is kept in the address bar — `?view=posters&poster=dont-drop-it&part=credit` — so a
// link to a part of a poster opens it there, from anywhere on the site.

import { useCallback, useEffect, useRef, useState } from 'react'
import { NavigationContext, SiteLink, useNavigate } from '../site/navigation.jsx'
import { POSTERS, SERIES, neighbours, seriesOf } from './catalogue.js'
import { PosterViewer } from './PosterViewer.jsx'
import coastalThumb from './coastal-forest/thumbnail.jpg'
import dropThumb from './forest-service/dont-drop-it.svg?url'
import gambleThumb from './forest-service/dont-gamble-with-fire.svg?url'
import rewardThumb from './forest-service/reward-living-forest.svg?url'
import enjoyThumb from './forest-service/enjoy-protect-forests.svg?url'
import './posters.css'

// Each poster's drawing and parts, fetched when it is opened.
const forestService = (id) => () => import('./forest-service/index.js').then((module) => module.loaderFor(id)())
const LOADERS = {
  'coastal-forest': () => import('./coastal-forest/index.jsx').then((module) => module.load()),
  'dont-drop-it': forestService('dont-drop-it'),
  'dont-gamble-with-fire': forestService('dont-gamble-with-fire'),
  'reward-living-forest': forestService('reward-living-forest'),
  'enjoy-protect-forests': forestService('enjoy-protect-forests')
}

const THUMBNAILS = {
  'coastal-forest': coastalThumb,
  'dont-drop-it': dropThumb,
  'dont-gamble-with-fire': gambleThumb,
  'reward-living-forest': rewardThumb,
  'enjoy-protect-forests': enjoyThumb
}

const readPlace = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const poster = POSTERS[params.get('poster')] ? params.get('poster') : null
  return { poster, part: poster ? params.get('part') || 'overview' : 'overview' }
}

const writePlace = ({ poster, part }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'posters')
  if (poster) url.searchParams.set('poster', poster)
  else url.searchParams.delete('poster')
  if (poster && part && part !== 'overview') url.searchParams.set('part', part)
  else url.searchParams.delete('part')
  globalThis.history.replaceState(null, '', url)
}

const PosterCard = ({ id, cardRef }) => {
  const meta = POSTERS[id]
  return (
    <SiteLink to={{ view: 'posters', poster: id }} className="posters__card" ref={cardRef}>
      <span className="posters__thumb" style={{ background: meta.background ?? undefined }}>
        <img src={THUMBNAILS[id]} alt="" loading="lazy" />
      </span>
      <span className="posters__card-text">
        <span className="posters__title">{meta.title}</span>
        <span className="posters__issuer">{meta.issuer}</span>
        <span className="posters__summary">{meta.summary}</span>
        <span className="posters__dated">{meta.dated}</span>
        <span className="posters__open">Explore its parts <span aria-hidden="true">→</span></span>
      </span>
    </SiteLink>
  )
}

export const PostersView = () => {
  const [place, setPlace] = useState(readPlace)
  const [module, setModule] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const cards = useRef({})
  const parentNavigate = useNavigate()

  const go = useCallback((next) => {
    setPlace(next)
    writePlace(next)
  }, [])

  // Load the open poster's drawing; keep it while only the part changes.
  useEffect(() => {
    if (!place.poster) { setModule(null); return undefined }
    let gone = false
    setModule(null)
    setFailed(false)
    LOADERS[place.poster]()
      .then((loaded) => { if (!gone) setModule({ id: place.poster, ...loaded }) })
      .catch((error) => { console.error(error); if (!gone) setFailed(true) })
    return () => { gone = true }
  }, [place.poster, attempt])

  // Links inside the posters land here without leaving the view; links elsewhere go to the App.
  const navigate = useCallback((params) => {
    if (params.view === 'posters') {
      go({ poster: POSTERS[params.poster] ? params.poster : null, part: params.part || 'overview' })
      if (!params.poster) globalThis.scrollTo?.({ top: 0 })
    } else parentNavigate?.(params)
  }, [go, parentNavigate])

  const exit = useCallback(() => {
    const id = place.poster
    go({ poster: null, part: 'overview' })
    requestAnimationFrame(() => cards.current[id]?.focus())
  }, [go, place.poster])

  const meta = place.poster ? POSTERS[place.poster] : null
  const around = meta ? neighbours(meta.id) : {}
  const step = (id) => id && { title: POSTERS[id].title, open: () => go({ poster: id, part: 'overview' }) }

  return (
    <NavigationContext.Provider value={navigate}>
      <section className="posters" aria-label="Posters">
        <div className="posters__intro">
          <h2>Posters</h2>
          <p>Printed pieces from the Province and its services, rebuilt as drawings and grouped by series. Open one and move across it: every part — a headline, a logo, a credit line — opens with its history, and links on to the marks and the bodies behind it.</p>
        </div>
        {SERIES.map((series) => (
          <section key={series.id} className="posters__series" aria-labelledby={`series-${series.id}`}>
            <header className="posters__series-head">
              <p className="posters__kind">{series.kind} · {series.posters.length}</p>
              <h3 id={`series-${series.id}`}>{series.title}</h3>
              <p>{series.description}</p>
            </header>
            <div className="posters__grid">
              {series.posters.map((id) => <PosterCard key={id} id={id} cardRef={(element) => { cards.current[id] = element }} />)}
            </div>
          </section>
        ))}
        <p className="posters__footnote">Each drawing is a reconstruction from a photograph of a printed copy, not an original production master. Where a date, a typeface or a colour is not established, the panels say so.</p>
      </section>

      {meta && module?.id === meta.id && (
        <PosterViewer
          key={meta.id}
          meta={meta}
          series={seriesOf(meta.id)}
          module={module}
          part={place.part}
          onPart={(part) => go({ poster: meta.id, part })}
          onExit={exit}
          previous={step(around.previous)}
          next={step(around.next)}
        />
      )}
      {meta && module?.id !== meta.id && (
        <div className="pv pv-loading" role="status">
          {failed
            ? <p>Could not load {meta.title}. <button type="button" className="pv-ghost" onClick={() => setAttempt((n) => n + 1)}>Retry</button> <button type="button" className="pv-ghost" onClick={exit}>Back to the posters</button></p>
            : <p>Loading {meta.title}…</p>}
        </div>
      )}
    </NavigationContext.Provider>
  )
}
