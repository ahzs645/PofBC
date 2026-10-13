/** A row of colour swatches with a hex field. `swatches` is [{ name, value }]. */
export const Swatches = ({ value, onChange, swatches, id, hex = true, small = false }) => (
  <div className="pv-swatches" role="group">
    {swatches.map((s) => (
      <button
        key={s.value}
        type="button"
        className={`pv-swatch ${small ? 'pv-small' : ''}`}
        style={{ background: s.value }}
        aria-label={s.name}
        aria-pressed={String(value).toLowerCase() === s.value.toLowerCase()}
        title={s.name}
        onClick={() => onChange(s.value)}
      />
    ))}
    {hex && (
      <input
        id={id}
        className="pv-hex"
        type="text"
        defaultValue={value}
        key={value}
        spellCheck={false}
        aria-label="Colour as hex"
        onChange={(e) => { const v = e.target.value.trim(); if (/^#[0-9a-f]{3,6}$/i.test(v)) onChange(v) }}
      />
    )}
  </div>
)
