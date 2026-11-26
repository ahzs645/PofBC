// The Crown corporations' and agencies' supplied marks, opened from the gallery.
//
// These are shown as supplied (renderSupplied.js): the mark is not recoloured or redrawn, so the
// choices are only where it sits — its ground, its clear space, and, for a mark supplied in a
// reversed version too, which of the two. What the file says of itself is shown beside it, since
// the packages' files each say whether they are supplied paths, a recolour or a reconstruction.

import { PreviewBackground } from '../gallery/PreviewBackground.jsx'
import { useMemo, useState } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { TRANSPARENT } from '../logo/logoColors.js'
import { useSiteTheme } from '../site/useTheme.js'
import { HydroDownload } from '../hydro/HydroDownload.jsx'
import { CROWN_MARKS } from '../assets/crownMarks.js'
import { isReversed, renderSuppliedSvg } from './renderSupplied.js'
import { suppliedPreviewFile } from './tileArt.js'

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
  { name: 'Recreation and Conservation report paper (scan approximation)', value: '#e3e0cb' },
  { name: 'Recreation and Conservation report dark (scan approximation)', value: '#0c1c1b' },
  { name: 'black', value: '#000000' }
]

/**
 * @param {object} props
 * @param {object} props.entry  A gallery entry of kind 'supplied'.
 */
export const SuppliedMarkView = ({ entry, family, onChooseVersion }) => {
  const { name: theme } = useSiteTheme()
  const [chosenVersion, setVersion] = useState(null)
  const [background, setBackground] = useState(TRANSPARENT)
  const [clearSpace, setClearSpace] = useState(0.25)
  const [backdrop, setBackdrop] = useState('auto')
  const version = chosenVersion ?? (theme === 'dark' && backdrop !== 'light' && entry.reverse ? entry.reverse : entry.mark)
  const mark = CROWN_MARKS[version]

  const transparent = background === TRANSPARENT
  const followsTheme = entry.themedPreview && version === entry.mark
  const shownOn = backdrop !== 'auto' ? backdrop
    : transparent && (version === entry.reverse || isReversed(version) || (followsTheme && theme === 'dark')) ? 'dark' : 'light'
  const previewFile = transparent ? suppliedPreviewFile(entry, version, shownOn) : undefined
  const draw = (width, displayFile) => renderSuppliedSvg({
    id: version, background, clearSpace, width, title: `${entry.label}: ${mark.title}`, previewFile: displayFile
  })
  const { svg } = useMemo(() => draw(1200, previewFile), [version, background, clearSpace, previewFile])

  // A mark supplied in other inks too (the Recreation and Conservation symbols' report greens)
  // offers each as a version: the same paths, in a colour the package itself supplied.
  const alternates = entry.alternates ?? []
  const versions = (entry.reverse || alternates.length > 0) && [
    { value: entry.mark, label: entry.markLabel ?? 'As supplied' },
    ...alternates.map(({ mark: value, label, title }) => ({ value, label, title })),
    ...(entry.reverse ? [{ value: entry.reverse, label: 'Reversed', title: 'The same paths in white, supplied for dark grounds' }] : [])
  ]

  return (
    <div className="hydro">
      <div className="gallery__head hydro__head">
        <div>
          <h2>{family?.label ?? entry.label} <span className="gallery__years">{entry.years}</span></h2>
          <p className="gallery__note">{entry.note}</p>
        </div>
      </div>

      <div className="layout">
        <section className="stage" aria-label="Preview">
          <PreviewBackground white={backdrop === 'light'} onToggle={() => setBackdrop(backdrop === 'light' ? 'auto' : 'light')}>
            <div
              className="stage__frame"
              data-backdrop={shownOn}
              data-transparent={transparent || undefined}
              role="img"
              aria-label={entry.label}
              // Built by this project's own renderer from the supplied artwork; values are escaped.
              dangerouslySetInnerHTML={{ __html: svg }}
            />
          </PreviewBackground>
          <div className="stage__bar">
            <Segmented compact label="Preview on" options={BACKDROP_OPTIONS} value={backdrop} onChange={setBackdrop} />
          </div>
          <div className="contrast-list hydro__rules" aria-live="polite">
            <p className="contrast" data-level="pass">
              <span className="contrast__surface">{followsTheme ? 'Reconstruction' : 'As supplied'}</span>
              <span className="contrast__message">
                {followsTheme
                  ? <>{mark.description} {previewFile && shownOn === 'dark' && entry.darkPreviewNote}</>
                  : <>Drawn exactly as the research package’s file has it, so it is not recoloured here. The file
                    calls itself “{mark.title}”. {mark.description}</>}
              </span>
            </p>
          </div>
        </section>

        <div className="controls">
          {family?.editorVersions && <section className="panel">
            <h2>Version</h2>
            <Segmented label="Version" options={family.editorVersions.map(({ id, label }) => ({ value: id, label }))}
              value={entry.id} onChange={onChooseVersion} />
          </section>}
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
              hint="No clear-space rule was supplied with these marks, so this is a margin, not a standard."
            />
          </section>

          <HydroDownload fileName={(extension) => `${version}.${extension}`} draw={({ width }) => draw(width)} />
        </div>
      </div>
    </div>
  )
}
