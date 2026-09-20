// The gallery of one-off marks.
//
// A shelf rather than a set of presets: these marks follow no pattern the generator can offer, so
// there is nothing to load them into. Each still opens for editing — its colours are a choice even
// where its arrangement is not — and each draws itself from the same renderer everything else here
// uses, so a card cannot drift from what it gives you.

import { useState } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { renderFlagSvg } from '../flag/renderFlagSvg.js'
import { FLAG_PALETTE_HINTS, FLAG_PALETTE_LABELS, FLAG_PALETTE_ORDER, FLAG_SWATCHES } from '../flag/flagPalettes.js'
import { ONE_OFFS } from './oneOffs.js'

const PALETTE_OPTIONS = FLAG_PALETTE_ORDER.map((value) => ({
  value, label: FLAG_PALETTE_LABELS[value], title: FLAG_PALETTE_HINTS[value]
}))

const drawing = (entry, colours) => renderFlagSvg({
  ...entry.draw,
  letterColor: colours.ink,
  textColor: colours.ink,
  flagPalette: colours.palette,
  background: colours.background,
  clearSpaceFactor: 0.05
}).svg

const download = (entry, colours, suffix) => {
  const blob = new Blob([drawing(entry, colours)], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `bc-${entry.id}${suffix ? `-${suffix}` : ''}.svg`
  document.body.append(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

/** One mark, opened: its colours editable, its arrangement not. */
const Detail = ({ entry, onClose }) => {
  const [colours, setColours] = useState(entry.presets[0])
  const change = (patch) => setColours((current) => ({ ...current, ...patch }))
  const matches = (preset) => preset.ink === colours.ink &&
    preset.palette === colours.palette && preset.background === colours.background

  return (
    <section className="panel gallery__detail">
      <div className="gallery__head">
        <h2>{entry.label}</h2>
        <button type="button" className="button button--ghost" onClick={onClose}>Back</button>
      </div>
      <p className="gallery__note">{entry.note}</p>

      <div className="gallery__editor">
        <span
          className="gallery__art gallery__art--large"
          role="img"
          aria-label={entry.label}
          // Built here from this project's own artwork; every value is escaped where written.
          dangerouslySetInnerHTML={{ __html: drawing(entry, colours) }}
        />

        <div className="gallery__controls">
          <div className="field">
            <span className="field__label">Start from</span>
            <div className="segmented" role="group" aria-label="Starting colours">
              {entry.presets.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  aria-pressed={matches(preset)}
                  onClick={() => setColours(preset)}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <Segmented
            label="Flag"
            options={PALETTE_OPTIONS}
            value={colours.palette}
            onChange={(palette) => change({ palette })}
            hint={FLAG_PALETTE_HINTS[colours.palette]}
          />
          <ColourField
            label="Ink"
            value={colours.ink}
            onChange={(ink) => change({ ink })}
            palette={FLAG_SWATCHES}
          />
          <ColourField
            label="Background"
            value={colours.background}
            onChange={(background) => change({ background })}
            palette={FLAG_SWATCHES}
            allowTransparent
          />
          <div className="row" style={{ marginTop: 12 }}>
            <button type="button" className="button" onClick={() => download(entry, colours)}>
              Download SVG
            </button>
          </div>
          {entry.caveat && <p className="gallery__caveat">{entry.caveat}</p>}
        </div>
      </div>
    </section>
  )
}

export const GalleryView = () => {
  const [openId, setOpenId] = useState(null)
  const open = ONE_OFFS.find((entry) => entry.id === openId)

  if (open) return <div className="gallery"><Detail entry={open} onClose={() => setOpenId(null)} /></div>

  return (
    <div className="gallery">
      <p className="gallery__intro">
        Marks drawn once, for one body, following no pattern that generalises — so they sit here
        rather than in the generator, which is built on patterns. Open one to recolour it.
      </p>

      {ONE_OFFS.map((entry) => (
        <section key={entry.id} className="panel gallery__entry">
          <div className="gallery__head">
            <h2>{entry.label}</h2>
            <span className="gallery__years">{entry.years}</span>
          </div>
          <p className="gallery__note">{entry.note}</p>

          <button
            type="button"
            className="gallery__pick"
            onClick={() => setOpenId(entry.id)}
            aria-label={`Open ${entry.label}`}
          >
            <span
              className="gallery__art"
              dangerouslySetInnerHTML={{ __html: drawing(entry, entry.presets[0]) }}
            />
            <span className="gallery__label">Open to recolour</span>
          </button>
        </section>
      ))}
    </div>
  )
}
