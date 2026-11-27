import { SafetyAuthorityHistory } from './SafetyAuthorityHistory.jsx'
// The gallery: marks the generator does not make, grouped by whose they are.
//
// A shelf rather than a set of presets: these marks follow no pattern the generator can offer, so
// there is nothing to load them into. Each still opens for editing — the Province's one-offs for
// their colours, BC Hydro's signatures into the generator's layout — and each draws itself from the
// renderer its download comes from, so a card cannot drift from what it gives you.
//
// Every mark also says what it is as an artefact — where its artwork came from, how closely it has
// been checked, what its dates rest on, and that nobody has permission to show it — as chips on its
// card and in full when it is open (the identity records are in collections.js). And the bodies
// whose marks have not been obtained get a shelf of their own, while there are any, so a gap reads
// as a gap rather than as a body with no mark.

import { coverFirst } from './collectedCollections.js'
import { PreviewBackground } from './PreviewBackground.jsx'
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { formatEventDate } from '../government/events.js'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { Disclosure } from '../site/Disclosure.jsx'
import { holdScrollFrom } from '../site/holdScroll.js'
import { renderFlagSvg } from '../flag/renderFlagSvg.js'
import { FLAG_PALETTE_HINTS, FLAG_PALETTE_LABELS, FLAG_PALETTE_ORDER, FLAG_SWATCHES } from '../flag/flagPalettes.js'
import {
  APPLICABILITY, FIDELITY, GALLERY_COLLECTIONS, PROVENANCE, RIGHTS, collectionById, entriesOf,
  entriesOfNode, eraStatus, findGalleryEntry, timelineOf,
  FOLDED_GROUPS, childCollectionsOf
} from './collections.js'
import { ASSET_STATUS, WANTED, WANTED_AS_OF } from './wanted.js'
import { HydroStudio } from '../hydro/HydroStudio.jsx'
import { HydroMarkView } from '../hydro/HydroMarkView.jsx'
import { hasGlow, renderOneOffSvg, rolesOf } from './renderOneOff.js'
import { useSiteTheme } from '../site/useTheme.js'
import { BCTS_FOREST, BCTS_TEAL } from './oneOffs.js'
import { SuppliedMarkView } from './SuppliedMarkView.jsx'
import { CollectedMarkView } from './CollectedMarkView.jsx'
import { supportProvidedBy } from '../government/forrex.js'
import { FundingHistory, SupportProvided, RuralHealthConnections } from '../government/FundingHistory.jsx'
import { ParksFoundationHistory } from './ParksFoundationHistory.jsx'
import { RailwayHistory, RailwayHistoryLinks } from './RailwayHistory.jsx'
import { Breadcrumbs } from '../site/Breadcrumbs.jsx'
import { Lineage } from '../site/Lineage.jsx'
import { InitiativeLink } from '../initiatives/InitiativeLink.jsx'
import { UnbcOriginsTeaser } from './UnbcOrigins.jsx'
import { defaultCollectedAsset, generatorArt, onPage, tileArt } from './tileArt.js'
import { GALLERY_TYPE_OPTIONS, browseGallery, gallerySections, isSearchShortcut } from './gallerySearch.js'
import { CouncilTimeline } from './CouncilTimeline.jsx'
import { COUNCIL_TIMELINE_OWNERS } from './scienceCouncilHistory.js'
import { galleryHistoryOf, hasGalleryHistory } from './galleryHistory.js'
import { identitySubjectById } from './identityCoverage.js'
import { CNC_SUBJECT } from './cncIdentity.js'
import { CncIdentityCard, IdentityCollectionLinks, IdentityCoverageBrowser, IdentityCoverageOverview, IdentitySearchResults, IdentitySubjectDetail, RegionalDistrictMembers, SubjectLink } from './IdentityCoverage.jsx'
import { SiteLink, useNavigate } from '../site/navigation.jsx'
import { movedGalleryPlace } from './movedGalleryPlaces.js'
import { galleryPlaceUrl } from './galleryPlace.js'
import { writeHistory } from '../site/browserHistory.js'
import { AllLogos, CurrentOrganizations, GalleryModeSwitch, GalleryTimeline, TimelineScrubber } from './GalleryModes.jsx'
import { PRESENT_YEAR, isGalleryMode } from './galleryModes.js'
import { MARK_ROLE_LABELS } from './markRoles.js'

const PALETTE_OPTIONS = FLAG_PALETTE_ORDER.map((value) => ({
  value, label: FLAG_PALETTE_LABELS[value], title: FLAG_PALETTE_HINTS[value]
}))

// A mark is either set by the flag renderer (BC Parks) or drawn from its own published shapes
// (everything else), and the two take their colours differently.
const drawing = (entry, colours) => entry.kind === 'artwork'
  ? renderOneOffSvg({ id: entry.mark, colours: colours.colours, sun: colours.sun, clearSpaceFactor: 0.05 }).svg
  : renderFlagSvg({
    ...entry.draw,
    letterColor: colours.ink,
    textColor: colours.ink,
    flagPalette: colours.palette,
    background: colours.background,
    clearSpaceFactor: 0.05
  }).svg

/** The BC identity colours these marks were published in, then the neutrals. */
const ARTWORK_SWATCHES = [
  { name: 'white', value: '#ffffff' },
  { name: 'BC gold', value: '#fdb913' },
  { name: 'BC red', value: '#d1401e' },
  { name: 'light blue', value: '#4a6ea7' },
  { name: 'WelcomeBC blue', value: '#0c68a9' },
  { name: 'BC blue', value: '#004b8d' },
  { name: 'BCTS teal', value: BCTS_TEAL },
  { name: 'BCTS forest green', value: BCTS_FOREST },
  { name: 'black', value: '#000000' }
]

const SUN_OPTIONS = [
  { value: 'glow', label: 'Shaded', title: 'The sun, rays and core shaded as the print files shade them.' },
  { value: 'flat', label: 'Flat', title: 'One colour, with the rays and core cut out of it in the light colour.' }
]

/** What each part is called in the controls, and which parts share one control. */
const PART_CONTROLS = [
  { label: 'Sun', roles: ['sun'] },
  { label: 'Light', roles: ['light'], hint: 'The sun’s core and the rays it fades to (or, flat, the colour cut out of the sun).' },
  { label: 'Mountains', roles: ['mountains'] },
  { label: 'BRITISH COLUMBIA', roles: ['wordmark'] },
  { label: 'Tagline', roles: ['tagline'] },
  { label: 'Rules', roles: ['rule', 'divider'] },
  { label: 'Name', roles: ['name'] },
  { label: 'Descriptor', roles: ['descriptor'], hint: 'The line under the name, in a colour of its own.' },
  { label: 'Accent', roles: ['accent'], hint: 'The part of the name picked out in gold.' },
  { label: 'Maple leaf', roles: ['leaf'] }
]

/** The controls for a drawn mark: its sun, then a colour for each part it has. */
const ArtworkControls = ({ entry, colours, change }) => {
  const roles = rolesOf(entry.mark)
  // The light is the sun's, so a name set without the mark has none.
  const present = new Set(roles.includes('sun') ? [...roles, 'light'] : roles)
  const setParts = (roles, value) => change({
    colours: { ...colours.colours, ...Object.fromEntries(roles.map((role) => [role, value])) }
  })

  return (
    <>
      {hasGlow(entry.mark) && (
        <Segmented
          label="Shading"
          options={SUN_OPTIONS}
          value={colours.sun}
          onChange={(sun) => change({ sun })}
          hint={SUN_OPTIONS.find((option) => option.value === colours.sun)?.title}
        />
      )}
      <ColourField
        label="Background"
        value={colours.colours.background}
        onChange={(background) => setParts(['background'], background)}
        palette={ARTWORK_SWATCHES}
        allowTransparent
      />
      {PART_CONTROLS.filter(({ roles }) => roles.some((role) => present.has(role))).map(({ label, roles, hint }) => (
        <ColourField
          key={label}
          label={label}
          value={colours.colours[roles.find((role) => present.has(role))]}
          onChange={(value) => setParts(roles, value)}
          palette={ARTWORK_SWATCHES}
          hint={hint}
        />
      ))}
    </>
  )
}

