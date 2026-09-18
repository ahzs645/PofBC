// Picks between the three lockups, with a miniature of each rather than a name alone — the
// difference between "stacked" and "centred" is a shape, and a shape is what should be shown.

import { LAYOUT_ORDER, LAYOUTS } from '../logo/layouts.js'

// Schematic proportions, not renderings: a real lockup at 46px tall would be an illegible smudge,
// and this only has to communicate where the mark sits relative to the text.
const DIAGRAMS = {
  stacked: (
    <>
      <rect x="4" y="2" width="16" height="16" rx="4" />
      <rect x="4" y="22" width="34" height="4" rx="2" opacity="0.85" />
      <rect x="4" y="29" width="42" height="4" rx="2" opacity="0.85" />
      <rect x="4" y="36" width="28" height="3" rx="1.5" opacity="0.55" />
    </>
  ),
  centred: (
    <>
      <rect x="26" y="2" width="16" height="16" rx="4" />
      <rect x="13" y="24" width="42" height="4" rx="2" opacity="0.85" />
      <rect x="18" y="31" width="32" height="4" rx="2" opacity="0.55" />
    </>
  ),
  horizontal: (
    <>
      <rect x="4" y="11" width="16" height="16" rx="4" />
      <rect x="25" y="13" width="40" height="4" rx="2" opacity="0.85" />
      <rect x="25" y="21" width="30" height="3" rx="1.5" opacity="0.55" />
    </>
  )
}

const VIEWBOXES = { stacked: '0 0 50 42', centred: '0 0 68 38', horizontal: '0 0 68 38' }

export const LayoutPicker = ({ value, onChange }) => (
  <div className="layouts" role="group" aria-label="Lockup">
    {LAYOUT_ORDER.map((id) => (
      <button
        key={id}
        type="button"
        aria-pressed={value === id}
        onClick={() => onChange(id)}
        title={LAYOUTS[id].description}
      >
        <svg viewBox={VIEWBOXES[id]} fill="currentColor" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
          {DIAGRAMS[id]}
        </svg>
        {LAYOUTS[id].label}
      </button>
    ))}
  </div>
)
