// One patch: its vector drawing beside the same drawing sewn by Patcher's digitizer, with the size,
// edge and thread finish to sew it at, and the machine files to download.

import { useEffect, useRef, useState } from 'react'
import { createDigitizer, renderTextured, writeDst, writeExp } from 'patcher'
import { LIBRARY, cardLabel, loadPatchSvg, variantsOf } from 'patcher/library'
import { Segmented } from '../site/Segmented.jsx'
import { SiteLink } from '../site/navigation.jsx'
import { FOREST_SERVICE_TIMELINE, historyOf } from './patchHistory.js'

/** Patcher's own site, which opens a library patch with every digitizing setting exposed. */
const PATCHER_URL = 'https://ahzs645.github.io/patcher/'

const SIZES = [
  { value: '76', label: '3″', title: '76 mm wide' },
  { value: '89', label: '3½″', title: '89 mm wide' },
  { value: '102', label: '4″', title: '102 mm wide' },
  { value: '127', label: '5″', title: '127 mm wide' }
]
const BORDERS = [
  { value: 'merrow', label: 'Merrow', title: 'An overlocked edge, as most cloth patches have' },
  { value: 'satin', label: 'Satin', title: 'A satin-stitch edge' },
  { value: 'none', label: 'None' }
]
const FINISHES = [
  { value: 'matte', label: 'Matte', title: 'Polyester or cotton thread' },
  { value: 'glossy', label: 'Glossy', title: 'Rayon thread with a satin sheen' }
]
const LIGHT_DEG = 225

/** The photographs a design was seen in: one per source (S27-O01 and S27-O03 are both photo S27). */
export const photosOf = (patch) => {
  const photos = new Map()
  for (const { id, sourceUrl } of patch.sightings ?? []) {
    const photo = id.replace(/-O\d+$/, '')
    if (!photos.has(photo)) photos.set(photo, { photo, sourceUrl, ids: [] })
    photos.get(photo).ids.push(id)
  }
  return [...photos.values()]
}

const mergedLabels = new Map(LIBRARY.merged.map((m) => [m.id, m.label]))
const absorbedLabels = new Map((LIBRARY.absorbed ?? []).map((m) => [m.id, m.label]))

/** What the BC Forest Service timeline says about the patch's wording, and a Forest Oval's own history. */
function PatchHistory({ patch }) {
  const { notes, logo } = historyOf(patch)
  if (!notes.length && !logo) return null
  return (
    <section className="patch__history" aria-label="History">
      <h3>History</h3>
      {notes.length > 0 && (
        <ul>
          {notes.map((note) => (
            <li key={note.id}><span className="patch__era">{note.era}</span> {note.text}</li>
          ))}
        </ul>
      )}
      {notes.length > 0 && (
        <p className="patch__source">
          From the <a href={FOREST_SERVICE_TIMELINE.url} target="_blank" rel="noreferrer">BC Forest Service timeline</a>: the dates
          bound the wording, not the patch itself.
        </p>
      )}
      {logo && (
        <p className="patch__source">
          {logo.evidence}. <SiteLink to={{ view: 'internal', internal: 'forests', 'internal-logo': logo.id }}>{logo.name} in Internal Logos</SiteLink> has
          its dated research.
        </p>
      )}
    </section>
  )
}

const download = (blob, name) => {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = name
  link.click()
  setTimeout(() => URL.revokeObjectURL(link.href), 1000)
}

const textured = (result, finish, scale, canvas) => renderTextured(result, {
  scale,
  lightDeg: LIGHT_DEG,
  colors: result.palette,
  borderColor: result.borderColor,
  dropShadow: true,
  finish
}, canvas)

/**
 * @param {object} props
 * @param {object} props.patch      A resolved library patch (patcher/library).
 * @param {object} props.org        Its organization.
 * @param {{index: number, count: number}} props.position  Where it sits among the organization's patches.
 * @param {object|null} props.previous
 * @param {object|null} props.next
 * @param {(patch: object) => void} props.onOpen
 * @param {() => void} props.onClose
 */
