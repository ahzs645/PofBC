// The live logo studio: era switch, preview, the era's controls, and the footer actions.

import { useMemo } from 'react'
import { LogoPreview } from './LogoPreview.jsx'
import { CrestControls } from './CrestControls.jsx'
import { CurrentControls } from './CurrentControls.jsx'
import { DEFAULT_LOGO, contrastRatio, isOriginalLogo, renderLogo } from './renderLogo.js'

export function LogoStudio({ config, onChange, live, onLive, onExport, eras = { crest: 'Crest era', current: "Today's mark" } }) {
  const svg = useMemo(() => renderLogo(config), [config])
  const set = (patch) => onChange({ ...config, ...patch })

  const contrastFor = config.era === 'crest'
    ? (bg) => Math.min(contrastRatio(config.markColor, bg) ?? 21, contrastRatio(config.textColor, bg) ?? 21)
    : null

  return (
    <div className="pv-studio">
      <div className="pv-era-tabs" role="tablist" aria-label="Era">
        {Object.entries(eras).map(([era, label]) => (
          <button key={era} type="button" role="tab" className="pv-era-tab" aria-selected={config.era === era} onClick={() => set({ era })}>{label}</button>
        ))}
      </div>

      <LogoPreview svg={svg} contrastFor={contrastFor} />

      {config.era === 'crest' ? <CrestControls config={config} set={set} /> : <CurrentControls config={config} set={set} />}

      <div className="pv-studio-footer">
        {onLive && <label className="pv-check"><input type="checkbox" id="live" checked={live} onChange={(e) => onLive(e.target.checked)} /> Show it on the poster</label>}
        <button type="button" className="pv-link-btn" disabled={isOriginalLogo(config)} onClick={() => onChange(DEFAULT_LOGO)}>Back to the poster's logo</button>
        {onExport && <button type="button" className="pv-link-btn pv-primary" onClick={onExport}>Export this logo</button>}
      </div>
    </div>
  )
}
