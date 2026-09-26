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
// whose marks have not been obtained get a shelf of their own, so a gap reads as a gap rather than
// as a body with no mark.

import { useState } from 'react'
import { ColourField } from '../site/ColourField.jsx'
import { Segmented } from '../site/Segmented.jsx'
import { renderFlagSvg } from '../flag/renderFlagSvg.js'
import { FLAG_PALETTE_HINTS, FLAG_PALETTE_LABELS, FLAG_PALETTE_ORDER, FLAG_SWATCHES } from '../flag/flagPalettes.js'
import {
  APPLICABILITY, COLLECTIONS_ON_SHELF, FIDELITY, GALLERY_COLLECTIONS, PROVENANCE, RIGHTS, entriesOf, findGalleryEntry
} from './collections.js'
import { ASSET_STATUS, WANTED, WANTED_AS_OF } from './wanted.js'
import { HydroStudio } from '../hydro/HydroStudio.jsx'
import { HydroMarkView } from '../hydro/HydroMarkView.jsx'
import { renderCurrentHydroSvg, renderHydroMarkSvg } from '../hydro/hydroMarks.js'
import { HYDRO_PRESETS, hydroDefaults } from '../hydro/hydroLayout.js'
import { renderHydroSvg } from '../hydro/renderHydroSvg.js'
import { hasGlow, renderOneOffSvg, rolesOf } from './renderOneOff.js'
import { pageColoursFor } from './pageColours.js'
import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'
import { TRANSPARENT } from '../logo/logoColors.js'
import { useSiteTheme } from '../site/useTheme.js'
import { BCTS_FOREST, BCTS_TEAL } from './oneOffs.js'
import { renderCurrentSvg } from '../current/currentMarks.js'

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
  { label: 'Light', roles: ['light'], hint: 'The sun’s core and the rays it fades to — or, flat, the colour cut out of the sun.' },
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
  reconstructed: 'Reconstructed: redrawn by this project from pictures or written rules, not taken from ' +
    'original artwork.',
  synthetic_name_variant: 'A generated interpretation — a name set in a style it never had — and not an ' +
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

/** The short form, for a card: where it came from, what its date rests on, whether it may be shown. */
const chipsOf = (identity) => [
  PROVENANCE[identity.provenance],
  APPLICABILITY[identity.applicability.kind],
  RIGHTS[identity.rights.status]
]

/**
 * A card's chips. They sit inside buttons, where a list would be flattened anyway, so the
 * separators are text a screen reader hears and the page does not show.
 */