/** The controls for a mark set by the flag renderer. */
const FlagControls = ({ colours, change }) => (
  <>
    <Segmented
      label="Flag"
      options={PALETTE_OPTIONS}
      value={colours.palette}
      onChange={(palette) => change({ palette })}
      hint={FLAG_PALETTE_HINTS[colours.palette]}
    />
    <ColourField
      label="Ink"
      value={colours.ink}
      onChange={(ink) => change({ ink })}
      palette={FLAG_SWATCHES}
    />
    <ColourField
      label="Background"
      value={colours.background}
      onChange={(background) => change({ background })}
      palette={FLAG_SWATCHES}
      allowTransparent
    />
  </>
)

/** Whether the colours on screen are still exactly a preset's. */
const samePreset = (preset, colours) => JSON.stringify(preset) === JSON.stringify(colours)

const download = (entry, colours, suffix) => {
  const blob = new Blob([drawing(entry, colours)], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `bc-${entry.id}${suffix ? `-${suffix}` : ''}.svg`
  document.body.append(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

// ── What each mark is ────────────────────────────────────────────────────────────────────────────

/** Each classification as a sentence, for the fuller account on a mark's own page. */
const PROVENANCE_SENTENCES = {
  original_supplied: 'Drawn from original artwork supplied to this project, as it was drawn.',
  extracted_from_official_vector: 'Extracted from vector artwork in an official document of the body’s own.',
  extracted_from_published_artwork: 'Extracted from artwork as it was published, not redrawn.',
  archival_raster: 'An archival image, not vector artwork.',
  published_vector: 'Vector artwork recovered from a published source, with that source recorded.',
  published_raster: 'An image recovered from a published source, with that source recorded.',
  third_party_reconstruction: 'An existing third-party redraw, retained with its attribution. It is not an original historical master.',
  reconstructed: 'Reconstructed: redrawn by this project from pictures or written rules, not taken from ' +
    'original artwork.',
  synthetic_name_variant: 'A generated interpretation (a name set in a style it never had), and not an ' +
    'authentic historical mark.'
}

const FIDELITY_SENTENCES = {
  'source compared': 'Checked against its source.',
  'partially compared': 'Only partly checked against its source.',
  'font substitution': 'Its lettering is a substitute: the original typeface was not recovered.',
  'no comparison': 'Not checked against any source.'
}

// An unknown date is said to be unknown, never left to read as "did not exist" (QA_CASES 19).
const DATE_SENTENCES = {
  documented_adoption: (years) => `${years}, from a record of its adoption.`,
  first_observation: (years) => `First seen ${years}.`,
  dated_specimen: (years) => `Seen in the cited specimen dated ${years}.`,
  estimated_era: (years) => `Estimated: ${years}.`,
  unknown: () => 'Unknown. That is not to say it was never in use.'
}

const sentencesOf = (identity) => ({
  Provenance: PROVENANCE_SENTENCES[identity.provenance],
  Fidelity: [FIDELITY_SENTENCES[identity.fidelity], identity.fidelityNote].filter(Boolean).join(' '),
  Dates: [DATE_SENTENCES[identity.applicability.kind](identity.applicability.years), identity.applicability.note]
    .filter(Boolean).join(' '),
  Rights: `${RIGHTS[identity.rights.status]}. ${identity.rights.note}`
})

/**
 * The short form, for a card: where it came from, what its date rests on, and whether it may be
 * shown once that is anything but unresolved. Every mark here is unresolved, so that chip told no
 * card apart; the mark's own page still says so under "About this mark".
 */
const chipsOf = (identity) => [
  PROVENANCE[identity.provenance],
  APPLICABILITY[identity.applicability.kind],
  identity.rights.status !== 'unresolved' && RIGHTS[identity.rights.status]
].filter(Boolean)

/**
 * A card's chips. They sit inside buttons, where a list would be flattened anyway, so the
 * separators are text a screen reader hears and the page does not show.
 */
const Chips = ({ labels, title }) => labels.length > 0 && (
  <span className="gallery__chips" title={title}>
    {labels.map((label, index) => (
      <span key={label} className="gallery__chip">
        {index > 0 && <span className="visually-hidden">, </span>}
        {label}
      </span>
    ))}
  </span>
)

const IdentityChips = ({ identity }) => (
  <Chips labels={chipsOf(identity)} title={FIDELITY[identity.fidelity]} />
)

/** The four classifications as a definition list, one sentence or a few each. */
const Facts = ({ rows }) => (
  <dl className="gallery__facts">
    {rows.map(([term, detail]) => (
      <div key={term}>
        <dt>{term}</dt>
        <dd>{detail}</dd>
      </div>
    ))}
  </dl>
)

/** The fuller account, under a mark that is open, with how this page draws it where that is said. */
export const AboutMark = ({ identity, drawing }) => identity && (
  <section className="panel gallery__about" aria-labelledby="about-mark">
    <h2 id="about-mark">About this mark</h2>
    <Facts rows={[...Object.entries(sentencesOf(identity)), ...(drawing ? [['Drawing', drawing]] : [])]} />
  </section>
)

const listOf = (names) => names.length < 3
  ? names.join(' and ')
  : `${names.slice(0, -1).join(', ')} and ${names.at(-1)}`

/**
 * Who a sentence applies to, in a collection: whole eras by their names, and marks left over by
 * theirs, so BC Hydro's reads "The Rimmer signature" rather than seven signatures one by one.
 */
const whoOf = (collection, entries) => {
  const ids = new Set(entries.map((entry) => entry.id))
  const names = []
  for (const era of collection.eras ?? []) {
    if (era.entries.length && era.entries.every((entry) => ids.has(entry.id))) {
      names.push(era.label)
      era.entries.forEach((entry) => ids.delete(entry.id))
    }
  }
  return listOf([...names, ...entries.filter((entry) => ids.has(entry.id)).map((entry) => entry.label)])
}

/**
 * The account for a whole collection, one classification at a time: a sentence that holds for
 * every mark is said once, and one that differs is said for each group it holds for.
 */
export const AboutCollection = ({ collection }) => {
  const entries = entriesOf(collection)
  const terms = [...new Set(entries.flatMap((entry) => Object.keys(sentencesOf(entry.identity))))]
  const rows = terms.map((term) => {
    const groups = new Map()
    for (const entry of entries) {
      const sentence = sentencesOf(entry.identity)[term]
      if (sentence === undefined) continue
      groups.set(sentence, [...(groups.get(sentence) ?? []), entry])
    }
    const detail = groups.size === 1
      ? [...groups.keys()][0]
      : (
        <ul className="gallery__facts-groups">
          {[...groups].map(([sentence, group]) => (
            <li key={sentence}><span className="gallery__facts-who">{whoOf(collection, group)}.</span> {sentence}</li>
          ))}
        </ul>
        )
    return [term, detail]
  })
  // Closed at first: the cards already carry the short form, and this is the long one.
  return (
    <section className="panel gallery__about" aria-labelledby="gallery-about-title">
      <h2 id="gallery-about-title">{entries.length === 1 ? 'About this mark' : 'About these marks'}</h2>
      <Disclosure summary="Provenance, fidelity, dates and rights">
        <Facts rows={rows} />
      </Disclosure>
    </section>
  )
}

/**
 * Where a collection's marks came from — the one provenance they share, or that they do not share
 * one — as the card's tooltip. The collection's own page says it in full.
 */
const collectionProvenance = (collection) => {
  const provenances = new Set(entriesOf(collection).map((entry) => PROVENANCE[entry.identity.provenance]))
  if (!provenances.size) return undefined
  return provenances.size === 1 ? [...provenances][0] : 'Mixed provenance'
}

/** One mark, opened: its colours editable, its arrangement not. */
const Detail = ({ entry, onClose }) => {
  const [white, setWhite] = useState(false)
  const [colours, setColours] = useState(entry.presets[0])
  const change = (patch) => setColours((current) => ({ ...current, ...patch }))
  const matches = (preset) => samePreset(preset, colours)

  return (
    <section className="panel gallery__detail">
      <div className="gallery__head">
        <h2>{entry.label}</h2>
        {onClose && <button type="button" className="button button--ghost" onClick={onClose}>Back</button>}
      </div>
      <p className="gallery__note">{entry.note}</p>

      <div className="gallery__editor">
        <PreviewBackground white={white} onToggle={() => setWhite(!white)}>
          <span
            className="gallery__art gallery__art--large"
            role="img"
            aria-label={entry.label}
            // Built here from this project's own artwork; every value is escaped where written.
            dangerouslySetInnerHTML={{ __html: drawing(entry, colours) }}
          />
        </PreviewBackground>

        <div className="gallery__controls">
          <div className="field">
            <span className="field__label">Start from</span>
            <div className="segmented" role="group" aria-label="Starting colours">
              {entry.presets.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  aria-pressed={matches(preset)}
                  onClick={(event) => {
                    if (!matches(preset)) holdScrollFrom(event)
                    setColours(preset)
                  }}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          {entry.kind === 'artwork'
            ? <ArtworkControls entry={entry} colours={colours} change={change} />
            : <FlagControls colours={colours} change={change} />}
          <div className="row" style={{ marginTop: 12 }}>
            <button type="button" className="button" onClick={() => download(entry, colours)}>
              Download SVG
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

/**
 * A mark, opened, in the view its kind is edited in. Shared with Departmental Logos, so a mark
 * opens the same wherever its collection is shown.
 */
export const OpenMark = ({ entry, openId, onChooseVersion }) => {
  const editorVersion = entry.editorVersions?.find((version) => version.id === openId) ?? entry.editorVersions?.[0]
  if (entry.kind === 'hydro') return <HydroStudio initialPreset={entry.preset} />
  if (entry.kind === 'hydro-mark') {
    return <HydroMarkView key={openId} mark={entry.mark} variant={editorVersion?.variant ?? entry.variant} options={entry.editorVersions?.map((version) => version.variant)} />
  }
  if (entry.kind === 'supplied') return <SuppliedMarkView key={entry.id} entry={editorVersion ?? entry} family={entry} onChooseVersion={onChooseVersion} />
  if (entry.kind === 'collected') return <CollectedMarkView key={openId} entry={entry} />
  return <Detail key={entry.id} entry={entry} />
}

/**
 * A card in an era, with only the chips its era has not already said for every mark in it. Given the
 * mark's address (`href`), it is a link to it, which a plain click still opens through `onOpen`.
 */
export const Tile = ({ entry, onOpen, theme, said = [], owner, href }) => {
  const Control = href ? 'a' : 'button'
  const control = href
    ? { href, onClick: (event) => { if (!isPlainClick(event)) return; event.preventDefault(); onOpen() } }
    : { type: 'button', onClick: onOpen }
  return (
  <Control {...control} className="gallery__pick gallery__pick--tile" aria-label={`Open ${entry.label}${owner ? `, ${owner}` : ''}`}>
    <span
      className="gallery__art"
      data-ground={onPage(entry, theme) ? 'page' : 'own'}
      // Built by this project's own renderers; every value is escaped where written.
      dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }}
    />
    {owner && <span className="gallery__owner">{owner}</span>}
    <span className="gallery__label">{entry.label}{entry.kind === 'collected' && <span className="gallery__asset-format"> · {defaultCollectedAsset(entry, theme).format.toUpperCase()}</span>}</span>
    <span className="gallery__note">{owner ? entry.years : entry.note}</span>
    <Chips labels={[...(entry.markRole ? [MARK_ROLE_LABELS[entry.markRole]] : []), ...chipsOf(entry.identity).filter((label) => !said.includes(label))]} title={FIDELITY[entry.identity.fidelity]} />
  </Control>
  )
}

/** The mark already open, on its own timeline: drawn as its tile is, but not a way to itself. */
const ThisMark = ({ entry, theme }) => (
  <div className="gallery__pick gallery__pick--tile gallery__pick--this" aria-current="true">
    <span
      className="gallery__art"
      data-ground={onPage(entry, theme) ? 'page' : 'own'}
      // Built by this project's own renderers; every value is escaped where written.
      dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }}
    />
    <span className="gallery__label">{entry.label}</span>
    <span className="gallery__note">The mark open above.</span>
  </div>
)

/**
 * A one-off: a card of its own, with what it is beside it. One remade in the current identity is
 * drawn by the generator's current era, and opens there rather than in the gallery.
 */
const OneOffEntry = ({ entry, onOpen, theme, onOpenGovernment, said = [] }) => (
  <section className="panel gallery__entry">
    <div className="gallery__head">
      <h2>{entry.label}</h2>
      <span className="gallery__years">
        {entry.markRole && `${MARK_ROLE_LABELS[entry.markRole]} · `}
        {entry.years}
        {timelineOf(entry) && ` · ${timelineOf(entry).eras.length} eras`}
      </span>
    </div>
    {/* Two lines here; the mark's own page has the rest. */}
    <p className="gallery__note gallery__note--clamped" title={entry.note}>{entry.note}</p>
    {/* A collected file's dates are the line above, so its card does not say them twice; nor does a
        card repeat a chip every card in its collection carries. */}
    <Chips
      labels={chipsOf(entry.identity).filter((label) => !said.includes(label) && (entry.kind !== 'collected' || label !== APPLICABILITY[entry.identity.applicability.kind]))}
      title={FIDELITY[entry.identity.fidelity]}
    />

    <button
      type="button"
      className={entry.kind === 'flag' ? 'gallery__pick' : 'gallery__pick gallery__pick--wide'}
      onClick={onOpen}
      aria-label={`Open ${entry.label}`}
    >
      <span
        className="gallery__art"
        data-ground="page"
        dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }}
      />
      {/* Only a mark that opens somewhere else says so; every other card opens here. */}
      {entry.kind === 'current' && <span className="gallery__label">Open in the generator</span>}
    </button>
    <GraphLink node={entry.graphNode} onOpenGovernment={onOpenGovernment} />
  </section>
)

