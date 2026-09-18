import { BcLockup } from '../logo/BcLockup.jsx'
import { CurrentControls } from '../current/CurrentControls.jsx'
import { CurrentLockup } from '../current/CurrentLockup.jsx'
import {
  alignsVertically, CLEAR_SPACE, CLEAR_SPACE_ORDER, LAYOUTS, MARK_ALIGNMENTS, MARK_ALIGNMENT_ORDER
} from '../logo/layouts.js'
import { ColourField } from './ColourField.jsx'
import { ExportPanel } from './ExportPanel.jsx'
import { LayoutPicker } from './LayoutPicker.jsx'
import { MinistryField } from './MinistryField.jsx'
import { Segmented } from './Segmented.jsx'
import { ShareLink } from './ShareLink.jsx'
import { useAgentTools } from './useAgentTools.js'
import { useLockupState } from './useLockupState.js'

const CLEAR_SPACE_OPTIONS = CLEAR_SPACE_ORDER.map((value) => ({
  value,
  label: CLEAR_SPACE[value].label,
  title: `${CLEAR_SPACE[value].factor}× the width of the mark`
}))

const MARK_ALIGNMENT_OPTIONS = MARK_ALIGNMENT_ORDER.map((value) => ({
  value,
  label: MARK_ALIGNMENTS[value].label,
  title: MARK_ALIGNMENTS[value].description
}))

const ERA_OPTIONS = [
  {
    value: 'historical',
    label: 'Historical',
    title: 'The crest lockups, built from the supplied artwork. Any ministry, any colour.'
  },
  {
    value: 'current',
    label: 'Current',
    title: 'The Province’s official ministry marks, used exactly as published.'
  }
]

const BACKDROP_OPTIONS = [
  { value: 'auto', label: 'Auto', title: 'Dark when the lockup would otherwise vanish' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' }
]

export const App = () => {
  const { state, update, reset, lockup, artwork, contrast, backdrop, isTransparent, swapColors } = useLockupState()
  const layout = LAYOUTS[state.layout]
  const isCurrent = state.era === 'current'

  // Registers this page's tools with an agent driving the browser, where the browser supports it.
  // A no-op everywhere else.
  useAgentTools({ state, lockup, update, reset })

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
            {isCurrent ? (
              <CurrentLockup
                code={state.currentMinistry}
                language={state.language}
                variant={state.currentVariant}
                background={state.background}
                clearSpaceFactor={lockup.clearSpaceFactor}
                title="Province of British Columbia ministry mark"
              />
            ) : (
              <BcLockup {...artwork} />
            )}
          </div>

          <div className="stage__bar">
            <p className="stage__caption">
              {isCurrent ? (
                <span>
                  Official mark
                  <span className="stage__detail"> — published artwork, used as provided</span>
                </span>
              ) : (
                <span>{layout.label}<span className="stage__detail"> — {layout.description}</span></span>
              )}
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
            <h2>Identity</h2>
            <Segmented
              ariaLabel="Identity"
              options={ERA_OPTIONS}
              value={state.era}
              onChange={(value) => update({ era: value })}
              hint={
                isCurrent
                  ? 'The Province’s current marks, served exactly as published. The wording is part of the artwork.'
                  : 'The crest identity, rebuilt from the supplied artwork. Any ministry, any colourway.'
              }
            />
          </section>

          {isCurrent && <CurrentControls state={state} update={update} />}

          {isCurrent && (
            <section className="panel">
              <h2>Placement</h2>
              <Segmented
                label="Clear space"
                options={CLEAR_SPACE_OPTIONS}
                value={state.clearSpace}
                onChange={(value) => update({ clearSpace: value })}
                hint="Margin around the mark. The background colour fills it."
              />
              <ColourField
                label="Background"
                value={state.background}
                onChange={(value) => update({ background: value })}
                allowTransparent
              />
            </section>
          )}

          {!isCurrent && (
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

            {alignsVertically(layout) && (
              <Segmented
                label="Mark alignment"
                options={MARK_ALIGNMENT_OPTIONS}
                value={state.markAlign}
                onChange={(value) => update({ markAlign: value })}
                hint="Where the mark sits against the type, measured from the cap height of the first line to the baseline of the last."
              />
            )}

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

          )}

          {!isCurrent && (
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

          )}

          {!isCurrent && (
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

          )}

          <ExportPanel lockup={lockup} era={state.era} />

          <ShareLink state={state} update={update} />
        </div>
      </div>

      <p className="footnote">
        The mark is reproduced from the supplied artwork and is a provincial symbol; use of it is
        governed by the Government of British Columbia. The typeface is embedded in exports under
        whatever licence covers the copy this site was built with.
      </p>

      {/* Linked rather than only sitting at a path, so it is reachable from the page itself —
          by a person wondering what the generator can do, and by an agent reading the document. */}
      <p className="footnote">
        Every option this generator offers is listed in{' '}
        <a href={`${import.meta.env.BASE_URL}capabilities.json`}>capabilities.json</a>.
      </p>
    </div>
  )
}
