// BC Hydro, opened from the gallery, in the generator's own layout.
//
// BC Hydro's historical identity is a small system rather than one mark — four signatures, and the
// manual's rules for signs, backgrounds and vehicles — so it opens into a working view rather than
// a recolouring card. That view is built from the generator's parts: the preview stage with its
// backdrop control, then a column of panels, ending in a Download panel offering the same formats.
// Every preset keeps its own settings while you move between them, and a linked vehicle pair moves
// together.

import { useMemo, useRef, useState } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { TRANSPARENT } from '../logo/logoColors.js'
import { HydroDownload, saveText } from './HydroDownload.jsx'
import { HYDRO_STANDARDS } from './standards.js'
import {
  allHydroDefaults, effectiveMode, formatRecipe, HYDRO_ADVANCED_SLIDERS, HYDRO_GROUP_ORDER, HYDRO_GROUPS,
  HYDRO_MODE_ORDER, HYDRO_MODES, HYDRO_PRESETS, HYDRO_RANGES, HYDRO_SCREEN_PALETTES, HYDRO_SLIDERS,
  HYDRO_TYPE_ORDER, HYDRO_TYPES, hydroDefaults, hydroProject, pairedPreset, productionSpec, readHydroProject,
  ruleDescription, updateHydroSettings, validateHydro
} from './hydroLayout.js'
import { renderHydroSheet, renderHydroSvg } from './renderHydroSvg.js'

