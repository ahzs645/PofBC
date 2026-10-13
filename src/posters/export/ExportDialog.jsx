// The export dialog: any of the provided targets, any format, any size.
//
// `targets` is [{ id, label, getSvg: async (opts) => string, inches: {w, h} | (aspect) => {w, h},
// widths: [px], backgrounds?: [{ name, value }], fileName: (spec, width, bg) => string }].

import { useEffect, useMemo, useState } from 'react'
import { Dialog } from '../ui/Dialog.jsx'
import { Segmented } from '../ui/Segmented.jsx'
import { FORMATS, FORMAT_ORDER, downloadBlob, exportSvg, formatBytes, isFormatSupported } from './exportSvg.js'

const aspectOf = (svg) => {
  const vb = /viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"/.exec(svg)
  return vb ? +vb[4] / +vb[3] : 1
}

export function ExportDialog({ open, onClose, targets, target, onTarget, dpiBase }) {
  const [format, setFormat] = useState('pdf')
  const [width, setWidth] = useState(null)
  const [background, setBackground] = useState(null)
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState(null)

  const supported = useMemo(() => Object.fromEntries(FORMAT_ORDER.map((f) => [f, isFormatSupported(f)])), [])
  const spec = FORMATS[format]
  const t = targets.find((x) => x.id === target) ?? targets[0]

  useEffect(() => {
    if (!open) return
    setStatus(null)
    setWidth(t.widths[Math.min(1, t.widths.length - 1)])
    setBackground(t.backgrounds?.[0]?.value ?? null)
  }, [open, t])

  const fileName = t.fileName(spec, spec.vector ? null : width, background)

  const run = async () => {
    setBusy(true)
    setStatus(null)
    try {
      const svg = await t.getSvg({ background })
      const inches = typeof t.inches === 'function' ? t.inches(aspectOf(svg)) : t.inches
      const bg = background ?? (spec.alpha ? null : '#ffffff')
      const blob = await exportSvg(svg, { format, width, inches, background: bg })
      downloadBlob(blob, fileName)
      setStatus({ ok: true, text: `Saved ${fileName} (${formatBytes(blob.size)}).` })
    } catch (error) {
      setStatus({ ok: false, text: error.message || String(error) })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} title="Export">
      {targets.length > 1 && (
        <Segmented wide label="What to export" value={t.id} onChange={onTarget} options={targets.map((x) => ({ value: x.id, label: x.label }))} />
      )}

      <div className="pv-control">
        <span className="pv-control-label">Format</span>
        <div className="pv-formats">
          {FORMAT_ORDER.map((f) => (
            <button key={f} type="button" className="pv-format-btn" aria-pressed={format === f} disabled={!supported[f]} title={supported[f] ? FORMATS[f].note : 'This browser cannot encode this format'} onClick={() => setFormat(f)}>
              <b>{FORMATS[f].label}</b>
              <span>{FORMATS[f].note}</span>
            </button>
          ))}
        </div>
      </div>

      {!spec.vector && (
        <div className="pv-control">
          <span className="pv-control-label">Width</span>
          <Segmented wrap label="Pixel width" value={width} onChange={setWidth} options={t.widths.map((w) => ({
            value: w, label: `${w} px`, extra: t.dpiBase ? `${Math.round(w / t.dpiBase)} dpi` : undefined
          }))} />
          {t.largeNote && width >= t.largeNote.from && <p className="pv-dialog-note">{t.largeNote.text}</p>}
          {t.backgrounds && (
            <Segmented wrap label="Background" value={background} onChange={setBackground} style={{ marginTop: 8 }} options={t.backgrounds.map((b) => ({
              value: b.value, label: b.name, disabled: b.value === null && !spec.alpha
            }))} />
          )}
        </div>
      )}

      {spec.vector && t.vectorNote && <p className="pv-dialog-note">{t.vectorNote(format)}</p>}

      <div className="pv-dialog-foot">
        <code className="pv-file-name">{fileName}</code>
        <button type="button" className="pv-link-btn pv-primary" disabled={busy} onClick={run}>{busy ? 'Working…' : 'Download'}</button>
      </div>
      {status && <p className={`pv-status ${status.ok ? 'pv-ok' : 'pv-err'}`} role="status">{status.text}</p>}
    </Dialog>
  )
}