/** A card for a whole collection on the gallery's first page: its cover mark, whose it is, how many. */
const isPlainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
const collectionHref = (id) => `?view=gallery&logos=${encodeURIComponent(id)}`

export const CollectionCard = ({ collection, onOpen, theme, href, coverEntry, children }) => {
  const entries = entriesOf(collection)
  const specimen = !coverEntry && collection.shelfSpecimen && entries.find((entry) => entry.id === collection.shelfSpecimen)
  const cover = coverEntry || specimen || findGalleryEntry(collection.cover) || entries[0]
  const count = entries.length
  const fileCount = collection.fileCollection ? entries.reduce((total, entry) => total + (entry.versions?.length || 1), 0) : 0
  const Control = href ? 'a' : 'button'
  const controlProps = href ? { href } : { type: 'button', id: `collection-card-${collection.id}` }
  return (
    <Control {...controlProps} className="gallery__collection" onClick={(event) => {
      if (href && !isPlainClick(event)) return
      if (href) event.preventDefault()
      onOpen()
    }} aria-label={`Open ${collection.label}`} title={collectionProvenance(collection)}>
      <span
        className="gallery__art gallery__art--cover"
        data-ground="page"
        // Built by this project's own renderers; every value is escaped where written.
        dangerouslySetInnerHTML={{ __html: tileArt(cover, theme, { cover: true }) }}
      />
      <span className="gallery__collection-text">
        <span className="gallery__collection-title">{collection.label}</span>
        <span className="gallery__note">{collection.body}</span>
        {specimen && <span className="gallery__note gallery__specimen">{specimen.label} · {specimen.years}</span>}
        {/* A collection holding only secondary marks shows one, and says what it is. */}
        {!specimen && cover?.markRole && <span className="gallery__note gallery__specimen">{MARK_ROLE_LABELS[cover.markRole]}</span>}
        <span className="gallery__years">
          {collection.years} · {collection.fileCollection ? `${fileCount} artwork ${fileCount === 1 ? 'file' : 'files'}` : `${count} ${count === 1 ? 'mark' : 'marks'}`}
          {collection.eras ? ` · ${collection.eras.length} ${collection.eras.length === 1 ? 'era' : 'eras'}` : ''}
        </span>
        {children}
      </span>
    </Control>
  )
}

const historyLabels = {
  replaced: { predecessors: 'Replaced', successors: 'Replaced by' },
  merger: { predecessors: 'Formed by merger', successors: 'Merged to form' },
  'legal-rename': { predecessors: 'Previous legal name', successors: 'Renamed' },
  'registered-name': { predecessors: 'Former name of the same society', successors: 'Society continued as' },
  renamed: { predecessors: 'Former operating name', successors: 'Operating name adopted' },
  amalgamated: { predecessors: 'Amalgamated into this authority', successors: 'Amalgamated into' },
  services: { predecessors: 'Services received from', successors: 'Services transferred to' },
  territory: { predecessors: 'Territory reassigned', successors: 'Former service area moved to' },
  ministry: { predecessors: 'Earlier ministry, renamed into this one', successors: 'Renamed into' }
}

