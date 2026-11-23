// Paper models: fold-up models made in PackCAD, shown folding in 3D, with their printable sheets.
//
// The model on the stage is PackCAD's own viewer (vendor/packcad, built into public/packcad/ by
// scripts/build-packcad.mjs) in a frame: the same fold solver and renderer as the editor, so what
// folds here is what the downloaded file reopens as. This view draws the rest in the site's own
// chrome — the choice of model, the folding stages, play, and the downloads — and drives the
// viewer with messages (packcadFrame.js).
//
// The place is kept in the address bar (`?view=paper-models&model=bc-transit`).

import { useEffect, useMemo, useRef, useState } from 'react'
import { writeHistory } from '../site/browserHistory.js'
import { SiteLink } from '../site/navigation.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { useSiteTheme } from '../site/useTheme.js'
import { PACKCAD_EDITOR_URL, PAPER_MODEL_SERIES, filesOf, modelById, sheetWords } from './catalogue.js'
import { PackcadFrame, usePackcadViewer } from './PackcadFrame.jsx'
import { STAGE_GROUND, stagesOf, viewerSrc } from './packcadFrame.js'
import './paperModels.css'

const BASE = import.meta.env.BASE_URL
// Half PackCAD's editing pace, so each stage can be watched: the viewer turns to the panels a
// stage moves as it begins, and that needs the stage to last longer than the turn.
const FOLD_SPEED = 0.5
const LAYOUTS = [
  { value: '3d', label: '3D', title: 'The model folded in 3D' },
  { value: '2d', label: 'Flat', title: 'The sheet as printed, folding in 2D' },
  { value: 'split', label: 'Both', title: 'The 3D model beside the flat sheet' }
]

const readModel = () => modelById(new URLSearchParams(globalThis.location?.search ?? '').get('model'))

const PlayIcon = ({ playing }) => (
  <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
    {playing
      ? <path d="M3.5 2h2.5v10H3.5zM8 2h2.5v10H8z" fill="currentColor" />
      : <path d="M3.5 1.8v10.4L12 7z" fill="currentColor" />}
  </svg>
)

