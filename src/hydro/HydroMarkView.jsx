// BC Hydro's 1990 and current marks, opened from the gallery, in the generator's layout.
//
// The two take opposite approaches to colour. The 1990 mark is history: every part is yours to
// colour, as the Province's one-offs are. The current logo is BC Hydro's in use today, and its
// guidelines allow only the variations they give — so those are what it offers, drawn from BC
// Hydro's own artwork, with the background and clear space the only choices left.

import { useMemo, useState } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { TRANSPARENT, isLightColor } from '../logo/logoColors.js'
import { HydroDownload } from './HydroDownload.jsx'
import {
  CURRENT_VARIANT_ORDER, CURRENT_VARIANTS, HYDRO_PALETTE_SWATCHES, MARK_1990_PARTS, MARK_1990_PRESETS,
  renderCurrentHydroSvg, renderHydroMarkSvg
} from './hydroMarks.js'

const BACKDROP_OPTIONS = [
  { value: 'auto', label: 'Auto', title: 'Dark when the mark would otherwise vanish' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' }
]

const clearSpaceOptions = (current) => [
  { value: 'symbol', label: current ? 'One symbol (guidelines)' : 'One symbol', title: 'A symbol’s width on every side' },
  { value: 'none', label: 'None' }
]

const Notes = ({ notes }) => (
  <div className="contrast-list hydro__rules" aria-live="polite">
    {notes.map((note) => (
      <p key={note.text} className="contrast" data-level={note.level}>
        <span className="contrast__surface">{note.title}</span>
        <span className="contrast__message">{note.text}</span>
      </p>
    ))}
  </div>
)

/** The view's frame: a heading, the stage with its backdrop control, and the panels beside it. */
const Frame = ({ years, title, note, onClose, svg, label, transparent, lightInk, notes, children }) => {
  const [backdrop, setBackdrop] = useState('auto')
  const shownOn = backdrop !== 'auto' ? backdrop : transparent && lightInk ? 'dark' : 'light'

  return (
    <div className="hydro">
      <div className="gallery__head hydro__head">
        <div>
          <h2>{title} <span className="gallery__years">{years}</span></h2>
          <p className="gallery__note">{note}</p>
        </div>
        {onClose && <button type="button" className="button button--ghost" onClick={onClose}>Back to the gallery</button>}
      </div>

      <div className="layout">
        <section className="stage" aria-label="Preview">
          <div
            className="stage__frame"
            data-backdrop={shownOn}
            data-transparent={transparent || undefined}
            role="img"
            aria-label={label}
            // Built by this project's own renderer from the supplied artwork; values are escaped.
            dangerouslySetInnerHTML={{ __html: svg }}
          />
          <div className="stage__bar">
            <Segmented compact label="Preview on" options={BACKDROP_OPTIONS} value={backdrop} onChange={setBackdrop} />
          </div>
          <Notes notes={notes} />
        </section>

        <div className="controls">{children}</div>
      </div>
    </div>
  )
}

/** The current logo: its variations, and where it is put. */
const CurrentView = ({ initialVariant = 'colour', onClose }) => {
  const [variant, setVariant] = useState(CURRENT_VARIANTS[initialVariant] ? initialVariant : 'colour')
  const [background, setBackground] = useState(CURRENT_VARIANTS[variant].background)
  const [clearSpace, setClearSpace] = useState('symbol')
  const spec = CURRENT_VARIANTS[variant]
  const pick = (next) => {
    setVariant(next)
    setBackground(CURRENT_VARIANTS[next].background)
  }

  const { svg } = useMemo(() => renderCurrentHydroSvg({ variant, background, clearSpace, width: 1200 }), [variant, background, clearSpace])
  const transparent = background === TRANSPARENT
  const lightInk = variant === 'reverse'

  const notes = [{ level: 'pass', title: spec.label, text: spec.hint }]
  // The guidelines say what each variation is for; say so when the ground is not that.
  const onWhite = ['colour', 'black', 'signage', 'symbol'].includes(variant)
  if (!transparent && onWhite && background.toLowerCase() !== '#ffffff') {
    notes.push({ level: 'warn', title: 'Check', text: 'This variation is for a white background. On colour, or anything busy, the guidelines use the reverse logo or the symbol with its border.' })
  }
  if (!transparent && variant === 'reverse' && isLightColor(background)) {
    notes.push({ level: 'fail', title: 'Breaks a rule', text: 'The reverse logo is for colourful, dark or busy backgrounds; on a light one it all but disappears.' })
  }
  notes.push({
    level: 'pass',
    title: 'Clear space',
    text: 'The guidelines use the symbol as the clear-space guide: nothing is placed within one symbol’s width of the logo.'
  })
  notes.push({
    level: 'pass',
    title: 'As supplied',
    text: 'Drawn from BC Hydro’s own artwork in its February 2020 brand guidelines. The logo is not to be reconfigured, recoloured, distorted or reset in another font, so only its own variations are offered.'
  })

  return (
    <Frame
      years="2016–present"
      title="BC Hydro"
      note="The logo in use today: the symbol turned into a circle and moved to the left, “BC Hydro” in a contemporary sans, and the “Power smart” tagline."
      onClose={onClose}
      svg={svg}
      label={`BC Hydro logo — ${spec.label}`}
      transparent={transparent}
      lightInk={lightInk}
      notes={notes}
    >
      <section className="panel">
        <h2>Logo</h2>
        <div className="layouts hydro__picker" role="group" aria-label="Variation">
          {CURRENT_VARIANT_ORDER.map((id) => (
            <button key={id} type="button" aria-pressed={id === variant} onClick={() => pick(id)} title={CURRENT_VARIANTS[id].hint}>
              <span
                aria-hidden="true"
                dangerouslySetInnerHTML={{ __html: renderCurrentHydroSvg({ variant: id, clearSpace: 1 / 3, width: 240 }).svg }}
              />
              {CURRENT_VARIANTS[id].label}
            </button>
          ))}
        </div>
        <p className="field__note">{spec.hint}</p>
      </section>

      <section className="panel">
        <h2>Placement</h2>
        <ColourField label="Background" value={background} onChange={setBackground} palette={HYDRO_PALETTE_SWATCHES} allowTransparent />
        <Segmented
          label="Clear space"
          options={clearSpaceOptions(true)}
          value={clearSpace}
          onChange={setClearSpace}
          hint={clearSpace === 'symbol'
            ? 'The guidelines’ clear space. The background fills it.'
            : 'For placing the logo into a layout that already keeps its clear space.'}
        />
      </section>

      <HydroDownload
        fileName={(extension) => `bc-hydro-${variant}.${extension}`}
        draw={({ width }) => renderCurrentHydroSvg({ variant, background, clearSpace, width })}
      />
    </Frame>
  )
}

/** The 1990 mark: history, so every part can be coloured. */
const View1990 = ({ onClose }) => {
  const [colours, setColours] = useState(MARK_1990_PRESETS[0].colours)
  const [clearSpace, setClearSpace] = useState('symbol')
  const change = (patch) => setColours((current) => ({ ...current, ...patch }))
  const draw = (width) => renderHydroMarkSvg({ id: 'bc-hydro-1990', colours, background: colours.background, clearSpace, width, title: 'BC hydro, 1990' })
  const { svg } = useMemo(() => draw(1400), [colours, clearSpace])
  const transparent = colours.background === TRANSPARENT
  const lightInk = MARK_1990_PARTS.every(({ role }) => isLightColor(colours[role]))

  return (
    <Frame
      years="1990–2016"
      title="BC hydro"
      note="“BC” and “hydro” in a heavy slab, with the symbol squared off and set after the name — the mark the 2016 logo rounded and moved to the front."
      onClose={onClose}
      svg={svg}
      label="BC hydro, 1990"
      transparent={transparent}
      lightInk={lightInk}
      notes={[
        { level: 'pass', title: 'As supplied', text: 'Drawn from the supplied Illustrator artwork, shape for shape. Only the colours are chosen here.' },
        { level: 'pass', title: 'Colours', text: 'The supplied green and light blue are the file’s own; no colour specification for this mark was supplied.' }
      ]}
    >
      <section className="panel">
        <h2>Colour</h2>
        <Segmented
          label="Start from"
          options={MARK_1990_PRESETS.map(({ id, label }) => ({ value: id, label }))}
          value={MARK_1990_PRESETS.find((preset) => JSON.stringify(preset.colours) === JSON.stringify(colours))?.id}
          onChange={(id) => setColours(MARK_1990_PRESETS.find((preset) => preset.id === id).colours)}
        />
        {MARK_1990_PARTS.map(({ label, role }) => (
          <ColourField key={role} label={label} value={colours[role]} onChange={(value) => change({ [role]: value })} palette={HYDRO_PALETTE_SWATCHES} />
        ))}
        <ColourField
          label="Background"
          value={colours.background}
          onChange={(background) => change({ background })}
          palette={HYDRO_PALETTE_SWATCHES}
          allowTransparent
        />
      </section>

      <section className="panel">
        <h2>Placement</h2>
        <Segmented label="Clear space" options={clearSpaceOptions(false)} value={clearSpace} onChange={setClearSpace} hint="Measured in the symbol, as the later guidelines do; the 1990 mark’s own rule was not supplied." />
      </section>

      <HydroDownload fileName={(extension) => `bc-hydro-1990.${extension}`} draw={({ width }) => draw(width)} />
    </Frame>
  )
}

/**
 * @param {object} props
 * @param {'1990'|'current'} props.mark
 * @param {string} [props.variant]  For the current logo: the variation to open on.
 * @param {() => void} props.onClose
 */
export const HydroMarkView = ({ mark, variant, onClose }) => mark === '1990'
  ? <View1990 onClose={onClose} />
  : <CurrentView initialVariant={variant} onClose={onClose} />
