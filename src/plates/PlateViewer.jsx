// One licence plate: drawn large by PlateForge's renderer, with its serial and appearance fields to
// edit, its era and sources, and SVG and PNG downloads. Editing here is for looking; the full editor
// (lettering, decals, batches) is a link away in PlateForge.

import { useEffect, useMemo, useRef, useState } from 'react'
import {
  PlateView, createRng, download, exportName, exportPlate, formatPeriod, makePlate, plateforgeLink,
  researchDiesEnabled, samplePlate, setResearchDiesEnabled, statusBadge, useResearchDiesVersion
} from 'plateforge'

/** A fresh serial, keeping the fields a format marks as appearance (finish, decal, palette…). */
const regenerate = (format, parts) => {
  const next = format.generate(createRng())
  for (const field of format.fields) if (field.preserveOnGenerate && parts[field.key] !== undefined) next[field.key] = parts[field.key]
  return next
}

const Field = ({ field, value, onChange }) => {
  const id = `plate-field-${field.key}`
  if (field.options) {
    return (
      <div className="plate__field">
        <label htmlFor={id}>{field.label}</label>
        <select id={id} value={value ?? ''} onChange={(event) => onChange(event.target.value)}>
          {field.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
    )
  }
  if (field.input === 'color') {
    return (
      <div className="plate__field plate__field--inline">
        <label htmlFor={id}>{field.label}</label>
        <input id={id} type="color" value={value || '#000000'} onChange={(event) => onChange(event.target.value)} />
      </div>
    )
  }
  if (field.input === 'range') {
    return (
      <div className="plate__field">
        <label htmlFor={id}>{field.label} <span className="plate__value">{value}</span></label>
        <input id={id} type="range" min={field.min} max={field.max} step={field.step} value={value ?? ''} onChange={(event) => onChange(event.target.value)} />
      </div>
    )
  }
  return (
    <div className="plate__field">
      <label htmlFor={id}>{field.label}</label>
      <input
        id={id}
        type="text"
        value={value ?? ''}
        maxLength={field.maxLength}
        placeholder={field.placeholder}
        spellCheck={false}
        autoComplete="off"
        onChange={(event) => onChange(field.uppercase === false ? event.target.value : event.target.value.toUpperCase())}
      />
    </div>
  )
}

/**
 * @param {object} props
 * @param {object} props.region     The PlateForge region (British Columbia).
 * @param {object} props.format     The design on screen.
 * @param {object} props.family     Its family ({ id, label, summary }).
 * @param {object} [props.section]  Its era, as a gallery section ({ label, period, summary }).
 * @param {{ index: number, count: number }} props.position  Where it sits in its family.
 * @param {object|null} props.previous
 * @param {object|null} props.next
 * @param {(format: object) => void} props.onOpen
 * @param {() => void} props.onClose
 */
export const PlateViewer = ({ region, format, family, section, position, previous, next, onOpen, onClose }) => {
  // Opens on the same sample its card shows, so the plate does not change on the way in.
  const [parts, setParts] = useState(() => ({ ...samplePlate(region, format).parts }))
  const [status, setStatus] = useState(null)
  const stage = useRef(null)
  useResearchDiesVersion()

  const plate = useMemo(() => makePlate(region, format, parts), [region, format, parts])
  const invalid = format.validate?.(parts) ?? null
  const badge = statusBadge(format)

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

  const save = async (kind) => {
    const svg = stage.current?.querySelector('svg')
    if (!svg) return
    setStatus({ busy: true, text: `Preparing the ${kind.toUpperCase()}…` })
    try {
      download(await exportPlate(svg, plate, kind), exportName(plate, kind))
      setStatus(null)
    } catch (error) {
      console.error(error)
      setStatus({ text: error instanceof Error ? error.message : 'The export failed.' })
    }
  }

  return (
    <section className="plate" aria-label={format.label}>
      <nav className="plate__bar" aria-label="Licence plates">
        <button type="button" className="button button--ghost" onClick={onClose}>← All plates</button>
        <span className="plate__crumb">{family.label}{section?.label && ` · ${section.label}`} · {position.index + 1} of {position.count}</span>
        <span className="plate__steps">
          <button type="button" className="button" disabled={!previous} onClick={() => onOpen(previous)} title={previous?.label} aria-label="Previous">
            <span aria-hidden="true">‹</span><span className="plate__step-label"> Previous</span>
          </button>
          <button type="button" className="button" disabled={!next} onClick={() => onOpen(next)} title={next?.label} aria-label="Next">
            <span className="plate__step-label">Next </span><span aria-hidden="true">›</span>
          </button>
        </span>
      </nav>

      <div className="plate__body">
        <figure className="plate__stage">
          <div ref={stage} className="plate__art-frame" role="img" aria-label={`${format.label}${plate.text ? `, ${plate.text}` : ''}`}>
            <PlateView plate={plate} className="plate__art" />
          </div>
        </figure>

        <aside className="plate__panel">
          <h2>{format.label}</h2>
          <p className="plate__meta">
            {format.period && formatPeriod(format.period)}
            {format.pattern && <> · <span className="plate__pattern">{format.pattern}</span></>}
            {badge && <span className="plates__status">{badge}</span>}
          </p>

          <div className="plate__fields">
            {format.fields.map((field) => (
              <Field key={field.key} field={field} value={parts[field.key]} onChange={(value) => setParts((current) => ({ ...current, [field.key]: value }))} />
            ))}
          </div>
          {invalid && <p className="plate__invalid" role="alert">{invalid}</p>}
          <button type="button" className="button" onClick={() => setParts((current) => regenerate(format, current))}>New serial</button>

          <div className="plate__exports">
            <button type="button" className="button button--primary" disabled={!!invalid || status?.busy} onClick={() => save('png')}>PNG</button>
            <button type="button" className="button" disabled={!!invalid || status?.busy} onClick={() => save('svg')}>SVG</button>
          </div>
          {status && <p className="plate__note" role="status">{status.text}</p>}

          <label className="plate__toggle">
            <input type="checkbox" checked={researchDiesEnabled()} onChange={(event) => setResearchDiesEnabled(event.target.checked)} />
            Research lettering
          </label>
          <p className="plate__note">
            Letters traced from source photographs where they were seen; the rest use PlateForge’s earlier dies. Unvalidated candidates.
          </p>

          <p className="plate__more">
            <a href={plateforgeLink(region, format)} target="_blank" rel="noreferrer">Open in PlateForge</a> for lettering,
            decals, batches and the rest of its timeline.
          </p>

          {section?.summary && (
            <div className="plate__era">
              <h3>{section.label}{section.period && <span className="plate__era-period">{section.period}</span>}</h3>
              <p>{section.summary}</p>
            </div>
          )}
          {format.description && <p className="plate__description">{format.description}</p>}
          {format.references?.length > 0 && (
            <div className="plate__sources">
              <h3>Sources</h3>
              <ul>
                {format.references.map((reference) => (
                  <li key={reference.url}><a href={reference.url} target="_blank" rel="noreferrer">{reference.title}</a></li>
                ))}
              </ul>
            </div>
          )}
          {region.notes && (
            <details className="plate__limits">
              <summary>About these reconstructions</summary>
              <p>{region.notes}</p>
            </details>
          )}
        </aside>
      </div>
    </section>
  )
}
