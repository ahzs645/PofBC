import { BcLockup } from '../logo/BcLockup.jsx'
import { CLEAR_SPACE, CLEAR_SPACE_ORDER, LAYOUTS } from '../logo/layouts.js'
import { ColourField } from './ColourField.jsx'
import { ExportPanel } from './ExportPanel.jsx'
import { LayoutPicker } from './LayoutPicker.jsx'
import { MinistryField } from './MinistryField.jsx'
import { Segmented } from './Segmented.jsx'
import { ShareLink } from './ShareLink.jsx'
import { useLockupState } from './useLockupState.js'

const CLEAR_SPACE_OPTIONS = CLEAR_SPACE_ORDER.map((value) => ({
  value,
  label: CLEAR_SPACE[value].label,
  title: `${CLEAR_SPACE[value].factor}× the width of the mark`
}))

const BACKDROP_OPTIONS = [
  { value: 'auto', label: 'Auto', title: 'Dark when the lockup would otherwise vanish' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' }
]

export const App = () => {
  const { state, update, reset, lockup, contrast, backdrop, isTransparent, swapColors } = useLockupState()
  const layout = LAYOUTS[state.layout]

  return (
    <div className="app">
      <header className="masthead">
        <h1>Province of British Columbia — logo generator</h1>
        <p>
          Three official lockups, any ministry, any colourway. Everything is drawn from the source
          artwork, so what you see here is exactly what downloads.
        </p>
      </header>

      <div className="layout">
        <section className="stage" aria-label="Preview">
          <div className="stage__frame" data-backdrop={backdrop} data-transparent={isTransparent || undefined}>
            <BcLockup {...lockup} />
          </div>

          <div className="stage__bar">
            <p className="stage__caption">
              <span>{layout.label}<span className="stage__detail"> — {layout.description}</span></span>
            </p>
            <Segmented
              compact
              label="Preview on"
              options={BACKDROP_OPTIONS}
              value={state.backdrop}
              onChange={(value) => update({ backdrop: value })}
            />
          </div>
        </section>

        <div className="controls">
          <section className="panel">
            <h2>Lockup</h2>
            <LayoutPicker value={state.layout} onChange={(value) => update({ layout: value })} />

            <label className="checkbox">
              <input
                type="checkbox"
                checked={state.wordmark}
                onChange={(event) => update({ wordmark: event.target.checked })}
              />
              <span>Show “Province of British Columbia”</span>
            </label>
            <p className="field__note">The centred lockup is drawn without it in the source artwork.</p>

            <Segmented
              label="Clear space"
              options={CLEAR_SPACE_OPTIONS}
              value={state.clearSpace}
              onChange={(value) => update({ clearSpace: value })}
              hint={
                isTransparent
                  ? 'Margin around the lockup, measured against the mark so it holds at any size.'
                  : 'Margin around the lockup. The background colour fills it, so this also sets how much of a coloured panel the export is.'
              }
            />
          </section>

          <section className="panel">
            <h2>Wording</h2>
            <MinistryField
              source={state.source}
              ministry={state.ministry}
              manualMinistry={state.manualMinistry}
              program={state.program}
              onChange={update}
            />
          </section>

          <section className="panel">
            <h2>Colour</h2>

            <ColourField
              label={state.linkColors ? 'Mark and text' : 'Mark'}
              value={state.markColor}
              onChange={(value) => update({ markColor: value })}
            />

            <label className="checkbox">
              <input
                type="checkbox"
                checked={state.linkColors}
                onChange={(event) => update({ linkColors: event.target.checked })}
              />
              <span>Text matches the mark</span>
            </label>

            {!state.linkColors && (
              <ColourField
                label="Text"
                value={state.textColor}
                onChange={(value) => update({ textColor: value })}
              />
            )}

            <ColourField
              label="Background"
              value={state.background}
              onChange={(value) => update({ background: value })}
              allowTransparent
            />

            <div className="row" style={{ marginTop: 12 }}>
              <button type="button" className="button" onClick={swapColors}>Swap</button>
              <button type="button" className="button button--ghost" onClick={reset}>Reset all</button>
            </div>

            <div className="contrast-list">
              {contrast.map((entry) => (
                <p key={entry.surface} className="contrast" data-level={entry.level}>
                  <span className="contrast__surface">{entry.surface}</span>
                  <strong>{entry.ratio == null ? '—' : `${entry.ratio}:1`}</strong>
                  <span className="contrast__message">
                    {entry.message}
                    {entry.differs && entry.ratio != null ? ` The ${entry.part} is the weaker of the two.` : ''}
                  </span>
                </p>
              ))}
            </div>
            {isTransparent && (
              <p className="field__note">
                A transparent export has no background of its own, so it has to read against whatever
                it is placed on. Both figures matter.
              </p>
            )}
          </section>

          <ExportPanel lockup={lockup} />

          <ShareLink state={state} />
        </div>
      </div>

      <p className="footnote">
        The mark is reproduced from the supplied artwork and is a provincial symbol; use of it is
        governed by the Government of British Columbia. The typeface is embedded in exports under
        whatever licence covers the copy this site was built with.
      </p>
    </div>
  )
}