const isTimelineRename = (row) => row.type === 'registered-name' && row.collection

const HistoryCollectionLink = ({ row, onChooseCollection, className, children }) => (
  <a className={className} href={collectionHref(row.collection.id)} onClick={(event) => {
    if (!isPlainClick(event)) return
    event.preventDefault()
    onChooseCollection(row.collection.id)
  }}>{children}</a>
)

/**
 * A collection's predecessors and successors, in the site's shared lineage (site/Lineage.jsx). The
 * other body opens at its collection, else its ministry in the atlas, else its register entry; the
 * first two with collections also show their covers where the page asks for previews.
 */
export const GalleryHistory = ({ id, theme, onChooseCollection, onOpenSubject, showPreviews = false, successorsOnly = false, hasTimeline = false }) => {
  const history = galleryHistoryOf(id)
  const predecessors = successorsOnly ? [] : history.predecessors.filter((row) => !(hasTimeline && isTimelineRename(row)))
  const successors = history.successors.filter((row) => !(hasTimeline && isTimelineRename(row)))
  if (!predecessors.length && !successors.length) return null
  const records = (rows, direction) => rows.map((row, at) => ({
    key: `${row.type}:${row.id}:${row.date}`,
    name: row.collection
      ? <HistoryCollectionLink row={row} onChooseCollection={onChooseCollection}>{row.label}</HistoryCollectionLink>
      : row.graphNode
        ? <SiteLink to={{ view: 'government', node: row.graphNode, year: row.graphYear }}>{row.label}</SiteLink>
        : <SubjectLink id={row.id} onOpen={onOpenSubject}>{row.label}</SubjectLink>,
    relation: historyLabels[row.type][direction],
    date: formatEventDate({ start: row.date }),
    note: row.note,
    source: row.source,
    preview: showPreviews && row.collection && at < 2
      ? <CollectionCard collection={row.collection} theme={theme} href={collectionHref(row.collection.id)} onOpen={() => onChooseCollection(row.collection.id)} />
      : undefined
  }))
  return (
    <section className="gallery__shelf" aria-labelledby={`history-${id}`}>
      <h2 id={`history-${id}`} className="gallery__shelf-title">{successorsOnly ? 'Successors' : 'Predecessors and successors'}</h2>
      <Lineage predecessors={records(predecessors, 'predecessors')} successors={records(successors, 'successors')} />
    </section>
  )
}

/** Where an era's dates and description come from, each a link to the page it rests on. */
const Sources = ({ sources }) => sources?.length > 0 && (
  <p className="gallery__sources">
    <span>{sources.length === 1 ? 'Source' : 'Sources'}:</span>{' '}
    {sources.map((source, index) => (
      <span key={source.url ?? source.title}>
        {index > 0 && '; '}
        {/* A printed source not found online is named, with no link. */}
        {source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a> : <cite>{source.title}</cite>}
        {source.locator && <span className="gallery__sources-locator">, {source.locator}</span>}
      </span>
    ))}
  </p>
)

const TimelineRenames = ({ rows, direction, onChooseCollection }) => rows.filter(isTimelineRename).map((row) => (
  <li key={row.id}>
    <HistoryCollectionLink className="gallery__timeline-link" row={row} onChooseCollection={onChooseCollection}>
      <span className="gallery__timeline-years">{row.collection.years}</span>
      <span className="gallery__timeline-label">{row.label}</span>
      <span className="gallery__timeline-count">{direction === 'predecessors' ? 'Previous name' : 'Next name'}</span>
    </HistoryCollectionLink>
  </li>
))

/**
 * A collection's eras in order, oldest first, as a rail across the top of its page. Each step is
 * the same width whatever its years: most of these dates are estimated or first seen, and a scale
 * would claim a precision they do not have. An era with no artwork keeps its place, drawn hollow,
 * because a gap in the gallery is not a gap in the body's history.
 */
export const Timeline = ({ eras, current, onPick, history, onChooseCollection, collectionId, opensCollection }) => {
  const steps = eras.length + [...history.predecessors, ...history.successors].filter(isTimelineRename).length
  // A rail of one step says only what the era's own heading below it says.
  if (steps < 2) return null
  const rail = (
    <nav className="gallery__timeline" aria-label="Eras, oldest first">
      <ol>
        <TimelineRenames rows={history.predecessors} direction="predecessors" onChooseCollection={onChooseCollection} />
        {eras.map((era) => (
          <li key={era.id} data-status={eraStatus(era)}>
            <a className="gallery__timeline-link" href={`${opensCollection ? collectionHref(collectionId) : ''}#era-${era.id}`}
              aria-current={era.id === current ? 'step' : undefined} onClick={(event) => {
                if (!isPlainClick(event)) return
                event.preventDefault()
                onPick(era.id)
              }}>
              <span className="gallery__timeline-years">{era.years}</span>
              <span className="gallery__timeline-label">{era.shortLabel ?? era.label}</span>
              <span className="gallery__timeline-count">{STATUS_COUNT[eraStatus(era)](era.entries.length)}</span>
            </a>
          </li>
        ))}
        <TimelineRenames rows={history.successors} direction="successors" onChooseCollection={onChooseCollection} />
      </ol>
    </nav>
  )
  return steps > 5
    ? <Disclosure className="gallery__timeline-index" summary="Jump to an era" hint={`${steps} steps`}>{rail}</Disclosure>
    : rail
}

/** What the rail says an era holds. */
const STATUS_COUNT = {
  held: (count) => `${count} ${count === 1 ? 'mark' : 'marks'}`,
  generator: () => 'In the generator',
  sought: () => 'No artwork yet',
  none: () => 'No mark of its own'
}

/** What stands where an era's marks would be, when the gallery has none to show. */
const EMPTY_SLOT = { generator: 'Drawn in the generator', sought: 'Not in the gallery yet', none: 'No mark of its own' }

/**
 * Where an era's mark can be seen outside the gallery — the artwork to obtain, or, beside a mark
 * the gallery holds, the pictures still to compare it with. Each is a picture, not a source for a
 * date, so they are listed apart from the sources.
 */
const SeenAt = ({ urls }) => urls?.length > 0 && (
  <p className="gallery__sources">
    <span>Artwork seen at:</span>{' '}
    {urls.map((url, index) => (
      <span key={url}>{index > 0 && '; '}<a href={url} target="_blank" rel="noreferrer">{hostOf(url)}</a></span>
    ))}
  </p>
)

/**
 * An era without marks in the gallery: for an identity the generator draws, that drawing, the mark
 * alone, and a way to it there; otherwise an empty slot where the marks would be, as a body on the
 * "not yet in the gallery" shelf has.
 */
const EmptyEra = ({ era, theme, onOpenInGenerator }) => {
  const art = eraStatus(era) === 'generator' ? generatorArt(era.generator, theme) : null
  return (
  <div className="gallery__era-missing">
    {art
      ? (
        <div
          className="gallery__art gallery__era-generator"
          data-ground="page"
          role="img"
          aria-label={`${era.label}, as the generator draws it`}
          // Built by this project's own renderers; every value is escaped where written.
          dangerouslySetInnerHTML={{ __html: art }}
        />
        )
      : <div className="gallery__wanted-slot" data-status={eraStatus(era)}>{EMPTY_SLOT[eraStatus(era)]}</div>}
    {era.generator && onOpenInGenerator && (
      <button type="button" className="gallery__graph-link" onClick={() => onOpenInGenerator(era.generator)}>
        Open in the generator <span aria-hidden="true">→</span>
      </button>
    )}
  </div>
  )
}

/**
 * A picture's link, named for the site it is on and the file it is — two files on one site would
 * otherwise read the same. A Wayback capture is named for the site it captured, and its year.
 */
