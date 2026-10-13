import { Segmented } from '../../ui/Segmented.jsx'
import { Swatches } from '../../ui/Swatches.jsx'
import { LayoutPicker } from './LayoutPicker.jsx'
import { CREST_MINISTRIES, CREST_SWATCHES, MARK_ALIGNMENT_ORDER, alignsVertically } from './renderLogo.js'

/** Controls for the crest-era lockup: layout, wording, wordmark, alignment, colours. */
export const CrestControls = ({ config, set }) => {
  const flat = config.ministry.replace(/\n/g, ' ')
  return (
    <div className="pv-controls">
      <div className="pv-control">
        <span className="pv-control-label">Lockup</span>
        <LayoutPicker config={config} onChange={set} />
      </div>

      <div className="pv-control">
        <label className="pv-control-label" htmlFor="ministry-pick">Ministry</label>
        <select id="ministry-pick" value={CREST_MINISTRIES.includes(flat) || flat === 'Ministry of Environment' ? flat : ''} onChange={(e) => { if (e.target.value) set({ ministry: e.target.value }) }}>
          <option value="">Type your own below…</option>
          <option value="Ministry of Environment">Ministry of Environment (1979–86)</option>
          {CREST_MINISTRIES.map((name) => <option key={name} value={name}>{name}</option>)}
        </select>
        <textarea id="ministry-text" rows={2} value={config.ministry} spellCheck={false} aria-label="Ministry wording, line breaks honoured" onChange={(e) => set({ ministry: e.target.value })} />
        <input id="program-text" type="text" placeholder="Second line, e.g. Fish and Wildlife Branch" value={config.program} onChange={(e) => set({ program: e.target.value })} />
      </div>

      <div className="pv-control-row">
        <label className="pv-check"><input type="checkbox" id="wordmark" checked={config.wordmark} onChange={(e) => set({ wordmark: e.target.checked })} /> Province wordmark</label>
        {alignsVertically(config.layout) && (
          <Segmented className="pv-caps" label="Mark alignment" value={config.markAlign} onChange={(markAlign) => set({ markAlign })} options={MARK_ALIGNMENT_ORDER.map((a) => ({ value: a, label: a }))} />
        )}
      </div>

      <div className="pv-control">
        <label className="pv-control-label" htmlFor="mark-colour">Mark</label>
        <Swatches id="mark-colour" value={config.markColor} swatches={CREST_SWATCHES} onChange={(markColor) => set({ markColor })} />
      </div>
      <div className="pv-control">
        <label className="pv-control-label" htmlFor="type-colour">Type</label>
        <Swatches id="type-colour" value={config.textColor} swatches={CREST_SWATCHES} onChange={(textColor) => set({ textColor })} />
      </div>
    </div>
  )
}
