// The site's checkbox: the browser's own input, drawn in the view's palette.
//
// It stays a real <input type="checkbox">, so a surrounding <label>, the keyboard, forms and screen
// readers all treat it as one; only its look is replaced. Its colour is `--ui-accent`, which each
// view sets to its own (ink here, amber on the posters).

import './ui.css'

const cx = (...names) => names.filter(Boolean).join(' ')

/**
 * @param {object} props
 * @param {boolean} props.checked
 * @param {(checked: boolean, event: Event) => void} [props.onChange]
 */
export const Checkbox = ({ checked, onChange, className, ...rest }) => (
  <input
    {...rest}
    type="checkbox"
    className={cx('ui-check', className)}
    checked={Boolean(checked)}
    onChange={(event) => onChange?.(event.target.checked, event)}
  />
)
