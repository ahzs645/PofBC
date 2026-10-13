import { Segmented } from '../../ui/Segmented.jsx'
import { CURRENT_MINISTRIES, CURRENT_VARIANTS, CURRENT_VARIANT_ORDER } from './renderLogo.js'

/** Controls for the current-era mark: language, ministry, wording, colourway. */
export const CurrentControls = ({ config, set }) => {
  const pick = (code, language = config.language) => {
    const m = CURRENT_MINISTRIES.find((x) => x.code === code)
    return m ? { currentCode: m.code, currentText: m[language], language } : { language }
  }
  return (
    <div className="pv-controls">
      <div className="pv-control-row">
        <Segmented
          label="Language"
          value={config.language}
          onChange={(language) => set(pick(config.currentCode, language))}
          options={[{ value: 'en', label: 'English' }, { value: 'fr', label: 'Français' }]}
        />
      </div>
      <div className="pv-control">
        <label className="pv-control-label" htmlFor="current-pick">Ministry</label>
        <select id="current-pick" value={config.currentCode} onChange={(e) => set(pick(e.target.value))}>
          <option value="">Custom wording</option>
          {CURRENT_MINISTRIES.map((m) => <option key={m.code} value={m.code}>{m.en.replace(/\n/g, ' ')}</option>)}
        </select>
        <textarea id="current-text" rows={3} value={config.currentText} spellCheck={false} aria-label="Ministry wording, line breaks honoured" onChange={(e) => set({ currentText: e.target.value, currentCode: '' })} />
      </div>
      <div className="pv-control">
        <span className="pv-control-label">Colourway</span>
        <div className="pv-variants-row">
          {CURRENT_VARIANT_ORDER.map((v) => (
            <button key={v} type="button" className="pv-variant-btn" aria-pressed={config.variant === v} title={CURRENT_VARIANTS[v].description} onClick={() => set({ variant: v })}>
              <b>{CURRENT_VARIANTS[v].label}</b>
              <span>{CURRENT_VARIANTS[v].description}</span>
            </button>
          ))}
        </div>
        {(config.variant === 'colour' || config.variant === 'black') && (
          <p className="pv-contrast-warn">This colourway is for light backgrounds. On the poster's black it will mostly disappear; Reverse or Solid white are the ones that read there.</p>
        )}
      </div>
    </div>
  )
}
