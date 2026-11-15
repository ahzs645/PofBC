// One badge: its drawing built as a solid metal (or leather) badge you can turn, bend across its
// width or into a shallow dome, and export as a PNG or a GLB model, with the vector a tab away.
//
// Preliminary. It follows the curved badge trial of 14 November 2026 (research/badges/), which
// compared Medal Forge and Luster on S51-O01 and preferred Medal Forge for metal badges with raised
// lettering. Size, relief, finish and curvature are illustrative choices, not measurements.

import { useEffect, useRef, useState } from 'react'
import { cardLabel, loadPatchSvg, variantsOf } from 'patcher/library'
import { Segmented } from '../site/Segmented.jsx'
import { PatchStage } from '../patches/PatchStage.jsx'
import { PatchHistory, photosOf } from '../patches/PatchDetails.jsx'
import { METALS, NOMINAL_SIZE_MM } from './badgeParts.js'
import { MEDAL_FORGE, buildBadge } from './medalBadge.js'
import { BadgeScene } from './badgeScene.js'
import { BADGE_VIEW_DEFAULTS, badgeModeFor, loadBadgeView, saveBadgeView } from './badgeView.js'
import { badgeReviewAssetUrl, badgeReviewSources } from './badgeReview.js'
import './badges.css'

const REVIEW_URL = `${import.meta.env.BASE_URL}badge-review/index.json`
const REVIEW_LABELS = { refine: 'Needs refinement', reconstruct: 'Needs reconstruction', reviewed: 'Reviewed', unreviewed: 'Not yet reviewed' }
const MODES = [
  { value: 'metal', label: 'Metal', title: 'The drawing built as a solid badge' },
  { value: 'vector', label: 'Vector' }
]
const REVIEW_MODES = [
  { value: 'source', label: 'Source', title: 'The original photograph crop' },
  { value: 'compare', label: 'Compare', title: 'The source photograph beside the vector' }
]
const CURVES = [
  { value: 'flat', label: 'Flat' },
  { value: 'cylinder', label: 'Curve', title: 'Bent across its width, as a badge curves to a chest or a cap' },
  { value: 'dome', label: 'Dome', title: 'A shallow dome' }
]
const CAMERAS = [
  { value: 'front', label: 'Front' },
  { value: 'oblique', label: 'Oblique' },
  { value: 'top', label: 'Top', title: 'Looking down on the curve' },
  { value: 'side', label: 'Side' },
  { value: 'back', label: 'Back', title: 'The reverse: generated, without fittings or marks' }
]

const storage = () => { try { return globalThis.localStorage } catch { return null } }

const download = (blob, name) => {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = name
  link.click()
  setTimeout(() => URL.revokeObjectURL(link.href), 1000)
}

const webglAvailable = () => {
  try {
    const canvas = document.createElement('canvas')
    return Boolean(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}

/** The 3D stage: a canvas that fills its pane, the mode switch and the camera presets above it. */
function MetalStage ({ sceneRef, toolbar, status, onReady, label, camera, onCamera }) {
  const canvas = useRef(null)
  const pane = useRef(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (!webglAvailable()) { setFailed(true); return undefined }
    let scene
    try {
      scene = new BadgeScene(canvas.current)
    } catch (error) {
      console.error(error)
      setFailed(true)
      return undefined
    }
    sceneRef.current = scene
    const observer = new ResizeObserver(([entry]) => scene.resize(entry.contentRect.width, entry.contentRect.height))
    observer.observe(pane.current)
    onReady(scene)
    return () => { observer.disconnect(); onReady(null); scene.dispose(); if (sceneRef.current === scene) sceneRef.current = null }
  }, [])

  const onKeyDown = (event) => {
    const scene = sceneRef.current
    if (!scene) return
    const step = 0.1
    if (event.key === 'r' || event.key === 'R') { scene.setView('oblique'); onCamera('oblique'); return }
    const moves = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] }
    if (!moves[event.key]) return
    event.preventDefault()
    event.stopPropagation()
    scene.orbit(...moves[event.key])
  }

  return (
    <div className="patch-stage badge-stage">
      <div className="patch-stage__bar">
        <div className="patch-stage__tools">{toolbar}</div>
        <div className="badge-stage__cameras">
          <Segmented ariaLabel="Camera" options={CAMERAS} value={camera} onChange={(value) => { sceneRef.current?.setView(value); onCamera(value) }} compact />
        </div>
      </div>
      <div ref={pane} className="badge-stage__pane">
        {failed
          ? <p className="patch__status" role="alert">This browser can’t show 3D (WebGL is off or unavailable). The vector is a tab away.</p>
          : <canvas ref={canvas} tabIndex={0} role="img" aria-label={label} onKeyDown={onKeyDown} />}
        {!failed && status && <p className="patch__status badge-stage__status" role="status">{status}</p>}
      </div>
    </div>
  )
}

