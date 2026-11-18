// One patch: its vector drawing beside the same drawing sewn by Patcher's digitizer, with the size,
// edge and thread finish to sew it at, and the machine files to download.

import { useEffect, useMemo, useRef, useState } from 'react'
import { createDigitizer, renderTextured, writeDst, writeExp } from 'patcher'
import { LIBRARY, cardLabel, loadPatchSvg, variantsOf } from 'patcher/library'
import sourceCrops from './sourceCrops.json'
import { SourceOverlay } from './SourceOverlay.jsx'
import { BadgeRelief } from './BadgeRelief.jsx'
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
          describe when the wording was used.
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
  const badge = patch.collection === 'badges'
  const textile = ['Cloth patch', 'Cloth rocker', 'Cloth embroidery'].includes(patch.medium)
  const [choice, setPreview] = useState('vector')
  const reference = sourceCrops[patch.id]
  const preview = choice === 'source' && !reference ? 'vector' : choice
  const overlay = preview === 'source'
  const embroidery = !overlay && (textile || preview === 'embroidered')
  const [attempt, setAttempt] = useState(0)
  const [loaded, setLoaded] = useState(null)
  const [sewn, setSewn] = useState(null)
  const canvas = useRef(null)
  const back = useRef(null)
  // Returning to an earlier variant starts a fresh fetch. Its previous blob URL has been revoked.
  const request = useMemo(() => ({ patch, attempt }), [patch, attempt])
  const drawing = loaded?.request === request ? loaded : null
  const sameSettings = sewn?.drawing === drawing && sewn.widthMm === widthMm && sewn.border === border
  const stitchJob = drawing?.url && sameSettings ? sewn : null
  const result = embroidery ? stitchJob?.result : null

  useEffect(() => { back.current?.focus({ preventScroll: true }) }, [])

  useEffect(() => {
    let active = true
    let url
    loadPatchSvg(request.patch)
      .then((text) => {
        if (!active) return
        url = URL.createObjectURL(new Blob([text], { type: 'image/svg+xml' }))
        setLoaded({ request, text, url })
      })
      .catch((error) => {
        if (!active) return
        console.error(error)
        setLoaded({ request, failed: true })
      })
    return () => { active = false; if (url) URL.revokeObjectURL(url) }
  }, [request])

  useEffect(() => {
    if (!embroidery || !drawing?.url) return
    const digitizer = createDigitizer()
    let active = true
    digitizer.digitize(drawing.text, { widthMm: Number(widthMm), border })
      .then((result) => { if (active) setSewn({ drawing, widthMm, border, result }) })
      .catch((error) => {
        if (!active) return
        console.error(error)
        setSewn({ drawing, widthMm, border, failed: true })
      })
    return () => { active = false; digitizer.dispose() }
  }, [embroidery, drawing, widthMm, border])

  useEffect(() => {
    if (!result || !canvas.current) return
    const ratio = Math.min(2, globalThis.devicePixelRatio || 1)
    textured(result, finish, (Math.min(16, 3200 / Math.max(result.widthMm, result.heightMm)) * ratio) / 1.4, canvas.current)
  }, [result, finish])

  useEffect(() => {
    const onKey = (event) => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) return
      if (event.target.closest?.('input, select, textarea, [contenteditable="true"], [role="menu"]')) return
      if (event.target !== document.body && !event.target.closest?.('.patch')) return
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
  const photos = photosOf(patch)
  const failed = drawing?.failed || stitchJob?.failed
  const retry = <button type="button" className="button--inline" onClick={() => setAttempt((n) => n + 1)}>Try again</button>
  const exportPng = () => {
    const png = textured(result, finish, Math.min(24, 6000 / Math.max(result.widthMm, result.heightMm)))
    png.toBlob((blob) => blob && download(blob, `${name}-embroidered.png`), 'image/png')
  }

  return (
    <section className="patch" aria-label={title}>
      <nav className="patch__bar" aria-label={noun === 'badges' ? 'Badges' : 'Patches'}>
        <button type="button" className="button button--ghost" ref={back} onClick={onClose}>← All {noun}</button>
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

      <header className="patch__heading">
        <h2>{title}</h2>
        <p className="patch__meta">{[patch.medium, patch.finish, patch.quality].filter(Boolean).join(' · ')}</p>
        <div className={!textile ? 'patch__preview-choice' : 'patch__preview-choice patch__preview-choice--mobile'}>
          <Segmented
            ariaLabel="Preview"
            options={[
              { value: 'vector', label: 'Vector' },
              ...(reference ? [{ value: 'source', label: 'Source overlay' }] : []),
              ...(badge ? [{ value: 'relief', label: '3D relief' }] : []),
              { value: 'embroidered', label: textile ? 'Embroidered' : 'Embroidery adaptation' }
            ]}
            value={preview}
            onChange={setPreview}
          />
        </div>
        {textile && reference && <div className="patch__preview-choice patch__preview-choice--desktop">
          <Segmented ariaLabel="Preview" value={overlay ? 'source' : 'vector'} onChange={setPreview}
            options={[{ value: 'vector', label: 'Vector & embroidery' }, { value: 'source', label: 'Source overlay' }]} />
        </div>}
      </header>
      <div className="patch__body">
        <div className={`patch__stages${!textile || overlay ? ' patch__stages--single' : ''}`} data-preview={preview}>
          {overlay && <SourceOverlay key={patch.id} record={reference} drawing={drawing} title={title} />}
          {badge && preview === 'relief' && <BadgeRelief key={patch.id} drawing={drawing} patch={patch} title={title} />}
          {!overlay && (textile || preview === 'vector') && (
            <figure className="patch__stage patch__stage--vector">
              <figcaption>Vector</figcaption>
              <img src={drawing?.url ?? patch.previewUrl} alt={title} />
            </figure>
          )}
          {embroidery && (
            <figure className="patch__stage patch__stage--embroidered" aria-busy={!failed && !result}>
              <figcaption>{textile ? 'Embroidered' : 'Embroidery adaptation'}</figcaption>
              {result
                ? <canvas ref={canvas} aria-label={`${title}, embroidered`} role="img" />
                : !failed && <p className="patch__status" role="status">Sewing…</p>}
              {stitchJob?.failed && <p className="patch__status" role="alert">Embroidery preview failed. {retry}</p>}
            </figure>
          )}
        </div>

        <aside className="patch__panel">
          {badge && preview === 'relief' && <p className="patch__more">The front surface is modeled from the artwork and source photographs. Depth and finish are approximate.</p>}
          {drawing?.failed && <p className="patch__status" role="alert">The vector drawing couldn’t load. {retry}</p>}
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
          {embroidery && (
            <>
              <Segmented label="Width" options={SIZES} value={widthMm} onChange={setWidthMm} compact />
              <Segmented label="Edge" options={BORDERS} value={border} onChange={setBorder} compact />
              <Segmented label="Thread" options={FINISHES} value={finish} onChange={setFinish} compact />

              {result && (
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
            </>
          )}
          <div className="patch__exports">
            {embroidery && (
              <>
                <button type="button" className="button button--primary" disabled={!result} onClick={exportPng}>PNG</button>
                <button type="button" className="button" disabled={!result} onClick={() => download(new Blob([writeDst(result, name)]), `${name}.dst`)} title="Tajima machine file">DST</button>
                <button type="button" className="button" disabled={!result} onClick={() => download(new Blob([writeExp(result)]), `${name}.exp`)} title="Melco machine file">EXP</button>
              </>
            )}
            {drawing?.url
              ? <a className="button" href={drawing.url} download={`${name}.svg`}>SVG</a>
              : <button type="button" className="button" disabled>SVG</button>}
          </div>
          {embroidery && <p className="patch__more">
            <a href={`${PATCHER_URL}?patch=${encodeURIComponent(patch.id)}`} target="_blank" rel="noreferrer">Open in Patcher</a> for
            stitch density, thread charts and the sew-out.
          </p>}

          {!reference && <p className="patch__source">No individual source crop is available for this design.</p>}
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
            {photos.length <= 1 && patch.sourceUrl && <> · <a href={patch.sourceUrl} target="_blank" rel="noreferrer">source reference</a></>}
          </p>
          {photos.length > 1 && (
            <p className="patch__source">
              Seen {patch.sightings.length} times in {photos.length} sources:{' '}
              {photos.map(({ photo, sourceUrl, ids }, index) => (
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
