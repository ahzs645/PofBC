// What the gallery holds, grouped by whose marks they are.
//
// It began as the Province's one-off marks, and those are still its first collection. Other public
// bodies in British Columbia have identities of their own that belong beside them — BC Hydro first
// — and a collection is how the gallery tells them apart. Each entry says what kind of mark it is,
// and the kind decides what opening it shows: a one-off is recoloured on its card, while BC Hydro's
// marks open into the generator's own layout. BC Timber Sales has a collection of its own because
// it has several marks, not because it stands apart from the Province. A collection with a history is split into eras, each
// with the years it ran.
//
// Every entry also carries an identity record: where its artwork came from, how closely what the
// gallery draws has been checked against that, what its dates rest on, and whether anyone has
// permission to show it. The four are kept apart because they vary apart — a reconstruction can be
// well dated and still have the wrong lettering, and an exact vector can be undated and still need
// permission (see the research companion's MODEL_NOTES, "Identity assets", 2026-09-25). Where an
// era's marks all share one record it is written once, on the era, and each entry inherits it.

import { BCTS_ENTRIES, ONE_OFFS } from './oneOffs.js'
import { CURRENT_VARIANT_ORDER, CURRENT_VARIANTS } from '../hydro/hydroMarks.js'

// ── The identity record ──────────────────────────────────────────────────────────────────────────

/** Where a mark's artwork came from, most direct first. */
export const PROVENANCE = {
  original_supplied: 'Supplied original artwork',
  extracted_from_official_vector: 'Extracted from official vector',
  extracted_from_published_artwork: 'Extracted from published artwork',
  archival_raster: 'Archival image',
  reconstructed: 'Reconstructed',
  synthetic_name_variant: 'Generated name variant'
}

/** How closely the drawing has been checked against its source. */
export const FIDELITY = {
  'source compared': 'Compared with its source',
  'partially compared': 'Partly compared with its source',
  'font substitution': 'Substitute lettering',
  'no comparison': 'Not compared with a source'
}

/** What a mark's dates rest on. */
export const APPLICABILITY = {
  documented_adoption: 'Date documented',
  first_observation: 'Date first seen',
  estimated_era: 'Date estimated',
  unknown: 'Date unknown'
}

/**
 * Whether the gallery may show a mark. None has documented permission, so nothing here is
 * 'permitted'; the value exists so that a mark cleared later can say so without a new field.
 */
export const RIGHTS = {
  unresolved: 'Rights unresolved',
  permission_requested: 'Permission requested',
  permitted: 'Permission documented'
}

const NO_PERMISSION = 'No permission to reproduce it here has been sought or documented.'

const PROVINCE_RIGHTS = {
  status: 'unresolved',
  note: `A provincial mark, whose use is governed by the Government of British Columbia. ${NO_PERMISSION}`
}

const HYDRO_RIGHTS = { status: 'unresolved', note: `BC Hydro’s mark. ${NO_PERMISSION}` }

/**
 * The Province's drawn marks are lifted from published files (scripts/build-one-offs.mjs), so their
 * shapes are the files' own. They count as only partly compared because some of what the gallery
 * draws is sampled rather than given — the sun's shading, a ground behind a reversed mark — and no
 * side-by-side check of the drawing against the file is recorded.
 */
const PUBLISHED = {
  provenance: 'extracted_from_published_artwork',
  fidelity: 'partially compared',
  fidelityNote: 'Every shape is the published file’s own. The sun’s shading and any ground behind the ' +
    'mark are sampled from the file rather than given by it, and no side-by-side check of the drawing ' +
    'against the file is recorded.',
  rights: PROVINCE_RIGHTS
}

const BEST_PLACE_YEARS = {
  kind: 'estimated_era',
  years: 'Best Place on Earth years',
  note: 'Dated by its style — the shaded sun and the gold-accented Garamond of the Best Place on Earth ' +
    'identity — not by a record of when it was adopted or retired.'
}

const UNSOURCED = (years) => ({
  kind: 'estimated_era',
  years,
  note: 'No record of adoption is cited for these dates in this project.'
})

const SUPPLIED_FIDELITY = 'Every shape is the supplied file’s own. Where and when that file was published ' +
  'is not recorded, and no side-by-side check of the drawing against it is recorded.'

const UNDATED = (note) => ({ kind: 'unknown', years: 'undated', note })