/**
 * @param {object} props  As PatchViewer's: a library badge, its organization, where it sits among
 *   its organization's badges, its neighbours, and how to open another or close.
 */
export const BadgeViewer = ({ patch, org, position, previous, next, onOpen, onClose, noun = 'badges' }) => {
  const [view, setView] = useState(() => loadBadgeView(storage()))
  const set = (change) => setView((current) => { const next = { ...current, ...change }; saveBadgeView(storage(), next); return next })
  const [drawing, setDrawing] = useState(null)
  const [attempt, setAttempt] = useState(0)
  const [built, setBuilt] = useState(null)
  const [phase, setPhase] = useState('loading')
  const [scene, setScene] = useState(null)
  const [bend, setBend] = useState(null)
  const [exporting, setExporting] = useState(false)
  const [reviewIndex, setReviewIndex] = useState({ status: 'loading', data: null })
  const [reviewAttempt, setReviewAttempt] = useState(0)
  const [sourceSelection, setSourceSelection] = useState(null)
  const [failedSource, setFailedSource] = useState(null)
  const [sourceAttempt, setSourceAttempt] = useState(0)
  const sceneRef = useRef(null)
  // A rebuilt scene (a new badge, or back from the Vector tab) opens at the chosen camera.
  const cameraRef = useRef(view.camera)
  cameraRef.current = view.camera
  const current = drawing?.patchId === patch.id ? drawing : null
  const review = reviewIndex.data?.patches.find((entry) => entry?.id === patch.id) ?? null
  const sources = badgeReviewSources(patch, review)
  const source = sources.find((entry) => sourceSelection?.patchId === patch.id && entry.occurrenceId === sourceSelection.occurrenceId) ?? sources[0] ?? null
  const sourceCropUrl = badgeReviewAssetUrl(source?.cropUrl, import.meta.env.BASE_URL)
  const sourceKey = `${patch.id}:${source?.occurrenceId ?? ''}:${sourceCropUrl ?? ''}`
  const sourceAvailable = Boolean(sourceCropUrl) && failedSource !== sourceKey
  const mode = badgeModeFor(view.mode, sources.length > 0)
  const reviewIsCurrent = !review?.svgSha256 || review.svgSha256 === patch.sha256
  const candidateChanges = Array.isArray(review?.candidateChanges) ? review.candidateChanges.filter((change) => typeof change === 'string' && change.trim()) : []

  useEffect(() => {
    let gone = false
    const controller = new AbortController()
    setReviewIndex({ status: 'loading', data: null })
    fetch(REVIEW_URL, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`Badge review: HTTP ${response.status}`)
        return response.json()
      })
      .then((data) => {
        if (data?.version !== 1 || !Array.isArray(data.patches)) throw new Error('Badge review index is invalid')
        if (!gone) setReviewIndex({ status: 'ready', data })
      })
      .catch((error) => { if (!gone) { console.error(error); setReviewIndex({ status: 'failed', data: null }) } })
    return () => { gone = true; controller.abort() }
  }, [reviewAttempt])

  // The whole drawing, joined from the library's shared parts.
  useEffect(() => {
    let gone = false
    let url = null
    setDrawing(null)
    setBuilt(null)
    setPhase('loading')
    loadPatchSvg(patch)
      .then((text) => {
        if (gone) return
        url = URL.createObjectURL(new Blob([text], { type: 'image/svg+xml' }))
        setDrawing({ patchId: patch.id, text, url })
      })
      .catch((error) => { if (!gone) { console.error(error); setPhase('failed-source') } })
    return () => { gone = true; if (url) URL.revokeObjectURL(url) }
  }, [patch, attempt])

  // Build the badge once its drawing and the stage are both there. Building takes a moment on a
  // detailed badge, so let "Building…" paint first.
  useEffect(() => {
    if (!current || !scene || mode !== 'metal') return undefined
    // A stage that remounted (back from the Vector tab) is a new, empty scene.
    if (built?.patchId === patch.id && built.scene === scene) return undefined
    setPhase('building')
    const timer = setTimeout(() => {
      try {
        const badge = buildBadge(current.text, { medium: patch.medium, sizeMm: NOMINAL_SIZE_MM, family: patch.family })
        scene.setModel(badge.group, { metal: badge.metal })
        scene.setView(cameraRef.current)
        setBuilt({ patchId: patch.id, scene, metal: badge.metal, sizeMm: badge.sizeMm, stats: badge.stats })
        setPhase('ready')
      } catch (error) {
        console.error(error)
        scene.clearModel()
        setPhase('failed-build')
      }
    }, 30)
    return () => clearTimeout(timer)
  }, [current, scene, mode, patch.id, patch.medium, patch.family, built?.patchId, built?.scene])

  // Bend whenever the model or the curvature changes.
  const ready = mode === 'metal' && phase === 'ready' && built?.patchId === patch.id && built.scene === scene && Boolean(scene)
  const maxRise = ready && scene ? scene.maxRise(view.curvature) : 0
  const rise = Math.min(view.rise, maxRise || view.rise)
  useEffect(() => {
    if (!ready || !scene) return
    try { setBend(scene.bend(view.curvature, rise)) } catch (error) { console.error(error) }
  }, [ready, scene, view.curvature, rise])

  useEffect(() => {
    const onKey = (event) => {
      if (event.target.closest?.('input, select, textarea, canvas') || event.metaKey || event.ctrlKey || event.altKey) return
      if (event.key === 'Escape') onClose()
      else if (event.key === 'ArrowLeft' && previous) onOpen(previous)
      else if (event.key === 'ArrowRight' && next) onOpen(next)
    }
    globalThis.addEventListener('keydown', onKey)
    return () => globalThis.removeEventListener('keydown', onKey)
  }, [onClose, onOpen, previous, next])

  const name = `${patch.id}-${org.id}`
  const variants = variantsOf(patch)
  const title = patch.variant ? `${cardLabel(patch)} — ${patch.variant}` : patch.label
  const metal = built ? METALS[built.metal] : null
  const curveLabel = CURVES.find((c) => c.value === view.curvature)?.label ?? 'Flat'

  const exportPng = async () => {
    if (!ready) return
    download(await scene.png(), `${name}-${built.metal}-${view.curvature}.png`)
  }
  const exportGlb = async () => {
    if (!ready || exporting) return
    setExporting(true)
    try {
      const blob = await scene.glb({
        badge: patch.id,
        label: patch.label,
        organization: org.name,
        material: metal.name,
        nominalLongerSideMm: NOMINAL_SIZE_MM,
        physicalMeasurements: false,
        curvature: bend,
        engine: MEDAL_FORGE,
        drawingSha256: patch.sha256,
        limitations: 'Interpreted relief, size, finish and curvature; the reverse is generated, without fittings or marks.'
      })
      download(blob, `${name}-${view.curvature}-${rise.toFixed(1)}mm.glb`)
    } catch (error) {
      console.error(error)
    } finally {
      setExporting(false)
    }
  }

  const status = phase === 'loading' ? 'Loading drawing…'
    : phase === 'building' ? 'Building the badge…'
      : phase === 'failed-build' ? 'This badge couldn’t be built in 3D. The vector is a tab away.'
        : phase === 'failed-source' ? 'The drawing could not be loaded.'
          : null
  const modeSwitch = <Segmented ariaLabel="View" options={sources.length ? [...MODES, ...REVIEW_MODES] : MODES} value={mode} onChange={(value) => set({ mode: value })} compact />
  const sourcePane = {
    key: 'source',
    label: 'Source photograph',
    node: sourceAvailable
      ? <img key={`${sourceKey}:${sourceAttempt}`} src={sourceCropUrl} width={source.width} height={source.height} alt={`${title}, source occurrence ${source.occurrenceId}`} draggable={false} onError={() => setFailedSource(sourceKey)} />
      : <p className="patch__status" role="status">This source image could not be loaded. <button type="button" className="button--inline" onClick={() => { setFailedSource(null); setSourceAttempt((n) => n + 1) }}>Retry source</button></p>
  }
  const vectorPane = {
    key: 'vector',
    label: sources.length ? 'Vector reconstruction' : 'Vector',
    node: <img className="patch__vector" src={current?.url ?? patch.previewUrl} alt={title} draggable={false} />
  }

  return (
    <section className="patch badge" aria-label={title}>
      <nav className="patch__bar" aria-label="Badges">
        <button type="button" className="button button--ghost" onClick={onClose}>← All {noun}</button>
        <span className="patch__crumb">{org.name} · {position.index + 1} of {position.count}</span>
        <span className="patch__steps">
          <button type="button" className="button" disabled={!previous} onClick={() => onOpen(previous)} title={previous?.label} aria-label="Previous">
            <span aria-hidden="true">‹</span><span className="patch__step-label"> Previous</span>
          </button>
          <button type="button" className="button" disabled={!next} onClick={() => onOpen(next)} title={next?.label} aria-label="Next">
            <span className="patch__step-label">Next </span><span aria-hidden="true">›</span>
          </button>
        </span>
      </nav>

      <div className="patch__body">
        <div className="patch__visuals">
          {mode === 'metal'
            ? <MetalStage
                sceneRef={sceneRef}
                toolbar={modeSwitch}
                status={status}
                onReady={setScene}
                label={`${title}, 3D model`}
                camera={view.camera}
                onCamera={(camera) => set({ camera })}
              />
            : <PatchStage
                resetKey={`${patch.id}:${mode}:${sourceKey}`}
                toolbar={modeSwitch}
                panes={mode === 'compare' ? [sourcePane, vectorPane] : mode === 'source' ? [sourcePane] : [vectorPane]}
              />}
        </div>

        <aside className="patch__panel">
          <h2>{cardLabel(patch)}</h2>
          <p className="patch__meta">{patch.medium} · {patch.quality}</p>
          <p className="badge__preliminary">Preliminary 3D view: relief, size, finish and curve are modelling choices, not measurements.</p>

          {variants && (
            <div className="patch__variants">
              <Segmented
                label="Variant"
                options={variants.members.map((m) => ({ value: m.id, label: m.variant, title: m.label }))}
                value={patch.id}
                onChange={(id) => onOpen(variants.members.find((m) => m.id === id))}
              />
            </div>
          )}
          <Segmented label="Shape" options={CURVES} value={view.curvature} onChange={(value) => set({ curvature: value })} compact />
          <label className="patch__light">
            <span>Rise</span>
            <input
              type="range" min="0" max="8" step="0.5"
              value={view.rise}
              disabled={view.curvature === 'flat'}
              onChange={(event) => set({ rise: Number(event.target.value) })}
              aria-valuetext={`${rise.toFixed(1)} millimetres`}
            />
            <output>{view.curvature === 'flat' ? '—' : `${rise.toFixed(1)} mm`}</output>
          </label>
          {ready && view.rise > maxRise && view.curvature !== 'flat' && <p className="patch__source">Held at {maxRise.toFixed(1)} mm, the most this badge’s width allows.</p>}
          {(view.curvature !== BADGE_VIEW_DEFAULTS.curvature || view.rise !== BADGE_VIEW_DEFAULTS.rise) && (
            <button type="button" className="button--inline patch__reset" onClick={() => set({ curvature: BADGE_VIEW_DEFAULTS.curvature, rise: BADGE_VIEW_DEFAULTS.rise })}>Reset the shape</button>
          )}

          {ready && (
            <dl className="patch__facts">
              <div><dt>Size</dt><dd>{Math.round(built.sizeMm.width)} × {Math.round(built.sizeMm.height)} mm</dd></div>
              <div><dt>Finish</dt><dd>{metal.name}</dd></div>
              <div><dt>Pieces</dt><dd>{built.stats.pieces}</dd></div>
            </dl>
          )}
          {ready && (
            <p className="patch__source">
              {curveLabel === 'Flat' ? 'Flat' : `${curveLabel}, ${rise.toFixed(1)} mm rise${bend?.radius ? ` (radius ${Math.round(bend.radius)} mm)` : ''}`}.
              The longer side is set to a nominal {NOMINAL_SIZE_MM} mm. {Math.round(built.stats.triangles).toLocaleString()} triangles.
            </p>
          )}

          <div className="patch__exports">
            <button type="button" className="button button--primary" disabled={!ready} onClick={exportPng} title="The view as it is now">PNG</button>
            <button type="button" className="button" disabled={!ready || exporting} onClick={exportGlb} title="The model as it is bent now, in metres">{exporting ? 'GLB…' : 'GLB'}</button>
            {current
              ? <a className="button" href={current.url} download={`${name}.svg`}>SVG</a>
              : <button type="button" className="button" disabled>SVG</button>}
          </div>
          {(phase === 'failed-source' || (mode === 'metal' && phase === 'failed-build')) && (
            <p className="patch__status" role="alert">
              {phase === 'failed-source' ? 'The drawing could not be loaded.' : 'The 3D model could not be built.'} <button type="button" className="button--inline" onClick={() => setAttempt((n) => n + 1)}>Try again</button>
            </p>
          )}

          <details className="patch__limits">
            <summary>How the badge is built</summary>
            <p>
              The drawing goes through the <a href={`${MEDAL_FORGE.repository}/tree/${MEDAL_FORGE.commit}`} target="_blank" rel="noreferrer">Medal Forge</a> geometry
              core: every painted region is extruded and bevelled over a body that is the outline of the whole badge. Lettering
              and the rim stand highest, lighter metal above darker, enamel just proud of the field, and dark fields lowest.
              The illustration’s drawn shadows are left out; the lighting makes its own. The curve bends the whole object,
              front, back and sides, so it stays in the GLB.
            </p>
            <p>
              The size, depths, finish and curvature are not measured from a specimen, and the reverse has no pin, clutch
              or maker’s marks. Fine detail in the drawing (letter shapes, the arms) is its reconstruction, not the die’s.
            </p>
          </details>
          <PatchHistory patch={patch} />
          {patch.limitations && (
            <details className="patch__limits">
              <summary>Limitations of the drawing</summary>
              <p>{patch.limitations}</p>
            </details>
          )}
          <p className="patch__source">
            {patch.id} in the atlas
            {photosOf(patch).length <= 1 && patch.sourceUrl && <> · <a href={patch.sourceUrl} target="_blank" rel="noreferrer">source image</a></>}
          </p>
        </aside>

        {(review || reviewIndex.status === 'failed') && <section className="patch__review" aria-label="Source review">
          <div className="patch__review-heading">
            <h3>Source comparison</h3>
            {review && <span className={`patch__review-status patch__review-status--${reviewIsCurrent ? review.status : 'unreviewed'}`}>{reviewIsCurrent ? REVIEW_LABELS[review.status] ?? 'Not yet reviewed' : 'Drawing changed since review'}</span>}
          </div>
          {reviewIndex.status === 'failed' && <p role="status">The source comparison could not be loaded. <button type="button" className="button--inline" onClick={() => setReviewAttempt((n) => n + 1)}>Retry comparison</button></p>}
          {!reviewIsCurrent && <p>The findings below describe an earlier drawing. The current reconstruction needs another comparison.</p>}
          {review?.findings?.length > 0 && <ul>{review.findings.map((finding, index) => <li key={index}>{finding}</li>)}</ul>}
          {candidateChanges.length > 0 && <div className="patch__candidate"><h4>Correction prepared</h4><ul>{candidateChanges.map((change, index) => <li key={index}>{change}</li>)}</ul></div>}
          {review?.evidenceLimitations && <p className="patch__review-limits">{review.evidenceLimitations}</p>}
          {sources.length > 1 && <label className="patch__source-select"><span>Source occurrence</span><select value={source?.occurrenceId ?? ''} onChange={(event) => setSourceSelection({ patchId: patch.id, occurrenceId: event.target.value })}>{sources.map((entry) => <option key={entry.occurrenceId} value={entry.occurrenceId}>{entry.occurrenceId}</option>)}</select></label>}
          {source && <div className="patch__source-caption">
            <p><strong>{source.occurrenceId}</strong> · {source.width} × {source.height} source pixels</p>
            {source.medium && <p>{source.medium}</p>}
            {source.note && <p>{source.note}</p>}
            <a href={source.url} target="_blank" rel="noreferrer">Open full source</a>
          </div>}
          {review && <p className="patch__review-date">Evidence record: {review.reviewedAt ?? reviewIndex.data.reviewedAt}. Source images keep their original proportions.</p>}
        </section>}
      </div>
    </section>
  )
}
