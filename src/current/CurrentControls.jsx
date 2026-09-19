// The controls that only the current era has.
//
// There is no lockup to choose — a ministry mark is one arrangement — but the wording is now
// editable. The mark beside it is the Province's own drawing, used exactly as published; the
// wording is set from the same alphabet, so a ministry that has been renamed, or that never had a
// mark published at all, can still have one made.
//
// Picking from the list loads the official wording, line breaks and all. Editing it takes over,
// and the list stops overwriting what has been typed until it is put back.

import { useId } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import {
  BCID_PALETTE, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, LANGUAGES, LANGUAGE_ORDER, recommendedVariant
} from './currentMarks.js'
import { unsupported } from './currentLayout.js'
import { BREAKS_STATED, MINISTRIES, findMinistry } from './ministries.js'

const LANGUAGE_OPTIONS = LANGUAGE_ORDER.map((value) => ({ value, label: LANGUAGES[value] }))

const VARIANT_OPTIONS = CURRENT_VARIANT_ORDER.map((value) => ({
  value,
  label: CURRENT_VARIANTS[value].label,
  title: CURRENT_VARIANTS[value].description
}))

/** The official wording for a ministry in a language, or '' if there is none. */
export const officialName = (code, language) => findMinistry(code)?.[language] ?? ''

export const CurrentControls = ({ state, update }) => {
  const selectId = useId()
  const nameId = `${selectId}-name`

  const official = officialName(state.currentMinistry, state.language)
  const edited = state.currentName !== official
  // Two marks break against the rules their siblings follow, so their wording states its breaks.
  const stated = BREAKS_STATED.includes(`${state.currentMinistry.toLowerCase()}-${state.language}`)

  // The committed alphabet is the letters the Province's own marks are drawn with. Anything else
  // needs the local build against a licensed Adobe Garamond Pro, and saying so beats drawing a
  // name with a hole in it.
  const missing = unsupported(state.currentName)

  const suggested = recommendedVariant(state.currentBackground)
  const mismatched = suggested && suggested !== state.currentVariant

  return (
    <section className="panel">
      <h2>Ministry mark</h2>
      <p className="panel__hint">
        The Province’s mark, used exactly as published, with the wording set in the same alphabet
        its own marks are lettered with and broken by the same rules — which reproduce 44 of their
        46 marks exactly.
      </p>

      <Segmented
        label="Language"
        options={LANGUAGE_OPTIONS}
        value={state.language}
        onChange={(value) => update({ language: value })}
      />

      <div className="field">
        <label htmlFor={selectId}>Ministry</label>
        <select
          id={selectId}
          value={state.currentMinistry}
          onChange={(event) => update({ currentMinistry: event.target.value })}
        >
          {MINISTRIES.map((ministry) => (
            <option key={ministry.code} value={ministry.code}>
              {ministry[state.language].replace(/\n/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor={nameId}>Wording</label>
        {/* A textarea, because the line breaks are part of the wording: the Province's own marks
            are broken by hand rather than wrapped to a measure, so pressing Enter is how you get
            the break you want. */}
        <textarea
          id={nameId}
          rows={3}
          value={state.currentName}
          spellCheck={false}
          autoComplete="off"
          onChange={(event) => update({ currentName: event.target.value })}
        />
        <p className="field__note">
          {edited
            ? 'Edited. '
            : stated
              ? 'Official wording. This mark breaks against the Province’s own pattern, so its breaks are written in. '
              : 'Official wording. Lines break by the Province’s own rules — the opening on its own line, the rest on one line or two. '}
          Press Enter to override.
          {edited && (
            <>
              {' '}
              <button
                type="button"
                className="button button--ghost button--inline"
                onClick={() => update({ currentName: official, currentNameTouched: false })}
              >
                Restore the official wording
              </button>
            </>
          )}
        </p>
      </div>

      {missing.length > 0 && (
        <p className="contrast" data-level="warn">
          <span className="contrast__surface">No letterform for</span>
          <strong>{missing.join(' ')}</strong>
          <span className="contrast__message">
            so {missing.length === 1 ? 'it is' : 'they are'} left out of the drawing. The alphabet
            here is the one the Province’s published marks use; run{' '}
            <code>npm run build:current-glyphs</code> against a licensed Adobe Garamond Pro to
            extend it.
          </span>
        </p>
      )}

      <ColourField
        label="Background"
        value={state.currentBackground}
        onChange={(value) => update({ currentBackground: value })}
        allowTransparent
        palette={BCID_PALETTE}
        hint="The BC identity colours. Changing this moves the colourway to the one the guidance pairs with it."
      />

      <Segmented
        label="Colourway"
        options={VARIANT_OPTIONS}
        value={state.currentVariant}
        onChange={(value) => update({ currentVariant: value })}
        hint={CURRENT_VARIANTS[state.currentVariant]?.description}
      />

      {mismatched && (
        <p className="contrast" data-level="warn">
          <span className="contrast__surface">On this background</span>
          <strong>{CURRENT_VARIANTS[suggested].label}</strong>
          <span className="contrast__message">
            is the colourway the Province’s guidance pairs with it.{' '}
            <button
              type="button"
              className="button button--ghost button--inline"
              onClick={() => update({ currentVariant: suggested })}
            >
              Use it
            </button>
          </span>
        </p>
      )}
    </section>
  )
}
