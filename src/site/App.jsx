import { Suspense, lazy, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { BcLockup } from '../logo/BcLockup.jsx'
import { CrestLockup } from '../crest/CrestLockup.jsx'
import { FlagLockup } from '../flag/FlagLockup.jsx'
import { DocumentArmsPanel } from './DocumentArmsPanel.jsx'
const loadDocumentArms = () => import('./DocumentArmsPreview.jsx')
const DocumentArmsPreview = lazy(loadDocumentArms)
const DocumentArmsReference = lazy(() => loadDocumentArms().then((module) => ({ default: module.DocumentArmsReference })))
// The current identity's drawing and alphabet come with its lockup and controls, so they are fetched
// when that identity is chosen (or a link opens on it), not with every page.
const loadCurrentLockup = () => import('../current/CurrentLockup.jsx')
const loadCurrentControls = () => import('../current/CurrentControls.jsx')
const CurrentLockup = lazy(() => loadCurrentLockup().then((module) => ({ default: module.CurrentLockup })))
const CurrentControls = lazy(() => loadCurrentControls().then((module) => ({ default: module.CurrentControls })))
// Every other view is loaded when it is opened (viewLoaders.js says why each is its own chunk).
const lazyView = (id, name) => lazy(() => VIEW_LOADERS[id]().then((module) => ({ default: module[name] })))
const GalleryView = lazyView('gallery', 'GalleryView')
const InitiativesView = lazyView('initiatives', 'InitiativesView')
const SchoolDistrictsView = lazyView('school-districts', 'SchoolDistrictsView')
const PartiesView = lazyView('parties', 'PartiesView')
const GovernmentView = lazyView('government', 'GovernmentView')
const InternalLogosView = lazyView('internal', 'InternalLogosView')
const PostersView = lazyView('posters', 'PostersView')
const SignsView = lazyView('signs', 'SignsView')
const CardsView = lazyView('cards', 'CardsView')
const PinsView = lazyView('pins', 'PinsView')
const PatchesView = lazyView('patches', 'PatchesView')
const PlatesView = lazyView('plates', 'PlatesView')
const PaperModelsView = lazyView('paper-models', 'PaperModelsView')
const ArmsView = lazyView('arms', 'ArmsView')
const GuidesView = lazyView('guides', 'GuidesView')
const StationeryView = lazyView('stationery', 'StationeryView')
const SalariesView = lazyView('salaries', 'SalariesView')
const HealthStoryView = lazyView('health-map', 'HealthStoryView')
import { generatorPatchFor } from '../government/generatorPatch.js'
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
import { HIDDEN_VIEWS, ViewSwitcher, VIEWS } from './ViewSwitcher.jsx'
import { VIEW_LOADERS } from './viewLoaders.js'
import { NavigationContext, searchFor } from './navigation.jsx'
import { writeHistory } from './browserHistory.js'
import { salaryPlaceUrl } from '../salaries/viewState.js'
import { legacyInitiativeUrl } from '../initiatives/initiativePlace.js'
import { retiredPatchUrl } from '../patches/retiredPatches.js'
import { SunGlyph, ThemeIcon } from './icons.jsx'
import { useSiteTheme } from './useTheme.js'
import { useAgentTools } from './useAgentTools.js'
import { useLockupState } from './useLockupState.js'
import { DEFAULT_TITLE, documentTitle, setDocumentMeta } from './documentMeta.js'
import { Checkbox } from './ui/Checkbox.jsx'
import { holdScroll, holdScrollFrom } from './holdScroll.js'

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

// Short enough that the three share one row on a phone; the hint carries the full description.
const CREST_ARRANGEMENT_SHORT = { 'vertical-arms': 'Large arms' }
const CREST_ARRANGEMENT_OPTIONS = CREST_ARRANGEMENTS.map((value) => ({
  value, label: CREST_ARRANGEMENT_SHORT[value] ?? CREST_ARRANGEMENT_LABELS[value], title: CREST_ARRANGEMENT_HINTS[value]
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
    value: 'document',
    // One word, so five identities fit one row on a phone; beside "Arms" it reads as the earlier arms.
    label: 'Historic',
    title: 'Earlier document-heading studies using the shared plate arms reconstruction.'
  },
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
  { value: 'auto', label: 'Auto', title: 'Follows the site theme, or goes dark when a light lockup on a transparent background would otherwise vanish' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' }
]

const GENERATOR_DESCRIPTION = 'Explore British Columbia identity artwork and historical layout studies, with SVG, PDF, PNG, WebP and JPEG export.'
const VIEW_IDS = [...VIEWS, ...HIDDEN_VIEWS].map(({ id }) => id)

/** The view in the address bar, so a link to the gallery or the diagram opens it. */
const initialView = () => {
  // Replace once before reading the view, including on Back/Forward. No navigation event or extra
  // history entry is needed, and the entry's return/focus metadata remains attached to it.
  // A link to a design no longer offered as a patch opens the place that holds it now.
  const href = globalThis.location?.href
  const migrated = href ? legacyInitiativeUrl(href) ?? retiredPatchUrl(href) : null
  if (migrated) globalThis.history?.replaceState(globalThis.history.state, '', migrated)
  const view = new URLSearchParams(migrated?.search ?? globalThis.location?.search ?? '').get('view')
  return VIEW_IDS.includes(view) ? view : 'generator'
}

/**
 * Moving to another view leaves the last one's place behind — the diagram's year and body, the
 * gallery's collection — so each view's link stays its own. The generator carries no view at all.
 */
const writeView = (view) => {
  const url = salaryPlaceUrl(globalThis.location.href, {})
  for (const key of ['view', 'year', 'node', 'mode', 'compare', 'undated', 'local', 'instrument', 'logos', 'mark', 'subject', 'coverage', 'identity-family', 'identity-state', 'identity-scope', 'identity-query', 'internal', 'internal-logo', 'poster', 'sign', 'card', 'pin', 'part', 'guide', 'page', 'org', 'patch', 'group', 'family', 'plate', 'area', 'chapter', 'story', 'holder', 'initiative', 'section', 'record', 'district', 'school-query', 'school-scope', 'party', 'party-query', 'party-scope', 'party-design']) url.searchParams.delete(key)
  if (/^#tourism-/.test(url.hash)) url.hash = ''
  if (view !== 'generator') url.searchParams.set('view', view)
  writeHistory(url)
}

export const App = () => {
  const theme = useSiteTheme()
  const { state, update, reset, lockup, artwork, background, contrast, backdrop, isTransparent, swapColors } = useLockupState(theme.name)
  // Separate views, not modes of one: neither the gallery nor the government diagram has anything
  // to do with the generator's state. The diagram keeps its place in the address bar, so a link to
  // it opens it.
  const [view, setView] = useState(initialView)
  // Bumped by every link between views, so the view it lands on opens afresh and reads its place
  // from the address — even when it is the view already on screen.
  const [visit, setVisit] = useState(0)
  useEffect(() => {
    const restore = () => {
      setView(initialView())
      // Each view reads its selection from the restored URL when mounted.
      setVisit((value) => value + 1)
    }
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [])
  // Detail views that own their metadata also name the selected page in the tab.
  useEffect(() => {
    if (view === 'salaries' || view === 'initiatives' || view === 'school-districts' || view === 'parties') return
    const entry = [...VIEWS, ...HIDDEN_VIEWS].find(({ id }) => id === view)
    setDocumentMeta({
      title: view === 'generator' || !entry ? DEFAULT_TITLE : documentTitle(entry.label),
      description: view === 'generator' || !entry ? GENERATOR_DESCRIPTION : `${entry.description}.`
    })
  }, [view])
  // On the generator, the current identity is fetched once the page has settled, so choosing it
  // does not wait on the network. The other views never ask for it.
  useEffect(() => {
    if (view !== 'generator') return undefined
    const fetchCurrent = () => { loadCurrentLockup().catch(() => {}); loadCurrentControls().catch(() => {}) }
    if (globalThis.requestIdleCallback) {
      const id = globalThis.requestIdleCallback(fetchCurrent, { timeout: 4000 })
      return () => globalThis.cancelIdleCallback?.(id)
    }
    const id = setTimeout(fetchCurrent, 1500)
    return () => clearTimeout(id)
  }, [view])
  const showView = (next) => {
    writeView(next)
    setView(next)
    setVisit((value) => value + 1)
  }
  // A link from one view to a place in another: the posters to the emblem they carry, the emblem to
  // the posters, either to the body in the government diagram.
  const navigate = (params) => {
    const next = VIEW_IDS.includes(params.view) ? params.view : 'generator'
    const url = new URL(globalThis.location.href)
    url.search = searchFor({ ...params, view: next === 'generator' ? null : next })
    if (/^#tourism-/.test(url.hash)) url.hash = ''
    writeHistory(url)
    setView(next)
    setVisit((value) => value + 1)
    globalThis.scrollTo?.({ top: 0 })
  }
  // A mark in the gallery leads to the body it stands for in the government diagram, which reads
  // its body from the address bar when it opens.
  // A body that no longer stands opens in a year it did, which the caller passes.
  const openInGovernment = (node, year) => {
    // Use a fresh view URL: a prior related/compare mode must not strand a provincial node.
    navigate({ view: 'government', node, ...(year ? { year } : {}) })
  }
  // The diagram hands a ministry over in the identity of the year it was looking at.
  const openInGenerator = ({ era, name }) => {
    update(generatorPatchFor({ era, name }))
    showView('generator')
    globalThis.scrollTo?.({ top: 0 })
  }
  const preloadIdentities = () => {
    loadDocumentArms().catch(() => {})
    loadCurrentLockup().catch(() => {})
    loadCurrentControls().catch(() => {})
  }
  // The historic and current identities draw from code of their own, which on a slow connection can
  // arrive well after the choice: the panel holds its place on screen until it has, so the drawing
  // landing in the stage above cannot push the choice off the screen. Nothing extra is downloaded.
  const identityPanel = useRef(null)
  const IDENTITY_CODE = {
    document: loadDocumentArms,
    current: () => Promise.all([loadCurrentLockup(), loadCurrentControls()])
  }
  // While the next identity's drawing is on its way, the stage keeps the height of the one it is
  // replacing rather than shrinking to a line of "Loading…" and growing again when it lands: the
  // choice below it stays still. Measured after every drawing; read before the switch.
  const stageFrame = useRef(null)
  const stageHeight = useRef(0)
  useLayoutEffect(() => {
    const frame = stageFrame.current
    if (frame && !frame.querySelector(':scope > .stage__loading')) stageHeight.current = frame.getBoundingClientRect().height
  })
  const chooseIdentity = (era) => {
    const load = era !== state.era && IDENTITY_CODE[era]
    if (load) holdScroll(identityPanel.current, { until: load() })
    update({ era })
  }
  const layout = LAYOUTS[state.layout]
  const isCurrent = state.era === 'current'
  const isFlag = state.era === 'flag'
  const isCrest = state.era === 'crest'
  const isDocument = state.era === 'document'
  const hasLettering = !isDocument || state.documentLayout !== 'emblem'
  // A one-off from the gallery: its arrangement is the mark, not a choice.
  const isBadge = isFlag && state.flagSymbol === 'badge'
  // The crest era is the only one with lockups to choose between, a province wordmark to show or
  // hide, and a mark to align.
  const isOldCrest = !isCurrent && !isFlag && !isCrest && !isDocument

  // Registers this page's tools with an agent driving the browser, where the browser supports it.
  // A no-op everywhere else.
  useAgentTools({ state, lockup, update, reset })

  // The government diagram takes the whole page, as the site it is modelled on does, and carries
  // the view switch in its own breadcrumb.
  if (view === 'government') {
    // Its links to other views go through `navigate` like every other view's, not a page reload.
    return (
      <NavigationContext.Provider value={navigate}>
        <Suspense fallback={<p className="gallery__intro">Loading the government…</p>}>
          <GovernmentView key={visit} onOpenInGenerator={openInGenerator} onChangeView={showView} />
        </Suspense>
      </NavigationContext.Provider>
    )
  }

  return (
    <NavigationContext.Provider value={navigate}>
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

      {view === 'internal' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the oval logos…</p>}>
          <InternalLogosView key={visit} />
        </Suspense>
      )}

      {view === 'signs' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the signs…</p>}>
          <SignsView key={visit} />
        </Suspense>
      )}

      {view === 'school-districts' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the school districts…</p>}>
          <SchoolDistrictsView key={visit} />
        </Suspense>
      )}

      {view === 'parties' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the political parties…</p>}>
          <PartiesView key={visit} />
        </Suspense>
      )}

      {view === 'cards' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the cards…</p>}>
          <CardsView key={visit} />
        </Suspense>
      )}

      {view === 'pins' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the pins…</p>}>
          <PinsView key={visit} />
        </Suspense>
      )}

      {view === 'patches' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the patches…</p>}>
          <PatchesView key={visit} />
        </Suspense>
      )}

      {view === 'badges' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the badges…</p>}>
          <PatchesView key={visit} collection="badges" />
        </Suspense>
      )}

      {view === 'paper-models' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the paper models…</p>}>
          <PaperModelsView key={visit} />
        </Suspense>
      )}

      {view === 'plates' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the licence plates…</p>}>
          <PlatesView key={visit} />
        </Suspense>
      )}

      {view === 'arms' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the coats of arms…</p>}>
          <ArmsView key={visit} />
        </Suspense>
      )}

      {view === 'guides' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the visual guides…</p>}>
          <GuidesView key={visit} />
        </Suspense>
      )}

      {view === 'stationery' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the stationery…</p>}>
          <StationeryView key={visit} />
        </Suspense>
      )}

      {view === 'health-map' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the historical health maps…</p>}>
          <HealthStoryView key={visit} />
        </Suspense>
      )}

      {view === 'salaries' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the salaries…</p>}>
          <SalariesView key={visit} onOpenGovernment={openInGovernment} />
        </Suspense>
      )}

      {view === 'posters' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the posters…</p>}>
          <PostersView key={visit} />
        </Suspense>
      )}

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

      {view === 'initiatives' && (
        <Suspense fallback={<p className="gallery__intro" role="status">Loading the initiatives…</p>}>
          <InitiativesView key={visit} />
        </Suspense>
      )}

      {view === 'generator' && (
      <div className="layout">
        <section className="stage" aria-label="Preview">
          <div
            ref={stageFrame}
            className="stage__frame"
            data-backdrop={backdrop}
            data-transparent={isTransparent || undefined}
            style={stageHeight.current ? { '--stage-held': `${Math.round(stageHeight.current)}px` } : undefined}
          >
            {isDocument ? (
              <Suspense fallback={<p role="status" className="stage__loading">Loading the historical arms study…</p>}>
                <DocumentArmsPreview lockup={lockup} />
              </Suspense>
            ) : isCurrent ? (
              <Suspense fallback={<p role="status" className="stage__loading">Loading the current mark…</p>}>
                <CurrentLockup
                  text={state.currentName}
                  language={state.language}
                  variant={state.currentVariant}
                  background={state.currentBackground}
                  clearSpaceFactor={lockup.clearSpaceFactor}
                  title="Province of British Columbia ministry mark"
                />
              </Suspense>
            ) : isCrest ? (
              <CrestLockup
                arrangement={state.crestArrangement}
                placement={state.crestPlacement}
                ministry={lockup.ministry}
                extra={state.crestExtra}
                bold={state.crestBold}
                align={state.crestAlign}
                ministrySize={state.crestMinistrySize}
                extraStep={state.crestExtraStep}
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
          {isDocument && (
            <Suspense fallback={null}>
              <DocumentArmsReference key={state.documentLayout} layout={state.documentLayout} />
            </Suspense>
          )}
        </section>

        <div className="controls">
          {/* The historic and current identities are drawn from chunks of their own. They are fetched
              as soon as a finger or the keyboard reaches for this panel, so that by the time a choice
              lands its drawing has usually arrived; on a slow connection, chooseIdentity holds the
              panel in place until it has. */}
          <section className="panel" ref={identityPanel} onPointerDown={preloadIdentities} onFocus={preloadIdentities}>
            <h2>Identity</h2>
            <Segmented
              ariaLabel="Identity"
              options={ERA_OPTIONS}
              value={state.era}
              onChange={chooseIdentity}
              hint={
                isDocument
                  ? 'Earlier government document headings. A reconstruction study using the plate artwork; the original engraving and typefaces remain unverified.'
                  : isCurrent
                  ? 'The Province’s current marks, used exactly as published, with the wording set to match.'
                  : isFlag
                    ? 'BC beside the waving provincial flag. Any ministry, any colour.'
                    : isCrest
                      ? 'The coat of arms with the BRITISH COLUMBIA wordmark. Any ministry, any colourway.'
                      : 'The crest identity, rebuilt from the supplied artwork. Any ministry, any colourway.'
              }
            />
            <Segmented
              label="Preview on"
              options={BACKDROP_OPTIONS}
              value={state.backdrop}
              onChange={(value) => update({ backdrop: value })}
            />
          </section>

          {isDocument && <DocumentArmsPanel state={state} update={update} clearSpaceOptions={CLEAR_SPACE_OPTIONS} />}

          {isCurrent && <Suspense fallback={null}><CurrentControls state={state} update={update} /></Suspense>}

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
                <Checkbox
                  checked={state.crestBold}
                  onChange={(checked, event) => { holdScrollFrom(event); update({ crestBold: checked }) }}
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
                <Checkbox
                  checked={state.flagProvince}
                  onChange={(checked, event) => { holdScrollFrom(event); update({ flagProvince: checked }) }}
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
              <Checkbox
                checked={state.wordmark}
                onChange={(checked, event) => { holdScrollFrom(event); update({ wordmark: checked }) }}
              />
              <span>Show “Province of British Columbia”</span>
            </label>
            {state.layout === 'centred' && (
              <p className="field__note">The centred lockup is drawn without it in the source artwork.</p>
            )}

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

          {!isCurrent && !isDocument && (
          <section className="panel">
            <h2>Wording</h2>
            <MinistryField
              source={state.source}
              ministry={state.ministry}
              manualMinistry={state.manualMinistry}
              program={state.program}
              onChange={update}
            />
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
                  title="A minister, a place, a bulletin number, as the documents do."
                  onChange={(event) => update(
                    isCrest ? { crestExtra: event.target.value } : { flagExtra: event.target.value }
                  )}
                />
              </div>
            )}
          </section>

          )}

          {!isCurrent && (
          <section className="panel">
            <h2>Colour</h2>

            <ColourField
              label={!hasLettering ? 'Arms' : state.linkColors
                ? (isFlag ? 'Letters and text' : 'Mark and text')
                : (isFlag ? 'Letters' : 'Mark')}
              value={isDocument ? state.documentMarkColor : isFlag ? state.flagMarkColor : isCrest ? state.crestMarkColor : state.markColor}
              onChange={(value) => update(
                isDocument ? { documentMarkColor: value } : isFlag ? { flagMarkColor: value } : isCrest ? { crestMarkColor: value } : { markColor: value }
              )}
              palette={isFlag ? FLAG_SWATCHES : undefined}
            />

            {hasLettering && <label className="checkbox">
              <Checkbox
                checked={state.linkColors}
                onChange={(checked) => update({ linkColors: checked })}
              />
              <span>{isFlag ? 'Text matches the letters' : 'Text matches the mark'}</span>
            </label>}

            {hasLettering && !state.linkColors && (
              <ColourField
                label="Text"
                value={isDocument ? state.documentTextColor : isFlag ? state.flagTextColor : isCrest ? state.crestTextColor : state.textColor}
                onChange={(value) => update(
                  isDocument ? { documentTextColor: value } : isFlag ? { flagTextColor: value } : isCrest ? { crestTextColor: value } : { textColor: value }
                )}
              />
            )}

            <ColourField
              label="Background"
              value={isDocument ? state.documentBackground : isFlag ? state.flagBackground : isCrest ? state.crestBackground : state.background}
              onChange={(value) => update(
                isDocument ? { documentBackground: value } : isFlag ? { flagBackground: value } : isCrest ? { crestBackground: value } : { background: value }
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

    </div>
    </NavigationContext.Provider>
  )
}
