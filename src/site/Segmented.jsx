// A labelled row of mutually exclusive choices.
//
// Buttons rather than radios: these all sit on one line, the options are short, and every one of
// them is a live preview change rather than a form value waiting to be submitted.
//
// A choice changes what is below the control, never where the reader is: the control stays put on
// screen while the page under it grows or shrinks (holdScroll.js).

import { useId, useRef, useState } from 'react'
import { holdScroll } from './holdScroll.js'

/**
 * @param {object} props
 * @param {string} [props.label]     Omit for a control whose purpose is clear from context; pass
 *                                   `ariaLabel` instead so it is still announced.
 * @param {string} [props.ariaLabel]
 * @param {Array<{value: string, label: string, title?: string}>} props.options
 * @param {string} props.value
 * @param {(value: string) => void} props.onChange
 * @param {string} [props.hint]   Explanatory line beneath the control. Under a labelled control it
 *                                   waits behind a “?” beside the label, so a panel of controls is not
 *                                   also a page of prose; a control with no label shows it outright.
 * @param {boolean} [props.compact]
 */
export const Segmented = ({ label, ariaLabel, options, value, onChange, hint, compact = false }) => {
  const id = useId()
  const hintId = useId()
  const [explained, setExplained] = useState(false)
  const shown = hint && (explained || !label)
  const group = useRef(null)

  return (
    <div className={compact ? 'field field--compact' : 'field'}>
      {label ? (
        <span className="field__head">
          <span className="field__label" id={id}>{label}</span>
          {hint ? (
            <button
              type="button"
              className="field__help"
              aria-expanded={explained}
              aria-controls={explained ? hintId : undefined}
              aria-label={`About ${label.toLowerCase()}`}
              title={explained ? undefined : hint}
              onClick={() => setExplained(!explained)}
            >
              ?
            </button>
          ) : null}
        </span>
      ) : null}
      <div
        ref={group}
        className="segmented"
        role="group"
        aria-labelledby={label ? id : undefined}
        aria-label={label ? undefined : ariaLabel}
      >
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            aria-pressed={value === option.value}
            disabled={option.disabled}
            title={option.title}
            aria-label={option.ariaLabel}
            onClick={() => {
              if (value !== option.value) holdScroll(group.current)
              onChange(option.value)
            }}
          >
            {option.label}
          </button>
        ))}
      </div>
      {shown ? <p className="field__note" id={hintId}>{hint}</p> : null}
    </div>
  )
}
