/**
 * A segmented control. `options` is [{ value, label, disabled, title, extra }]; `extra` renders
 * as a small suffix (a dpi figure, say).
 */
export const Segmented = ({ options, value, onChange, label, wide = false, wrap = false, className = '', ...rest }) => (
  <div className={`pv-seg ${wide ? 'pv-wide' : ''} ${wrap ? 'pv-wrap' : ''} ${className}`} role="group" aria-label={label} {...rest}>
    {options.map((o) => (
      <button
        key={String(o.value)}
        type="button"
        aria-pressed={o.value === value}
        disabled={o.disabled}
        title={o.title}
        onClick={() => onChange(o.value)}
      >
        {o.label}{o.extra != null && <small>{o.extra}</small>}
      </button>
    ))}
  </div>
)
