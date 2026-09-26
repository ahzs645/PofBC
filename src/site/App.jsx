import { Suspense, lazy, useState } from 'react'
import { BcLockup } from '../logo/BcLockup.jsx'
import { CurrentControls } from '../current/CurrentControls.jsx'
import { CurrentLockup } from '../current/CurrentLockup.jsx'
import { CrestLockup } from '../crest/CrestLockup.jsx'
import { FlagLockup } from '../flag/FlagLockup.jsx'
// Loaded when it is opened: the gallery's marks are drawn from their own artwork and renderers,
// which the generator never needs.
const GalleryView = lazy(() => import('../gallery/GalleryView.jsx').then((module) => ({ default: module.GalleryView })))
// Likewise the government diagram, which carries a century and a half of ministries with it.
const GovernmentView = lazy(() => import('../government/GovernmentView.jsx').then((module) => ({ default: module.GovernmentView })))
import { generatorPatchFor } from '../government/eraMark.js'
import {
  FLAG_PALETTE_ORDER, FLAG_PALETTE_HINTS, FLAG_PALETTE_LABELS, FLAG_SWATCHES
} from '../flag/flagPalettes.js'
import {
  FLAG_SYMBOLS, FLAG_SYMBOL_HINTS, FLAG_SYMBOL_LABELS,
  NAME_PLACEMENTS, NAME_PLACEMENT_HINTS, NAME_PLACEMENT_LABELS
} from '../flag/flagLayout.js'
import {
  CREST_ARRANGEMENTS, CREST_ARRANGEMENT_HINTS, CREST_ARRANGEMENT_LABELS,
  CREST_PLACEMENTS, CREST_PLACEMENT_LABELS,
  CREST_ALIGNMENTS, CREST_ALIGNMENT_LABELS, CREST_LAYOUTS,
  MINISTRY_SIZE_ORDER, MINISTRY_SIZE_LABELS, MINISTRY_SIZE_HINTS,
  MINISTRY_STEPS, MINISTRY_STEP_LABELS
} from '../crest/crestLayout.js'
import {
  alignsVertically, CLEAR_SPACE, CLEAR_SPACE_ORDER, LAYOUTS, MARK_ALIGNMENTS, MARK_ALIGNMENT_ORDER
} from '../logo/layouts.js'
import { ColourField } from './ColourField.jsx'
import { ExportPanel } from './ExportPanel.jsx'
import { LayoutPicker } from './LayoutPicker.jsx'
import { MinistryField } from './MinistryField.jsx'
import { Segmented } from './Segmented.jsx'
import { ShareLink } from './ShareLink.jsx'
import { ViewSwitcher } from './ViewSwitcher.jsx'
import { SunGlyph, ThemeIcon } from './icons.jsx'
import { useSiteTheme } from './useTheme.js'
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

const CREST_ARRANGEMENT_OPTIONS = CREST_ARRANGEMENTS.map((value) => ({
  value, label: CREST_ARRANGEMENT_LABELS[value], title: CREST_ARRANGEMENT_HINTS[value]
}))

const CREST_PLACEMENT_OPTIONS = CREST_PLACEMENTS.map((value) => ({
  value, label: CREST_PLACEMENT_LABELS[value]
}))

const CREST_ALIGNMENT_OPTIONS = CREST_ALIGNMENTS.map((value) => ({
  value, label: CREST_ALIGNMENT_LABELS[value]
}))

const MINISTRY_SIZE_OPTIONS = MINISTRY_SIZE_ORDER.map((value) => ({
  value, label: MINISTRY_SIZE_LABELS[value], title: MINISTRY_SIZE_HINTS[value]
}))

const MINISTRY_STEP_OPTIONS = MINISTRY_STEPS.map((value) => ({
  value, label: MINISTRY_STEP_LABELS[value]
}))

const FLAG_SYMBOL_OPTIONS = FLAG_SYMBOLS.map((value) => ({
  value, label: FLAG_SYMBOL_LABELS[value], title: FLAG_SYMBOL_HINTS[value]
}))

const NAME_PLACEMENT_OPTIONS = NAME_PLACEMENTS.map((value) => ({
  value, label: NAME_PLACEMENT_LABELS[value], title: NAME_PLACEMENT_HINTS[value]
}))

const FLAG_PALETTE_OPTIONS = FLAG_PALETTE_ORDER.map((value) => ({
  value,
  label: FLAG_PALETTE_LABELS[value],
  title: FLAG_PALETTE_HINTS[value]
}))

