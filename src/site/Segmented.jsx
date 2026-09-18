// A labelled row of mutually exclusive choices.
//
// Buttons rather than radios: these all sit on one line, the options are short, and every one of
// them is a live preview change rather than a form value waiting to be submitted.

import { useId } from 'react'

/**
 * @param {object} props
 * @param {string} [props.label]     Omit for a control whose purpose is clear from context; pass
 *                                   `ariaLabel` instead so it is still announced.
 * @param {string} [props.ariaLabel]
 * @param {Array<{value: string, label: string, title?: string}>} props.options
 * @param {string} props.value
 * @param {(value: string) => void} props.onChange
 * @param {string} [props.hint]   Explanatory line beneath the control.
 * @param {boolean} [props.compact]
 */
export const Segmented = ({ label, ariaLabel, options, value, onChange, hint, compact = false }) => {
  const id = useId()

  return (
    <div className={compact ? 'field field--compact' : 'field'}>
      {label ? <span className="field__label" id={id}>{label}</span> : null}
      <div
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
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
      {hint ? <p className="field__note">{hint}</p> : null}
    </div>
  )
}