const Chips = ({ labels, title }) => (
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

/** The fuller account, under a mark that is open. */
const AboutMark = ({ identity }) => identity && (
  <section className="panel gallery__about" aria-labelledby="about-mark">
    <h2 id="about-mark">About this mark</h2>
    <Facts rows={Object.entries(sentencesOf(identity))} />
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
    if (era.entries.every((entry) => ids.has(entry.id))) {
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
const AboutCollection = ({ collection }) => {
  const entries = entriesOf(collection)
  const rows = Object.keys(sentencesOf(entries[0].identity)).map((term) => {
    const groups = new Map()
    for (const entry of entries) {
      const sentence = sentencesOf(entry.identity)[term]
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
  return (
    <section className="panel gallery__about" aria-labelledby="about-collection">
      <h2 id="about-collection">{entries.length === 1 ? 'About this mark' : 'About these marks'}</h2>
      <Facts rows={rows} />
    </section>
  )
}

/**
 * A collection card's chips: every provenance its marks have, then the date and rights where all
 * its marks agree. A collection that mixes them says so by listing each, not by picking one.
 */
const collectionChips = (collection) => {
  const identities = entriesOf(collection).map((entry) => entry.identity)
  const distinct = (read) => [...new Set(identities.map(read))]
  const dates = distinct((identity) => APPLICABILITY[identity.applicability.kind])
  const rights = distinct((identity) => RIGHTS[identity.rights.status])
  return [
    ...distinct((identity) => PROVENANCE[identity.provenance]),
    ...(dates.length === 1 ? dates : []),
    ...(rights.length === 1 ? rights : [])
  ]
}

/** One mark, opened: its colours editable, its arrangement not. */
const Detail = ({ entry, onClose }) => {
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
        <span
          className="gallery__art gallery__art--large"
          role="img"
          aria-label={entry.label}
          // Built here from this project's own artwork; every value is escaped where written.
          dangerouslySetInnerHTML={{ __html: drawing(entry, colours) }}
        />

        <div className="gallery__controls">
          <div className="field">
            <span className="field__label">Start from</span>
            <div className="segmented" role="group" aria-label="Starting colours">
              {entry.presets.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  aria-pressed={matches(preset)}
                  onClick={() => setColours(preset)}
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
          {entry.caveat && <p className="gallery__caveat">{entry.caveat}</p>}
        </div>
      </div>
    </section>
  )
}

/** What a card in an era shows: the entry drawn as it opens. */
/**
 * What a card shows: the entry drawn for the page it sits on — no ground of its own, in the version
 * its identity sanctions for a light or a dark page (see pageColours.js). BC Hydro's 1961
 * signatures take their white form on dark, as the manual's reverse forms do. The exceptions keep
 * their ground because the ground is the point: the 1961 manual's backgrounds and vehicles, and
 * BC Hydro's current colourways, each of which is defined by what it sits on.
 */
const tileArt = (entry, theme = 'light', { cover = false } = {}) => {
  if (entry.kind === 'artwork') {
    const printed = ONE_OFF_MARKS[entry.mark].printed
    return renderOneOffSvg({ id: entry.mark, colours: pageColoursFor(printed, theme), sun: 'glow', clearSpaceFactor: 0.02 }).svg
  }
  // Remade in the current identity: drawn by the generator's current era, reversed on dark.
  if (entry.kind === 'current') {
    return renderCurrentSvg({ text: entry.text, variant: theme === 'dark' ? 'reverse' : 'colour', clearSpaceFactor: 0.02 })
  }
  if (entry.kind === 'flag') {
    const dark = theme === 'dark'
    return renderFlagSvg({
      ...entry.draw,
      letterColor: dark ? '#ffffff' : '#10069f',
      textColor: dark ? '#ffffff' : '#10069f',
      flagPalette: dark ? 'ink' : 'official',
      background: TRANSPARENT,
      clearSpaceFactor: 0.02
    }).svg
  }
  if (entry.kind === 'hydro') {
    const settings = hydroDefaults(entry.preset)
    const signature = HYDRO_PRESETS[entry.preset]?.group === 'signature'
    return renderHydroSvg(signature && theme === 'dark' ? { ...settings, mode: 'white' } : settings, { metadata: false, width: 480 }).svg
  }
  if (entry.mark === '1990') return renderHydroMarkSvg({ id: 'bc-hydro-1990', clearSpace: 0.08, background: TRANSPARENT, width: 480 }).svg
  // A collection's cover stands for the whole identity, so it takes the page's version of it.
  if (cover) return renderCurrentHydroSvg({ variant: theme === 'dark' ? 'reverse' : 'colour', background: TRANSPARENT, clearSpace: 0.08, width: 480 }).svg
  return renderCurrentHydroSvg({ variant: entry.variant, clearSpace: 1 / 3, width: 480 }).svg
}

/** Whether a card draws on the page's ground, or keeps a ground of its own. */
const onPage = (entry) => entry.kind === 'artwork' || entry.kind === 'current' || entry.kind === 'flag' || entry.mark === '1990' ||
  (entry.kind === 'hydro' && HYDRO_PRESETS[entry.preset]?.group === 'signature')

/** A card in an era. */
const Tile = ({ entry, onOpen, theme }) => (
  <button type="button" className="gallery__pick gallery__pick--tile" onClick={onOpen} aria-label={`Open ${entry.label}`}>
    <span
      className="gallery__art"
      data-ground={onPage(entry) ? 'page' : 'own'}
      // Built by this project's own renderers; every value is escaped where written.
      dangerouslySetInnerHTML={{ __html: tileArt(entry, theme) }}
    />
    <span className="gallery__label">{entry.label}</span>
    <span className="gallery__note">{entry.note}</span>
    <IdentityChips identity={entry.identity} />
  </button>
)

/**
 * A one-off: a card of its own, with what it is beside it. One remade in the current identity is
 * drawn by the generator's current era, and opens there rather than in the gallery.
 */
const OneOffEntry = ({ entry, onOpen, theme, onOpenGovernment }) => (
  <section className="panel gallery__entry">
    <div className="gallery__head">
      <h2>{entry.label}</h2>
      <span className="gallery__years">{entry.years}</span>
    </div>
    <p className="gallery__note">{entry.note}</p>
    <IdentityChips identity={entry.identity} />

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
      <span className="gallery__label">
        {entry.kind === 'current' ? 'Open in the generator' : 'Open to recolour, or to see it as published'}
      </span>
    </button>
    <GraphLink node={entry.graphNode} onOpenGovernment={onOpenGovernment} />
  </section>
)

/** A card for a whole collection on the gallery's first page: its cover mark, whose it is, how many. */
const CollectionCard = ({ collection, onOpen, theme }) => {
  const cover = findGalleryEntry(collection.cover) ?? entriesOf(collection)[0]
  const count = entriesOf(collection).length
  return (
    <button type="button" className="gallery__collection" onClick={onOpen} aria-label={`Open ${collection.label}`}>
      <span
        className="gallery__art gallery__art--cover"
        data-ground="page"
        // Built by this project's own renderers; every value is escaped where written.
        dangerouslySetInnerHTML={{ __html: tileArt(cover, theme, { cover: true }) }}
      />
      <span className="gallery__collection-text">
        <span className="gallery__collection-title">{collection.label}</span>
        <span className="gallery__note">{collection.body}</span>
        <span className="gallery__years">
          {collection.years} · {count} {count === 1 ? 'mark' : 'marks'}
          {collection.eras ? ` · ${collection.eras.length} eras` : ''}
        </span>
        <Chips labels={collectionChips(collection)} />
      </span>
    </button>
  )
}

/** A link from a mark to the body it stands for, in the government diagram. */
const GraphLink = ({ node, onOpenGovernment }) => node && onOpenGovernment && (
  <button type="button" className="gallery__graph-link" onClick={() => onOpenGovernment(node)}>
    In the government graph <span aria-hidden="true">→</span>
  </button>
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
  const id = readParam('logos')
  if (GALLERY_COLLECTIONS.some((collection) => collection.id === id)) return id
  const mark = readParam('mark')
  return GALLERY_COLLECTIONS.find((collection) => entriesOf(collection).some((entry) => entry.id === mark))?.id ?? null
}

// A mark remade in the current identity opens in the generator, not here, so it is never the open one.
const readMark = () => {
  const entry = readParam('mark') && findGalleryEntry(readParam('mark'))
  return entry && entry.kind !== 'current' ? entry.id : null
}

/**
 * Where the gallery is lives in the address bar — the collection, and the mark open in it — so a
 * link to BC Hydro's page, or to one of its signatures, opens there.
 */
const writePlace = (collection, mark) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  for (const [key, value] of [['logos', collection], ['mark', mark]]) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  globalThis.history.replaceState(null, '', url)
}

/**
 * The trail every page of the gallery starts with: back to all the logos, then the collection —
 * a way back to it when a mark is open — then the mark. A collection of one mark is that mark, so
 * its trail names it once.
 */
const Crumbs = ({ collection, entry, onHome, onCollection }) => (
  <nav className="gallery__crumbs" aria-label="Gallery">
    <button type="button" className="gallery__back" onClick={onHome}>
      <span aria-hidden="true">←</span> All logos
    </button>
    {collection && <span aria-hidden="true">/</span>}
    {collection && (entry && entriesOf(collection).length > 1
      ? <button type="button" className="gallery__crumb" onClick={onCollection}>{collection.label}</button>
      : <span aria-current="page">{collection.label}</span>)}
    {entry && entriesOf(collection).length > 1 && <span aria-hidden="true">/</span>}
    {entry && entriesOf(collection).length > 1 && <span aria-current="page">{entry.label}</span>}
  </nav>
)

/**
 * @param {object} props
 * @param {(nodeId: string) => void} [props.onOpenGovernment]  Opens the government diagram at a body.
 * @param {(patch: object) => void} [props.onOpenInGenerator]  Loads a patch into the generator and
 *   shows it — how a mark remade in the current identity opens.
 */
export const GalleryView = ({ onOpenGovernment, onOpenInGenerator }) => {
  const { name: theme } = useSiteTheme()
  const [collectionId, setCollectionId] = useState(readCollection)
  const [openId, setOpenId] = useState(readMark)
  const open = openId && findGalleryEntry(openId)
  const collection = GALLERY_COLLECTIONS.find((candidate) => candidate.id === collectionId)

  const go = (nextCollection, nextMark) => {
    setCollectionId(nextCollection)
    setOpenId(nextMark)
    writePlace(nextCollection, nextMark)
    globalThis.scrollTo?.({ top: 0 })
  }
  // A collection of one mark opens straight to it: there is nothing to choose between.
  const choose = (id) => {
    const chosen = GALLERY_COLLECTIONS.find((candidate) => candidate.id === id)
    const only = chosen && entriesOf(chosen).length === 1 ? entriesOf(chosen)[0].id : null
    go(id, only)
  }
  const openMark = (id) => {
    const entry = findGalleryEntry(id)
    if (entry?.kind === 'current' && onOpenInGenerator) onOpenInGenerator({ era: 'current', currentName: entry.text })
    else go(collectionId, id)
  }
  const home = () => go(null, null)
  const backToCollection = () => go(collectionId, null)
  const crumbs = <Crumbs collection={collection} entry={open} onHome={home} onCollection={backToCollection} />

  if (open) {
    return (
      <div className="gallery">
        {crumbs}
        {open.kind === 'hydro'
          ? <HydroStudio initialPreset={open.preset} />
          : open.kind === 'hydro-mark'
            ? <HydroMarkView mark={open.mark} variant={open.variant} />
            : <Detail entry={open} />}
        <AboutMark identity={open.identity} />
      </div>
    )
  }

  // The first page: the bodies with identities of their own, then the Province's one-offs.
  if (!collection) {
    return (
      <div className="gallery">
        <p className="gallery__intro">
          Logos the generator does not make. First, public bodies with identities of their own — a Crown
          corporation, a program, a division — each through the eras it has had. Then the Province’s own
          one-off marks, the names set beside the BC mark. Last, the bodies whose marks are still being
          sought.
        </p>
        <section className="gallery__shelf" aria-labelledby="shelf-bodies">
          <h2 id="shelf-bodies" className="gallery__shelf-title">Crown corporations and public bodies</h2>
          <div className="gallery__collections">
            {COLLECTIONS_ON_SHELF('bodies').map((entry) => (
              <CollectionCard key={entry.id} collection={entry} theme={theme} onOpen={() => choose(entry.id)} />
            ))}
          </div>
        </section>
        <section className="gallery__shelf" aria-labelledby="shelf-bc-mark">
          <h2 id="shelf-bc-mark" className="gallery__shelf-title">The Province’s one-off marks</h2>
          <div className="gallery__collections">
            {COLLECTIONS_ON_SHELF('bc-mark').map((entry) => (
              <CollectionCard key={entry.id} collection={entry} theme={theme} onOpen={() => choose(entry.id)} />
            ))}
          </div>
        </section>
        <section className="gallery__shelf" aria-labelledby="shelf-wanted">
          <h2 id="shelf-wanted" className="gallery__shelf-title">Not yet in the gallery</h2>
          <p className="gallery__intro gallery__shelf-intro">
            Public bodies whose marks have been looked for and not obtained. None is drawn, because no
            artwork for it has been verified; each says how far the search has got. From the research
            companion’s logo routes, as of {WANTED_AS_OF}.
          </p>
          <div className="gallery__collections">
            {WANTED.map((item) => <WantedCard key={item.id} item={item} onOpenGovernment={onOpenGovernment} />)}
          </div>
        </section>
      </div>
    )
  }

  return (
    <div className="gallery">
      {crumbs}
      <div className="gallery__collection-head">
        <div>
          <h2 className="gallery__collection-heading">{collection.label}</h2>
          <p className="gallery__note">{collection.body} · {collection.years}</p>
        </div>
        <GraphLink node={collection.graphNode} onOpenGovernment={onOpenGovernment} />
      </div>
      <p className="gallery__intro">{collection.intro}</p>

      {collection.eras
        ? collection.eras.map((era) => (
          <section key={era.id} className="gallery__era" aria-labelledby={`${era.id}-heading`}>
            <div className="gallery__head">
              <h2 id={`${era.id}-heading`}>{era.label}</h2>
              <span className="gallery__years">{era.years}</span>
            </div>
            <p className="gallery__note">{era.note}</p>
            <div className="gallery__tiles">
              {era.entries.map((entry) => <Tile key={entry.id} entry={entry} theme={theme} onOpen={() => openMark(entry.id)} />)}
            </div>
          </section>
          ))
        : (
          <div className="gallery__list">
            {collection.entries.map((entry) => (
              <OneOffEntry key={entry.id} entry={entry} theme={theme} onOpen={() => openMark(entry.id)} onOpenGovernment={onOpenGovernment} />
            ))}
          </div>
          )}
      <AboutCollection collection={collection} />
    </div>
  )
}
