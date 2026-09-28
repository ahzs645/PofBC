// ICBC's and BCLC's marks, opened from the gallery.
//
// These are shown as supplied (renderSupplied.js): the mark is not recoloured or redrawn, so the
// choices are only where it sits — its ground, its clear space, and, for a mark supplied in a
// reversed version too, which of the two. What the file says of itself is shown beside it, since
// the packages' files each say whether they are supplied paths, a recolour or a reconstruction.

import { useMemo, useState } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { TRANSPARENT } from '../logo/logoColors.js'
import { HydroDownload } from '../hydro/HydroDownload.jsx'
import { CROWN_MARKS } from '../assets/crownMarks.js'
import { isReversed, renderSuppliedSvg } from './renderSupplied.js'

const BACKDROP_OPTIONS = [
  { value: 'auto', label: 'Auto', title: 'Dark when the mark would otherwise vanish' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' }
]

const CLEAR_SPACE_OPTIONS = [
  { value: 0.25, label: 'A quarter', title: 'A quarter of the mark’s shorter side on every side' },
  { value: 0, label: 'None', title: 'For placing the mark into a layout that already keeps its clear space' }
]

/** The grounds offered: white and black, then the colours the marks themselves use. */
const GROUND_SWATCHES = [
  { name: 'white', value: '#ffffff' },
  { name: 'ICBC blue (declared recolour)', value: '#00aeef' },
  { name: 'ICBC orange (as supplied)', value: '#f37224' },
  { name: 'BCLC purple', value: '#9936d2' },
  { name: 'BCLC ink', value: '#28222a' },
  { name: 'black', value: '#000000' }
]

/**
 * @param {object} props
 * @param {object} props.entry  A gallery entry of kind 'supplied'.
 */
export const SuppliedMarkView = ({ entry }) => {
  const [version, setVersion] = useState(entry.mark)
  const [background, setBackground] = useState(TRANSPARENT)
  const [clearSpace, setClearSpace] = useState(0.25)
  const [backdrop, setBackdrop] = useState('auto')
  const mark = CROWN_MARKS[version]

  const draw = (width) => renderSuppliedSvg({ id: version, background, clearSpace, width, title: `${entry.label} — ${mark.title}` })
  const { svg } = useMemo(() => draw(1200), [version, background, clearSpace])
  const transparent = background === TRANSPARENT
  const shownOn = backdrop !== 'auto' ? backdrop : transparent && isReversed(version) ? 'dark' : 'light'

  const versions = entry.reverse && [
    { value: entry.mark, label: 'As supplied' },
    { value: entry.reverse, label: 'Reversed', title: 'The same paths in white, supplied for dark grounds' }
  ]

  return (
    <div className="hydro">
      <div className="gallery__head hydro__head">
        <div>
          <h2>{entry.label} <span className="gallery__years">{entry.years}</span></h2>
          <p className="gallery__note">{entry.note}</p>
        </div>
      </div>

      <div className="layout">
        <section className="stage" aria-label="Preview">
          <div
            className="stage__frame"
            data-backdrop={shownOn}
            data-transparent={transparent || undefined}
            role="img"
            aria-label={entry.label}
            // Built by this project's own renderer from the supplied artwork; values are escaped.
            dangerouslySetInnerHTML={{ __html: svg }}
          />
          <div className="stage__bar">
            <Segmented compact label="Preview on" options={BACKDROP_OPTIONS} value={backdrop} onChange={setBackdrop} />
          </div>
          <div className="contrast-list hydro__rules" aria-live="polite">
            <p className="contrast" data-level="pass">
              <span className="contrast__surface">As supplied</span>
              <span className="contrast__message">
                Drawn exactly as the research package’s file has it, so it is not recoloured here. The file
                calls itself “{mark.title}”. {mark.description}
              </span>
            </p>
          </div>
        </section>

        <div className="controls">
          {versions && (
            <section className="panel">
              <h2>Version</h2>
              <Segmented label="Version" options={versions} value={version} onChange={setVersion} />
            </section>
          )}

          <section className="panel">
            <h2>Placement</h2>
            <ColourField label="Background" value={background} onChange={setBackground} palette={GROUND_SWATCHES} allowTransparent />
            <Segmented
              label="Clear space"
              options={CLEAR_SPACE_OPTIONS}
              value={clearSpace}
              onChange={setClearSpace}
              hint="Neither body’s clear-space rule was supplied, so this is a margin, not a standard."
            />
          </section>

          <HydroDownload fileName={(extension) => `${version}.${extension}`} draw={({ width }) => draw(width)} />
        </div>
      </div>
    </div>
  )
}