export const PaperModelsView = () => {
  const [model, setModel] = useState(readModel)
  const [layout, setLayout] = useState('3d')
  const files = filesOf(model)
  const { name: theme } = useSiteTheme()
  const themeRef = useRef(theme)
  themeRef.current = theme
  // Opens on the finished model and folds it once from the flat sheet. The address is made once
  // per model, in the theme of the moment: a later change of theme is sent to the frame (below)
  // rather than written into the address, which would reload it and fold the model again.
  const src = useMemo(() => viewerSrc(BASE, files.json, {
    autoplay: true,
    layout: '3d',
    speed: FOLD_SPEED,
    theme: themeRef.current,
    background: STAGE_GROUND[themeRef.current]
  }), [files.json])
  const { frame, ready, state, error, send } = usePackcadViewer(src)

  // Follow the site's light/dark toggle without reloading the frame.
  useEffect(() => {
    if (!ready) return
    send({ type: 'packcad:theme', theme })
    send({ type: 'packcad:background', color: STAGE_GROUND[theme] })
  }, [ready, send, theme])
  const { setup, folds } = stagesOf(ready?.steps)

  // Back and Forward move between models.
  useEffect(() => {
    const restore = () => setModel(readModel())
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [])

  // A new model opens in 3D, as the frame does.
  useEffect(() => { setLayout('3d') }, [model.id])

  const choose = (next) => {
    if (next.id === model.id) return
    const url = new URL(globalThis.location.href)
    url.searchParams.set('view', 'paper-models')
    url.searchParams.set('model', next.id)
    writeHistory(url)
    // The picker lists the series' bare entries; the page needs the model with its series.
    setModel(modelById(next.id))
  }

  const playing = Boolean(state?.playing)
  const stepIndex = state?.stepIndex ?? (ready ? ready.steps.length - 1 : 0)
  const seek = (index) => { send({ type: 'packcad:pause' }); send({ type: 'packcad:seek', step: index }) }

  return (
    <section className="paper-models" aria-label="Paper models">
      {PAPER_MODEL_SERIES.map((series) => (
        <div key={series.id} className="paper-models__series" role="group" aria-label={series.label}>
          <div className="paper-models__series-head">
            <h2>{series.label}</h2>
            <p>{series.summary}</p>
          </div>
          <div className="paper-models__picker">
            {series.models.map((entry) => (
              <a
                key={entry.id}
                className="paper-models__choice"
                href={`?view=paper-models&model=${entry.id}`}
                aria-current={entry.id === model.id ? 'true' : undefined}
                onClick={(event) => {
                  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
                  event.preventDefault()
                  choose(entry)
                }}
              >
                <strong>{entry.title}</strong>
                <span>{entry.livery}</span>
              </a>
            ))}
          </div>
        </div>
      ))}

      <div className="paper-models__body">
        <div className="paper-models__stage">
          <PackcadFrame ref={frame} src={src} title={`${model.title}, folding in 3D`} className="paper-models__frame" loading={!ready} />
          {!ready && !error && <p className="paper-models__status" role="status">Opening the {model.title}…</p>}
          {error && (
            <p className="paper-models__status paper-models__status--error" role="alert">
              The model could not be opened: {error}
            </p>
          )}
        </div>

        <aside className="paper-models__panel" aria-label={model.title}>
          <header>
            <h3>{model.title}</h3>
            <p>{model.livery}</p>
          </header>

          <div className="paper-models__transport">
            <button
              type="button"
              className="paper-models__play"
              disabled={!ready}
              aria-label={playing ? 'Pause folding' : 'Play the folding'}
              onClick={() => send({ type: playing ? 'packcad:pause' : 'packcad:play' })}
            >
              <PlayIcon playing={playing} />
              {playing ? 'Pause' : 'Fold it'}
            </button>
            <Segmented
              ariaLabel="View"
              options={LAYOUTS}
              value={layout}
              onChange={(value) => { setLayout(value); send({ type: 'packcad:layout', layout: value }) }}
            />
          </div>
          <div className="paper-models__progress" aria-hidden="true">
            <span style={{ width: `${Math.round((state?.progress ?? 1) * 100)}%` }} />
          </div>

          <ol className="paper-models__stages" aria-label="Folding stages">
            {setup && (
              <li>
                <button type="button" disabled={!ready} aria-current={stepIndex === 0 ? 'step' : undefined} onClick={() => seek(0)}>
                  <span className="paper-models__stage-n">0</span> Flat sheet
                </button>
              </li>
            )}
            {folds.map((step, index) => (
              <li key={step.id}>
                <button type="button" disabled={!ready} aria-current={stepIndex === index + 1 ? 'step' : undefined} onClick={() => seek(index + 1)}>
                  <span className="paper-models__stage-n">{index + 1}</span> {step.label.replace(/^\d+\s*[-–]\s*/, '')}
                </button>
              </li>
            ))}
          </ol>

          <dl className="paper-models__facts">
            <div><dt>Sheet</dt><dd>{sheetWords(model.sheetMm)}</dd></div>
            <div><dt>Panels</dt><dd>{model.panels}</dd></div>
            <div><dt>Folding stages</dt><dd>{model.stages}</dd></div>
            <div><dt>Board</dt><dd>{model.board}</dd></div>
          </dl>

          <ul className="paper-models__notes">
            {model.instructions.map((line) => <li key={line}>{line}</li>)}
            <li>{model.series.note}</li>
          </ul>

          <div className="paper-models__downloads">
            <a className="paper-models__download" href={`${BASE}${files.pdf}`} download>Printable PDF</a>
            <a href={`${BASE}${files.json}`} download>PackCAD project (.json)</a>
            <a href={PACKCAD_EDITOR_URL} target="_blank" rel="noreferrer">Open PackCAD</a>
          </div>
          <p className="paper-models__fineprint">
            The PDF carries the editable project: drop it onto PackCAD to reopen the model with its folding stages.
          </p>

          {model.related.length > 0 && (
            <p className="paper-models__related">
              {model.related.map((link) => <SiteLink key={link.label} to={link.to}>{link.label} →</SiteLink>)}
            </p>
          )}
        </aside>
      </div>
    </section>
  )
}
