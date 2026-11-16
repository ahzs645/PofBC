// The site's slider: the browser's own range input, with its track and handle drawn in the view's
// palette. The stretch up to the handle is filled with `--ui-accent`, so the value reads at a glance.
//
// It stays a real <input type="range">: arrow keys, Page Up and Down, Home and End, touch and screen
// readers behave exactly as they do on any slider.

import './ui.css'

const cx = (...names) => names.filter(Boolean).join(' ')

/**
 * @param {object} props
 * @param {number|string} props.value
 * @param {(value: number, event: Event) => void} [props.onChange] Called with the value as a number.
 */
export const Slider = ({ value, min = 0, max = 100, step = 1, onChange, className, style, ...rest }) => {
  const low = Number(min)
  const high = Number(max)
  const at = Number(value)
  const fill = high > low && Number.isFinite(at) ? ((Math.min(high, Math.max(low, at)) - low) / (high - low)) * 100 : 0
  return (
    <input
      {...rest}
      type="range"
      className={cx('ui-range', className)}
      min={min}
      max={max}
      step={step}
      value={value ?? ''}
      style={{ ...style, '--ui-range-fill': `${fill}%` }}
      onChange={(event) => onChange?.(Number(event.target.value), event)}
    />
  )
}