const TYPE_OPTIONS = HYDRO_TYPE_ORDER.map((value) => ({
  value, label: value === 'authority' ? 'Authority' : value === 'gas' ? 'Gas' : HYDRO_TYPES[value], title: HYDRO_TYPES[value]
}))
const MODE_OPTIONS = HYDRO_MODE_ORDER.map((value) => ({
  value, label: { colour: 'Colour', black: 'Black', white: 'White', single: 'One ink' }[value], title: HYDRO_MODES[value]
}))
const GROUP_OPTIONS = HYDRO_GROUP_ORDER.map((value) => ({
  value,
  label: { signature: 'Signatures', sign: 'Signs', general: 'Backgrounds', vehicle: 'Vehicles' }[value],
  title: HYDRO_GROUPS[value]
}))
const BACKDROP_OPTIONS = [
  { value: 'auto', label: 'Auto', title: 'Dark when the signature would otherwise vanish' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' }
]
const LAYOUT_OPTIONS = [
  { value: 'none', label: 'None' },
  { value: 'horizontal', label: 'One line' },
  { value: 'vertical', label: 'Stacked' }
]

const HYDRO_SWATCHES = [
  { name: 'white', value: '#ffffff' },
  { name: 'Hydro green (screen)', value: '#00af00' },
  { name: 'Hydro blue (screen)', value: '#0069a2' },
  { name: 'dark teal ink', value: '#003b4d' },
  { name: 'value 80% grey', value: '#333333' },
  { name: 'black', value: '#000000' }
]

const Slider = ({ name, label, step, unit, settings, update }) => {
  const [low, high] = HYDRO_RANGES[name]
  const value = settings[name]
  return (
    <div className="field hydro__slider">
      <label htmlFor={`hydro-${name}`}>
        {label}
        <output htmlFor={`hydro-${name}`}>{Number(value).toFixed(Number.isInteger(value) ? 0 : 1)}{unit}</output>
      </label>
      <input
        id={`hydro-${name}`}
        type="range"
        min={low}
        max={high}
        step={step}
        value={value}
        onChange={(event) => update(name, Number(event.target.value))}
      />
    </div>
  )
}

const Check = ({ label, checked, onChange, disabled, note }) => (
  <>
    <label className="checkbox">
      <input type="checkbox" checked={checked} disabled={disabled} onChange={(event) => onChange(event.target.checked)} />
      <span>{label}</span>
    </label>
    {note ? <p className="field__note">{note}</p> : null}
  </>
)

const NumberField = ({ label, name, settings, update, note }) => {
  const [low, high] = HYDRO_RANGES[name]
  return (
    <div className="field">
      <label htmlFor={`hydro-${name}`}>{label}</label>
      <input
        id={`hydro-${name}`}
        type="number"
        min={low}
        max={high}
        step="1"
        value={settings[name]}
        onChange={(event) => {
          if (event.target.value === '') return
          const value = Number(event.target.value)
          if (Number.isFinite(value)) update(name, Math.max(low, Math.min(high, value)))
        }}
      />
      {note ? <p className="field__note">{note}</p> : null}
    </div>
  )
}

const TextField = ({ id, label, value, onChange, maxLength = 120, note }) => (
  <div className="field">
    <label htmlFor={id}>{label}</label>
    <input id={id} type="text" maxLength={maxLength} spellCheck="false" autoComplete="off" value={value} onChange={(event) => onChange(event.target.value)} />
    {note ? <p className="field__note">{note}</p> : null}
  </div>
)

/** The presets of one application, each shown as itself — the generator's lockup picker, drawn. */
const PresetPicker = ({ all, group, active, onPick }) => (
  <div className="layouts hydro__picker" role="group" aria-label={HYDRO_GROUPS[group]}>
    {Object.entries(HYDRO_PRESETS).filter(([, preset]) => preset.group === group).map(([id, preset]) => (
      <button key={id} type="button" aria-pressed={id === active} onClick={() => onPick(id)} title={preset.caption}>
        <span
          aria-hidden="true"
          // Built by this project's own renderer; every value is escaped where written.
          dangerouslySetInnerHTML={{ __html: renderHydroSvg(all[id], { metadata: false, width: 240, prefix: `pick-${id}` }).svg }}
        />
        {preset.name}
      </button>
    ))}
  </div>
)

/** The manual's rules against the settings, loudest first, in the generator's contrast styling. */
const RuleNotes = ({ notes }) => {
  const order = { error: 0, warning: 1, info: 2 }
  const level = { error: 'fail', warning: 'warn', info: 'pass' }
  return (
    <div className="contrast-list hydro__rules" aria-live="polite">
      {[...notes].sort((a, b) => order[a.kind] - order[b.kind]).map((note) => (
        <p key={note.text} className="contrast" data-level={level[note.kind]}>
          <span className="contrast__surface">{note.kind === 'error' ? 'Breaks a rule' : note.kind === 'warning' ? 'Check' : 'Rule'}</span>
          <span className="contrast__message">{note.text}</span>
        </p>
      ))}
    </div>
  )
}

/** The files only this identity has, under the Download panel's fold. */
const MoreFiles = ({ all, active, settings, outline, run, onLoad }) => {
  const fileInput = useRef(null)
  const group = HYDRO_PRESETS[active].group
  const save = (text, name, type) => run(async () => {
    saveText(text, name, type)
    return `Saved ${name}`
  })

  return (
    <details className="hydro__more">
      <summary>More files</summary>
      <div className="row hydro__buttons">
        <button
          type="button"
          className="button"
          onClick={() => save(renderHydroSvg({ ...settings, emblemOnly: true }, { outline }).svg,
            `bc-hydro-${settings.preset}-emblem-${effectiveMode(settings)}.svg`, 'image/svg+xml')}
        >
          Emblem SVG
        </button>
        <button type="button" className="button" onClick={() => save(renderHydroSheet(all, group, { outline }), `bc-hydro-${group}-specimen.svg`, 'image/svg+xml')}>
          {HYDRO_GROUPS[group]} sheet
        </button>
        <button type="button" className="button" onClick={() => save(renderHydroSheet(all, 'all', { outline }), 'bc-hydro-specimen.svg', 'image/svg+xml')}>
          All {Object.keys(all).length} presets
        </button>
        <button type="button" className="button" onClick={() => save(JSON.stringify(HYDRO_STANDARDS, null, 2), 'bc-hydro-historical-standards.json', 'application/json')}>
          The rules as JSON
        </button>
      </div>
      <p className="field__note">Every preset’s settings, as a file to come back to — the original studio’s v1 and v2 files load too.</p>
      <div className="row hydro__buttons">
        <button type="button" className="button" onClick={() => save(JSON.stringify(hydroProject(all, active), null, 2), 'bc-hydro-template-settings-v2.json', 'application/json')}>
          Save settings
        </button>
        <button type="button" className="button" onClick={() => fileInput.current?.click()}>Load settings</button>
        <input
          ref={fileInput}
          type="file"
          accept="application/json,.json"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0]
            event.target.value = ''
            if (!file) return
            run(async () => {
              if (file.size > 250_000) throw new Error('A settings file is under 250 KB.')
              const { templates, active: opened, note } = readHydroProject(JSON.parse(await file.text()))
              onLoad(templates, opened)
              return note || `Loaded ${file.name}`
            })
          }}
        />
      </div>
    </details>
  )
}

