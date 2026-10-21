// The 1977 stationery, filled in: a calling card, letterhead and No. 10 envelope in the B.C.
// Visual Identity Program's General Use format, for any ministry.
//
// The templates are data (bcStationery.js) drawn by brandkit's template engine, in the site's own
// Helvetica (helveticaFonts.js); the studio around them is brandkit's too. What is here is the
// Province's part: the ministry list, and the symbol's two printings.

import { useEffect, useMemo, useState } from 'react'
import { TemplateStudio } from 'brandkit/studio'
import { ALL_GROUPS } from '../site/MinistryField.jsx'
import { SiteLink } from '../site/navigation.jsx'
import { createStationeryBrand, ministryLines, PANTONE_462 } from './bcStationery.js'
import { createHelveticaProvider, loadHelveticaProvider } from './helveticaFonts.js'
import './stationery.css'

const STORE = 'pofbc-stationery'
const INKS = [
  { id: 'brown', label: 'Pantone 462', colour: PANTONE_462, title: 'The specification’s colour for the symbol, as Pantone converts it for screens' },
  { id: 'black', label: 'Black', colour: '#000000', title: 'One colour, for a black-only printing' }
]

const read = () => {
  try { return JSON.parse(localStorage.getItem(STORE) ?? 'null') ?? {} } catch { return {} }
}

export const StationeryView = () => {
  const [saved] = useState(read)
  const [values, setValues] = useState(saved.values ?? {})
  const [ministry, setMinistry] = useState(saved.ministry ?? '')
  const [ink, setInk] = useState(saved.ink ?? 'brown')
  // Measurement works from the committed metrics straight away; the outlines arrive after.
  const [fonts, setFonts] = useState(() => createHelveticaProvider(null))
  useEffect(() => { loadHelveticaProvider().then(setFonts) }, [])
  useEffect(() => { try { localStorage.setItem(STORE, JSON.stringify({ values, ministry, ink })) } catch { /* not kept */ } }, [values, ministry, ink])

  const brand = useMemo(() => createStationeryBrand({ symbolColour: INKS.find((entry) => entry.id === ink).colour }), [ink])
  const chooseMinistry = (name) => {
    setMinistry(name)
    setValues((current) => ({ ...current, ministry: name ? ministryLines(name) : undefined }))
  }

  return (
    <section className="stationery" aria-label="Stationery">
      <div className="stationery__intro">
        <h2>Stationery, 1977</h2>
        <p>
          The Visual Identity Program’s General Use calling card, letterhead and envelope, rebuilt from the
          millimetre grid on the <SiteLink to={{ view: 'guides', guide: 'reproduction', page: 'R08' }}>Reproduction Manual’s specification sheet</SiteLink>.
          Fill in the fields once; every piece uses them.
        </p>
      </div>
      <TemplateStudio
        brand={brand}
        fonts={fonts}
        values={values}
        onValuesChange={setValues}
        fileName={(template, fieldValues) => ['bc-1977', template.id, (fieldValues.name ?? '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')].filter(Boolean).join('-')}
        note="Helvetica Medium is set in the bold the site carries, and the italic is the regular slanted. Pantone 462 is shown as Pantone’s screen conversion; proof the ink with the printer."
      >
        <label className="field">
          <span className="field__label">Ministry</span>
          <select value={ministry} onChange={(event) => chooseMinistry(event.target.value)}>
            <option value="">Type it below</option>
            {ALL_GROUPS.map((group) => (
              <optgroup key={group.label} label={group.label}>
                {group.options.map((option) => (typeof option === 'string'
                  ? <option key={option} value={option}>{option}</option>
                  : <option key={option.value} value={option.value}>{option.label}</option>))}
              </optgroup>
            ))}
          </select>
        </label>
        <div className="field">
          <span className="field__label" id="stationery-ink">Symbol</span>
          <div className="stationery__inks" role="group" aria-labelledby="stationery-ink">
            {INKS.map((entry) => (
              <button key={entry.id} type="button" className="button button--quiet" aria-pressed={ink === entry.id} title={entry.title} onClick={() => setInk(entry.id)}>
                <span className="stationery__swatch" style={{ background: entry.colour }} />{entry.label}
              </button>
            ))}
          </div>
        </div>
      </TemplateStudio>
    </section>
  )
}
