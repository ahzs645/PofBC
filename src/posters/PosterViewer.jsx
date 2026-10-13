// One poster on the stage: hidden hotspots over the drawing, a panel for whichever part is open, a
// dock to step through them, a tour, and export.
//
// Generic over posters. A poster module supplies its drawing and parts; one that needs more than a
// data panel per part (the coastal poster's live logo studio, say) adds a `useExtras` hook, which
// can take over the frame, the stage's class, the panel and the export targets.

import { useCallback, useEffect, useMemo, useState } from 'react'
import { Poster } from './stage/Poster.jsx'
import { useMedia } from './hooks/useMedia.js'
import { useKeyboardNav } from './hooks/useKeyboardNav.js'
import { useTour } from './hooks/useTour.js'
import { Panel } from './ui/Panel.jsx'
import { Dock } from './ui/Dock.jsx'
import { DataPanel } from './ui/DataPanel.jsx'
import { posterSvgString } from './export/exportSvg.js'
import { ExportDialog } from './export/ExportDialog.jsx'
import { posterTarget } from './export/targets.js'

const PANEL_INSET = 440 + 40
// Keep in step with --pv-dock-h and the narrow sheet's height in posters.css.
const DOCK_HEIGHT = 60
const SHEET_SHARE = 0.52
const TOUR_SECONDS = 12
const noExtras = () => ({})

export function PosterViewer({ meta, series, module, part, onPart, onExit, previous, next, backLabel = 'Posters', noun = 'poster' }) {
  const { parts, order, regions, spotlight, svgRaw, prepare } = module
  const useExtras = module.useExtras ?? noExtras
  const [svg, setSvg] = useState(null)
  const [aboutOpen, setAboutOpen] = useState(false)
  const [exportOpen, setExportOpen] = useState(false)
  const [exportTarget, setExportTarget] = useState('poster')
  const narrow = useMedia('(max-width: 900px)')
  const coarse = useMedia('(hover: none)')
  const current = parts[part] ? part : 'overview'

  // The page under the viewer stays where it was and does not scroll behind it.
  useEffect(() => {
    const root = document.documentElement
    const before = { overflow: root.style.overflow, gutter: root.style.scrollbarGutter }
    root.style.overflow = 'hidden'
    root.style.scrollbarGutter = 'auto'
    return () => { root.style.overflow = before.overflow; root.style.scrollbarGutter = before.gutter }
  }, [])

  // Navigation: manual moves stop the tour; the tour's own moves do not.
  const tour = useTour({ order, current, onAdvance: (id) => move(id, false), seconds: TOUR_SECONDS })
  const move = useCallback((id, manual = true) => {
    onPart(id ?? 'overview')
    setAboutOpen(false)
    if (manual) tour.stop()
  }, [onPart, tour.stop]) // eslint-disable-line react-hooks/exhaustive-deps
  const select = useCallback((id) => move(id, true), [move])
  const openExport = useCallback((target) => { setExportTarget(target); setExportOpen(true) }, [])

  useKeyboardNav({
    order, current, onSelect: select, onExit, enabled: !exportOpen,
    keys: useMemo(() => ({ e: () => setExportOpen(true), p: tour.toggle }), [tour.toggle])
  })

  const extras = useExtras({ svg, part: current, select, openExport, tour })

  const frame = extras.frame ?? { box: parts[current].box, pad: parts[current].pad, initial: parts.overview.box }
  const panelOpen = current !== 'overview' || aboutOpen
  const inset = { right: panelOpen && !narrow ? PANEL_INSET : 0, bottom: DOCK_HEIGHT + (panelOpen && narrow ? Math.round(innerHeight * SHEET_SHARE) : 0) }
  const steps = useMemo(() => order.filter((id) => id !== 'overview').map((id) => ({ id, label: parts[id].label })), [order, parts])
  const regionList = useMemo(() => regions.map((id) => ({ id, ...parts[id] })), [regions, parts])

  const targets = [
    posterTarget({ meta, noun, getSvg: () => posterSvgString(svg, meta), tag: extras.posterTag }),
    ...(extras.targets ?? [])
  ]

  const content = extras.content ?? <DataPanel partId={current} parts={parts} order={order} onSelect={select} tour={tour} />

  return (
    <div className="pv" role="region" aria-label={`${meta.title}, interactive ${noun}`}>
      <div className="pv-app">
        <Poster
          svgRaw={svgRaw}
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
          {tour.playing && (
            <div className="pv-tour-bar" aria-hidden="true">
              <div className="pv-tour-fill" key={current} style={{ animationDuration: `${tour.seconds}s` }} />
            </div>
          )}
        </Poster>

        <header className="pv-top">
          <div className="pv-top-start">
            <button type="button" className="pv-ghost pv-back" onClick={onExit} title={`All ${backLabel.toLowerCase()} (Esc from the whole ${noun})`} aria-label={`Back to all ${backLabel.toLowerCase()}`}>← <span className="pv-back-label">{backLabel}</span></button>
            <button type="button" className="pv-brand" onClick={() => select('overview')} aria-label={`Back to the whole ${noun}`}>
              <b>{meta.title}</b>
              <span>{series.title}</span>
            </button>
          </div>
          <div className="pv-top-actions">
            {previous && <button type="button" className="pv-ghost pv-step-poster" onClick={previous.open} title={`Previous: ${previous.title}`} aria-label={`Previous poster: ${previous.title}`}>‹</button>}
            {next && <button type="button" className="pv-ghost pv-step-poster" onClick={next.open} title={`Next: ${next.title}`} aria-label={`Next poster: ${next.title}`}>›</button>}
            <button type="button" className="pv-ghost" aria-pressed={aboutOpen && current === 'overview'} onClick={() => { if (current !== 'overview') select('overview'); setAboutOpen((o) => !o) }}>About</button>
            <button type="button" className="pv-ghost pv-tour-btn" aria-pressed={tour.playing} onClick={tour.toggle} title="Play the tour (P)">{tour.playing ? 'Stop' : 'Tour'}</button>
            <button type="button" className="pv-ghost pv-solid" onClick={() => openExport('poster')} title="Export (E)">Export</button>
          </div>
        </header>

        <Panel open={panelOpen} narrow={narrow} contentKey={current} onClose={() => select('overview')}>
          {content}
        </Panel>

        <Dock steps={steps} current={current} onSelect={select} coarse={coarse} hint={`Move across the ${noun} to find its parts`} startLabel="Start the story →" />

        <ExportDialog open={exportOpen} onClose={() => setExportOpen(false)} targets={targets} target={exportTarget} onTarget={setExportTarget} />
      </div>
    </div>
  )
}
