// The controls that only the current era has.
//
// There is no wording to set and no lockup to choose: a ministry mark is one official file, and
// the only real decisions are which ministry, which language, and which of the Province's four
// colourways. That is the point of this era — it is a picker, not a generator, and the guidelines
// say so.

import { useId } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import {
  CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, LANGUAGES, LANGUAGE_ORDER, recommendedVariant
} from './currentMarks.js'
import { useCurrentCatalogue } from './CurrentLockup.jsx'

const LANGUAGE_OPTIONS = LANGUAGE_ORDER.map((value) => ({ value, label: LANGUAGES[value] }))

const VARIANT_OPTIONS = CURRENT_VARIANT_ORDER.map((value) => ({
  value,
  label: CURRENT_VARIANTS[value].label,
  title: CURRENT_VARIANTS[value].description
}))

export const CurrentControls = ({ state, update }) => {
  const selectId = useId()
  const catalogue = useCurrentCatalogue()

  // The guidance pairs a colourway with each background; saying so beats making someone
  // cross-reference the table, without taking the choice away.
  const suggested = recommendedVariant(state.background)
  const mismatched = suggested && suggested !== state.currentVariant

  return (
    <section className="panel">
      <h2>Ministry mark</h2>
      <p className="panel__hint">
        The Province’s official marks, used exactly as published. Nothing here is typeset — the
        wording is part of the artwork, so it cannot be edited.
      </p>

      <Segmented
        label="Language"
        options={LANGUAGE_OPTIONS}
        value={state.language}
        onChange={(value) => update({ language: value })}
      />

      <div className="field">
        <label htmlFor={selectId}>Ministry</label>
        {catalogue.status === 'ready' ? (
          <select
            id={selectId}
            value={state.currentMinistry}
            onChange={(event) => update({ currentMinistry: event.target.value })}
          >
            {catalogue.catalogue.ministries.map((ministry) => (
              <option key={ministry.code} value={ministry.code}>{ministry.name}</option>
            ))}
          </select>
        ) : (
          <p className="field__note" data-tone={catalogue.status === 'error' ? 'error' : undefined}>
            {catalogue.status === 'error' ? catalogue.message : 'Loading the ministry list…'}
          </p>
        )}
        <p className="field__note">
          {catalogue.status === 'ready'
            ? `${catalogue.catalogue.ministries.length} official marks, English and French. A ministry not listed here has no published mark to use.`
            : ''}
        </p>
      </div>

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
