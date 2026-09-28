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
import { COLLECTION_ERAS, TIMELINES, timelineKeyOf } from './timelines.js'
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

/**
 * A mark dated by the timeline it sits on (timelines.js), which cites the sources. What the dates
 * rest on is said here in brief, for the mark's own account of itself.
 */
const DATED_BY_TIMELINE = (kind, years, note) => ({ kind, years, note: `${note} Its timeline cites the sources.` })

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
    applicability: DATED_BY_TIMELINE('first_observation', 'by 2002',
      'Seen on park brochures printed in 2002. A start in the 1980s is inferred from the flag-era identity ' +
      'it belongs to, and no adoption record is cited.'),
    rights: PROVINCE_RIGHTS
  },
  'welcome-bc': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('estimated_era', 'before 2016',
      'Its shaded sun puts it before the flat mark WelcomeBC.ca carried from March 2016; the program itself ' +
      'was announced in June 2007.')
  },
  'work-bc': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('estimated_era', '2007–2011',
      'Bounded by WorkBC.ca’s first capture, in April 2007, and by its tagline, which the Province dropped ' +
      'in 2011.')
  },
  'bc-stats': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('estimated_era', '2007–2012',
      'Most likely the lockup in BC Stats’ site header from 2007 to 2012, which has not been compared with it.')
  },
  'environmental-reporting-bc': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('estimated_era', '2012–2016',
      'The program launched in 2012; a lockup with the shaded sun is in its report templates of 2015–2016.')
  },
  'public-service': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('estimated_era', 'from 2007',
      'The “Where ideas work” brand launched in 2007; when this lockup of it was replaced is not recorded.')
  },
  'pacific-gateway': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('estimated_era', '2008–2011',
      'The brand is first seen on gov.bc.ca in April 2008 and was replaced in 2011; nothing dates this lockup ' +
      'of it in particular.')
  },
  'best-place-on-earth': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('documented_adoption', '2005–2011',
      'The slogan and the sun mark were launched in 2005, and the slogan dropped in 2011; neither is dated ' +
      'to the month.')
  },
  'stronger-bc': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('documented_adoption', 'from 2020',
      'The recovery plan it names was released in September 2020, and its guidelines give this word mark in ' +
      'January 2021.')
  },
  'bc-wildfire-service': {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('first_observation', 'by 2023',
      'Its file on the wildfire situation site is first captured in May 2023; it may be older.')
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
    fidelityNote: SUPPLIED_FIDELITY + ' The file is the same Illustrator export as the mark on the lab’s ' +
      'page on gov.bc.ca.',
    applicability: DATED_BY_TIMELINE('first_observation', 'by 2025',
      'Its file on the lab’s page is first captured in April 2025, after the lab took the name.')
  },
  // Remade, not lifted: the program's own marks have not been obtained, so the card is the published
  // BC mark with the name set beside it.
  'prepared-bc': {
    provenance: 'synthetic_name_variant',
    fidelity: 'no comparison',
    fidelityNote: 'The BC mark is the published one; “PreparedBC” is set in the ministry alphabet, not ' +
      'taken from any artwork of the program’s own. The program’s own lockup, which it has used since 2015, ' +
      'sets “BC” in gold; this does not.',
    applicability: UNDATED('A remake, not a mark the program used. The program was launched on 1 May 2015, ' +
      'and its own lockup is first seen that September.'),
    rights: PROVINCE_RIGHTS
  },
  bcts: {
    ...PUBLISHED,
    applicability: DATED_BY_TIMELINE('first_observation', 'by 2023',
      'On BC Timber Sales’ business plan of August 2023 and its reports since.')
  },
  // Its file came to the project without a record of where it was published, so this claims only
  // what the build did with it; its dates are the website's, where the same wordmark is seen.
  'bcts-wordmark-earlier': {
    ...PUBLISHED,
    fidelityNote: SUPPLIED_FIDELITY,
    applicability: DATED_BY_TIMELINE('first_observation', '2005–2017',
      'The wordmark heads BC Timber Sales’ website from May 2005 to November 2017.')
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

// ── ICBC and BCLC ────────────────────────────────────────────────────────────────────────────────
//
// Both come from research packages (research/identity/icbc, research/identity/bclc) whose every file
// says what it is: a supplied vector with its paths kept, a declared recolour of one, or a
// reconstruction. The records below say the same, and the marks are drawn exactly as supplied
// (renderSupplied.js). Their dates are the eras' (timelines.js), which cite the sources.

const ICBC_RIGHTS = {
  status: 'unresolved',
  note: 'ICBC’s mark. ICBC’s trademark policy asks for written permission to associate its marks with ' +
    `products, services and events. ${NO_PERMISSION}`
}

const BCLC_RIGHTS = { status: 'unresolved', note: `BCLC’s mark. ${NO_PERMISSION}` }

/** A mark from a package, drawn as the file has it, with `reverse` the file to show on a dark page. */
const supplied = (identity) => ({ id, label, note, years, reverse }) => ({
  id, kind: 'supplied', mark: id, label, note, years, ...(reverse ? { reverse } : {}), identity
})

/** Rebuilt by the package's researcher from a registry drawing, a photograph or a screenshot. */
const RECONSTRUCTED = (fidelityNote) => ({ provenance: 'reconstructed', fidelity: 'partially compared', fidelityNote })

/** Paths kept from a supplied file; only what surrounded the mark was removed. */
const SUPPLIED_PATHS = (fidelityNote) => ({ provenance: 'original_supplied', fidelity: 'partially compared', fidelityNote })

const ICBC_ENTRIES = {
  'icbc-1974': [
    supplied({
      ...RECONSTRUCTED('Outlines rebuilt by hand from the drawing in CIPO record 0374886, and compared with it in ' +
        'the package’s proofs. The drawing is hatched for colour; neither the colours nor which shapes were ' +
        'filled are inferred, so it is drawn as boundaries only.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'from 1974', 'Its trademark record claims use from 1 March 1974.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-1974-emblem',
      label: 'Registry emblem',
      years: 'from 1974',
      note: 'The half-disc in its frame under the upper component, as outlines: the record’s drawing, without ' +
        'its colour hatching.'
    })
  ],
  'icbc-half-disc': [
    supplied({
      ...RECONSTRUCTED('Rebuilt from CIPO image 0903609 and a supplied screenshot. The lettering is approximate; ' +
        'the typeface was not identified.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'by 1989', 'Filed as an official mark in January 1989.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-half-disc-lockup',
      label: 'Half-disc and ICBC',
      years: 'by 1989',
      note: 'The arrangement in the 1989 official-mark record: the half-disc beside the initials.'
    }),
    supplied({
      ...RECONSTRUCTED('Rebuilt from a supplied screenshot, letter by letter, in a tapered sans. The lettering ' +
        'is approximate; the typeface was not identified.'),
      applicability: {
        kind: 'unknown',
        years: 'undated',
        note: 'Its picture was supplied filed under 1989, which nothing independent confirms. Its timeline ' +
          'cites the record of the related half-disc arrangement.'
      },
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-full-name',
      label: 'Half-disc and full name',
      years: 'undated',
      note: '“Insurance Corporation of British Columbia” on three lines beside the half-disc.'
    }),
    supplied({
      ...RECONSTRUCTED('The half-disc alone, rebuilt geometrically from CIPO image 0903609 and a supplied screenshot.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'by 1989', 'Part of the arrangement filed in January 1989.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-half-disc',
      label: 'Half-disc',
      years: 'by 1989',
      note: 'The emblem of both lockups, on its own.'
    })
  ],
  'icbc-serif-road': [
    supplied({
      ...RECONSTRUCTED('Rebuilt from a supplied photograph filed under 1994, with its perspective squared up. The ' +
        'road’s curves and the letters’ proportions are approximate, and the serif was not identified.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'about 1992', 'On the back cover of the 1992 annual report.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-serif-road',
      label: 'Serif road badge',
      years: 'about 1992',
      note: '“ICBC” in a narrow serif, reversed out of the square badge above the road.'
    })
  ],
  'icbc-square-sans': [
    supplied({
      ...SUPPLIED_PATHS('Every path is the supplied file’s own; its page background, unused clips and empty ' +
        'groups were removed. Where the file was published is not recorded.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'by 2007–2008', 'On the service plans of January 2007 and January 2008.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-square-sans',
      label: 'Square sans badge',
      years: 'by 2007–2008',
      note: 'The square-cornered badge with “ICBC” in a heavy sans.'
    })
  ],
  'icbc-rounded': [
    supplied({
      ...SUPPLIED_PATHS('The paths are the supplied orange file’s. The blue is a declared recolour, sampled from ' +
        'a supplied screenshot — the right colour family, not a certified brand value.'),
      applicability: DATED_BY_TIMELINE('estimated_era', '2008–present', 'Blue use is claimed from January 2008; a 2008 rollout is inferred.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-rounded-blue',
      label: 'Blue',
      years: '2008–present',
      note: 'The rounded badge in blue, as on ICBC’s reports.'
    }),
    supplied({
      ...SUPPLIED_PATHS('Every path and the orange fill are the supplied file’s own. Where the file came from is ' +
        'not recorded beyond a capture of icbc.com.'),
      applicability: {
        kind: 'first_observation',
        years: 'by 2026',
        note: 'On icbc.com on 27 September 2026. Whether it replaces the blue, or marks a campaign, is not known.'
      },
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-rounded-orange',
      label: 'Orange',
      years: 'by 2026',
      note: 'The same drawing in orange, as on icbc.com in 2026.'
    }),
    supplied({
      ...SUPPLIED_PATHS('The supplied orange file’s paths in black: a recolour made for reference, not a version ' +
        'ICBC is known to publish.'),
      applicability: DATED_BY_TIMELINE('estimated_era', '2008–present', 'The rounded drawing’s years.'),
      rights: ICBC_RIGHTS
    })({
      id: 'icbc-rounded-black',
      label: 'Black',
      years: '2008–present',
      note: 'The same drawing in one dark ink.'
    })
  ]
}

const BCLC_ENTRIES = {
  'bclc-legacy': [
    supplied({
      ...SUPPLIED_PATHS('The supplied file’s four paths, unchanged; its lilac background and page clip were ' +
        'removed. Drawn in one ink, which is not a claim about the colours it was printed in.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'by 2007–2008', 'On the 2006/07 annual report and the service plan of early 2008.'),
      rights: BCLC_RIGHTS
    })({
      id: 'bclc-legacy',
      label: 'Full-name lockup',
      years: 'by 2007–2008',
      reverse: 'bclc-legacy-reversed',
      note: 'The sun and waves beside the corporation’s full name.'
    }),
    supplied({
      ...SUPPLIED_PATHS('The emblem’s three paths from the supplied file, isolated and unchanged.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'by 2007–2008', 'Part of the lockup seen in 2007 and 2008.'),
      rights: BCLC_RIGHTS
    })({
      id: 'bclc-legacy-symbol',
      label: 'Sun and waves',
      years: 'by 2007–2008',
      note: 'The emblem on its own.'
    })
  ],
  'bclc-2008': [
    supplied({
      provenance: 'reconstructed',
      fidelity: 'no comparison',
      fidelityNote: 'The supplied present-day letters, recoloured in the grey, red, orange and green of BCLC’s ' +
        'digital design system. No 2008 master was available to compare the letters with, and the palette is ' +
        'the design system’s, not a 2008 print specification. The launch tagline is not set.',
      applicability: DATED_BY_TIMELINE('documented_adoption', '2008–by 2022', 'Reported on 13 August 2008; the palette is still on a report of 2022.'),
      rights: BCLC_RIGHTS
    })({
      id: 'bclc-2008',
      label: 'Red, orange and green',
      years: '2008–by 2022',
      note: 'The lowercase initials with the older palette’s dots.'
    })
  ],
  'bclc-contemporary': [
    supplied({
      ...SUPPLIED_PATHS('Every path and colour is the supplied file’s own; three rectangular masks were redrawn ' +
        'as the clips they amount to. The report it is seen on confirms the colour family, not these exact values.'),
      applicability: DATED_BY_TIMELINE('first_observation', 'by 2025/26', 'On a community impact report for 2025/26.'),
      rights: BCLC_RIGHTS
    })({
      id: 'bclc-contemporary',
      label: 'Purple, coral and yellow',
      years: 'by 2025/26–present',
      note: 'The lowercase initials as BCLC uses them now.'
    })
  ]
}

// ── BC Ferries ───────────────────────────────────────────────────────────────────────────────────
//
// From a third package of the same kind (research/identity/bc-ferries). The dogwood marks are all
// reconstructions; the wave is supplied paths.

const BCF_RIGHTS = {
  status: 'unresolved',
  note: 'BC Ferries’ mark; since 2003 it has belonged to BC Ferry Services Inc., which is not a public ' +
    `body. ${NO_PERMISSION}`
}

const BCF_ENTRIES = {
  'bcf-early-dogwood': [
    supplied({
      provenance: 'reconstructed',
      fidelity: 'no comparison',
      fidelityNote: 'A simplified interpretation of the flag illustrated on the 1963 brochure’s cover — not a ' +
        'facsimile, and not a claim about its exact colours. No side-by-side check is recorded.',
      applicability: DATED_BY_TIMELINE('first_observation', 'by 1963', 'On the cover of the 1963 season brochure.'),
      rights: BCF_RIGHTS
    })({
      id: 'bcf-1963-flag',
      label: 'Dogwood flag, 1963',
      years: 'by 1963',
      note: 'The outlined dogwood on a green waving flag.'
    })
  ],
  'bcf-geometric-dogwood': [
    supplied({
      ...RECONSTRUCTED('Rebuilt from a small supplied picture of the lockup. The drop shadow is left out; the ' +
        'green and the letters are approximate, and no substitute font was used.'),
      applicability: DATED_BY_TIMELINE('estimated_era', 'about 1978–2003', 'The start is inferred; the end, 2 April 2003, is documented.'),
      rights: BCF_RIGHTS
    })({
      id: 'bcf-dogwood-lockup',
      label: 'Flag and wordmark',
      years: 'about 1978–2003',
      note: 'The geometric dogwood on its waving flag, beside “BC FERRIES”.'
    }),
    supplied({
      ...RECONSTRUCTED('The flower redrawn as smooth contours from a supplied GIF, on the flat flag; the green ' +
        'and yellow are sampled from it.'),
      applicability: DATED_BY_TIMELINE('estimated_era', 'about 1978–2003', 'The same drawing’s years; when this flat ' +
        'flag was first used has not been found.'),
      rights: BCF_RIGHTS
    })({
      id: 'bcf-dogwood-flag',
      label: 'House flag',
      years: 'about 1978–2003',
      note: 'The geometric dogwood on a flat green flag.'
    }),
    supplied({
      ...RECONSTRUCTED('Letter contours drawn from a small supplied picture, not set in a lookalike font; their ' +
        'shapes and spacing may differ slightly from the original.'),
      applicability: DATED_BY_TIMELINE('estimated_era', 'about 1978–2003', 'The lockup’s years.'),
      rights: BCF_RIGHTS
    })({
      id: 'bcf-dogwood-wordmark',
      label: 'Wordmark',
      years: 'about 1978–2003',
      note: '“BC FERRIES” on its own.'
    })
  ],
  'bcf-wave': [
    supplied({
      ...SUPPLIED_PATHS('Every path is the supplied file’s own; its page background and clips were removed. ' +
        'The blue is sampled from a supplied picture, not an official colour value, and the document the file ' +
        'came from is not identified.'),
      applicability: DATED_BY_TIMELINE('documented_adoption', '2003–present', 'Announced on 2 April 2003.'),
      rights: BCF_RIGHTS
    })({
      id: 'bcf-wave',
      label: 'Wave and wordmark',
      years: '2003–present',
      reverse: 'bcf-wave-white',
      note: 'The wave into “BCFerries”, in blue; the same paths in white for dark grounds.'
    })
  ]
}

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

/** Which timeline a one-off sits on (timelines.js), where one has been researched. */
const withTimeline = (entry) => (timelineKeyOf(entry.id) ? { ...entry, timeline: timelineKeyOf(entry.id) } : entry)

/**
 * One of the Province's marks as the gallery shows it: its body in the diagram, its identity, and
 * the timeline it sits on.
 */
const provincial = (entry) => withTimeline(withIdentity(withNode(entry)))

/** A collection's researched eras (timelines.js), with the gallery's marks put into the held ones. */
const withMarks = (eras, marks) => eras.map((each) => ({ ...each, entries: marks[each.id] ?? [] }))

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
    years: '2003–present',
    graphNode: 'sub-bc-timber-sales',
    cover: 'bcts',
    intro: 'BC Timber Sales’ marks since it was established in 2003: its initials over its name, first on ' +
      'their own, then beside a ministry crest, then beside the BC mark. The initials have been published ' +
      'in two greens — forest on white, teal reversed — and every mark here starts from either. Open one ' +
      'to recolour it.',
    eras: withMarks(COLLECTION_ERAS.bcts, {
      'bcts-earlier': BCTS_ENTRIES.earlier.map(withIdentity),
      'bcts-current': BCTS_ENTRIES.current.map(withIdentity)
    })
  },
  {
    id: 'icbc',
    shelf: 'bodies',
    label: 'ICBC',
    body: 'Crown corporation · Ministry of Attorney General',
    years: '1973–present',
    graphNode: 'icbc',
    cover: 'icbc-rounded-blue',
    intro: 'The Insurance Corporation of British Columbia’s marks, as dated evidence rather than a clean run ' +
      'of eras: a registry emblem of 1974, a half-disc beside its name by 1989, then the road badge — in a ' +
      'serif, a heavier sans, and since 2008 with rounded corners. The early marks are reconstructions; ' +
      'the later ones are supplied paths, shown as they came.',
    eras: withMarks(COLLECTION_ERAS.icbc, ICBC_ENTRIES)
  },
  {
    id: 'bclc',
    shelf: 'bodies',
    label: 'BCLC',
    body: 'Crown corporation · Ministry of Finance',
    years: '1984–present',
    graphNode: 'bclc',
    cover: 'bclc-contemporary',
    intro: 'The British Columbia Lottery Corporation’s marks: the sun and waves beside its full name, then ' +
      'from August 2008 its initials in lowercase with three dots of colour, which have since changed ' +
      'from red, orange and green to purple, coral and yellow. Shown as supplied; the 2008 colours are a ' +
      'reconstruction.',
    eras: withMarks(COLLECTION_ERAS.bclc, BCLC_ENTRIES)
  },
  {
    id: 'bc-ferries',
    shelf: 'bodies',
    label: 'BC Ferries',
    body: 'Crown corporation until 2003',
    years: '1960–present',
    // The diagram has the Crown corporation, which ended in 2003; the company that followed it is not
    // a public body, so the link goes to the years it was one.
    graphNode: 'bc-ferry-corporation',
    cover: 'bcf-wave',
    intro: 'BC Ferries’ two symbols: the dogwood, from the ferry system’s start in 1960 — first as an ' +
      'outlined flower on a waving flag, later redrawn in geometric petals beside a squared wordmark — ' +
      'then the wave, introduced on 2 April 2003 with the company that replaced the Crown corporation. ' +
      'The dogwood marks are reconstructions; the wave is supplied paths, shown as they came.',
    eras: withMarks(COLLECTION_ERAS['bc-ferries'], BCF_ENTRIES)
  },
  {
    id: 'bc-parks',
    shelf: 'bodies',
    label: 'BC Parks',
    body: 'Division · Ministry of Environment and Parks',
    years: '2002–present',
    graphNode: 'sub-bc-parks',
    cover: 'bc-parks',
    intro: 'BC Parks’ marks, oldest first: its badge from the flag years — the flag symbol in a rounded ' +
      'frame with “Parks” set at the size of “BC”, which opens to recolour — then the marks that followed ' +
      'it on the Province’s sun, which the gallery does not have yet.',
    eras: withMarks(COLLECTION_ERAS['bc-parks'], {
      'parks-badge': ONE_OFFS.filter((entry) => entry.id === 'bc-parks').map(provincial)
    })
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

/**
 * The timeline a one-off sits on, with each era's marks resolved to the gallery's own entries, so a
 * mark on it opens as it does anywhere else. Undefined for a mark with no researched history.
 */
export const timelineOf = (entry) => {
  const timeline = entry?.timeline && TIMELINES[entry.timeline]
  if (!timeline) return undefined
  return {
    ...timeline,
    eras: timeline.eras.map((each) => ({ ...each, entries: (each.marks ?? []).map(findGalleryEntry) }))
  }
}

/**
 * What an era holds: its marks, a mark the generator draws, a mark of its own the gallery has not
 * obtained, or none of its own (the body went under the Province's or its ministry's marks). An era
 * that does not say — BC Hydro's — is held if it has marks.
 */
export const eraStatus = (each) => each.status ?? (each.entries.length > 0 ? 'held' : 'sought')