const ERA_OPTIONS = [
  {
    value: 'historical',
    label: 'Crest',
    title: 'The crest lockups, built from the supplied artwork. Any ministry, any colour.'
  },
  {
    value: 'flag',
    label: 'Flag',
    title: 'BC beside the waving provincial flag, with the ministry beneath.'
  },
  {
    value: 'crest',
    label: 'Arms',
    title: 'The coat of arms with the BRITISH COLUMBIA wordmark.'
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

const VIEW_IDS = ['generator', 'gallery', 'government']

/** The view in the address bar, so a link to the gallery or the diagram opens it. */
const initialView = () => {
  const view = new URLSearchParams(globalThis.location?.search ?? '').get('view')
  return VIEW_IDS.includes(view) ? view : 'generator'
}

/**
 * Moving to another view leaves the last one's place behind — the diagram's year and body, the
 * gallery's collection — so each view's link stays its own. The generator carries no view at all.
 */
const writeView = (view) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  for (const key of ['view', 'year', 'node', 'logos', 'mark']) url.searchParams.delete(key)
  if (view !== 'generator') url.searchParams.set('view', view)
  globalThis.history.replaceState(null, '', url)
}

export const App = () => {
  const { state, update, reset, lockup, artwork, background, contrast, backdrop, isTransparent, swapColors } = useLockupState()
  // Separate views, not modes of one: neither the gallery nor the government diagram has anything
  // to do with the generator's state. The diagram keeps its place in the address bar, so a link to
  // it opens it.
  const [view, setView] = useState(initialView)
  const theme = useSiteTheme()
  const showView = (next) => {
    setView(next)
    writeView(next)
  }
  // A mark in the gallery leads to the body it stands for in the government diagram, which reads
  // its body from the address bar when it opens.
  const openInGovernment = (node) => {
    const url = new URL(globalThis.location.href)
    url.searchParams.delete('logos')
    url.searchParams.delete('mark')
    url.searchParams.set('view', 'government')
    url.searchParams.set('node', node)
    url.searchParams.delete('year')
    globalThis.history?.replaceState(null, '', url)
    setView('government')
  }
  // The diagram hands a ministry over in the identity of the year it was looking at.
  const openInGenerator = ({ era, name }) => {
    update(generatorPatchFor({ era, name }))
    showView('generator')
    globalThis.scrollTo?.({ top: 0 })
  }
  const layout = LAYOUTS[state.layout]
  const isCurrent = state.era === 'current'
  const isFlag = state.era === 'flag'
  const isCrest = state.era === 'crest'
  // A one-off from the gallery: its arrangement is the mark, not a choice.
  const isBadge = isFlag && state.flagSymbol === 'badge'
  // The crest era is the only one with lockups to choose between, a province wordmark to show or
  // hide, and a mark to align.
  const isOldCrest = !isCurrent && !isFlag && !isCrest

  // Registers this page's tools with an agent driving the browser, where the browser supports it.
  // A no-op everywhere else.
  useAgentTools({ state, lockup, update, reset })

  // The government diagram takes the whole page, as the site it is modelled on does, and carries
  // the view switch in its own breadcrumb.
  if (view === 'government') {
    return (
      <Suspense fallback={<p className="gallery__intro">Loading the government…</p>}>
        <GovernmentView onOpenInGenerator={openInGenerator} onChangeView={showView} />
      </Suspense>
    )
  }

  return (
    <div className="app">
      {/* A breadcrumb card, as the government view has: the site, then the view, which opens the
          menu of the others. The heading is kept so the page still has one. */}
      <header className="masthead">
        <h1 className="masthead__crumbs">
          <SunGlyph className="masthead__sun" />
          <span className="masthead__site">Province of BC</span>
          <span className="masthead__slash" aria-hidden="true">/</span>
          <ViewSwitcher view={view} onChange={showView} />
        </h1>
        <button
          type="button"
          className="icon-button"
          onClick={theme.toggle}
          aria-label={`Switch to ${theme.name === 'dark' ? 'light' : 'dark'} mode`}
          title={`Switch to ${theme.name === 'dark' ? 'light' : 'dark'} mode`}
        >
          <ThemeIcon name={theme.name} />
        </button>
      </header>

      {view === 'gallery' && (
        <Suspense fallback={<p className="gallery__intro">Loading the gallery…</p>}>
          <GalleryView
            onOpenGovernment={openInGovernment}
            onOpenInGenerator={(patch) => {
              update(patch)
              showView('generator')
              globalThis.scrollTo?.({ top: 0 })
            }}
          />
        </Suspense>
      )}

      {view === 'generator' && (
      <div className="layout">
        <section className="stage" aria-label="Preview">
          <div className="stage__frame" data-backdrop={backdrop} data-transparent={isTransparent || undefined}>
            {isCurrent ? (
              <CurrentLockup
                text={state.currentName}
                language={state.language}
                variant={state.currentVariant}
                background={state.currentBackground}
                clearSpaceFactor={lockup.clearSpaceFactor}
                title="Province of British Columbia ministry mark"
              />
            ) : isCrest ? (
              <CrestLockup
                arrangement={state.crestArrangement}
                placement={state.crestPlacement}
                ministry={lockup.ministry}
                extra={state.crestExtra}
                bold={state.crestBold}
                align={state.crestAlign}
                markColor={state.crestMarkColor}
                textColor={state.linkColors ? state.crestMarkColor : state.crestTextColor}
                background={state.crestBackground}
                clearSpaceFactor={lockup.clearSpaceFactor}
                title="British Columbia coat of arms lockup"
              />
            ) : isFlag ? (
              <FlagLockup
                ministry={lockup.ministry}
                letterColor={state.flagMarkColor}
                textColor={state.linkColors ? state.flagMarkColor : state.flagTextColor}
                symbol={state.flagSymbol}
                placement={state.flagPlacement}
                province={state.flagProvince}
                extra={state.flagExtra}
                flagPalette={state.flagPalette}
                background={state.flagBackground}
                clearSpaceFactor={lockup.clearSpaceFactor}
                title="British Columbia flag lockup"
              />
            ) : (
              <BcLockup {...artwork} />
            )}
          </div>

          <div className="stage__bar">
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
                  ? 'The Province’s current marks, used exactly as published, with the wording set to match.'
                  : isFlag
                    ? 'BC beside the waving provincial flag. Any ministry, any colour.'
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
            </section>
          )}

          {isCrest && (
            <section className="panel">
              <h2>Arms</h2>
              <Segmented
                label="Arrangement"
                options={CREST_ARRANGEMENT_OPTIONS}
                value={state.crestArrangement}
                onChange={(value) => update({ crestArrangement: value })}
                hint={CREST_ARRANGEMENT_HINTS[state.crestArrangement]}
              />
              <Segmented
                label="Ministry"
                options={CREST_PLACEMENT_OPTIONS}
                value={state.crestPlacement}
                onChange={(value) => update({ crestPlacement: value })}
              />
              <Segmented
                label="Ministry size"
                options={MINISTRY_SIZE_OPTIONS}
                value={state.crestMinistrySize}
                onChange={(value) => update({ crestMinistrySize: value })}
                hint={MINISTRY_SIZE_HINTS[state.crestMinistrySize]}
              />
              {state.crestExtra.trim() && (
                <Segmented
                  label="Second line"
                  options={MINISTRY_STEP_OPTIONS}
                  value={state.crestExtraStep}
                  onChange={(value) => update({ crestExtraStep: value })}
                  hint="Two documents set the line under the ministry one size smaller than it."
                />
              )}
              {CREST_LAYOUTS[state.crestArrangement]?.centred && state.crestPlacement === 'below' && (
                <Segmented
                  label="Ministry lines"
                  options={CREST_ALIGNMENT_OPTIONS}
                  value={state.crestAlign}
                  onChange={(value) => update({ crestAlign: value })}
                  hint="Centred on the mark, or flush with the wordmark’s left edge. The documents do both."
                />
              )}
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={state.crestBold}
                  onChange={(event) => update({ crestBold: event.target.checked })}
                />
                <span>Set the ministry bold</span>
              </label>
              <Segmented
                label="Clear space"
                options={CLEAR_SPACE_OPTIONS}
                value={state.clearSpace}
                onChange={(value) => update({ clearSpace: value })}
                hint="Margin around the lockup. The background colour fills it."
              />
            </section>
          )}

          {isFlag && (
            <section className="panel">
              <h2>Flag</h2>
              {isBadge && (
                <p className="field__note" style={{ marginTop: 0 }}>
                  A one-off mark from the gallery. Its arrangement is fixed; its colours and
                  wording are not.{' '}
                  <button
                    type="button"
                    className="button button--ghost button--inline"
                    onClick={() => update({ flagSymbol: 'horizontal' })}
                  >
                    Back to the arrangements
                  </button>
                </p>
              )}
              {!isBadge && (
              <Segmented
                label="Symbol"
                options={FLAG_SYMBOL_OPTIONS}
                value={state.flagSymbol}
                onChange={(value) => update({ flagSymbol: value })}
                hint={FLAG_SYMBOL_HINTS[state.flagSymbol]}
              />
              )}
              {!isBadge && (
              <Segmented
                label="Wording"
                options={NAME_PLACEMENT_OPTIONS}
                value={state.flagPlacement}
                onChange={(value) => update({ flagPlacement: value })}
                hint={NAME_PLACEMENT_HINTS[state.flagPlacement]}
              />
              )}
              {!isBadge && (
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={state.flagProvince}
                  onChange={(event) => update({ flagProvince: event.target.checked })}
                />
                <span>Set “Province of British Columbia” above</span>
              </label>
              )}
              <Segmented
                label="Colour"
                options={FLAG_PALETTE_OPTIONS}
                value={state.flagPalette}
                onChange={(value) => update({ flagPalette: value })}
                hint={FLAG_PALETTE_HINTS[state.flagPalette]}
              />
              <Segmented
                label="Clear space"
                options={CLEAR_SPACE_OPTIONS}
                value={state.clearSpace}
                onChange={(value) => update({ clearSpace: value })}
                hint="Margin around the lockup. The background colour fills it."
              />
            </section>
          )}

          {isOldCrest && (
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
            {(isFlag || isCrest) && (
              <div className="field">
                <label htmlFor="flag-extra">
                  Third line <span className="field__note" style={{ display: 'inline' }}>(optional)</span>
                </label>
                <input
                  id="flag-extra"
                  type="text"
                  value={isCrest ? state.crestExtra : state.flagExtra}
                  placeholder={isCrest ? 'Research Branch' : 'Honourable Anthony J. Brummet, Minister'}
                  autoComplete="off"
                  onChange={(event) => update(
                    isCrest ? { crestExtra: event.target.value } : { flagExtra: event.target.value }
                  )}
                />
                <p className="field__note">A minister, a place, a bulletin number — as the documents do.</p>
              </div>
            )}
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
              label={state.linkColors
                ? (isFlag ? 'Letters and text' : 'Mark and text')
                : (isFlag ? 'Letters' : 'Mark')}
              value={isFlag ? state.flagMarkColor : isCrest ? state.crestMarkColor : state.markColor}
              onChange={(value) => update(
                isFlag ? { flagMarkColor: value } : isCrest ? { crestMarkColor: value } : { markColor: value }
              )}
              palette={isFlag ? FLAG_SWATCHES : undefined}
            />

            <label className="checkbox">
              <input
                type="checkbox"
                checked={state.linkColors}
                onChange={(event) => update({ linkColors: event.target.checked })}
              />
              <span>{isFlag ? 'Text matches the letters' : 'Text matches the mark'}</span>
            </label>

            {!state.linkColors && (
              <ColourField
                label="Text"
                value={isFlag ? state.flagTextColor : isCrest ? state.crestTextColor : state.textColor}
                onChange={(value) => update(
                  isFlag ? { flagTextColor: value } : isCrest ? { crestTextColor: value } : { textColor: value }
                )}
              />
            )}

            <ColourField
              label="Background"
              value={isFlag ? state.flagBackground : isCrest ? state.crestBackground : state.background}
              onChange={(value) => update(
                isFlag ? { flagBackground: value } : isCrest ? { crestBackground: value } : { background: value }
              )}
              palette={isFlag ? FLAG_SWATCHES : undefined}
              allowTransparent
              hint={isFlag
                ? 'The flag’s white is the page showing through it, so on anything but white it is set in one ink.'
                : undefined}
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
      )}

      <p className="footnote">
        The mark is reproduced from the supplied artwork and is a provincial symbol; use of it is
        governed by the Government of British Columbia. The typeface is embedded in exports under
        whatever licence covers the copy this site was built with.
        {view === 'gallery' && (
          <> The gallery also holds other public bodies’ marks, such as BC Hydro’s, which are theirs
            and are reconstructed here from historical material, not supplied by them.</>
        )}
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