/**
 * @param {object} props
 * @param {string} [props.initialPreset]  The preset to open on.
 * @param {() => void} props.onClose
 */
export const HydroStudio = ({ initialPreset = 'standard', onClose }) => {
  const [all, setAll] = useState(allHydroDefaults)
  const [active, setActive] = useState(HYDRO_PRESETS[initialPreset] ? initialPreset : 'standard')
  const [backdrop, setBackdrop] = useState('auto')

  const settings = all[active]
  const group = HYDRO_PRESETS[active].group
  const mode = effectiveMode(settings)
  const valued = settings.usage === 'general' || settings.usage === 'vehicle'
  const isSign = settings.usage === 'sign'
  const transparent = settings.background === 'transparent'
  const update = (key, value) => setAll((current) => updateHydroSettings(current, active, key, value))
  const reset = () => setAll((current) => ({ ...current, [active]: hydroDefaults(active) }))

  const preview = useMemo(
    () => renderHydroSvg(settings, { metadata: false, guides: settings.showGuides, prefix: 'hydro-preview' }),
    [settings]
  )
  const notes = useMemo(() => {
    const found = validateHydro(settings, preview.scene)
    // A vehicle pair should come out with one logotype height; say so when it does not.
    const partner = all[pairedPreset(active)]
    if (settings.usage === 'vehicle' && partner) {
      const height = (s) => {
        const { scene } = renderHydroSvg(s, { metadata: false, prefix: 'pair' })
        return scene.metrics.capHeight * s.exportWidth / scene.view.width
      }
      if (Math.abs(height(settings) - height(partner)) > 0.05) {
        found.push({ kind: 'warning', text: 'The positive and reverse presets export different logotype heights. Link them, or match the physical height in production.' })
      }
    }
    return found
  }, [settings, preview, all, active])

  // As the generator does it: dark only when the artwork would otherwise vanish into the page.
  const shownOn = backdrop !== 'auto' ? backdrop : mode === 'white' && transparent ? 'dark' : 'light'
  const spec = productionSpec(settings)
  const hidden = new Set([
    settings.type !== 'rail' && 'suffixGap',
    settings.type !== 'authority' && 'lineGap',
    (!isSign || settings.nameLayout === 'none') && 'nameScale',
    (!isSign || settings.nameLayout === 'none') && 'nameWidth',
    !isSign && 'borderWeight'
  ].filter(Boolean))

  return (
    <div className="hydro">
      <div className="gallery__head hydro__head">
        <div>
          <h2>BC Hydro <span className="gallery__years">historical identity</span></h2>
          <p className="gallery__note">{HYDRO_STANDARDS.status}</p>
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
            aria-label={`${HYDRO_PRESETS[active].name} — ${HYDRO_MODES[mode]}`}
            dangerouslySetInnerHTML={{ __html: preview.svg }}
          />

          <div className="stage__bar">
            {isSign && (
              <label className="checkbox hydro__guides">
                <input type="checkbox" checked={settings.showGuides} onChange={(event) => update('showGuides', event.target.checked)} />
                <span>Guides</span>
              </label>
            )}
            <Segmented compact label="Preview on" options={BACKDROP_OPTIONS} value={backdrop} onChange={setBackdrop} />
          </div>

          <RuleNotes notes={notes} />
          <p className="field__note hydro__rule">{ruleDescription(settings)}</p>
        </section>

        <div className="controls">
          <section className="panel">
            <h2>Signature</h2>
            <Segmented
              ariaLabel="Application"
              options={GROUP_OPTIONS}
              value={group}
              onChange={(next) => setActive(Object.keys(HYDRO_PRESETS).find((id) => HYDRO_PRESETS[id].group === next))}
              hint={`${HYDRO_PRESETS[active].name}: ${HYDRO_PRESETS[active].caption}.`}
            />
            <PresetPicker all={all} group={group} active={active} onPick={setActive} />
            <Segmented
              label="Signature"
              options={TYPE_OPTIONS}
              value={settings.type}
              onChange={(type) => update('type', type)}
              hint={HYDRO_TYPES[settings.type]}
            />
            <Check label="Emblem only" checked={settings.emblemOnly} onChange={(value) => update('emblemOnly', value)} />
            <div className="row" style={{ marginTop: 12 }}>
              <button type="button" className="button button--ghost" onClick={reset}>Reset this preset</button>
            </div>
          </section>

          <section className="panel">
            <h2>Wording</h2>
            {settings.type === 'authority'
              ? (
                <>
                  <TextField id="hydro-line1" label="First line" value={settings.line1} onChange={(value) => update('line1', value)} />
                  <TextField id="hydro-line2" label="Second line" value={settings.line2} onChange={(value) => update('line2', value)} />
                </>
                )
              : (
                <TextField
                  id="hydro-wordmark"
                  label="Wordmark"
                  value={settings.wordmark}
                  maxLength={100}
                  onChange={(value) => update('wordmark', value)}
                  note="“B.C.Hydro” is drawn from its fitted letters; anything else is typeset at the same size."
                />
                )}
            {settings.type === 'rail' && (
              <TextField id="hydro-suffix" label="Division" value={settings.suffix} maxLength={80} onChange={(value) => update('suffix', value)} />
            )}
            {isSign && (
              <>
                <Segmented label="Facility name" options={LAYOUT_OPTIONS} value={settings.nameLayout} onChange={(value) => update('nameLayout', value)} />
                {settings.nameLayout !== 'none' && (
                  <div className="field">
                    <label htmlFor="hydro-facility">Name{settings.nameLayout === 'vertical' ? ', a line each' : ''}</label>
                    <textarea id="hydro-facility" rows={3} maxLength={720} value={settings.facility} onChange={(event) => update('facility', event.target.value)} />
                  </div>
                )}
                <Check label="Border" checked={settings.showBorder} onChange={(value) => update('showBorder', value)} />
              </>
            )}
          </section>

          <section className="panel">
            <h2>Colour</h2>
            <Segmented
              label="Treatment"
              options={MODE_OPTIONS}
              value={mode}
              onChange={(value) => update('mode', value)}
              hint={settings.autoTreatment
                ? 'Chosen by the declared background value, where the manual defines a rule.'
                : HYDRO_MODES[mode]}
            />
            {valued && (
              <Check
                label="Choose positive or reverse from the declared value"
                checked={settings.autoTreatment}
                onChange={(value) => update('autoTreatment', value)}
              />
            )}
            {mode === 'single' && (
              <>
                <ColourField label="Ink" value={settings.ink} onChange={(value) => update('ink', value)} palette={HYDRO_SWATCHES} />
                <NumberField label="Declared ink value (%)" name="inkValue" settings={settings} update={update} />
                <Check label="Black is unavailable here" checked={settings.blackUnavailable} onChange={(value) => update('blackUnavailable', value)} />
              </>
            )}
            <ColourField
              label="Background"
              value={transparent ? TRANSPARENT : settings.backgroundColour}
              onChange={(value) => {
                if (value === TRANSPARENT) return update('background', 'transparent')
                update('background', 'solid')
                update('backgroundColour', value)
              }}
              palette={HYDRO_SWATCHES}
              allowTransparent
            />
            {valued && (
              <NumberField
                label="Declared background value (%)"
                name="backgroundValue"
                settings={settings}
                update={update}
                note="0 is the white end, 100 the dark end — the value of the real surface, which a screen colour cannot establish."
              />
            )}
            {settings.usage === 'vehicle' && (
              <Check
                label="Link the positive and reverse pair"
                checked={settings.linkVehiclePair}
                onChange={(value) => update('linkVehiclePair', value)}
                note="Keeps one logotype height across the pair, as the manual asks for a given vehicle type."
              />
            )}
          </section>

          <section className="panel">
            <h2>Proportions</h2>
            {HYDRO_SLIDERS.filter(([name]) => !hidden.has(name)).map(([name, label, step, unit]) => (
              <Slider key={name} name={name} label={label} step={step} unit={unit} settings={settings} update={update} />
            ))}
            <details className="hydro__more">
              <summary>Geometry, border and padding</summary>
              {HYDRO_ADVANCED_SLIDERS.filter(([name]) => !hidden.has(name)).map(([name, label, step, unit]) => (
                <Slider key={name} name={name} label={label} step={step} unit={unit} settings={settings} update={update} />
              ))}
            </details>
            {isSign && (
              <p className="field__note">
                Cap height {preview.scene.metrics.capHeight.toFixed(1)} · x-height {preview.scene.metrics.xHeight.toFixed(1)} units — the sign’s borders are measured in these.
              </p>
            )}
          </section>

          <section className="panel">
            <h2>Print</h2>
            <div className="field">
              <label htmlFor="hydro-process">Production method</label>
              <select id="hydro-process" value={settings.process} onChange={(event) => update('process', event.target.value)}>
                <option value="coated">Process · coated</option>
                <option value="uncoated">Process · uncoated</option>
                <option value="non-process">Non-process system</option>
              </select>
            </div>
            <dl className="hydro__recipe">
              <div><dt><i style={{ background: settings.green }} />Green</dt><dd>{formatRecipe(spec.green)}</dd></div>
              <div><dt><i style={{ background: settings.blue }} />Blue</dt><dd>{formatRecipe(spec.blue)}</dd></div>
              <div><dt><i style={{ background: '#000000' }} />Black</dt><dd>{formatRecipe(spec.black)}</dd></div>
            </dl>
            <p className="field__note">The manual’s recipes, carried in each SVG’s metadata. They do not change the screen colours.</p>
            <details className="hydro__more">
              <summary>Screen colours</summary>
              <div className="field">
                <label htmlFor="hydro-palette">Palette</label>
                <select id="hydro-palette" value={settings.screenPalette} onChange={(event) => update('screenPalette', event.target.value)}>
                  {Object.entries(HYDRO_SCREEN_PALETTES).map(([value, { label }]) => <option key={value} value={value}>{label}</option>)}
                  <option value="custom">Custom</option>
                </select>
              </div>
              <ColourField label="Green" value={settings.green} onChange={(value) => update('green', value)} palette={HYDRO_SWATCHES} />
              <ColourField label="Blue" value={settings.blue} onChange={(value) => update('blue', value)} palette={HYDRO_SWATCHES} />
              <p className="field__note">{HYDRO_STANDARDS.colours.screenPreview.basis}</p>
            </details>
          </section>

          <HydroDownload
            fileName={(extension) => `bc-hydro-${settings.preset}-${mode}.${extension}`}
            draw={(options) => {
              const { svg, scene } = renderHydroSvg(settings, options)
              return { svg, view: scene.view }
            }}
            canOutline
            width={settings.exportWidth}
            onWidth={(width) => update('exportWidth', width)}
            widthNote={settings.usage === 'vehicle' && settings.linkVehiclePair
              ? 'Shared with the other half of the vehicle pair, so both come out with one logotype height.'
              : undefined}
            more={(outline, run) => (
              <MoreFiles
                all={all}
                active={active}
                settings={settings}
                outline={outline}
                run={run}
                onLoad={(templates, opened) => {
                  setAll(templates)
                  setActive(opened)
                }}
              />
            )}
          />
        </div>
      </div>
    </div>
  )
}
