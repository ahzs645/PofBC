// One poster on the stage: hidden hotspots over the drawing, a panel for whichever part is open, a
// dock to step through them, a tour, export, and — for a poster whose parts tell one — a story.
//
// Generic over posters. A poster module supplies its drawing and parts; one that needs more than a
// data panel per part (the coastal poster's live logo studio, say) adds a `useExtras` hook, which
// can take over the frame, the stage's class, the panel and the export targets. One whose drawing
// is too large to wait for (Wildlife Trees) supplies a light stand-in as its drawing and an
// `upgrade` that resolves to the real one, which replaces it when it arrives. One with named
// recolourings (`variations`) gets a switch on its overview; the first is the drawing as it is. One
// with a picture of the original (`reference`) can be compared with it, the picture laid into the
// drawing's own frame; one made of pages (`pages`) can be read a page at a time.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Poster } from './stage/Poster.jsx'
import { useMedia } from './hooks/useMedia.js'
import { useKeyboardNav } from './hooks/useKeyboardNav.js'
import { useTour } from './hooks/useTour.js'
import { useColourSwap } from './stage/useColourSwap.js'
import { useReferenceOverlay } from './stage/useReferenceOverlay.js'
import { Panel } from './ui/Panel.jsx'
import { Dock } from './ui/Dock.jsx'
import { DataPanel } from './ui/DataPanel.jsx'
import { StoryRail } from './ui/StoryRail.jsx'
import { posterSvgString } from './export/exportSvg.js'
import { ExportDialog } from './export/ExportDialog.jsx'
import { posterTarget } from './export/targets.js'

const PANEL_INSET = 440 + 40
// Keep in step with --pv-dock-h and the narrow sheet's height in posters.css.
const DOCK_HEIGHT = 60
const SHEET_SHARE = 0.52
const TOUR_SECONDS = 12
const noExtras = () => ({})

// Story mode is kept in the address (`&story=1`), so a link can open a poster as its story.
const storyInAddress = () => new URLSearchParams(globalThis.location?.search ?? '').get('story') === '1'
const writeStory = (on) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  if (on) url.searchParams.set('story', '1')
  else url.searchParams.delete('story')
  globalThis.history.replaceState(null, '', url)
}

