// The Download panel for BC Hydro's marks: the generator's formats, for artwork drawn by BC Hydro's
// own renderers rather than the lockup's.
//
// Whatever is drawn arrives through `draw`, which returns an SVG and the view box it covers, so the
// 1961 signature, the 1990 mark and the current logo all download the same way.

import { useEffect, useMemo, useRef, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { downloadBlob, EXPORT_FORMAT_ORDER, EXPORT_FORMATS, isFormatSupported, rasterize, renderPdf, SIZE_PRESETS } from '../export/exportLogo.js'

export const saveText = (text, name, type) => downloadBlob(new Blob([text], { type: `${type};charset=utf-8` }), name)

/**
 * @param {object} props
 * @param {(extension: string) => string} props.fileName
 * @param {(options: {outline: boolean, width: number, metadata: boolean}) => {svg: string, view: object}} props.draw
 * @param {boolean} [props.canOutline]       Whether there is live text to outline at all.
 * @param {number} [props.width]             Pixel width, when the caller keeps it.
 * @param {(width: number) => void} [props.onWidth]
 * @param {string} [props.widthNote]
 * @param {(outline: boolean, run: Function) => any} [props.more]  Extra files, under a fold.
 */
export const HydroDownload = ({ fileName, draw, canOutline = false, width: keptWidth, onWidth, widthNote, more }) => {
  const [format, setFormat] = useState('svg')
  const [outline, setOutline] = useState(true)
  const [ownWidth, setOwnWidth] = useState(2048)
  const [status, setStatus] = useState({ message: '', tone: 'info' })
  const [busy, setBusy] = useState(false)
  const alive = useRef(true)
  useEffect(() => {
    alive.current = true
    return () => { alive.current = false }
  }, [])

  const width = keptWidth ?? ownWidth
  const setWidth = onWidth ?? setOwnWidth
  const supported = useMemo(() => Object.fromEntries(EXPORT_FORMAT_ORDER.map((id) => [id, isFormatSupported(id)])), [])
  const spec = EXPORT_FORMATS[format]
  const widths = [...new Set([...SIZE_PRESETS, width])].sort((a, b) => a - b)

  /** Runs one export, reporting what it saved or why it could not. */
  const run = async (task) => {
    setBusy(true)
    setStatus({ message: 'Rendering…', tone: 'info' })
    try {
      const saved = await task()
      if (alive.current) setStatus({ message: saved, tone: 'info' })
    } catch (error) {
      console.error(error)
      if (alive.current) setStatus({ message: error.message || 'The export failed.', tone: 'error' })
    } finally {
      if (alive.current) setBusy(false)
    }
  }

  const download = () => run(async () => {
    const name = fileName(spec.extension)
    if (format === 'svg') {
      saveText(draw({ outline: !canOutline || outline, width, metadata: true }).svg, name, spec.mimeType)
    } else if (format === 'pdf') {
      // Always outlined: the lettering then needs no font for the PDF writer to find.
      const { svg, view } = draw({ outline: true, width, metadata: false })
      downloadBlob(await renderPdf(svg, { viewBox: view }, { outlined: true }), name)
    } else {
      // Outlined for pixels too: an image cannot reach a web font.
      const { svg } = draw({ outline: true, width, metadata: false })
      downloadBlob(await rasterize(svg, { mimeType: spec.mimeType, quality: 0.92, background: spec.alpha ? null : '#ffffff' }), name)
    }
    return `Saved ${name}`
  })

  return (
    <section className="panel">
      <h2>Download</h2>
      <Segmented
        label="Format"
        options={EXPORT_FORMAT_ORDER.map((id) => ({
          value: id,
          label: EXPORT_FORMATS[id].label,
          disabled: !supported[id],
          title: supported[id] ? undefined : `This browser cannot encode ${EXPORT_FORMATS[id].label}`
        }))}
        value={format}
        onChange={(id) => supported[id] && setFormat(id)}
        hint={spec.vector ? 'Vector — scales to any size.' : 'Pixels. Choose a width at least as large as it will ever be shown.'}
      />

      {format === 'svg' && canOutline && (
        <>
          <label className="checkbox">
            <input type="checkbox" checked={outline} onChange={(event) => setOutline(event.target.checked)} />
            <span>Convert text to outlines</span>
          </label>
          <p className="field__note">
            {outline
              ? 'The lettering becomes shapes, the same on every machine. It can no longer be edited as text.'
              : 'The lettering stays live, asking for TeX Gyre Termes, then Nimbus Roman or Times — editable, but only as faithful as the font installed.'}
          </p>
        </>
      )}
      {format === 'svg' && !canOutline && (
        <p className="field__note">Drawn from the supplied artwork, so every letter is already a shape and no font is needed.</p>
      )}
      {!spec.vector && (
        <div className="field">
          <label htmlFor="hydro-width">Width</label>
          <select id="hydro-width" value={width} onChange={(event) => setWidth(Number(event.target.value))}>
            {widths.map((size) => <option key={size} value={size}>{size} px wide</option>)}
          </select>
          {widthNote ? <p className="field__note">{widthNote}</p> : null}
        </div>
      )}

      <div className="field">
        <button type="button" className="button button--primary" onClick={download} disabled={busy}>
          {busy ? 'Rendering…' : `Download ${spec.label}`}
        </button>
        <p className="field__note" style={{ wordBreak: 'break-all' }}>{fileName(spec.extension)}</p>
      </div>

      {more ? more(outline, run) : null}

      <p className="export__status" data-tone={status.tone} role="status" aria-live="polite">{status.message}</p>
    </section>
  )
}
