// Downloading the lockup, one file at a time or as a set.
//
// Formats the browser cannot encode are detected up front and disabled rather than offered and
// then quietly substituted — Safari's long-missing WebP encoder is the classic case.

import { useEffect, useMemo, useRef, useState } from 'react'
import {
  EXPORT_FORMATS,
  EXPORT_FORMAT_ORDER,
  SIZE_PRESETS,
  buildFileName,
  exportLogo,
  isFormatSupported
} from '../export/exportLogo.js'
import { BUNDLE_DEFAULTS, bundleName, exportBundle, planBundle } from '../export/exportBundle.js'
import { LAYOUTS, LAYOUT_ORDER } from '../logo/layouts.js'
import { MultiToggle } from './MultiToggle.jsx'
import { Segmented } from './Segmented.jsx'

const MODES = [
  { value: 'single', label: 'One file' },
  { value: 'bundle', label: 'Bundle' }
]

const LAYOUT_OPTIONS = LAYOUT_ORDER.map((value) => ({
  value,
  label: LAYOUTS[value].label,
  title: LAYOUTS[value].description
}))

const SIZE_OPTIONS = SIZE_PRESETS.map((value) => ({ value, label: `${value}px` }))

export const ExportPanel = ({ lockup, era = 'historical' }) => {
  const [mode, setMode] = useState('single')
  const [format, setFormat] = useState('svg')
  const [pixelWidth, setPixelWidth] = useState(2048)
  const [outlineText, setOutlineText] = useState(false)
  const [layouts, setLayouts] = useState(BUNDLE_DEFAULTS.layouts)
  const [formats, setFormats] = useState(BUNDLE_DEFAULTS.formats)
  const [sizes, setSizes] = useState(BUNDLE_DEFAULTS.sizes)
  const [status, setStatus] = useState({ message: '', tone: 'info' })
  const [busy, setBusy] = useState(false)
  const alive = useRef(true)

  // Set on the way in as well as cleared on the way out. React mounts, unmounts and remounts
  // effects under StrictMode, so a ref that is only ever cleared stays false for the rest of the
  // session — and every later export would finish without ever re-enabling the button.
  useEffect(() => {
    alive.current = true
    return () => { alive.current = false }
  }, [])

  // Probed once: it touches the DOM, and the answer cannot change during a session.
  const supported = useMemo(
    () => Object.fromEntries(EXPORT_FORMAT_ORDER.map((id) => [id, isFormatSupported(id)])),
    []
  )

  const formatOptions = useMemo(
    () => EXPORT_FORMAT_ORDER
      .filter((id) => supported[id])
      .map((id) => ({ value: id, label: EXPORT_FORMATS[id].label })),
    [supported]
  )

  const spec = EXPORT_FORMATS[format]
  const isRaster = !spec.vector
  const bundling = mode === 'bundle'
  // The current era's artwork is already outlined — the wording is drawn, not set — so there is
  // nothing to convert and no font to embed.
  const canOutline = era !== 'current'

  const bundleHasRaster = formats.some((id) => !EXPORT_FORMATS[id].vector)
  const bundleHasVector = formats.some((id) => EXPORT_FORMATS[id].vector)

  // Clear space travels with the lockup, so the export is whatever the preview is showing.
  // Outlining only changes how a vector file draws its type; a raster export has been through a
  // rasteriser either way, so the request is dropped rather than quietly named in the filename.
  const singleOptions = { ...lockup, format, pixelWidth, outlineText: canOutline && outlineText && spec.vector }
  const bundleOptions = { ...lockup, layouts, formats, sizes, outlineText: canOutline && outlineText && bundleHasVector }

  const plan = useMemo(() => (bundling ? planBundle(bundleOptions) : []), [
    bundling, layouts, formats, sizes, lockup
  ])

  const fileName = bundling
    ? `${bundleName(lockup)}-logos.zip`
    : buildFileName({ ...singleOptions, format })

  const download = async () => {
    setBusy(true)
    setStatus({ message: bundling ? `Rendering 0 of ${plan.length}…` : 'Rendering…', tone: 'info' })

    try {
      const saved = bundling
        ? await exportBundle(bundleOptions, ({ completed, total }) => {
            if (alive.current) setStatus({ message: `Rendering ${completed} of ${total}…`, tone: 'info' })
          })
        : await exportLogo(singleOptions)

      if (alive.current) setStatus({ message: `Saved ${saved}`, tone: 'info' })
    } catch (error) {
      console.error(error)
      if (alive.current) setStatus({ message: error.message || 'The export failed.', tone: 'error' })
    } finally {
      if (alive.current) setBusy(false)
    }
  }

  const outlineControl = (
    <>
      <label className="checkbox">
        <input
          type="checkbox"
          checked={outlineText}
          onChange={(event) => setOutlineText(event.target.checked)}
        />
        <span>Convert text to outlines</span>
      </label>
      <p className="field__note">
        {outlineText
          ? 'The type becomes shapes. Nothing depends on the font any more, so it cannot be substituted — this is what a printer usually asks for. It can no longer be edited or selected.'
          : 'The type stays live and selectable, with the font embedded. Keep this unless a printer or another application has asked for outlines.'}
      </p>
    </>
  )

  return (
    <section className="panel">
      <h2>Download</h2>

      <Segmented ariaLabel="Download as" options={MODES} value={mode} onChange={setMode} />

      {bundling ? (
        <>
          {canOutline && (
            <MultiToggle label="Lockups" options={LAYOUT_OPTIONS} value={layouts} onChange={setLayouts} />
          )}
          <MultiToggle label="Formats" options={formatOptions} value={formats} onChange={setFormats} />
          {bundleHasRaster && (
            <MultiToggle
              label="Pixel widths"
              options={SIZE_OPTIONS}
              value={sizes}
              onChange={setSizes}
              hint="Each raster format is rendered once per width."
            />
          )}
          {canOutline && bundleHasVector && outlineControl}
        </>
      ) : (
        <>
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
            hint={
              !spec.vector
                ? 'Pixels. Choose a width at least as large as it will ever be shown.'
                : outlineText
                  ? 'Vector, carrying its own shapes — scales to any size, and needs no font at all.'
                  : 'Vector, with the brand font embedded — scales to any size.'
            }
          />

          {isRaster ? (
            <div className="field">
              <label htmlFor="export-size">Width</label>
              <select
                id="export-size"
                value={pixelWidth}
                onChange={(event) => setPixelWidth(Number(event.target.value))}
              >
                {SIZE_PRESETS.map((size) => <option key={size} value={size}>{size} px wide</option>)}
              </select>
            </div>
          ) : canOutline ? outlineControl : (
            <p className="field__note">
              The official artwork is already outlined — the wording is drawn, not set — so it needs
              no font and nothing to convert.
            </p>
          )}
        </>
      )}

      <div className="field">
        <button type="button" className="button button--primary" onClick={download} disabled={busy || (bundling && !plan.length)}>
          {busy ? 'Rendering…' : bundling ? `Download ${plan.length} files` : `Download ${spec.label}`}
        </button>
        <p className="field__note" style={{ wordBreak: 'break-all' }}>{fileName}</p>
      </div>

      {/* Announced politely so a screen reader hears the result without the download stealing focus. */}
      <p className="export__status" data-tone={status.tone} role="status" aria-live="polite">{status.message}</p>
    </section>
  )
}