export const PatchViewer = ({ patch, org, position, previous, next, onOpen, onClose, noun = 'patches' }) => {
  const [widthMm, setWidthMm] = useState('89')
  const [border, setBorder] = useState('merrow')
  const [finish, setFinish] = useState('matte')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('sewing')
  const [attempt, setAttempt] = useState(0)
  // The whole drawing: library patches are stored with their shared crests and outlines apart, and
  // loadPatchSvg joins them back into the atlas's file (checked against its SHA-256).
  const [drawing, setDrawing] = useState(null)
  const digitizer = useRef(null)
  const canvas = useRef(null)

  useEffect(() => {
    const instance = createDigitizer()
    digitizer.current = instance
    return () => { instance.dispose(); if (digitizer.current === instance) digitizer.current = null }
  }, [])

  useEffect(() => {
    let gone = false
    let url = null
    setStatus('sewing')
    loadPatchSvg(patch)
      .then((text) => {
        if (gone) return
        url = URL.createObjectURL(new Blob([text], { type: 'image/svg+xml' }))
        setDrawing({ text, url })
      })
      .catch((error) => { if (!gone) { console.error(error); setStatus('failed') } })
    return () => { gone = true; if (url) URL.revokeObjectURL(url) }
  }, [patch, attempt])

  useEffect(() => {
    if (!drawing) return undefined
    let gone = false
    setStatus('sewing')
    digitizer.current.digitize(drawing.text, { widthMm: Number(widthMm), border })
      .then((sewn) => { if (!gone) { setResult(sewn); setStatus('ready') } })
      .catch((error) => { if (!gone) { console.error(error); setStatus('failed') } })
    return () => { gone = true }
  }, [drawing, widthMm, border])

  useEffect(() => {
    if (!result || !canvas.current) return
    const ratio = Math.min(2, globalThis.devicePixelRatio || 1)
    textured(result, finish, (Math.min(16, 3200 / Math.max(result.widthMm, result.heightMm)) * ratio) / 1.4, canvas.current)
  }, [result, finish])

  useEffect(() => {
    const onKey = (event) => {
      if (event.target.closest?.('input, select, textarea') || event.metaKey || event.ctrlKey || event.altKey) return
      if (event.key === 'Escape') onClose()
      else if (event.key === 'ArrowLeft' && previous) onOpen(previous)
      else if (event.key === 'ArrowRight' && next) onOpen(next)
    }
    globalThis.addEventListener('keydown', onKey)
    return () => globalThis.removeEventListener('keydown', onKey)
  }, [onClose, onOpen, previous, next])

  const name = `${patch.id}-${org.id}`
  // A variant is shown under its card's label, and named in full where it stands alone.
  const variants = variantsOf(patch)
  const title = patch.variant ? `${cardLabel(patch)} — ${patch.variant}` : patch.label
  const ready = status === 'ready' && result
  const exportPng = () => {
    const png = textured(result, finish, Math.min(24, 6000 / Math.max(result.widthMm, result.heightMm)))
    png.toBlob((blob) => blob && download(blob, `${name}-embroidered.png`), 'image/png')
  }

  return (
    <section className="patch" aria-label={title}>
      <nav className="patch__bar" aria-label={noun === 'badges' ? 'Badges' : 'Patches'}>
        <button type="button" className="button button--ghost" onClick={onClose}>← All {noun}</button>
        <span className="patch__crumb">{org.name} · {position.index + 1} of {position.count}</span>
        {/* On a phone the steps shrink to arrows, so the bar stays one row. */}
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
        <div className="patch__stages">
          <figure className="patch__stage">
            <figcaption>Vector</figcaption>
            <img src={drawing?.url ?? patch.previewUrl} alt={title} />
          </figure>
          <figure className="patch__stage" aria-busy={status === 'sewing'}>
            <figcaption>Embroidered</figcaption>
            <canvas ref={canvas} hidden={!ready} aria-label={`${title}, embroidered`} role="img" />
            {status === 'sewing' && <p className="patch__status" role="status">Sewing…</p>}
            {status === 'failed' && (
              <p className="patch__status" role="alert">
                This patch couldn’t be sewn. <button type="button" className="button--inline" onClick={() => setAttempt((n) => n + 1)}>Try again</button>
              </p>
            )}
          </figure>
        </div>

        <aside className="patch__panel">
          <h2>{cardLabel(patch)}</h2>
          <p className="patch__meta">{patch.medium} · {patch.quality}</p>

          {variants && (
            // Above the other controls and wrapping, since a design can have ten variants.
            <div className="patch__variants">
              <Segmented
                label="Variant"
                options={variants.members.map((m) => ({ value: m.id, label: m.variant, title: m.label }))}
                value={patch.id}
                onChange={(id) => onOpen(variants.members.find((m) => m.id === id))}
              />
            </div>
          )}
          <Segmented label="Width" options={SIZES} value={widthMm} onChange={setWidthMm} compact />
          <Segmented label="Edge" options={BORDERS} value={border} onChange={setBorder} compact />
          <Segmented label="Thread" options={FINISHES} value={finish} onChange={setFinish} compact />

          {ready && (
            <>
              <dl className="patch__facts">
                <div><dt>Size</dt><dd>{Math.round(result.widthMm - 2 * result.padMm)} × {Math.round(result.heightMm - 2 * result.padMm)} mm</dd></div>
                <div><dt>Stitches</dt><dd>{result.stitchCount.toLocaleString()}</dd></div>
                <div><dt>Threads</dt><dd>{result.palette.length}</dd></div>
              </dl>
              <ul className="patch__threads" aria-label="Thread colours">
                {result.palette.map((colour, index) => (
                  <li key={colour} title={`${colour} · ${Math.round(result.coverage[index] * 100)}%`} style={{ background: colour }} />
                ))}
              </ul>
            </>
          )}

          <div className="patch__exports">
            <button type="button" className="button button--primary" disabled={!ready} onClick={exportPng}>PNG</button>
            <button type="button" className="button" disabled={!ready} onClick={() => download(new Blob([writeDst(result, name)]), `${name}.dst`)} title="Tajima machine file">DST</button>
            <button type="button" className="button" disabled={!ready} onClick={() => download(new Blob([writeExp(result)]), `${name}.exp`)} title="Melco machine file">EXP</button>
            {drawing
              ? <a className="button" href={drawing.url} download={`${name}.svg`}>SVG</a>
              : <button type="button" className="button" disabled>SVG</button>}
          </div>
          <p className="patch__more">
            <a href={`${PATCHER_URL}?patch=${encodeURIComponent(patch.id)}`} target="_blank" rel="noreferrer">Open in Patcher</a> for
            stitch density, thread charts and the sew-out.
          </p>

          <PatchHistory patch={patch} />
          {patch.limitations && (
            <details className="patch__limits">
              <summary>Limitations</summary>
              <p>{patch.limitations}</p>
            </details>
          )}
          <p className="patch__source">
            {patch.supplied
              ? <>{patch.id}, a supplied drawing rather than an atlas entry</>
              : <>{patch.id} in the atlas</>}
            {photosOf(patch).length <= 1 && patch.sourceUrl && <> · <a href={patch.sourceUrl} target="_blank" rel="noreferrer">source photograph</a></>}
          </p>
          {photosOf(patch).length > 1 && (
            <p className="patch__source">
              Seen {patch.sightings.length} times in {photosOf(patch).length} photographs:{' '}
              {photosOf(patch).map(({ photo, sourceUrl, ids }, index) => (
                <span key={photo}>
                  {index > 0 && ', '}
                  {sourceUrl ? <a href={sourceUrl} target="_blank" rel="noreferrer">{photo}</a> : photo}
                  {ids.length > 1 && ` (×${ids.length})`}
                </span>
              ))}
            </p>
          )}
          {patch.absorbs?.length > 0 && (
            <p className="patch__source">
              It takes the place of the atlas’s {patch.absorbs.map((id) => `${id} “${absorbedLabels.get(id) ?? id}”`).join(', ')}.
            </p>
          )}
          {patch.merged.length > 0 && (
            <p className="patch__source">
              The atlas also lists it as {patch.merged.map((id) => `${id} “${mergedLabels.get(id) ?? id}”`).join(', ')}: the same
              drawing fitted to another photograph.
            </p>
          )}
        </aside>
      </div>
    </section>
  )
}