/** The identity of each of the Province's marks, by the id oneOffs.js gives it. */
const ONE_OFF_IDENTITY = {
  'bc-parks': {
    provenance: 'reconstructed',
    fidelity: 'partially compared',
    fidelityNote: 'Set by this project’s flag renderer, with its proportions read off a picture of the ' +
      'mark rather than measured from artwork.',
    applicability: {
      kind: 'estimated_era',
      years: 'from the 1980s',
      note: 'The decade is inferred from the flag-era identity it belongs to; no adoption record is cited.'
    },
    rights: PROVINCE_RIGHTS
  },
  'welcome-bc': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'work-bc': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'bc-stats': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'environmental-reporting-bc': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'public-service': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'pacific-gateway': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'best-place-on-earth': { ...PUBLISHED, applicability: BEST_PLACE_YEARS },
  'stronger-bc': { ...PUBLISHED, applicability: UNSOURCED('from 2021') },
  'bc-wildfire-service': {
    ...PUBLISHED,
    applicability: {
      kind: 'estimated_era',
      years: 'in use today',
      note: 'Seen in current published material; when it was adopted is not recorded here.'
    }
  },
  'bc-wildfire-service-one-line': {
    ...PUBLISHED,
    applicability: {
      kind: 'first_observation',
      years: '2025',
      note: 'Seen on the cover of the 2025 Cultural and Prescribed Fire annual summary report. That is ' +
        'where this project found it, not when it was adopted.'
    }
  },
  // Both came to the project as supplied files, with no record of where or when they were published,
  // so they say as much and no more — as the earlier BCTS wordmark does below.
  'environmental-lab-bc': {
    ...PUBLISHED,
    fidelityNote: SUPPLIED_FIDELITY,
    applicability: UNDATED('Its flat sun places it in the later marks; no date for it has been found.')
  },
  // Remade, not lifted: the program's own mark was the BC mark in outline, in one ink, which the
  // current identity does not draw, so the card is the published BC mark with the name set beside it.
  'prepared-bc': {
    provenance: 'synthetic_name_variant',
    fidelity: 'no comparison',
    fidelityNote: 'The BC mark is the published one; “PreparedBC” is set in the ministry alphabet, not ' +
      'taken from any artwork of the program’s own.',
    applicability: UNDATED('A remake, not a mark the program used. Its own outline mark has no date ' +
      'found for it either.'),
    rights: PROVINCE_RIGHTS
  },
  bcts: {
    ...PUBLISHED,
    applicability: {
      kind: 'estimated_era',
      years: 'in use today',
      note: 'Seen in current published material; when it was adopted is not recorded here.'
    }
  },
  // Its file came to the project without a record of where it was published, so this claims only
  // what the build did with it; the date is unknown rather than guessed.
  'bcts-wordmark-earlier': {
    ...PUBLISHED,
    fidelityNote: SUPPLIED_FIDELITY,
    applicability: UNDATED('Taken to be earlier than the mark beside the BC mark from its setting alone; ' +
      'no date for it has been found.')
  }
}

const withIdentity = (entry) => ({ ...entry, identity: ONE_OFF_IDENTITY[entry.id] })

/** An era whose marks share one identity record: written once, inherited by every entry. */
const era = ({ identity, entries, ...rest }) => ({
  ...rest,
  identity,
  entries: entries.map((entry) => ({ identity, ...entry }))
})

const hydro = (entry) => ({ kind: 'hydro', years: '1961–1990', ...entry })

/** BC Hydro's 1961 signatures, and the applications their manual sets them out for. */
export const HYDRO_ENTRIES = [
  hydro({
    id: 'bc-hydro-corporate',
    preset: 'standard',
    label: 'Corporate signature',
    note: 'The ringed symbol — an H of two four-pointed stars, green over blue — beside “B.C.Hydro”. ' +
      'Only the symbol is coloured; the lettering is black.'
  }),
  hydro({
    id: 'bc-hydro-gas',
    preset: 'gas',
    label: 'Gas Operations',
    note: 'The same symbol inside a flame. The flame and its H always match, in blue.'
  }),
  hydro({
    id: 'bc-hydro-rail',
    preset: 'rail',
    label: 'Rail',
    note: 'The corporate signature with the division named after the wordmark.'
  }),
  hydro({
    id: 'bc-hydro-authority',
    preset: 'authority',
    label: 'Full authority name',
    note: '“British Columbia Hydro and Power Authority” on two lines beside the symbol.'
  }),
  hydro({
    id: 'bc-hydro-signs',
    preset: 'sign-plant',
    label: 'Identification signs',
    note: 'A signature in a border measured in cap heights, with the facility named beneath it on one ' +
      'line or several.'
  }),
  hydro({
    id: 'bc-hydro-backgrounds',
    preset: 'reverse-black',
    label: 'General backgrounds',
    note: 'The five single-colour forms, and the background values each is allowed on.'
  }),
  hydro({
    id: 'bc-hydro-vehicles',
    preset: 'vehicle-gas-reverse',
    label: 'Vehicles',
    note: 'Positive and reverse pairs for each signature, switching at 30% background value.'
  })
]

