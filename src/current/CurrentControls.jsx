// The controls that only the current era has.
//
// There is no lockup to choose — a ministry mark is one arrangement — but the wording is now
// editable. The mark beside it is the Province's own drawing, used exactly as published; the
// wording is set from the same alphabet, so a ministry that has been renamed, or that never had a
// mark published at all, can still have one made.
//
// Picking from the list loads the official wording, line breaks and all. Editing it takes over,
// and the list stops overwriting what has been typed until it is put back.
//
// The list is the published marks first, then every other name the other three identities offer —
// today's ministries and agencies without a published mark, and every ministry since 1976. Those
// have no official wording, so they are set by the Province's rules instead.

import { useId } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import {
  BCID_PALETTE, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, LANGUAGES, LANGUAGE_ORDER, recommendedVariant
} from './currentMarks.js'
import { unsupported } from './currentLayout.js'
import { BREAKS_STATED, MINISTRIES } from './ministries.js'
import { chosenName, codeForName } from '../site/ministryLink.js'
import { ALL_GROUPS, History } from '../site/MinistryField.jsx'

const LANGUAGE_OPTIONS = LANGUAGE_ORDER.map((value) => ({ value, label: LANGUAGES[value] }))

const VARIANT_OPTIONS = CURRENT_VARIANT_ORDER.map((value) => ({
  value,
  label: CURRENT_VARIANTS[value].label,
  title: CURRENT_VARIANTS[value].description
}))

// A name without a published mark is chosen by the name itself, and a prefix keeps it apart from
// the codes the published marks are chosen by.
const BY_NAME = 'name:'

/**
 * Every name the other identities list that no published mark answers to.
 *
 * Built from the same groups, so the four identities cannot offer different ministries. Today's
 * ministries that do have a mark are dropped here, since the published marks above already list
 * them with their official wording.
 */
const UNPUBLISHED_GROUPS = ALL_GROUPS
  .map((group) => ({
    label: group.label === 'Ministries' ? 'Ministries without a published mark' : group.label,
    options: group.options
      .map((option) => (typeof option === 'string' ? { value: option, label: option } : option))
      .filter((option) => !codeForName(option.value))
  }))
  .filter((group) => group.options.length > 0)

const UNPUBLISHED_NAMES = new Set(UNPUBLISHED_GROUPS.flatMap((group) => group.options.map((option) => option.value)))

export const CurrentControls = ({ state, update }) => {
  const selectId = useId()
  const nameId = `${selectId}-name`

  const edited = state.currentNameTouched
  // Two marks break against the rules their siblings follow, so their wording states its breaks.
  const stated = BREAKS_STATED.includes(`${state.currentMinistry.toLowerCase()}-${state.language}`)
  const chosen = chosenName(state)
  const custom = state.source === 'manual' || !codeForName(state.ministry)
  // A name from the wider list is still a list choice, and the select should say which.
  const listed = custom && state.source === 'list' && UNPUBLISHED_NAMES.has(state.ministry)
  const selected = !custom ? state.currentMinistry : listed ? BY_NAME + state.ministry : ''

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

      {/* This era picks from the published marks; the Wording box below is where a name that is
          not one of them gets typed. Both write the same shared choice, so whatever ends up here
          is what the crest, flag and arms lockups set too. */}
      <div className="field">
        <label htmlFor={selectId}>Ministry</label>
        <select
          id={selectId}
          value={selected}
          onChange={(event) => {
            const { value } = event.target
            if (value.startsWith(BY_NAME)) update({ source: 'list', ministry: value.slice(BY_NAME.length) })
            else update({ currentMinistry: value })
          }}
        >
          {/* A name of your own is not in any list, and pretending one of them is selected would
              misreport what is on the mark. */}
          {custom && !listed && <option value="">{chosen || 'A name of your own'}</option>}
          <optgroup label="Published marks">
            {MINISTRIES.map((ministry) => (
              <option key={ministry.code} value={ministry.code}>
                {ministry[state.language].replace(/\n/g, ' ')}
              </option>
            ))}
          </optgroup>
          {UNPUBLISHED_GROUPS.map((group) => (
            <optgroup key={group.label} label={group.label}>
              {group.options.map((option) => (
                <option key={option.value} value={BY_NAME + option.value}>{option.label}</option>
              ))}
            </optgroup>
          ))}
        </select>
        {listed && <History name={state.ministry} />}
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
            : listed
              ? 'No published mark carries this name, so it is set by the Province’s own rules. '
              : custom
                // No published mark answers to this name, so there is no official wording to be
                // faithful to — the rules still set it, but they are the Province's rules applied to
                // your name rather than a reproduction of its artwork.
                ? 'A name of your own, set by the Province’s own rules rather than copied from a mark. '
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
                onClick={() => update({ currentNameTouched: false })}
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
            <code>npm run build:current-extras</code> with <code>GARAMOND_SOURCE</code> pointing at a
            licensed Adobe Garamond Pro to extend it.
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