const hostOf = (url) => {
  const { hostname, pathname } = new URL(url)
  const site = (host) => host.replace(/^www\d?\./, '')
  // A file name without the build hash a site stamps into it, which says nothing to a reader.
  const file = (path) => decodeURIComponent(path.split('/').filter(Boolean).at(-1) ?? '').replace(/-[0-9a-f]{16,}(?=\.)/, '')
  if (hostname === 'web.archive.org') {
    const captured = pathname.match(/^\/web\/(\d{4})\d*[a-z_]*\/(?:https?:\/\/)?([^/]+)(\/.*)?$/)
    if (captured) return `${site(captured[2])}, ${captured[1]} (Wayback Machine)${captured[3]?.length > 1 ? `: ${file(captured[3])}` : ''}`
  }
  return pathname.length > 1 ? `${site(hostname)}: ${file(pathname)}` : site(hostname)
}

/** What an era's dates rest on, in a sentence, for an era the identity records do not cover. */
const EraDates = ({ era }) => era.applicability && (
  <p className="gallery__era-dates">
    {APPLICABILITY[era.applicability.kind]}: {era.applicability.years}. {era.applicability.note}
  </p>
)

/** The chips every mark in an era shares, said once for the era rather than on each card. */
const eraChips = (entries) => entries.length === 0
  ? []
  : chipsOf(entries[0].identity).filter((label) => entries.every((entry) => chipsOf(entry.identity).includes(label)))

/** What an era's dates rest on and where its artwork was seen, folded under one line. */
const EraMore = ({ era }) => {
  const dated = Boolean(era.applicability)
  if (!dated && !era.seenAt?.length && !era.sources?.length) return null
  return (
    <Disclosure className="gallery__era-more" summary={dated ? 'Dates & sources' : 'Sources'}>
      <EraDates era={era} />
      <SeenAt urls={era.seenAt} />
      <Sources sources={era.sources} />
    </Disclosure>
  )
}

/**
 * One era: its name and years, what changed, what all its marks share, where that comes from, and
 * its marks — or the slot that stands for them — under the words, as every era has them. On a
 * mark's own timeline the open mark is marked as the one being looked at rather than offered again.
 */
export const EraSection = ({ era, theme, onOpen, openId, onOpenInGenerator, hrefFor }) => {
  const said = eraChips(era.entries)
  const fidelities = new Set(era.entries.map((entry) => entry.identity.fidelity))
  return (
    <section
      className="gallery__era"
      id={`era-${era.id}`}
      aria-labelledby={`${era.id}-heading`}
      data-current={era.entries.some((entry) => entry.id === openId) || undefined}
    >
      <div className="gallery__era-text">
        <div className="gallery__head">
          <h2 id={`${era.id}-heading`} tabIndex={-1}>{era.label}</h2>
          <span className="gallery__years">{era.years}</span>
        </div>
        <p className="gallery__note">{era.note}</p>
        <Chips labels={said} title={fidelities.size === 1 ? FIDELITY[[...fidelities][0]] : undefined} />
        <EraMore era={era} />
      </div>
      {era.entries.length > 0
        ? (
          <div className="gallery__tiles">
            {era.entries.map((entry) => entry.id === openId
              ? <ThisMark key={entry.id} entry={entry} theme={theme} />
              : <Tile key={entry.id} entry={entry} theme={theme} said={said} href={hrefFor?.(entry.id)} onOpen={() => onOpen(entry.id)} />)}
          </div>
          )
        : <EmptyEra era={era} theme={theme} onOpenInGenerator={onOpenInGenerator} />}
    </section>
  )
}

/** A link from a mark to the body it stands for, in the government diagram. */
export const GraphLink = ({ node, year, onOpenGovernment }) => node && onOpenGovernment && (
  <button type="button" className="gallery__graph-link" onClick={() => onOpenGovernment(node, year)}>
    Open in Government <span aria-hidden="true">→</span>
  </button>
)

/** A collection's page opens with its name, whose it is and its years, and a way to it in the atlas. */
export const CollectionHead = ({ collection, onOpenGovernment, headingRef }) => (
  <div className="gallery__collection-head">
    <div>
      <h2 className="gallery__collection-heading" ref={headingRef} tabIndex={headingRef ? -1 : undefined}>{collection.label}</h2>
      <p className="gallery__note">{collection.body} · {collection.years}</p>
    </div>
    <GraphLink node={collection.graphNode} year={collection.graphYear} onOpenGovernment={onOpenGovernment} />
  </div>
)

/**
 * A body whose mark has not been obtained. Deliberately unlike a mark's card: an outline with
 * nothing inside it where the artwork would be, and no way to open it, because there is nothing to
 * open. What it does carry is how far the search has got.
 */
const WantedCard = ({ item, onOpenGovernment }) => (
  <article className="gallery__wanted" aria-labelledby={`wanted-${item.id}`}>
    <div className="gallery__wanted-slot" aria-hidden="true">No artwork</div>
    <div className="gallery__collection-text">
      <h3 id={`wanted-${item.id}`} className="gallery__collection-title">{item.label}</h3>
      <span className="gallery__note">{item.body}</span>
    </div>
    <Facts
      rows={[
        ['Artwork', `No original artwork obtained. ${ASSET_STATUS[item.assetStatus]}.`],
        ['Verified', `${item.verified}.`],
        ['Next', item.nextAction],
        ['Contact', item.contact]
      ]}
    />
    <p className="gallery__caveat">{item.warning}</p>
    <GraphLink node={item.graphNode} onOpenGovernment={onOpenGovernment} />
  </article>
)

const readParam = (key) => new URLSearchParams(globalThis.location?.search ?? '').get(key)

/** The collection in the address bar — or, for a link to a mark alone, the one that holds it. */
const readCollection = () => {
  // A link to a body's collection from before it was folded into a later name's still opens there.
  const named = collectionById(readParam('logos'))
  if (named) return named.id
  const mark = findGalleryEntry(readParam('mark'))
  return GALLERY_COLLECTIONS.find((collection) => entriesOf(collection).some((entry) => entry.id === mark?.id))?.id ?? null
}

// A mark remade in the current identity opens in the generator, not here, so it is never the open one.
const readMark = () => {
  const requested = readParam('mark')
  const entry = requested && findGalleryEntry(requested)
  return entry && entry.kind !== 'current' ? requested : null
}

/**
 * Where the gallery is lives in the address bar — the collection, and the mark open in it — so a
 * link to BC Hydro's page, or to one of its signatures, opens there.
 */
const writePlace = (collection, mark, subject, coverage, filters, browse) => {
  if (globalThis.location) writeHistory(galleryPlaceUrl(globalThis.location.href, { collection, mark, subject, coverage, filters, browse }))
}

/** The first page's way through the logos, and the timeline's year, as the address bar has them. */
const readMode = () => (isGalleryMode(readParam('gallery-mode')) ? readParam('gallery-mode') : '')
const readYear = () => {
  const year = Number(readParam('gallery-year'))
  return Number.isInteger(year) && year > 1800 && year <= PRESENT_YEAR ? year : PRESENT_YEAR
}

/**
 * The trail leads back from a mark through its collection and the organization it belongs to.
 */
const Crumbs = ({ collection, entry, onHome, onCollection, onChooseCollection }) => {
  const parent = collectionById(collection?.foldedUnder)
  const markShown = entry && collection && hasPage(collection)
  return (
    <Breadcrumbs label="Gallery" steps={[
      { label: 'All logos', onClick: onHome },
      ...(collection?.shelf === 'airports' ? [{ label: 'Airports', to: { view: 'airports' } }] : []),
      ...(parent ? [{ label: parent.label, title: parent.label, onClick: () => onChooseCollection(parent.id) }] : []),
      ...(collection ? [{ label: collection.label, title: collection.label, onClick: onCollection }] : []),
      ...(markShown ? [{ label: entry.label }] : [])
    ]} />
  )
}

/**
 * Whether a collection has multiple marks, its own history, or organizational links to show.
 */
const hasPage = (collection) => collection.shelf === 'regional-districts' || Boolean(collection.eras) || entriesOf(collection).length > 1 ||
  childCollectionsOf(collection.id).length > 0 || Boolean(supportProvidedBy(collection.graphNode)) || hasGalleryHistory(collection.historyId ?? collection.graphNode)


/**
 * @param {object} props
 * @param {(nodeId: string) => void} [props.onOpenGovernment]  Opens the government diagram at a body.
 * @param {(patch: object) => void} [props.onOpenInGenerator]  Loads a patch into the generator and
 *   shows it — how a mark remade in the current identity opens.
 */
const IS_MAC = /Mac|iPhone|iPad/.test(globalThis.navigator?.platform ?? globalThis.navigator?.userAgent ?? '')

