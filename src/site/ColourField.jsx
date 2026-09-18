// A colour control: brand swatches for the colours that should be reached for first, and a free
// picker for everything else. Both write the same value, so there is no "custom mode" to get
// stuck in.

import { useId } from 'react'
import { BRAND_COLORS, TRANSPARENT, parseHex, resolveColor } from '../logo/logoColors.js'

// Roughly light to dark, so the row reads as a ramp rather than a jumble. One palette serves the
// mark, the type and the background — a brand colour is a brand colour wherever it lands.
const SWATCH_ORDER = ['white', 'silver', 'gold', 'red', 'green', 'blue', 'grey', 'black']

export const ColourField = ({ label, value, onChange, allowTransparent = false }) => {
  const inputId = useId()
  const isTransparent = value === TRANSPARENT
  const hex = parseHex(value) ? value.toLowerCase() : '#006837'

  return (
    <div className="field">
      <span className="field__label" id={`${inputId}-label`}>{label}</span>

      <div className="swatches" role="group" aria-labelledby={`${inputId}-label`}>
        {allowTransparent && (
          <button
            type="button"
            className="swatch swatch--transparent"
            aria-pressed={isTransparent}
            aria-label="Transparent"
            title="Transparent"
            onClick={() => onChange(TRANSPARENT)}
          />
        )}
        {SWATCH_ORDER.map((name) => (
          <button
            key={name}
            type="button"
            className="swatch"
            style={{ backgroundColor: BRAND_COLORS[name] }}
            aria-pressed={!isTransparent && resolveColor(value).toLowerCase() === BRAND_COLORS[name]}
            aria-label={name}
            title={`${name} ${BRAND_COLORS[name]}`}
            onClick={() => onChange(BRAND_COLORS[name])}
          />
        ))}
      </div>

      <div className="colour-custom">
        <input
          id={inputId}
          type="color"
          value={hex}
          onChange={(event) => onChange(event.target.value)}
          aria-label={`${label}: pick a custom colour`}
        />
        <input
          type="text"
          value={isTransparent ? 'transparent' : value}
          spellCheck="false"
          inputMode="text"
          aria-label={`${label}: hex value`}
          onChange={(event) => {
            const next = event.target.value.trim()
            // Typing is allowed to pass through unvalidated so the field does not fight the
            // person mid-keystroke; the renderer falls back safely on anything it cannot parse.
            onChange(next.toLowerCase() === 'transparent' ? TRANSPARENT : next)
          }}
        />
      </div>
    </div>
  )
}
