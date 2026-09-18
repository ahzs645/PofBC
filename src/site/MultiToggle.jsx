// A row of independent on/off chips.
//
// Distinct from Segmented, which picks exactly one. These are checkboxes underneath, because that
// is what they are — several can be on, none can be, and a screen reader should hear it that way
// rather than hearing a broken radio group.

import { useId } from 'react'

/**
 * @param {object} props
 * @param {string} props.label
 * @param {Array<{value: string|number, label: string, title?: string}>} props.options
 * @param {Array<string|number>} props.value  The selected values.
 * @param {(value: Array<string|number>) => void} props.onChange
 * @param {string} [props.hint]
 * @param {boolean} [props.allowEmpty]  When false, the last selected chip cannot be turned off.
 */
export const MultiToggle = ({ label, options, value, onChange, hint, allowEmpty = false }) => {
  const id = useId()

  const toggle = (option) => {
    const selected = value.includes(option)
    if (selected && !allowEmpty && value.length === 1) return
    onChange(selected ? value.filter((entry) => entry !== option) : [...value, option])
  }

  return (
    <fieldset className="chips-field">
      <legend className="field__label" id={id}>{label}</legend>
      <div className="chips">
        {options.map((option) => {
          const checked = value.includes(option.value)
          const last = checked && !allowEmpty && value.length === 1

          return (
            <label
              key={option.value}
              className="chip"
              data-checked={checked || undefined}
              title={last ? 'At least one is needed' : option.title}
            >
              <input
                type="checkbox"
                checked={checked}
                disabled={last}
                onChange={() => toggle(option.value)}
              />
              <span>{option.label}</span>
            </label>
          )
        })}
      </div>
      {hint ? <p className="field__note">{hint}</p> : null}
    </fieldset>
  )
}