/** The gallery's search box, with its shortcut shown where there is a keyboard to press it on. */
const GallerySearch = ({ query, onChange, inputRef }) => (
  <div className="gallery__search">
    <input
      ref={inputRef}
      type="search"
      value={query}
      placeholder="Search logos and identities…"
      aria-label="Search the logos"
      aria-keyshortcuts={IS_MAC ? 'Meta+K' : 'Control+K'}
      onChange={(event) => onChange(event.target.value)}
      onKeyDown={(event) => {
        if (event.key === 'Escape' && query) { event.preventDefault(); onChange('') }
      }}
    />
    {query
      ? (
        <button
          type="button"
          className="gallery__search-clear"
          aria-label="Clear the search"
          onClick={() => { onChange(''); inputRef?.current?.focus() }}
        >
          <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M3.5 3.5l7 7m0-7l-7 7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" /></svg>
        </button>
        )
      : <kbd className="gallery__search-key" aria-hidden="true">{IS_MAC ? '⌘K' : 'Ctrl K'}</kbd>}
  </div>
)

const GalleryTypeFilters = ({ value, onChange }) => {
  const rowRef = useRef(null)
  const [canScrollBack, setCanScrollBack] = useState(false)
  const [canScrollForward, setCanScrollForward] = useState(false)

  useLayoutEffect(() => {
    const row = rowRef.current
    const updateArrows = () => {
      setCanScrollBack(row.scrollLeft > 1)
      setCanScrollForward(row.scrollWidth - row.clientWidth - row.scrollLeft > 1)
    }
    updateArrows()
    row.addEventListener('scroll', updateArrows, { passive: true })
    const resize = new ResizeObserver(updateArrows)
    resize.observe(row)
    return () => {
      resize.disconnect()
      row.removeEventListener('scroll', updateArrows)
    }
  }, [])

  useLayoutEffect(() => {
    const row = rowRef.current
    const active = row.querySelector('[aria-pressed="true"]')
    const start = active.offsetLeft - 3
    const end = start + active.offsetWidth + 6
    if (start < row.scrollLeft) row.scrollLeft = start
    else if (end > row.scrollLeft + row.clientWidth) row.scrollLeft = end - row.clientWidth
  }, [value])

  const slide = (direction) => {
    const row = rowRef.current
    row.scrollBy({
      left: direction * row.clientWidth * 0.75,
      behavior: globalThis.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
    })
  }

  return (
    <div className="gallery__filters" role="group" aria-label="Organization type">
      <button type="button" className="gallery__filter-arrow" aria-label="Scroll to previous categories"
        aria-disabled={!canScrollBack} onClick={() => canScrollBack && slide(-1)}>
        <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="m10 4-4 4 4 4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
      </button>
      <div className="gallery__filter-row" ref={rowRef}>
        {GALLERY_TYPE_OPTIONS.map((option) => (
          <button key={option.value} type="button" className="gallery__filter-chip" aria-pressed={value === option.value}
            onClick={() => onChange(option.value)}>
            {option.label}
          </button>
        ))}
      </div>
      <button type="button" className="gallery__filter-arrow" aria-label="Scroll to more categories"
        aria-disabled={!canScrollForward} onClick={() => canScrollForward && slide(1)}>
        <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="m6 4 4 4-4 4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
      </button>
    </div>
  )
}

const GalleryCategory = ({ section, theme, onChooseCollection, onOpenRegister, onOpenSubject }) => {
  const { value, label, collections, records } = section
  const recordCount = `${records.length} identity ${records.length === 1 ? 'record' : 'records'}`
  const recordsLabel = `View ${recordCount} for ${label}`
  const direct = collections.filter((entry) => !entry.foldedUnder)
  const cnc = records.find(({ id }) => id === CNC_SUBJECT)
  const cards = (entries, subject) => (
    <div className="gallery__collections">
      {entries.map((entry) => (
        <CollectionCard key={entry.id} collection={entry} theme={theme} onOpen={() => onChooseCollection(entry.id)} />
      ))}
      {subject && <CncIdentityCard subject={subject} onOpen={onOpenSubject} theme={theme} />}
    </div>
  )
  const ids = new Set(collections.map(({ id }) => id))
  return (
    <section className="gallery__shelf gallery__category" aria-labelledby={`category-${value}`}>
      <div className="gallery__category-head">
        <h2 id={`category-${value}`} className="gallery__category-title">{label}</h2>
        {value === 'airports' && <SiteLink className="gallery__category-records-link" to={{ view: 'airports' }}>Airport directory</SiteLink>}
        {records.length > 0 && (
          <a
            className="gallery__category-records-link"
            href={`?view=gallery&coverage=1&identity-category=${encodeURIComponent(value)}`}
            aria-label={recordsLabel}
            title={recordsLabel}
            onClick={(event) => {
              if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
              event.preventDefault()
              onOpenRegister({ category: value })
            }}
          >
            <svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M6 3h6l3 3v11H5V3h1Zm6 0v4h3M8 10h4m-4 3h4" />
            </svg>
            {!collections.length && <span>{recordCount}</span>}
          </a>
        )}
      </div>
      {value === 'local' && (
        <p className="gallery__intro gallery__shelf-intro">
          The <a href="?view=gallery&coverage=1&identity-family=municipalities" onClick={(event) => {
            if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
            event.preventDefault()
            onOpenRegister({ family: 'municipalities' })
          }}>municipal register</a> lists official sources and artwork still wanted.
        </p>
      )}
      {value === 'regional-districts' && (
        <p className="gallery__intro gallery__shelf-intro">
          Explore district logos, historical artwork and member municipalities in the <a href="?view=gallery&coverage=1&identity-family=regional-districts" onClick={(event) => {
            if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
            event.preventDefault()
            onOpenRegister({ family: 'regional-districts' })
          }}>regional districts register</a>.
        </p>
      )}
      {(direct.length > 0 || cnc) && cards(direct, cnc)}
      {FOLDED_GROUPS.map(({ parent, children }) => {
        const inCategory = children.filter(({ id }) => ids.has(id))
        return inCategory.length > 0 && (
          <div key={parent.id} className="gallery__group">
            <h3 className="gallery__group-title">
              <button type="button" className="gallery__group-link" onClick={() => onChooseCollection(parent.id)}>{parent.label} →</button>
            </h3>
            {cards(inCategory)}
          </div>
        )
      })}
    </section>
  )
}

const BrowseResults = ({ query, type, theme, onChooseCollection, onOpenMark, onOpenSubject }) => {
  const { collections, marks, subjects } = browseGallery(query, type)
  if (!collections.length && !marks.length && !subjects.length) {
    return <p className="gallery__intro gallery__search-none" role="status">
      {`Nothing found for “${query.trim()}”${type ? ' in this organization type' : ''}.`}
    </p>
  }
  const identityResults = <IdentitySearchResults subjects={subjects} onOpen={onOpenSubject} theme={theme} />
  return (
    <>
      {!type && identityResults}
      {collections.length > 0 && (
        <section className="gallery__shelf" aria-labelledby="search-collections">
          <h2 id="search-collections" className="gallery__shelf-title">
            {collections.length === 1 ? '1 collection' : `${collections.length} collections`}
          </h2>
          <div className="gallery__collections">
            {collections.map((entry) => (
              <CollectionCard key={entry.id} collection={entry} theme={theme} onOpen={() => onChooseCollection(entry.id)} />
            ))}
          </div>
        </section>
      )}
      {marks.length > 0 && (
        <section className="gallery__shelf" aria-labelledby="search-marks">
          <h2 id="search-marks" className="gallery__shelf-title">
            {marks.length === 1 ? '1 logo' : `${marks.length} logos`}
          </h2>
          <div className="gallery__tiles">
            {marks.map(({ entry, collection }) => (
              <Tile key={entry.id} entry={entry} theme={theme} onOpen={() => onOpenMark(collection.id, entry)} />
            ))}
          </div>
        </section>
      )}
      {type && identityResults}
    </>
  )
}