export function PosterViewer({ meta, series, module, part, onPart, onExit, previous, next, shelf, backLabel = 'Posters', noun = 'poster' }) {
  const { parts, order, regions, spotlight, svgRaw, prepare, upgrade, variations, reference, pages, figures } = module
  const useExtras = module.useExtras ?? noExtras
  const [svg, setSvg] = useState(null)
  // The drawing on the stage: the module's, or once it arrives the one its `upgrade` fetches.
  const [drawing, setDrawing] = useState({ raw: svgRaw, state: upgrade ? 'loading' : 'ready' })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    if (!upgrade) return undefined
    let gone = false
    setDrawing((d) => ({ ...d, state: 'loading' }))
    upgrade()
      .then((raw) => { if (!gone) setDrawing({ raw, state: 'ready' }) })
      .catch((error) => { console.error(error); if (!gone) setDrawing((d) => ({ ...d, state: 'failed' })) })
    return () => { gone = true }
  }, [upgrade, attempt])
  const exportable = drawing.state === 'ready'
  const [aboutOpen, setAboutOpen] = useState(false)
  const [exportOpen, setExportOpen] = useState(false)
  const [exportTarget, setExportTarget] = useState('poster')
  const narrow = useMedia('(max-width: 900px)')
  const coarse = useMedia('(hover: none)')
  const current = parts[part] ? part : 'overview'
  // The parts with a story, in order; a poster with fewer than two has no story mode.
  const chapters = useMemo(() => order.filter((id) => parts[id].story?.length), [order, parts])
  const canTell = chapters.length > 1
  const [telling, setTelling] = useState(() => canTell && storyInAddress())
  const tell = useCallback((on) => {
    setTelling(on)
    writeStory(on)
    setAboutOpen(false)
  }, [])

  // Opening the viewer moves focus into it, unless focus is already there (stepping from one piece
  // to the next keeps it on the button pressed). The shelf behind is inert meanwhile (ShelfView).
  const root = useRef(null)
  useEffect(() => {
    if (!root.current?.contains(document.activeElement)) root.current?.focus({ preventScroll: true })
  }, [])

  // The page under the viewer stays where it was and does not scroll behind it.
  useEffect(() => {
    const root = document.documentElement
    const before = { overflow: root.style.overflow, gutter: root.style.scrollbarGutter }
    root.style.overflow = 'hidden'
    root.style.scrollbarGutter = 'auto'
    return () => { root.style.overflow = before.overflow; root.style.scrollbarGutter = before.gutter }
  }, [])

  // A piece made of pages can be read one page at a time; opening any part leaves that.
  const [page, setPage] = useState(null)
  const turnTo = useCallback((n) => {
    if (n !== null && current !== 'overview') onPart('overview')
    setAboutOpen(false)
    setPage(n)
  }, [current, onPart])

  // Navigation: manual moves stop the tour; the tour's own moves do not.
  const tour = useTour({ order, current, onAdvance: (id) => move(id, false), seconds: TOUR_SECONDS })
  const move = useCallback((id, manual = true) => {
    onPart(id ?? 'overview')
    setAboutOpen(false)
    setPage(null)
    if (manual) tour.stop()
  }, [onPart, tour.stop]) // eslint-disable-line react-hooks/exhaustive-deps
  const select = useCallback((id) => move(id, true), [move])
  const openAbout = () => {
    if (telling) { tell(false); select('overview'); setAboutOpen(true); return }
    if (current !== 'overview') select('overview')
    setAboutOpen((o) => !o)
  }
  const openExport = useCallback((target) => { setExportTarget(target); setExportOpen(true) }, [])

  useKeyboardNav({
    // Escape steps out of the story before it steps out of the poster.
    order, current, onSelect: select, onExit: telling ? () => tell(false) : onExit, enabled: !exportOpen,
    keys: useMemo(() => ({
      e: () => { if (exportable) setExportOpen(true) },
      p: tour.toggle,
      s: () => { if (canTell) tell(!telling) },
      '[': () => previous?.open(),
      ']': () => next?.open()
    }), [tour.toggle, previous, next, canTell, telling, tell, exportable])
  })

  const extras = useExtras({ svg, part: current, select, openExport, tour })

  // A named recolouring, if the poster offers any; the first is the drawing untouched.
  const [variationId, setVariationId] = useState(null)
  const variation = variations?.options.find(({ id }) => id === variationId) ?? variations?.options[0] ?? null
  useColourSwap(svg, variation?.swap ?? null)
  const variationControl = variations && { ...variations, value: variation.id, onChange: setVariationId }

  // The original, laid into the drawing's frame for comparison.
  const [compareMode, setCompareMode] = useState('reconstruction')
  const [compareOpacity, setCompareOpacity] = useState(0.5)
  useReferenceOverlay(svg, reference ?? null, compareMode, compareOpacity)
  const compareControl = reference && { reference, mode: compareMode, onMode: setCompareMode, opacity: compareOpacity, onOpacity: setCompareOpacity }
  const pagesControl = pages && { count: pages.length, open: () => turnTo(0) }

  const paging = pages && page !== null && current === 'overview' && !telling
  const frame = extras.frame ?? (paging
    ? { box: pages[page].box, pad: 0.04, initial: parts.overview.box }
    : { box: parts[current].box, pad: parts[current].pad, initial: parts.overview.box })
  const panelOpen = telling || current !== 'overview' || aboutOpen
  const inset = { right: panelOpen && !narrow ? PANEL_INSET : 0, bottom: DOCK_HEIGHT + (panelOpen && narrow ? Math.round(innerHeight * SHEET_SHARE) : 0) }
  const steps = useMemo(() => order.filter((id) => id !== 'overview').map((id) => ({ id, label: parts[id].label })), [order, parts])
  const regionList = useMemo(() => regions.map((id) => ({ id, ...parts[id] })), [regions, parts])

  const targets = [
    posterTarget({ meta, noun, getSvg: () => posterSvgString(svg, meta), tag: extras.posterTag ?? (variation?.swap ? variation.id : null), ...(variation?.changed && !extras.posterTag ? { changed: variation.changed } : {}) }),
    ...(extras.targets ?? [])
  ]

  const content = telling
    ? (
      <StoryRail
        chapters={chapters}
        parts={parts}
        current={current}
        title={meta.title}
        onChapter={select}
        onDetails={(id) => { tell(false); select(id) }}
        onLeave={() => tell(false)}
      />
    )
    : extras.content ?? <DataPanel partId={current} parts={parts} order={order} onSelect={select} tour={tour} story={canTell ? () => tell(true) : null} poster={meta.id} variation={variationControl} compare={compareControl} pages={pagesControl} figures={figures} />

  return (
    <div className="pv" role="region" aria-label={`${meta.title}, interactive ${noun}`} tabIndex={-1} ref={root}>
      <div className="pv-app">
        <Poster
          svgRaw={drawing.raw}
          prepare={prepare}
          regions={regionList}
          current={current}
          frame={frame}
          inset={inset}
          overview={current === 'overview'}
          spotlight={spotlight}
          className={extras.className ?? ''}
          onSelect={select}
          onReady={setSvg}
        >
          {drawing.state !== 'ready' && (
            <p className={'pv-drawing-status' + (drawing.state === 'failed' ? ' pv-drawing-failed' : '')} role="status">
              {drawing.state === 'failed'
                ? <>The full drawing did not load; this is a preview. <button type="button" className="pv-ghost" onClick={(e) => { e.stopPropagation(); setAttempt((n) => n + 1) }}>Retry</button></>
                : <><span className="pv-drawing-spinner" aria-hidden="true" />Loading the full drawing; this is a preview</>}
            </p>
          )}
          {paging && (
            <nav className="pv-pager" aria-label="Pages" onClick={(e) => e.stopPropagation()}>
              <button type="button" className="pv-ghost" disabled={page === 0} onClick={() => turnTo(0)}>Home</button>
              <button type="button" className="pv-ghost" disabled={page === 0} onClick={() => turnTo(page - 1)} aria-label="Previous page">‹ Back</button>
              <span className="pv-pager-at" aria-live="polite"><b>{page + 1}</b> / {pages.length} · {pages[page].label}</span>
              <button type="button" className="pv-ghost pv-solid" disabled={page === pages.length - 1} onClick={() => turnTo(page + 1)} aria-label="Next page">Next ›</button>
              <button type="button" className="pv-ghost" onClick={() => turnTo(null)}>All pages</button>
            </nav>
          )}
          {compareMode !== 'reconstruction' && reference && (
            <p className="pv-compare-flag" role="status">{compareMode === 'original' ? 'Showing the original' : 'Original over the reconstruction'} · <button type="button" className="pv-ghost" onClick={(e) => { e.stopPropagation(); setCompareMode('reconstruction') }}>Back to the reconstruction</button></p>
          )}
          {tour.playing && (
            <div className="pv-tour-bar" aria-hidden="true">
              <div className="pv-tour-fill" key={current} style={{ animationDuration: `${tour.seconds}s` }} />
            </div>
          )}
        </Poster>

        <header className="pv-top">
          {/* The way back sits in the title itself: "← Posters │ REWARD: A Living Forest". */}
          <nav className="pv-top-start pv-crumb" aria-label={`${meta.title}, in ${backLabel.toLowerCase()}`}>
            <button type="button" className="pv-back" onClick={onExit} title={`All ${backLabel.toLowerCase()} (Esc from the whole ${noun})`} aria-label={`Back to all ${backLabel.toLowerCase()}`}>
              <span aria-hidden="true">←</span> <span className="pv-back-label">{backLabel}</span>
            </button>
            <button type="button" className="pv-brand" onClick={() => select('overview')} aria-label={`Back to the whole ${noun}`}>
              <b>{meta.title}</b>
              <span>{series.title}</span>
            </button>
          </nav>
          <div className="pv-top-actions">
            {shelf && shelf.list.length > 1 && (
              <div className="pv-switch" role="group" aria-label={`Other ${backLabel.toLowerCase()}`}>
                <button type="button" className="pv-switch-step" disabled={!previous} onClick={previous?.open} title={previous ? `Previous: ${previous.title} ([)` : undefined} aria-label={previous ? `Previous ${noun}: ${previous.title}` : `No previous ${noun}`}>‹</button>
                {/* The count reads as "3 / 5"; under it, a native list of every one to jump to. */}
                <label className="pv-switch-pick" title={`Go to another ${noun}`}>
                  <span aria-hidden="true"><span className="pv-switch-noun">{noun[0].toUpperCase() + noun.slice(1)} </span>{shelf.index + 1} / {shelf.list.length}</span>
                  <select aria-label={`Go to another ${noun}`} value={meta.id} onChange={(event) => shelf.open(event.target.value)}>
                    {shelf.list.map((entry, i) => <option key={entry.id} value={entry.id}>{i + 1}. {entry.title}</option>)}
                  </select>
                </label>
                <button type="button" className="pv-switch-step" disabled={!next} onClick={next?.open} title={next ? `Next: ${next.title} (])` : undefined} aria-label={next ? `Next ${noun}: ${next.title}` : `No next ${noun}`}>›</button>
              </div>
            )}
            {canTell && <button type="button" className="pv-ghost pv-story-btn" aria-pressed={telling} onClick={() => tell(!telling)} title="Read it as a story (S)">Story</button>}
            <button type="button" className="pv-ghost" aria-pressed={!telling && aboutOpen && current === 'overview'} onClick={openAbout}>About</button>
            <button type="button" className="pv-ghost pv-tour-btn" aria-pressed={tour.playing} onClick={tour.toggle} title="Play the tour (P)">{tour.playing ? 'Stop' : 'Tour'}</button>
            <button type="button" className="pv-ghost pv-solid" onClick={() => openExport('poster')} disabled={!exportable} title={exportable ? 'Export (E)' : 'Export is ready once the full drawing has loaded'}>Export</button>
          </div>
        </header>

        <Panel open={panelOpen} narrow={narrow} contentKey={telling ? 'story' : current} onClose={telling ? () => tell(false) : () => select('overview')} className={telling ? 'pv-panel-story' : ''}>
          {content}
        </Panel>

        <Dock steps={steps} current={current} onSelect={select} coarse={coarse} hint={`Move across the ${noun} to find its parts`} startLabel="Start the story →" onStart={canTell ? () => tell(true) : undefined} />

        <ExportDialog open={exportOpen} onClose={() => setExportOpen(false)} targets={targets} target={exportTarget} onTarget={setExportTarget} />
      </div>
    </div>
  )
}
