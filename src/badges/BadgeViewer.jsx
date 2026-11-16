// One badge: its drawing built as a solid metal (or leather) badge you can turn, bend across its
// width or into a shallow dome, and export as a PNG or a GLB model, with the vector a tab away.
//
// Preliminary. It follows the curved badge trial of 14 November 2026 (research/badges/), which
// compared Medal Forge and Luster on S51-O01 and preferred Medal Forge for metal badges with raised
// lettering. Size, relief, finish and curvature are illustrative choices, not measurements.

import { useEffect, useId, useRef, useState } from 'react'
import { cardLabel, loadPatchSvg, variantsOf } from 'patcher/library'
import { Segmented } from '../site/Segmented.jsx'
import { PatchStage } from '../patches/PatchStage.jsx'
import { PatchHistory, photosOf } from '../patches/PatchDetails.jsx'
import { METALS, NOMINAL_SIZE_MM } from './badgeParts.js'
import { MEDAL_FORGE, buildBadge } from './medalBadge.js'
import { BadgeScene } from './badgeScene.js'
import { BADGE_VIEW_DEFAULTS, badgeModeFor, badgeShapeFor, badgeShapeStatus, applyBadgeShape, loadBadgeView, saveBadgeView } from './badgeView.js'
import { badgeReviewAssetUrl, badgeReviewSources } from './badgeReview.js'
import './badges.css'
import { Select } from '../site/ui/Select.jsx'
import { Slider } from '../site/ui/Slider.jsx'

