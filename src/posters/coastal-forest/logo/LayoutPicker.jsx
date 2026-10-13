import { useMemo } from 'react'
import { CREAM, LAYOUT_INFO, LAYOUT_ORDER, renderLogo } from './renderLogo.js'

/** The four crest-era lockups as thumbnails, each drawn with the current wording. */
export const LayoutPicker = ({ config, onChange }) => {
  const thumbs = useMemo(() => Object.fromEntries(LAYOUT_ORDER.map((layout) => [
    layout,
    renderLogo({ ...config, era: 'crest', layout, wordmark: layout !== 'centred', markColor: CREAM, textColor: CREAM })
  ])), [config])

  return (
    <div className="pv-layouts">
      {LAYOUT_ORDER.map((layout) => (
        <button
          key={layout}
          type="button"
          className="pv-layout-btn"
          aria-pressed={config.layout === layout}
          title={LAYOUT_INFO[layout].note}
          onClick={() => onChange({ layout, wordmark: layout !== 'centred', markAlign: layout === 'columns' ? 'top' : 'centre' })}
        >
          <span className="pv-layout-thumb" dangerouslySetInnerHTML={{ __html: thumbs[layout] }} />
          <span>{LAYOUT_INFO[layout].label}</span>
        </button>
      ))}
    </div>
  )
}