/**
 * Which one-offs stand for a body the government diagram draws, so a card can lead to it. The
 * Province's marks that name a campaign or a slogan rather than a body have none.
 */
const GRAPH_NODES = {
  'bc-parks': 'sub-bc-parks',
  'work-bc': 'sub-workbc',
  'bc-stats': 'sub-bc-stats',
  'bc-wildfire-service': 'sub-bc-wildfire-service',
  'bc-wildfire-service-one-line': 'sub-bc-wildfire-service',
  'public-service': 'bc-public-service-agency'
}

const withNode = (entry) => (GRAPH_NODES[entry.id] ? { ...entry, graphNode: GRAPH_NODES[entry.id] } : entry)

/** One of the Province's marks as the gallery shows it: its body in the diagram, and its identity. */
const provincial = (entry) => withIdentity(withNode(entry))

/**
 * The gallery in two shelves.
 *
 * The first is public bodies with identities of their own — a Crown corporation, a program, an
 * agency — each a collection that may run through several eras. The second is the Province's own
 * one-offs: names set beside the BC mark, drawn once, which sit together on a page of their own
 * because what they share is the mark, not the body.
 */
export const GALLERY_COLLECTIONS = [
  {
    id: 'bc-hydro',
    shelf: 'bodies',
    label: 'BC Hydro',
    body: 'Crown corporation · Ministry of Energy and Climate Solutions',
    years: '1961–present',
    graphNode: 'bc-hydro',
    cover: 'bc-hydro-current-colour',
    intro: 'BC Hydro’s three identities, oldest first. Each opens in the generator’s layout: the first ' +
      'rebuilt from its manual’s rules, the other two drawn from BC Hydro’s own artwork.',
    eras: [
      era({
        id: 'bc-hydro-1961',
        years: '1961–1990',
        label: 'The Rimmer signature',
        note: 'Designed by Jim Rimmer and launched in 1961: a ringed H of two four-pointed stars, green ' +
          'over blue, beside “B.C.Hydro” in a serif. Reconstructed from five pages of its identity ' +
          'manual — four signatures, and the rules for signs, backgrounds and vehicles, checked as you ' +
          'go. The typeface was never recovered; the lettering is set in a close substitute.',
        identity: {
          provenance: 'reconstructed',
          fidelity: 'font substitution',
          fidelityNote: '“B.C.Hydro” is fitted letter by letter over the printed signature; every other ' +
            'word is set in TeX Gyre Termes, standing in for a typeface that was never recovered. The ' +
            'colours are sampled from screenshots of the manual and are approximations.',
          applicability: {
            kind: 'estimated_era',
            years: '1961–1990',
            note: 'The manual pages carry no date or edition, and neither year is tied to a record of ' +
              'adoption or retirement. The government graph dates the authority itself from March 1962.'
          },
          rights: {
            status: 'unresolved',
            note: `BC Hydro’s historical identity. ${NO_PERMISSION} The substitute typeface’s own licence ` +
              'covers the lettering, not the mark.'
          }
        },
        entries: HYDRO_ENTRIES
      }),
      era({
        id: 'bc-hydro-1990',
        years: '1990–2016',
        label: 'BC hydro',
        note: 'The name reset in a heavy slab, “BC” green and “hydro” blue, with the symbol squared off ' +
          'and set after it.',
        identity: {
          provenance: 'original_supplied',
          fidelity: 'partially compared',
          fidelityNote: 'Every shape is the supplied Illustrator file’s own, unchanged; no side-by-side ' +
            'check of the drawing against the file is recorded.',
          applicability: UNSOURCED('1990–2016'),
          rights: HYDRO_RIGHTS
        },
        entries: [
          {
            id: 'bc-hydro-1990',
            kind: 'hydro-mark',
            mark: '1990',
            years: '1990–2016',
            label: 'BC hydro',
            note: 'From the supplied Illustrator artwork. Any part can be recoloured.'
          }
        ]
      }),
      era({
        id: 'bc-hydro-2016',
        years: '2016–present',
        label: 'BC Hydro, Power smart',
        note: 'The logo in use today, from BC Hydro’s brand guidelines: the symbol made a circle and moved ' +
          'to the front, a contemporary sans, and the “Power smart” tagline. Offered only in the ' +
          'variations the guidelines give.',
        identity: {
          provenance: 'extracted_from_official_vector',
          fidelity: 'partially compared',
          fidelityNote: 'Every shape is the guidelines’ own; the build checks that the black and reverse ' +
            'versions are the same shapes as the colour one. The colours are the guidelines’ screen ' +
            'values rather than the PDF’s print conversion, and no side-by-side check is recorded.',
          applicability: {
            kind: 'estimated_era',
            years: '2016–present',
            note: 'Shown in BC Hydro’s February 2020 brand guidelines; the 2016 start is not tied to a ' +
              'source in this project.'
          },
          rights: {
            status: 'unresolved',
            note: 'The guidelines forbid reconstructing, recolouring or rearranging the logo, which is ' +
              'why only their own variations are offered. They are not a grant of permission to ' +
              `reproduce it here. ${NO_PERMISSION}`
          }
        },
        entries: CURRENT_VARIANT_ORDER.map((variant) => ({
          id: `bc-hydro-current-${variant}`,
          kind: 'hydro-mark',
          mark: 'current',
          variant,
          years: '2016–present',
          label: CURRENT_VARIANTS[variant].label,
          note: CURRENT_VARIANTS[variant].hint
        }))
      })
    ]
  },
  {
    id: 'bcts',
    shelf: 'bodies',
    label: 'BC Timber Sales',
    body: 'Program · Ministry of Forests',
    years: 'earlier–present',
    graphNode: 'sub-bc-timber-sales',
    cover: 'bcts',
    intro: 'BC Timber Sales’ marks: its initials over its name, first on their own and then beside the ' +
      'BC mark. The initials have been published in two greens — forest on white, teal reversed — and ' +
      'every mark starts from either. Open one to recolour it.',
    eras: [
      {
        id: 'bcts-earlier',
        years: 'earlier',
        label: 'The wordmark on its own',
        note: '“BCTS” in green over “BC Timber Sales” in a slab serif, with no BC mark beside it.',
        entries: BCTS_ENTRIES.earlier.map(withIdentity)
      },
      {
        id: 'bcts-current',
        years: 'in use today',
        label: 'Beside the BC mark',
        note: 'The initials over the name in a sans, beside the BC mark with a grey divider.',
        entries: BCTS_ENTRIES.current.map(withIdentity)
      }
    ]
  },
  {
    id: 'bc-parks',
    shelf: 'bodies',
    label: 'BC Parks',
    body: 'Division · Ministry of Environment and Parks',
    years: 'from the 1980s',
    graphNode: 'sub-bc-parks',
    cover: 'bc-parks',
    intro: 'BC Parks’ badge from the flag years: the flag symbol in a rounded frame with “Parks” set at ' +
      'the size of “BC”. Open it to recolour it.',
    entries: ONE_OFFS.filter((entry) => entry.id === 'bc-parks').map(provincial)
  },
  {
    id: 'bc-mark',
    shelf: 'bc-mark',
    label: 'On the BC mark',
    body: 'The Province’s one-off marks',
    years: '2005–present',
    cover: 'welcome-bc',
    intro: 'Names set beside the BC mark, each drawn once for one body, program or campaign, following ' +
      'no pattern that generalises — so they sit here rather than in the generator, which is built on ' +
      'patterns. Open one to recolour it.',
    entries: ONE_OFFS.filter((entry) => entry.id !== 'bc-parks').map(provincial)
  }
]

export const COLLECTIONS_ON_SHELF = (shelf) => GALLERY_COLLECTIONS.filter((collection) => collection.shelf === shelf)

/** Every entry of a collection, across its eras. */
export const entriesOf = (collection) => collection.eras
  ? collection.eras.flatMap((each) => each.entries)
  : collection.entries

export const findGalleryEntry = (id) => GALLERY_COLLECTIONS
  .flatMap(entriesOf)
  .find((entry) => entry.id === id)