const REVIEW_URL = `${import.meta.env.BASE_URL}badge-review/index.json`
const REVIEW_LABELS = { refine: 'Needs refinement', reconstruct: 'Needs reconstruction', reviewed: 'Reviewed', unreviewed: 'Not yet reviewed' }
const MODES = [
  { value: 'metal', label: '3D', title: 'The drawing built as a solid badge' },
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
function BadgeStage ({ sceneRef, toolbar, status, onReady, label, camera, onCamera }) {
  const canvas = useRef(null)
  const pane = useRef(null)
  const hintId = useId()
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
          : <canvas ref={canvas} tabIndex={0} role="img" aria-label={label} aria-describedby={hintId} onKeyDown={onKeyDown} />}
        {!failed && status && <p className="patch__status badge-stage__status" role="status">{status}</p>}
      </div>
      {!failed && <p id={hintId} className="badge-stage__hint">Drag to rotate · Pinch or scroll to zoom · Arrow keys to turn · R to reset the view</p>}
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
  const [bendAttempt, setBendAttempt] = useState(0)
  const [exporting, setExporting] = useState(null)
  const [exportError, setExportError] = useState(null)
  const [reviewIndex, setReviewIndex] = useState({ status: 'loading', data: null })
  const [reviewAttempt, setReviewAttempt] = useState(0)
  const [sourceSelection, setSourceSelection] = useState(null)
  const [failedSource, setFailedSource] = useState(null)
  const [sourceAttempt, setSourceAttempt] = useState(0)
  const sceneRef = useRef(null)
  const exportRequest = useRef(null)
  const exportCurrent = useRef(null)
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
    setBend(null)
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
    if (built?.patchId === patch.id && built.drawing === current && built.scene === scene) return undefined
    setBend(null)
    setPhase('building')
    const timer = setTimeout(() => {
      try {
        const badge = buildBadge(current.text, { medium: patch.medium, sizeMm: NOMINAL_SIZE_MM, family: patch.family })
        scene.setModel(badge.group, { metal: badge.metal })
        scene.setView(cameraRef.current)
        setBuilt({ patchId: patch.id, drawing: current, scene, metal: badge.metal, sizeMm: badge.sizeMm, stats: badge.stats })
        setPhase('ready')
      } catch (error) {
        console.error(error)
        scene.clearModel()
        setPhase('failed-build')
      }
    }, 30)
    return () => clearTimeout(timer)
  }, [current, scene, mode, patch.id, patch.medium, patch.family, built?.patchId, built?.drawing, built?.scene])

  // A built model is not exportable until its current requested curve has actually been applied.
  const modelReady = mode === 'metal' && phase === 'ready' && built?.patchId === patch.id && built.drawing === current && built.scene === scene && Boolean(scene)
  const maxRise = modelReady ? scene.maxRise(view.curvature) : 8
  const shape = badgeShapeFor(view, maxRise)
  const shapeStatus = modelReady ? badgeShapeStatus(bend, built, shape) : 'pending'
  const ready = modelReady && shapeStatus === 'ready'
  const applied = ready ? bend.result : null
  const rise = shape.rise
  exportCurrent.current = ready ? bend : null
  useEffect(() => {
    if (!modelReady) return
    const next = applyBadgeShape(built, { mode: shape.mode, rise: shape.rise })
    if (next.error) console.error(next.error)
    setBend(next)
  }, [modelReady, built, shape.mode, shape.rise, bendAttempt])
  useEffect(() => { setBend(null) }, [scene])

  // A pending export belongs to one badge and shape. Navigating or changing either cancels its download.
  useEffect(() => {
    exportRequest.current = null
    setExporting(null)
    setExportError(null)
  }, [patch.id, scene, mode, built, shape.mode, shape.rise])
  useEffect(() => () => { exportRequest.current = null; exportCurrent.current = null }, [])

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
  const metal = modelReady ? METALS[built.metal] : null
  const leather = modelReady ? built.metal === 'leather' : /leather/i.test(patch.medium ?? '')
  const curveLabel = CURVES.find((c) => c.value === applied?.mode)?.label ?? 'Flat'

  const exportBadge = async (format) => {
    if (!ready || exportRequest.current) return
    const snapshot = bend
    const request = {}
    exportRequest.current = request
    setExporting(format)
    setExportError(null)
    try {
      const blob = format === 'png' ? await scene.png() : await scene.glb({
        badge: patch.id,
        label: patch.label,
        organization: org.name,
        material: metal.name,
        catalogueMedium: patch.medium,
        nominalLongerSideMm: NOMINAL_SIZE_MM,
        physicalMeasurements: false,
        curvature: snapshot.result,
        engine: MEDAL_FORGE,
        drawingSha256: patch.sha256,
        limitations: 'Interpreted relief, size, finish and curvature; the reverse is generated, without fittings or marks.'
      })
      if (exportRequest.current !== request || exportCurrent.current !== snapshot) return
      download(blob, `${name}-${built.metal}-${snapshot.result.mode}-${snapshot.result.rise.toFixed(1)}mm.${format}`)
    } catch (error) {
      if (exportRequest.current === request && exportCurrent.current === snapshot) {
        console.error(error)
        setExportError(`The ${format.toUpperCase()} export could not be created. Try again or download the SVG.`)
      }
    } finally {
      if (exportRequest.current === request) { exportRequest.current = null; setExporting(null) }
    }
  }

  const status = phase === 'loading' ? 'Loading drawing…'
    : phase === 'building' ? 'Building the badge…'
      : phase === 'failed-build' ? 'This badge couldn’t be built in 3D. The vector is a tab away.'
        : phase === 'failed-source' ? 'The drawing could not be loaded.'
          : modelReady && shapeStatus === 'pending' ? 'Applying the shape…' : null
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
            ? <BadgeStage
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
          {mode === 'metal' && <p className="badge__preliminary">{leather
            ? 'Shown as tooled leather from the catalogue attribution. Material, size, relief and curvature have not been measured from the specimen.'
            : 'Illustrative 3D view: size, relief, finish and curvature are modelling choices, not measurements.'}</p>}

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
          {mode === 'metal' && <>
            <Segmented label="Shape" options={CURVES} value={view.curvature} onChange={(value) => set({ curvature: value })} compact />
            <label className="patch__light">
              <span>Rise</span>
              <Slider min="0" max="8" step="0.5"
                value={view.rise}
                disabled={view.curvature === 'flat'}
                onChange={(value) => set({ rise: value })}
                aria-valuetext={`${rise.toFixed(1)} millimetres`}
              />
              <output>{view.curvature === 'flat' ? '—' : `${rise.toFixed(1)} mm`}</output>
            </label>
            {modelReady && view.rise > maxRise && view.curvature !== 'flat' && <p className="patch__source">Held at {maxRise.toFixed(1)} mm to keep the whole badge within the selected curve.</p>}
            {(view.curvature !== BADGE_VIEW_DEFAULTS.curvature || view.rise !== BADGE_VIEW_DEFAULTS.rise) && (
              <button type="button" className="button--inline patch__reset" onClick={() => set({ curvature: BADGE_VIEW_DEFAULTS.curvature, rise: BADGE_VIEW_DEFAULTS.rise })}>Reset the shape</button>
            )}

            {ready && (
              <dl className="patch__facts">
                <div><dt>Nominal size</dt><dd>{Math.round(built.sizeMm.width)} × {Math.round(built.sizeMm.height)} mm</dd></div>
                <div><dt>Finish</dt><dd>{metal.name}</dd></div>
              </dl>
            )}
            {ready && (
              <p className="patch__source">
                {curveLabel === 'Flat' ? 'Flat' : `${curveLabel}, ${applied.rise.toFixed(1)} mm rise${applied.radius ? ` (radius ${Math.round(applied.radius)} mm)` : ''}`}.
                The longer side is set to a nominal {NOMINAL_SIZE_MM} mm.
              </p>
            )}
            {modelReady && shapeStatus === 'failed' && <p className="patch__status" role="alert">The selected curve could not be applied. Choose Flat or <button type="button" className="button--inline" onClick={() => setBendAttempt((n) => n + 1)}>retry the curve</button>. 3D exports are unavailable until the shape is applied.</p>}
          </>}

          <div className="patch__exports">
            {mode === 'metal' && <>
              <button type="button" className="button button--primary" disabled={!ready || Boolean(exporting)} onClick={() => exportBadge('png')} title="The view as it is now">{exporting === 'png' ? 'PNG…' : 'PNG'}</button>
              <button type="button" className="button" disabled={!ready || Boolean(exporting)} onClick={() => exportBadge('glb')} title="The model as it is bent now, in metres">{exporting === 'glb' ? 'GLB…' : 'GLB'}</button>
            </>}
            {current
              ? <a className="button" href={current.url} download={`${name}.svg`}>SVG</a>
              : <button type="button" className="button" disabled>SVG</button>}
          </div>
          {exportError && <p className="patch__status" role="alert">{exportError}</p>}
          {(phase === 'failed-source' || (mode === 'metal' && phase === 'failed-build')) && (
            <p className="patch__status" role="alert">
              {phase === 'failed-source' ? 'The drawing could not be loaded.' : 'The 3D model could not be built.'} <button type="button" className="button--inline" onClick={() => setAttempt((n) => n + 1)}>Try again</button>
            </p>
          )}

          <details className="patch__limits">
            <summary>How the badge is built</summary>
            <p>
              The drawing goes through the <a href={`${MEDAL_FORGE.repository}/tree/${MEDAL_FORGE.commit}`} target="_blank" rel="noreferrer">Medal Forge</a> geometry
              core: the silhouette, rim, lettering and emblems form layers of bevelled relief.
              {leather ? ' Leather uses a matte finish and shallower tooling, following the catalogue attribution rather than a verified material measurement.' : ' Metal surfaces use raised lettering and emblems above a lower field, with enamel where the drawing records it.'}
              {' '}The lighting makes its own shadows. The curve bends the whole object,
              front, back and sides, so it stays in the GLB.
            </p>
            {modelReady && <p>{built.stats.pieces} modelled regions · {Math.round(applied?.triangles ?? built.stats.triangles).toLocaleString()} triangles.</p>}
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
          {sources.length > 1 && <label className="patch__source-select"><span>Source occurrence</span><Select value={source?.occurrenceId ?? ''} onChange={(value) => setSourceSelection({ patchId: patch.id, occurrenceId: value })}>{sources.map((entry) => <option key={entry.occurrenceId} value={entry.occurrenceId}>{entry.occurrenceId}</option>)}</Select></label>}
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