export const GalleryView = ({ onOpenGovernment, onOpenInGenerator }) => {
  const { name: theme } = useSiteTheme()
  const [collectionId, setCollectionId] = useState(readCollection)
  const [openId, setOpenId] = useState(readMark)
  const [subjectId, setSubjectId] = useState(() => readParam('subject'))
  const [showCoverage, setShowCoverage] = useState(() => readParam('coverage') === '1')
  const [mode, setMode] = useState(readMode)
  const [year, setYear] = useState(readYear)
  const open = openId && findGalleryEntry(openId)
  const editorVersion = open?.editorVersions?.find((version) => version.id === openId) ?? open?.editorVersions?.[0]
  const collection = collectionById(collectionId)
  const subject = identitySubjectById(subjectId)

  const navigate = useNavigate()

  // Going back — to all the logos, or from a mark to its collection — returns to where that page was
  // scrolled to when it was left, so the card just opened is where it was. A page not yet seen this
  // visit (one reached by a link) opens at its top, or for all the logos, at the card come back from.
  const scrolled = useRef(new Map())
  const [arrival, setArrival] = useState(null)
  const pageKey = (collection, mark, subject, coverage) => subject ? `subject/${subject}` : coverage ? 'coverage' : `${collection ?? ''}/${mark ?? ''}`
  const go = (nextCollection, nextMark, nextSubject = null, coverage = false, filters) => {
    const moved = movedGalleryPlace({ view: 'gallery', logos: nextCollection, mark: nextMark, subject: nextSubject, coverage })
    if (moved) {
      if (navigate) navigate(moved)
      else globalThis.location.assign(`?${new URLSearchParams(moved)}`)
      return
    }
    scrolled.current.set(pageKey(collectionId, openId, subjectId, showCoverage), globalThis.scrollY ?? 0)
    setCollectionId(nextCollection)
    setOpenId(nextMark)
    setSubjectId(nextSubject)
    setShowCoverage(coverage)
    writePlace(nextCollection, nextMark, nextSubject, coverage, filters, { mode, year })
    setArrival({ from: collectionId, key: pageKey(nextCollection, nextMark, nextSubject, coverage) })
  }
  // App remounts views on history navigation; the listener also makes the standalone review work.
  useEffect(() => {
    const restore = () => {
      setCollectionId(readCollection()); setOpenId(readMark())
      setSubjectId(readParam('subject')); setShowCoverage(readParam('coverage') === '1')
      setMode(readMode()); setYear(readYear())
    }
    globalThis.addEventListener?.('popstate', restore)
    return () => globalThis.removeEventListener?.('popstate', restore)
  }, [])
  useLayoutEffect(() => {
    if (!arrival) return
    const saved = scrolled.current.get(arrival.key)
    const card = arrival.key === '/' && arrival.from ? document.getElementById(`collection-card-${arrival.from}`) : null
    if (saved !== undefined) globalThis.scrollTo?.({ top: saved })
    else if (card) card.scrollIntoView({ block: 'center' })
    else globalThis.scrollTo?.({ top: 0 })
    setArrival(null)
  }, [arrival])
  // A standalone mark opens directly.
  const choose = (id, era, mark) => {
    const chosen = GALLERY_COLLECTIONS.find((candidate) => candidate.id === id)
    const only = chosen && !hasPage(chosen) ? entriesOf(chosen)[0].id : null
    go(id, mark ?? only)
    if (era) setEraTarget(era)
  }
  const openMark = (id) => {
    const entry = findGalleryEntry(id)
    if (entry?.kind === 'current' && onOpenInGenerator) onOpenInGenerator({ era: 'current', currentName: entry.text })
    else go(collectionId, id)
  }
  const home = () => go(null, null)
  const openSubject = (id) => go(null, null, id)
  const openRegister = (filters) => go(null, null, null, true, filters)

  // Search, on the first page. Cmd-K (Ctrl-K elsewhere) reaches it from any page of the gallery.
  const [query, setQuery] = useState('')
  const [organizationType, setOrganizationType] = useState('')
  const sections = useMemo(() => gallerySections(organizationType), [organizationType])
  // The mode and year change the page in place, so they replace the address rather than add to it.
  const replaceBrowse = (browse) => {
    if (globalThis.location) writeHistory(galleryPlaceUrl(globalThis.location.href, { browse }), { replace: true })
  }
  const pickYear = useCallback((value) => {
    setYear(value)
    replaceBrowse({ mode: 'timeline', year: value })
  }, [])
  const browsePage = useRef(null)
  const searchInput = useRef(null)
  const scrollToBrowseResults = () => {
    const top = browsePage.current?.getBoundingClientRect().top
    if (top < 0) globalThis.scrollBy({ top, behavior: 'instant' })
  }
  const [focusSearch, setFocusSearch] = useState(false)
  useEffect(() => {
    const onKey = (event) => {
      if (!isSearchShortcut(event)) return
      event.preventDefault()
      if (collectionId || openId || subjectId || showCoverage) go(null, null)
      setFocusSearch(true)
    }
    globalThis.addEventListener?.('keydown', onKey)
    return () => globalThis.removeEventListener?.('keydown', onKey)
  })
  useEffect(() => {
    if (!focusSearch || !searchInput.current) return
    searchInput.current.focus()
    searchInput.current.select()
    setFocusSearch(false)
  }, [focusSearch, collectionId, openId, subjectId, showCoverage])
  const openFound = (id, entry) => {
    if (entry.kind === 'current' && onOpenInGenerator) onOpenInGenerator({ era: 'current', currentName: entry.text })
    else go(id, entry.id)
  }
  const backToCollection = () => go(collectionId, null)
  const crumbs = <Crumbs collection={collection} entry={open} onHome={home} onCollection={backToCollection} onChooseCollection={choose} />

  // The eras a page puts on its rail: its collection's, or — for one of the Province's one-offs,
  // whose collection is not a history — the timeline of the body the open mark belongs to.
  const historyOwner = subject?.id ?? open?.owner ?? collection?.historyId ?? collection?.graphNode
  const safetyHistory = (historyOwner === 'bc-safety-authority' || historyOwner === 'technical-safety-bc')
    && <SafetyAuthorityHistory onChooseCollection={choose} />
  const councilTimeline = COUNCIL_TIMELINE_OWNERS.has(historyOwner)
    && <CouncilTimeline theme={theme} onChooseCollection={choose} />
  const markTimeline = open && !collection?.eras ? timelineOf(open) : undefined
  const initiativeId = collection?.initiativeId ?? markTimeline?.initiativeId
  const eras = collection?.eras ?? markTimeline?.eras

  const [eraTarget, setEraTarget] = useState(null)
  useLayoutEffect(() => {
    const hash = subjectId ? '' : globalThis.location.hash
    const id = eraTarget ? `era-${eraTarget}` : hash?.startsWith('#era-') ? hash.slice(1) : null
    const section = id && document.getElementById(id)
    if (section) {
      if (eraTarget) {
        const url = new URL(globalThis.location.href)
        url.hash = id
        writeHistory(url, { replace: true })
      }
      document.getElementById(section.getAttribute('aria-labelledby'))?.focus({ preventScroll: true })
      section.scrollIntoView({ block: 'start' })
    }
    if (eraTarget) setEraTarget(null)
  }, [eraTarget, openId, collectionId, subjectId])
  const pickEra = (id) => {
    if (open && !document.getElementById(`era-${id}`)) go(collectionId, null)
    setEraTarget(id)
  }
  const timeline = eras && (
    <Timeline key={collectionId} eras={eras} collectionId={collectionId} opensCollection={Boolean(open && !markTimeline)}
      history={galleryHistoryOf(collection?.historyId ?? collection?.graphNode)} onChooseCollection={choose}
      current={open ? eras.find((each) => each.entries.some((entry) => entry.id === open.id))?.id : undefined} onPick={pickEra} />
  )
  const eraSection = (era) => (
    <EraSection key={era.id} era={era} theme={theme} onOpen={openMark} openId={openId} onOpenInGenerator={onOpenInGenerator} />
  )

  if (subject) return <div className="gallery">
    <IdentitySubjectDetail subject={subject} theme={theme} onHome={home} onOpenRegister={openRegister} onOpenSubject={openSubject}
      onChooseCollection={choose} onOpenGovernment={onOpenGovernment}>
      <SupportProvided onChooseCollection={choose} id={subject.id} />
      <RuralHealthConnections id={subject.id} />
      <GalleryHistory id={subject.id} theme={theme} onChooseCollection={choose} onOpenSubject={openSubject} />
      {safetyHistory}
      {councilTimeline}
    </IdentitySubjectDetail>
  </div>
  if (showCoverage || subjectId) return <div className="gallery"><IdentityCoverageBrowser onHome={home} onOpenSubject={openSubject} /></div>

  if (open) {
    return (
      <div className="gallery">
        {crumbs}
        {/* A mark with its own history below lists the same eras there; the rail would say them twice. */}
        {!markTimeline && timeline}
        <UnbcOriginsTeaser owner={open.owner} />
        <OpenMark entry={open} openId={openId} onChooseVersion={(id) => go(collectionId, id)} />
        {markTimeline && (
          <section className="gallery__history" aria-labelledby="mark-history">
            <h2 id="mark-history" className="gallery__shelf-title">{markTimeline.label} through time</h2>
            {markTimeline.eras.map(eraSection)}
          </section>
        )}
        <RailwayHistory history={collection?.railwayHistory} compact />
        {initiativeId && <InitiativeLink id={initiativeId} />}
        <IdentityCollectionLinks collectionId={collection?.id} entryId={open.id} onOpenCollection={choose} onOpenSubject={openSubject} onOpenGovernment={onOpenGovernment} />
        <GalleryHistory hasTimeline={Boolean(eras && !markTimeline)} id={collection?.historyId ?? open.owner ?? collection?.graphNode} theme={theme} onChooseCollection={choose} onOpenSubject={openSubject} successorsOnly />
        <SupportProvided onChooseCollection={choose} id={open.owner ?? collection?.graphNode} />
        <RuralHealthConnections id={open.owner ?? collection?.graphNode} />
        {safetyHistory}
        {councilTimeline}
        <AboutMark identity={editorVersion?.identity ?? open.identity} drawing={open.caveat} />
      </div>
    )
  }

  if (!collection) {
    return (
      <div className="gallery" ref={browsePage}>
        <GalleryModeSwitch value={mode} onChange={(value) => {
          if (value === mode) return
          setMode(value)
          replaceBrowse({ mode: value, year })
        }} />
        <div className="gallery__toolbar" role="search" aria-label="Filter the logo gallery">
          <GallerySearch query={query} inputRef={searchInput} onChange={(value) => {
            scrollToBrowseResults()
            setQuery(value)
          }} />
          <GalleryTypeFilters value={organizationType} onChange={(value) => {
            if (value === organizationType) return
            scrollToBrowseResults()
            setOrganizationType(value)
          }} />
          {mode === 'timeline' && !query.trim() && <TimelineScrubber sections={sections} year={year} onYear={pickYear} />}
        </div>
        {query.trim()
          ? <BrowseResults query={query} type={organizationType} theme={theme} onChooseCollection={choose} onOpenMark={openFound} onOpenSubject={openSubject} />
          : mode === 'all'
            ? <AllLogos sections={sections} theme={theme} onOpenMark={openFound} />
            : mode === 'current'
              ? <CurrentOrganizations sections={sections} theme={theme} onChooseCollection={choose} />
              : mode === 'timeline'
                ? <GalleryTimeline sections={sections} year={year} theme={theme} onOpenMark={openFound} />
                : (
            <>
              {!organizationType && <IdentityCoverageOverview onOpenRegister={openRegister} />}
              {sections.map((section) => (
                <GalleryCategory
                  key={section.value}
                  section={section}
                  theme={theme}
                  onChooseCollection={choose}
                  onOpenRegister={openRegister}
                  onOpenSubject={openSubject}
                />
              ))}
              {!organizationType && WANTED.length > 0 && (
                <section className="gallery__shelf" aria-labelledby="shelf-wanted">
                  <h2 id="shelf-wanted" className="gallery__category-title">Not yet in the gallery</h2>
                  <p className="gallery__intro gallery__shelf-intro">
                    Public bodies whose marks have been looked for and not obtained. None is drawn, because no
                    artwork for it has been verified; each says how far the search has got. From the research
                    companion’s logo routes, as of {WANTED_AS_OF}.
                  </p>
                  <div className="gallery__collections">
                    {WANTED.map((item) => <WantedCard key={item.id} item={item} onOpenGovernment={onOpenGovernment} />)}
                  </div>
                </section>
              )}
            </>
          )}
      </div>
    )
  }

  const children = childCollectionsOf(collection.id)
  const artworkSections = collection.artworkSections ?? []
  const groupedArtwork = new Set(artworkSections.flatMap(({ entries }) => entries))
  const ungroupedArtwork = collection.entries?.filter((entry) => !groupedArtwork.has(entry))
  const artworkList = (entries) => {
    const said = entries.length > 1 ? eraChips(entries) : []
    return (
      <div className="gallery__list">
        {entries.map((entry) => <OneOffEntry key={entry.id} entry={entry} theme={theme} said={said} onOpen={() => openMark(entry.id)} onOpenGovernment={onOpenGovernment} />)}
      </div>
    )
  }
  const artworkSectionList = (sections) => sections.some(({ entries }) => entries.length) && (
    <div className="gallery__artwork-sections">
      {sections.filter(({ entries }) => entries.length).map(({ id, label, entries }) => (
        <section key={id} className="gallery__shelf" aria-labelledby={`${id}-heading`} data-single={entries.length === 1 || undefined}>
          <h2 id={`${id}-heading`} className="gallery__shelf-title">{label}</h2>
          {artworkList(entries)}
        </section>
      ))}
    </div>
  )

  return (
    <div className="gallery">
      {crumbs}
      <CollectionHead collection={collection} onOpenGovernment={onOpenGovernment} />
      <p className="gallery__intro">{collection.intro}</p>
      {councilTimeline && <a className="gallery__graph-link" href="#council-timeline-heading">Organization and logo timeline ↓</a>}
      {collection.relatedGenerator && onOpenInGenerator && (
        <button type="button" className="gallery__graph-link" onClick={() => onOpenInGenerator({ era: collection.relatedGenerator.era })}>
          {collection.relatedGenerator.label} <span aria-hidden="true">→</span>
        </button>
      )}
      <UnbcOriginsTeaser owner={collection.entries?.[0]?.owner} />
      <IdentityCollectionLinks collectionId={collection.id} graphShown={collection.graphNode} history={galleryHistoryOf(collection.historyId ?? collection.graphNode)} onOpenCollection={choose} onOpenSubject={openSubject} onOpenGovernment={onOpenGovernment} />
      <RailwayHistoryLinks history={collection.railwayHistory} />

      {collection.initiativeId && <InitiativeLink id={collection.initiativeId} />}
      <GalleryHistory id={collection.historyId ?? collection.graphNode} theme={theme} onChooseCollection={choose} onOpenSubject={openSubject} hasTimeline={Boolean(eras)} showPreviews />

      {timeline}
      {collection.eras
        ? collection.eras.map(eraSection)
        : (
          <>
            {artworkSectionList(artworkSections.filter(({ secondary }) => !secondary))}
            {ungroupedArtwork?.length > 0 && artworkList(coverFirst(ungroupedArtwork, collection.shelfSpecimen))}
            {/* Anniversary, campaign, event and decorative marks follow the body's identity (markRoles.js). */}
            {artworkSectionList(artworkSections.filter(({ secondary }) => secondary))}
          </>
          )}
      {collection.shelf === 'regional-districts' && (
        <RegionalDistrictMembers subject={identitySubjectById(collection.entries[0]?.owner)} onOpenSubject={openSubject} />
      )}
      {children.length > 0 && (
        <section className="gallery__shelf gallery__children" aria-labelledby="collection-children">
          <h2 id="collection-children" className="gallery__shelf-title">Under {collection.label}</h2>
          <p className="gallery__intro gallery__shelf-intro">Its programs, services and subsidiaries with logos of their own.</p>
          <div className="gallery__collections">
            {children.map((entry) => <CollectionCard key={entry.id} collection={entry} theme={theme} onOpen={() => choose(entry.id)} />)}
          </div>
        </section>
      )}
      {safetyHistory}
      {councilTimeline}
      {collection.id === 'collected-bc-parks-foundation' && <ParksFoundationHistory />}
      <RailwayHistory history={collection.railwayHistory} />
      <SupportProvided onChooseCollection={choose} id={collection.graphNode} />
      <RuralHealthConnections id={collection.graphNode} />
      {collection.fundingHistory && <FundingHistory rows={collection.fundingHistory} />}
      <AboutCollection collection={collection} />
    </div>
  )
}
