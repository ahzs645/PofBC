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
import { CURRENT_VARIANTS } from '../hydro/hydroMarks.js'
import { PROGRAM_ENTRY_OWNERS } from './reconciledSubjects.js'
import { COLLECTED_COLLECTIONS, SPECIMEN_COLLECTIONS, collectedEntriesOf, specimenEntriesOf, coverFirst, nodesOf } from './collectedCollections.js'
import { withMarkRoles } from './markRoles.js'
import { LIQUOR_DISTRIBUTION_COLLECTION } from './liquorHistory.js'
import { ENDORSED_2019 } from './endorsed2019.js'
import { bearAwareGalleryId, bearAwareId, bearAwareMarkId, bearAwareTitle } from '../initiatives/bearAwareArtwork.js'
import { environmentYouthCorpsGalleryId, environmentYouthCorpsId, environmentYouthCorpsScan } from '../initiatives/environmentYouthCorpsArtwork.js'
import { resWestBadgeEra } from './resWest.js'
import { DEPARTMENTAL_COLLECTIONS } from './movedGalleryPlaces.js'

// ── The identity record ──────────────────────────────────────────────────────────────────────────

/** Where a mark's artwork came from, most direct first. */
export const PROVENANCE = {
  original_supplied: 'Supplied original artwork',
  extracted_from_official_vector: 'Extracted from official vector',
  extracted_from_published_artwork: 'Extracted from published artwork',
  archival_raster: 'Archival image',
  published_vector: 'Published vector artwork',
  published_raster: 'Published image',
  third_party_reconstruction: 'Third-party reconstruction',
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
  dated_specimen: 'Dated specimen',
  estimated_era: 'Date estimated',
  unknown: 'Date unknown'
}

/**
 * A permission record applies only to the files and uses named in its note.
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
const PARKS_COMPOSED = (years, note) => ({
  provenance: 'reconstructed',
  fidelity: 'partially compared',
  fidelityNote: 'Put together from the gallery’s Best Place on Earth mark and letters of the same Garamond the ' +
    'Province published (WorkBC’s “BC” and “k”, the tagline’s “P”, “a”, “r” and “s”), placed as in the ' +
    'archived picture. The picture is small, so the spacing and placing are read off it, not measured.',
  applicability: DATED_BY_TIMELINE('first_observation', years, note),
  rights: PROVINCE_RIGHTS
})

const ONE_OFF_IDENTITY = {
  'bc-parks-banner': PARKS_COMPOSED('2005–2007', 'Seen on its site from November 2005 to February 2007.'),
  'bc-parks-best-place': PARKS_COMPOSED('2010–2016', 'Seen on its site from January 2010 to November 2016.'),
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
  'bc-lands': {
    provenance: 'reconstructed',
    fidelity: 'partially compared',
    fidelityNote: 'Set by this project’s flag renderer in BC Parks’ badge, with “Lands” as the second word ' +
      'in the regular weight and the frame’s wall thinned, compared by eye with a small photocopy of the ' +
      'mark. The frame’s shape and the letters are BC Parks’ and the identity’s; the weight, wall and ' +
      'spacing are read off the photocopy, not measured from BC Lands’ own artwork.',
    applicability: DATED_BY_TIMELINE('first_observation', 'by 1986–88',
      'Seen on a form naming the Ministry of Forests and Lands (August 1986 to July 1988). When BC Lands took ' +
      'the badge up is not known.'),
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
  'bc-bid': {
    provenance: 'reconstructed',
    fidelity: 'partially compared',
    fidelityNote: 'Put together from the gallery’s Best Place on Earth mark (without its tagline) and letters of the ' +
      'Garamond the Province published (WelcomeBC’s B and C, Environmental Lab BC’s i, BC Wildfire Service’s d). ' +
      'Placing is measured off the published 150 × 52 image, itself cropped at its edges, and the result laid over it.',
    applicability: {
      kind: 'first_observation',
      years: 'by 2026',
      note: 'Seen as the BC Bid portal’s header image in November 2026; when it was adopted is not established.'
    },
    rights: PROVINCE_RIGHTS
  },
  'bc-online': {
    provenance: 'reconstructed',
    fidelity: 'partially compared',
    fidelityNote: 'Put together from the gallery’s Best Place on Earth mark, rearranged horizontally, and letters of ' +
      'the Garamond the Province published (WelcomeBC’s “BC”, Environmental Lab BC’s L, n, i and e, and the ' +
      'mark’s own O, enlarged). Placing and spacing are measured off the published 372 × 49 image and the result ' +
      'laid over it; the name is scaled as a whole to the logo’s width.',
    applicability: {
      kind: 'first_observation',
      years: 'by 2026',
      note: 'The logo was supplied in November 2026 as the service’s web artwork. BC OnLine itself dates from July ' +
        '1989; when this logo was adopted is not established.'
    },
    rights: PROVINCE_RIGHTS
  },
  'coroners-service': {
    provenance: 'reconstructed',
    fidelity: 'partially compared',
    fidelityNote: 'Put together from the gallery’s Best Place on Earth mark (without its tagline) and letters of ' +
      'the same Garamond the Province published: BC Wildfire Service’s “Service” and C, and Environmental ' +
      'Reporting BC’s and BC Stats’ lowercase letters, scaled to one x-height. Its placing and spacing are ' +
      'measured off the 1241 × 385 image the Service’s reports embed, and the result was laid over that image.',
    applicability: {
      kind: 'first_observation',
      years: '2012–2026',
      note: 'Seen on the cover of the Service’s 2012–2014 strategic plan (https://oag.bc.ca/app/uploads/sites/963/2024/08/OAGBC-2012-10a-bccs-strategic-plan.pdf) ' +
        'and on a report posted 24 April 2026 (https://www2.gov.bc.ca/assets/gov/birth-adoption-death-marriage-and-divorce/deaths/coroners-service/statistical/deaths_incarceratedpeople_corrections_report_2015-2025.pdf). ' +
        'No adoption record is cited.'
    },
    rights: PROVINCE_RIGHTS
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
  // Drawn by the generator: its pattern is the one GCPE prints, as the 2024 Estimate Notes footer shows.
  gcpe: {
    provenance: 'synthetic_name_variant',
    fidelity: 'source compared',
    fidelityNote: 'The BC mark is the published one and the name is set in the ministry alphabet, broken ' +
      'after “Communications”. Laid beside the scanned footer of GCPE’s 2024 Estimate Notes, the mark, ' +
      'the divider, the line break and the lettering match; the scan’s print is heavier.',
    applicability: UNDATED('Seen on the footer of GCPE’s Estimate Notes of 29 April 2024 (its collection ' +
      'keeps the scan). That is a sighting, not when GCPE began to use the BC mark.'),
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
    note: 'The ringed symbol (an H of two four-pointed stars, green over blue) beside “B.C.Hydro”. ' +
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
const supplied = (identity) => ({ id, label, note, years, reverse, onDark, alternates, markLabel }) => ({
  id, kind: 'supplied', mark: id, label, note, years, ...(reverse ? { reverse } : {}), ...(onDark ? { onDark } : {}),
  ...(alternates ? { alternates } : {}), ...(markLabel ? { markLabel } : {}), identity
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
        'a supplied screenshot: the right colour family, not a certified brand value.'),
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

// Rebuilt from three small screenshots by setting the lettering in substitute outlines, one scale per
// line, and checking each against its screenshot in an overlay. The screenshots' sources are not
// recorded in the package.
const BCF_TOLL = (ground) => ({
  provenance: 'reconstructed',
  fidelity: 'font substitution',
  fidelityNote: `Lettering set in substitute outlines (${ground}), fitted to a small screenshot of the printed ` +
    'wordmark and compared with it in overlay proofs. The outlines name no original typeface, and where the ' +
    'screenshot came from is not recorded.',
  applicability: DATED_BY_TIMELINE('estimated_era', '1960–1964', 'The name’s years: from the service’s start ' +
    'in 1960 to the authority’s renaming on 1 April 1964.'),
  rights: BCF_RIGHTS
})

const BCF_ENTRIES = {
  'bcf-toll-authority': [
    supplied(BCF_TOLL('Roboto Condensed Bold'))({
      id: 'bcf-toll-condensed',
      reverse: 'bcf-toll-condensed-white',
      label: 'One line, condensed',
      years: '1960–1964',
      note: 'Condensed capitals on one line, “Toll Authority” stacked small between the two halves. Printed black on orange.'
    }),
    supplied(BCF_TOLL('Inter Display Black, with Liberation Sans for the middle line'))({
      id: 'bcf-toll-stacked',
      reverse: 'bcf-toll-stacked-white',
      label: 'Three lines',
      years: '1960–1964',
      note: 'Heavy extended capitals over “Toll Authority” in a light line. Printed black on pale blue, under “served by”.'
    }),
    supplied(BCF_TOLL('Inter Display Regular, with Roboto Condensed for the middle'))({
      id: 'bcf-toll-regular',
      reverse: 'bcf-toll-regular-white',
      label: 'One line, regular',
      years: '1960–1964',
      note: 'The one-line arrangement in lighter capitals. Printed white on a black strip.'
    })
  ],
  'bcf-early-dogwood': [
    supplied({
      provenance: 'reconstructed',
      fidelity: 'no comparison',
      fidelityNote: 'A simplified interpretation of the flag illustrated on the 1963 brochure’s cover, not a ' +
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

// ── WorkSafeBC ───────────────────────────────────────────────────────────────────────────────────
//
// The fourth package (research/identity/worksafebc) supplied reconstructions: the 1983 lockup from
// undated specimens, today's wordmark from a small picture. Original report vectors join them below.

const WCB_RIGHTS = {
  status: 'unresolved',
  note: 'WorkSafeBC’s mark. Its published terms require prior written permission to use its trademarks. ' +
    NO_PERMISSION
}

const WCB_ENTRIES = {
  'wcb-1983': [
    supplied({
      provenance: 'reconstructed',
      fidelity: 'font substitution',
      fidelityNote: 'The symbol is drawn by hand from undated specimens on two logo catalogues; the name is a ' +
        'fitted Noto Sans Condensed Medium converted to paths, standing in for a typeface not identified.',
      applicability: DATED_BY_TIMELINE('estimated_era', 'from 1983', 'The redesign’s year is documented; this ' +
        'lockup belongs to it by likeness, not by a dated example.'),
      rights: WCB_RIGHTS
    })({
      id: 'wcb-1983',
      label: 'Symbol and name',
      years: 'from 1983',
      note: 'The province-and-worker symbol beside the board’s name on three lines.'
    }),
    supplied({
      ...RECONSTRUCTED('The symbol’s paths from the reconstructed lockup, on their own. That the symbol was used ' +
        'alone is not established.'),
      applicability: DATED_BY_TIMELINE('estimated_era', 'from 1983', 'The lockup’s years.'),
      rights: WCB_RIGHTS
    })({
      id: 'wcb-1983-symbol',
      label: 'Symbol',
      years: 'from 1983',
      note: 'The province, the sheltering hand and the worker, without the name.'
    })
  ],
  // The black-and-orange wordmark is the 2004 and 2024 reports' own vectors (withSpecimens): the
  // reconstruction from a 210-pixel picture that stood in for them is superseded.
  'worksafebc-orange': [
  ]
}

// ── BC Transit ───────────────────────────────────────────────────────────────────────────────────
//
// From a fifth package (research/identity/bc-transit). It came with an installer that would have
// made these marks recolourable one-offs; they are drawn as supplied instead, like every Crown
// corporation's here. The colour version with its tagline is the package's all-vector derivative —
// the supplied file keeps a small shading bitmap (artwork/bc-transit/supplied/), which this gallery
// does not draw.

const BCT_RIGHTS = { status: 'unresolved', note: `BC Transit’s mark. ${NO_PERMISSION}` }

const BCT_LOOP_DATES = DATED_BY_TIMELINE('first_observation', 'by 2009', 'On the service plan tabled in February 2009.')

const BCT_ENTRIES = {
  'bct-double-arrow': [
    supplied({
      ...RECONSTRUCTED('The roof logo of the red-and-white Gallery In Transit paper model, cut from its printable PDF: ' +
        'its three paths (the two arrow halves and the outlined lettering) as the PDF draws them, nothing traced or ' +
        'redrawn. The model is a modern drawing of the June 1985 poster bus, so the photograph of that poster supports ' +
        'the design and its date but cannot certify these letterforms, their spacing or the colours: #f31410 and ' +
        '#172bb2 are the model file’s values, not brand specifications. The designer and typeface are not known.'),
      applicability: DATED_BY_TIMELINE('dated_specimen', 'June 1985', 'On the Gallery In Transit poster bus, Vancouver, 8–27 June 1985.'),
      rights: BCT_RIGHTS
    })({
      id: 'bct-double-arrow-paper-model',
      label: 'The double arrow and “BC Transit”, from the 1985 paper bus',
      years: 'June 1985',
      note: 'The red double arrow beside “BC Transit” in heavy blue sans, as on the roof of the Gallery In Transit poster bus.'
    })
  ],
  'bct-flag': [
    supplied({
      provenance: 'extracted_from_published_artwork',
      fidelity: 'partially compared',
      fidelityNote: 'The paths of a selection from a service plan’s cover, supplied as SVG: the angled flag above the ' +
        'name, the arrangement of the 2007 and 2008 plans. Only the rest of the page was cropped away; its grey is ' +
        'kept as the ground, since the type and the flag’s keyline are white. Which plan the selection came from is ' +
        'not recorded with it.',
      applicability: DATED_BY_TIMELINE('first_observation', 'by 2007–2008', 'On the service plans of 2007 and February 2008.'),
      rights: BCT_RIGHTS
    })({
      id: 'bct-flag',
      label: 'The flag above the name',
      years: 'by 2007–2008',
      note: 'The provincial flag, angled and waving inside a white keyline, above “BCTransit” in white, on the cover’s grey.',
      reverse: 'bct-flag-white'
    })
  ],
  'bct-loop': [
    // The package classes this derivative as reconstructed, and so does the gallery: its paths are the
    // supplied file's, but it is not the file as supplied.
    supplied({
      provenance: 'reconstructed',
      fidelity: 'partially compared',
      fidelityNote: 'The supplied colour file’s paths, with its tagline’s font outlined where it stood. The file ' +
        'shaded part of the loop with a tiny bitmap; here that part is flat blue, cut along the bitmap’s exact ' +
        'clip, and its white highlights are cut-outs: a derivative, not the file as supplied. When and where ' +
        'the file was published is not recorded.',
      applicability: BCT_LOOP_DATES,
      rights: BCT_RIGHTS
    })({
      id: 'bct-loop-colour',
      label: 'Colour, with tagline',
      years: 'by 2009',
      note: 'The loop in blue and green, “BCTransit”, and “Linking Communities, Businesses & Lifestyles”.'
    }),
    supplied({
      ...SUPPLIED_PATHS('Every path is the supplied file’s own, cropped. The navy, #004370, is the file’s value, ' +
        'not a brand standard.'),
      applicability: {
        kind: 'unknown',
        years: 'undated',
        note: 'When this one-colour version without the tagline was first published has not been found. Its ' +
          'timeline cites the sources for the loop.'
      },
      rights: BCT_RIGHTS
    })({
      id: 'bct-loop-navy',
      label: 'Navy, no tagline',
      years: 'undated',
      note: 'The loop and name in one navy, without the tagline.'
    })
  ]
}

// ── BC Parks' logo of 2023 ───────────────────────────────────────────────────────────────────────
//
// The two files bcparks.ca serves, both its “Primary Reversed”: white type and a gold bar, for its
// navy header. They are shown on that navy, which is the site's and not part of the mark; the files
// as served, without it, are the dark-page form.

const BCP_RIGHTS = { status: 'unresolved', note: `The Province’s mark for BC Parks. ${NO_PERMISSION}` }

const BCP_2023 = (id, label, note, reverse) => supplied({
  provenance: 'extracted_from_official_vector',
  fidelity: 'source compared',
  fidelityNote: 'The SVG bcparks.ca serves, fetched on 22 October 2026: every path is the file’s own, its stylesheet ' +
    'written out as fills. The navy behind it is the site header’s (#003366), not part of the file.',
  applicability: DATED_BY_TIMELINE('first_observation', '2023–present', 'On bcparks.ca from 2 February 2023.'),
  rights: BCP_RIGHTS
})({ id, label, years: '2023–present', note, reverse })

// ── The Department of Recreation and Conservation, 1970–1973 ──────────────────────────────────────
//
// The annual-report reconstructions are documented in research/identity/recreation-conservation-2026-11-21.
// The dogwood oval also has a reconstruction fitted to a supplied green-and-cream image.
// The square symbols come in black, the reports' dark and pale greens, and white, all the same paths.

const DRC_RIGHTS = {
  status: 'unresolved',
  note: `A mark of a former provincial department, whose use is governed by the Government of British Columbia. ${NO_PERMISSION}`
}

const DRC_SQUARE_FIDELITY = 'Redrawn by hand as geometry from scans of the printed annual reports, and overlaid ' +
  'on them in the package’s review sheets. The greens approximate the scans; they are not printing specifications.'

/** One of the five square symbols, in black, with the reports' greens and white as its versions. */
const drcSquare = (key, label, note) => supplied({
  ...RECONSTRUCTED(DRC_SQUARE_FIDELITY),
  applicability: DATED_BY_TIMELINE('dated_specimen', '1971–1973', 'Printed in the department’s annual reports for 1971 to 1973.'),
  rights: DRC_RIGHTS
})({
  id: `drc-${key}`,
  label,
  years: '1971–1973',
  note,
  markLabel: 'Black',
  alternates: [
    { mark: `drc-${key}-green`, label: 'Report green', title: 'The dark green of the reports’ full-ink symbol, approximated from the scans' },
    { mark: `drc-${key}-pale`, label: 'Report pale', title: 'The pale green of the reports’ other symbols, approximated from the scans' }
  ],
  reverse: `drc-${key}-white`
})

const DRC_SQUARES = {
  department: drcSquare('department', 'Department of Recreation and Conservation',
    'Four lobes around a ring in a rounded square: the department’s own symbol, set larger than the others at the foot of the reports’ back covers.'),
  fishWildlife: drcSquare('fish-wildlife', 'Fish and Wildlife Branch',
    'A deer’s head and a fish, interlocked in the rounded square.'),
  parks: drcSquare('parks', 'Provincial Parks Branch',
    'Two spirals on upright stems, mirrored, joined to the frame.'),
  museum: drcSquare('museum', 'British Columbia Provincial Museum',
    'BC over PM, the letters sharing their strokes, now the Royal BC Museum.'),
  fisheries: drcSquare('fisheries', 'Commercial Fisheries Branch',
    'Three fish across a grid. The 1973 report sets the same symbol beside the Marine Resources Branch, as the branch was renamed.')
}

/** One of the department's other emblems, as a single black master. */
const drcEmblem = (id, label, years, note, fidelityNote, dateNote = `Printed in the department’s annual report for ${years}.`) => supplied({
  ...RECONSTRUCTED(fidelityNote),
  applicability: DATED_BY_TIMELINE('dated_specimen', years, dateNote),
  rights: DRC_RIGHTS
})({ id, label, years, note })

const DRC_EMBLEMS = {
  oval: {
    ...drcEmblem('drc-dogwood-oval-1970', 'Dogwood oval', '1970',
      'An engraved dogwood in a dark oval, BRITISH COLUMBIA arched above it and the department’s name below.',
      'The dogwood, lettering and ring were drawn as vector outlines and fitted to a supplied green-and-cream image. ' +
        'The lower edge was completed from the visible oval. The period typeface and the source of the green-and-cream image remain unverified.'),
    themedPreview: true,
    darkPreviewNote: 'The dark preview has a thin cream outline for contrast.'
  },
  fwOval: {
    ...drcEmblem('drc-fw-oval-1973', 'Fish and Wildlife emblem', '1972–73 synopsis and 1973 report',
      'A framed oval above F&W on the 1972–73 hunting regulations cover and the 1973 Fish and Wildlife dividers.',
      'The supplied reconstruction uses one set of Bézier paths for the oval, frame and lettering. ' +
        'The bear’s eye follows the colour reference. Its exact original outline remains uncertain.',
      'The hunting synopsis and the annual report show the emblem in print.'),
    themedPreview: true,
    darkPreviewNote: 'The dark preview uses white ink. Choose White to download that version.',
    markLabel: 'Black',
    alternates: [
      { mark: 'drc-fw-oval-1973-white', label: 'White' },
      { mark: 'drc-fw-oval-1973-orange', label: 'Cream on orange' }
    ]
  },
  fwLockup: {
    ...drcEmblem('drc-fw-lockup-1973', 'Fish and Wildlife emblem and name', '1973',
      'The emblem beside a panel reading British Columbia Fish & Wildlife Branch.',
      'The left panel uses the standalone emblem’s reconstructed paths. The right panel’s lettering uses an outlined Bookman substitute.'),
    themedPreview: true,
    darkPreviewNote: 'The dark preview uses white ink.'
  },
  parksShield: drcEmblem('drc-parks-shield-1973', 'Parks dogwood shield', '1973',
    'A dogwood over the province in a shield, PARKS above and BRITISH COLUMBIA below.',
    'Shield, province, islands and bracts redrawn by hand from the 1973 report’s organization chart; the small ' +
      'captions are approximated with outlined substitutes, and the petals are less certain than the rest.')
}

const BCP_ENTRIES = {
  // The Parks Branch's own marks of the 1970s, also in the department's collection; held here under
  // their own ids so that each collection's page can scroll to its copy.
  'parks-spirals': [{ ...DRC_SQUARES.parks, id: 'bcp-1971-spirals' }],
  'parks-shield': [{ ...DRC_EMBLEMS.parksShield, id: 'bcp-1973-shield' }],
  'parks-current': [
    BCP_2023('bcp-2023', 'The logo, as on its site', 'The flat sun and mountains with “British Columbia”, a gold upright bar, ' +
      'and “BC Parks” in serif, reversed on the site’s navy.', 'bcp-2023-white'),
    BCP_2023('bcp-2023-vertical', 'Stacked', 'The same parts stacked, the mark above the name.', 'bcp-2023-vertical-white')
  ]
}

/**
 * Which one-offs stand for a body the government diagram draws, so a card can lead to it. The
 * Province's marks that name a campaign or a slogan rather than a body have none.
 */
const GRAPH_NODES = {
  'bc-parks': 'sub-bc-parks',
  'bc-parks-banner': 'sub-bc-parks',
  'bc-parks-best-place': 'sub-bc-parks',
  'work-bc': 'sub-workbc',
  'vector-workbc-2016': 'sub-workbc',
  'vector-workbc-current': 'sub-workbc',
  'bc-stats': 'sub-bc-stats',
  'bc-wildfire-service': 'sub-bc-wildfire-service',
  'bc-wildfire-service-one-line': 'sub-bc-wildfire-service',
  'coroners-service': 'sub-bc-coroners-service',
  'bc-online': 'sub-bc-online',
  'bc-bid': 'sub-bc-bid',
  'public-service': 'bc-public-service-agency',
  'vector-bc-public-service-where-ideas-work-2023-reverse': 'bc-public-service-agency',
  // A remake, not the program's own lockup: its card keeps that label wherever it is reached from.
  'prepared-bc': 'sub-preparedbc',
  gcpe: 'government-communications-and-public-engagement',
  'healthlink-bc-logo': 'sub-healthlink-bc'
}

/** BC Parks' marks, which its own collection holds rather than the Province's shelf. */
const PARKS_ONE_OFFS = ['bc-parks', 'bc-parks-banner', 'bc-parks-best-place']
/** BC Lands' badge, held by its own collection likewise. */
const LANDS_ONE_OFFS = ['bc-lands']
const BC_MARK_SPECIMEN_PROGRAMS = new Map(['public-service', 'welcome-bc', 'work-bc', 'stronger-bc']
  .map((program) => [program, `specimens-${program}`]))
const BC_MARK_GUIDE_SECTION = {
  id: ENDORSED_2019.id,
  label: ENDORSED_2019.name,
  entries: collectedEntriesOf(ENDORSED_2019.id)
}
const BC_MARK_COLLECTED_ALIASES = [
  'collected-office-of-the-premier',
  'collected-government-communications-and-public-engagement',
  `collected-${ENDORSED_2019.id}`
]

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
 * Add a body's collected files to an era: its own artwork, or files under an earlier name that the
 * government history records it continuing from.
 */
const withCollected = (marks, earlier) => Object.fromEntries([...new Set([...Object.keys(marks), ...Object.keys(earlier)])]
  .map((era) => [era, [...(marks[era] ?? []), ...(earlier[era] ?? []).flatMap(collectedEntriesOf)]]))

/** Add published specimens outside the body inventory to their recorded collection eras. */
const withSpecimens = (marks, program) => {
  const specimens = specimenEntriesOf(program)
  return Object.fromEntries([...new Set([...Object.keys(marks), ...specimens.map((entry) => entry.asset.timelineEra)])]
    .map((era) => [era, [...(marks[era] ?? []), ...specimens.filter((entry) => entry.asset.timelineEra === era)]]))
}

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
    id: 'health-program-signatures',
    shelf: 'provincial-programs',
    label: 'Provincial health signatures',
    body: 'Ministry of Health Services',
    years: 'Seen in 2003 and 2005',
    cover: 'bchealthcare-2003',
    graphNode: 'ministry-of-health-services-2001',
    graphYear: 2003,
    relatedGenerator: { era: 'crest', label: 'Explore the provincial crest in the generator' },
    intro: 'BCHealthCare and BCPharmaCare used blue provincial arms and a two-colour name. A January 2003 hospital project cover carries BCHealthCare. The 2003 Fair PharmaCare brochure and an April 2005 newsletter carry BCPharmaCare.',
    entries: specimenEntriesOf('health-program-signatures').map((entry) => ({ ...entry, owner: entry.asset.owner }))
  },
  {
    id: 'tourism-bc-destination-bc',
    shelf: 'bodies',
    label: 'Tourism BC & Destination BC',
    body: 'The tourism organizations’ corporate identities',
    years: '1997–present',
    graphNode: 'destination-bc',
    graphNodes: ['tourism-bc', 'destination-bc'],
    aliases: ['collected-tourism-bc', 'collected-destination-bc'],
    cover: 'source-destination-bc-destination-bc-svg',
    intro: 'The corporate identities of Tourism BC and Destination BC, with each organization’s own artwork and history. Their websites, campaigns and publications are connected in the Tourism initiative.',
    initiativeId: 'tourism',
    // Related custodians, not one corporation renamed: retain each body's own identity record.
    entries: [...collectedEntriesOf('destination-bc'), ...collectedEntriesOf('tourism-bc')]
  },
  {
    id: 'bc-hydro',
    shelf: 'bodies',
    label: 'BC Hydro',
    body: 'Crown corporation · Ministry of Energy and Climate Solutions',
    years: '1961–present',
    graphNode: 'bc-hydro',
    cover: 'bc-hydro-current-colour',
    // How each era's artwork was made is on its chips and under "About these marks".
    intro: 'BC Hydro’s three identities, oldest first.',
    eras: [
      era({
        id: 'bc-hydro-1961',
        years: '1961–1990',
        label: 'The Rimmer signature',
        note: 'Designed by Jim Rimmer and launched in 1961: a ringed H of two four-pointed stars, green ' +
          'over blue, beside “B.C.Hydro” in a serif, drawn from five pages of its identity ' +
          'manual: four signatures, and the rules for signs, backgrounds and vehicles, checked as you ' +
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
          },
          ...collectedEntriesOf('bc-hydro').filter(({ id }) => id === 'bc-hydro-for-generations-2012')
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
        entries: [
          ['Signature with Power smart', ['colour', 'black', 'reverse']],
          ['Without tagline', ['signage']],
          ['Symbol', ['symbol', 'symbol-border']]
        ].map(([label, variants]) => ({
          id: `bc-hydro-current-${variants[0]}`,
          kind: 'hydro-mark',
          mark: 'current',
          variant: variants[0],
          label,
          years: '2016–present',
          note: CURRENT_VARIANTS[variants[0]].hint,
          editorVersions: variants.map((variant) => ({
            id: `bc-hydro-current-${variant}`, variant, label: CURRENT_VARIANTS[variant].label
          }))
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
    initiativeId: 'dfam',
    cover: 'bcts',
    intro: 'The first BCTS website banner and two different printed identities overlapped. Its 2004 brochure shows the Forest Service oval beside green BCTS initials. ' +
      'It describes 12 business areas, a presence in 33 locations and a small headquarters in Victoria. Later publications pair the initials with a ministry crest or the provincial BC mark.',
    eras: withMarks(COLLECTION_ERAS.bcts, {
      'bcts-banner': specimenEntriesOf('bcts'),
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
    intro: 'The Insurance Corporation of British Columbia’s marks: a registry emblem of 1974, a half-disc ' +
      'beside its name by 1989, then the road badge: in a serif, a heavier sans, and since 2008 with ' +
      'rounded corners.',
    eras: withMarks(COLLECTION_ERAS.icbc, {
      ...ICBC_ENTRIES,
      'icbc-rounded': [{ ...ICBC_ENTRIES['icbc-rounded'][0], label: 'Rounded ICBC badge', editorVersions: ICBC_ENTRIES['icbc-rounded'] }]
    })
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
      'from red, orange and green to purple, coral and yellow. Original vectors from the 2009 service plan ' +
      'update and 2010/11 annual report sit beside the supplied artwork.',
    eras: withMarks(COLLECTION_ERAS.bclc, withCollected(BCLC_ENTRIES, {
      'bclc-2008': ['bclc']
    }))
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
    // The bodies it was before 1977, whose collected files are in its first two eras.
    graphNodes: ['bc-ferry-corporation', 'bc-ferry-authority', 'bc-toll-highways-and-bridges-authority'],
    aliases: ['collected-bc-ferry-authority', 'collected-bc-toll-highways-and-bridges-authority'],
    cover: 'bcf-wave',
    intro: 'BC Ferries from its start in 1960, when it sailed as the British Columbia Toll Authority Ferry ' +
      'System under that name’s wordmark, until 1964, when its authority was renamed. Then its two symbols: ' +
      'the dogwood, first an outlined flower on a waving flag and later redrawn in geometric petals beside a ' +
      'squared wordmark, and the wave, introduced on 2 April 2003 with the company that replaced the Crown ' +
      'corporation. Beside them are newspaper specimens as found: the Toll Authority ferry system’s emblem in ' +
      '1960, and the British Columbia Ferry Authority’s signature and dogwood flag in 1964.',
    eras: withMarks(COLLECTION_ERAS['bc-ferries'], withCollected(BCF_ENTRIES, {
      'bcf-toll-authority': ['bc-toll-highways-and-bridges-authority'],
      'bcf-early-dogwood': ['bc-ferry-authority']
    }))
  },
  {
    id: 'worksafebc',
    shelf: 'bodies',
    label: 'WorkSafeBC',
    body: 'Workers’ Compensation Board · agency',
    years: '1917–present',
    graphNode: 'workers-compensation-board',
    cover: 'vector-worksafebc-2024-colour-source-vector',
    intro: 'The Workers’ Compensation Board’s marks: a worker-protection emblem introduced in 1968, still ' +
      'sought; the province and worker from 1983; a distressed WorkSafe wordmark in ' +
      'the 2003 annual report; and black-and-orange WorkSafeBC in the 2004 and 2024 reports, as their ' +
      'original vectors. Report years do ' +
      'not establish logo introductions. WorkSafeBC became the operating name in 2005. What the board used ' +
      'from its founding in 1917 until 1968 is not known.',
    eras: withMarks(COLLECTION_ERAS.worksafebc, withSpecimens(WCB_ENTRIES, 'worksafebc'))
  },
  {
    id: 'bc-transit',
    shelf: 'bodies',
    label: 'BC Transit',
    body: 'Crown corporation · Ministry of Transportation and Transit',
    years: '1979–present',
    graphNode: 'bc-transit',
    graphNodes: ['bc-transit', 'urban-transit-authority'],
    aliases: ['collected-urban-transit-authority'],
    cover: 'bct-loop-colour',
    intro: 'BC Transit began as the Urban Transit Authority, whose lettering and double-arrow device are here from ' +
      'newspaper advertisements of 1979 and 1980. When it took the name BC Transit in 1982 the arrow went with it, ' +
      'red beside the new name in blue, as on the roof of the paper bus that was a June 1985 exhibition poster. ' +
      'Then the provincial flag with the name, seen in two arrangements (the one above the name is here, from a ' +
      'service plan’s cover), and by 2009 the blue-and-green loop, which it still uses. Its bus liveries changed ' +
      'in 2007 and 2024; neither is a new logo.',
    eras: withMarks(COLLECTION_ERAS['bc-transit'], withCollected(BCT_ENTRIES, {
      'bct-urban-transit-authority': ['urban-transit-authority']
    }))
  },
  {
    id: 'bc-parks',
    shelf: 'bodies',
    label: 'BC Parks',
    body: 'Division · Ministry of Environment and Parks',
    years: '1971–present',
    graphNode: 'sub-bc-parks',
    cover: 'bc-parks',
    intro: 'BC Parks’ marks, oldest first: the Parks Branch’s spirals and dogwood shield from the Department of ' +
      'Recreation and Conservation’s reports of 1971–1973, reconstructions shared with that department’s ' +
      'collection; its badge from the flag years (the flag symbol in a rounded ' +
      'frame with “Parks” set at the size of “BC”), then “BCParks” beside the shaded sun, and beside the ' +
      'Best Place on Earth mark, both put together here from the Province’s own artwork and lettering, ' +
      'and today’s logo as bcparks.ca serves it. The flag badge and the two banners open to recolour.',
    eras: withMarks(COLLECTION_ERAS['bc-parks'], {
      'parks-badge': ONE_OFFS.filter((entry) => entry.id === 'bc-parks').map(provincial),
      'parks-shaded-banner': ONE_OFFS.filter((entry) => entry.id === 'bc-parks-banner').map(provincial),
      'parks-best-place': ONE_OFFS.filter((entry) => entry.id === 'bc-parks-best-place').map(provincial),
      ...BCP_ENTRIES
    })
  },
  {
    id: 'recreation-conservation',
    // A department: it opens in Departmental Logos (movedGalleryPlaces.js), and is kept here unlisted
    // so the Royal BC Museum's and BC Parks' copies of its marks, and the register, still find it.
    shelf: 'departmental',
    showInGalleryIndex: false,
    label: 'Recreation and Conservation',
    body: 'Provincial department, 1957–1976',
    years: '1970–1973',
    cover: 'drc-department',
    intro: 'The Department of Recreation and Conservation’s marks, from its annual reports: an engraved dogwood ' +
      'oval in 1970; then, from 1971 to 1973, five square symbols, one for the department and one each for ' +
      'Fish and Wildlife, Provincial Parks, the Provincial Museum and Commercial Fisheries; and two emblems ' +
      'that join them in 1973. The dogwood oval opens in a green-and-cream reconstruction. The Fish and Wildlife ' +
      'oval opens in the supplied reconstruction, with white and cream-on-orange versions. The squares open in ' +
      'black, the reports’ two greens and white. The package’s report dividers, cover blocks, handbook panels ' +
      'and the 22 park signs proposed in 1971 are kept with it in artwork/recreation-conservation.',
    eras: withMarks(COLLECTION_ERAS['recreation-conservation'], {
      'drc-dogwood-oval': [DRC_EMBLEMS.oval],
      'drc-five-squares': Object.values(DRC_SQUARES),
      'drc-1973-emblems': [DRC_EMBLEMS.fwOval, DRC_EMBLEMS.fwLockup, DRC_EMBLEMS.parksShield]
    })
  },
  {
    id: 'royal-bc-museum',
    shelf: 'bodies',
    label: 'Royal BC Museum',
    body: 'Crown corporation · formerly the British Columbia Provincial Museum',
    years: '1886–present',
    graphNode: 'royal-bc-museum',
    // The collection the acquisition pass made for it, whose links still lead here.
    aliases: ['collected-royal-bc-museum'],
    cover: 'source-royal-bc-museum-royal-bc-museum-svg',
    intro: 'The museum’s marks, oldest first: the Provincial Museum’s BC-over-PM square from the Department of ' +
      'Recreation and Conservation’s reports of 1971–1973, a reconstruction shared with that department’s ' +
      'collection; then today’s logo as rbcm.ca serves it. The marks in between are still sought.',
    eras: withMarks(COLLECTION_ERAS['royal-bc-museum'], withCollected({
      // Held here under its own id, so that each collection's page can scroll to its copy.
      'rbcm-bcpm-square': [{ ...DRC_SQUARES.museum, id: 'rbcm-1971-bcpm' }]
    }, {
      'rbcm-current': ['royal-bc-museum']
    }))
  },
  {
    id: 'bc-lands',
    shelf: 'bodies',
    label: 'BC Lands',
    body: 'Provincial crown lands administration',
    years: '1986–88 ministry form and 1994 fax',
    cover: 'bc-lands',
    intro: 'BC Lands’ badge from the flag years: the flag symbol in a rounded frame with “Lands” set at ' +
      'the size of “BC”, the arrangement of BC Parks’ badge, but lighter, in regular letters and a thinner ' +
      'frame. The reconstruction follows the proportions of a photocopied ministry form. A 1994 Lands Operations ' +
      'Division fax also shows the badge beside a band of provincial silhouettes.',
    eras: withMarks(COLLECTION_ERAS['bc-lands'], {
      'lands-badge': ONE_OFFS.filter((entry) => LANDS_ONE_OFFS.includes(entry.id)).map(provincial)
    })
  },
  // Ministries' own marks from the flag years. A ministry is not a body of the atlas, but it is a
  // node of the government map, so each collection is tied to its ministry there.
  {
    id: 'bc-environment',
    shelf: 'bodies',
    label: 'BC Environment',
    body: 'Ministry of Environment, 1988–1991',
    years: 'flag years',
    graphNode: 'ministry-of-environment-1988',
    graphYear: 1989,
    cover: 'bc-environment-flag-years',
    intro: 'The Ministry of Environment’s mark from the flag years: “BC” beside the flag symbol with ' +
      '“Environment” below, as an undated cover prints it, cream on a diagonal green band. Rebuilt from ' +
      'the gallery’s own flag artwork and Helvetica Bold, fitted to a scan; it opens upright in one ink, ' +
      'with the cover’s cream and its diagonal band as versions. BC Parks’ and BC Lands’ badges are the ' +
      'same family.',
    eras: withMarks(COLLECTION_ERAS['bc-environment'], {
      'environment-flag': specimenEntriesOf('bc-environment')
    })
  },
  {
    id: 'tourism-recreation-culture',
    shelf: 'bodies',
    label: 'Tourism, Recreation and Culture',
    body: 'Ministry of Tourism, Recreation and Culture, 1986–1988',
    years: '1986–1988',
    graphNode: 'ministry-of-tourism-recreation-and-culture-1986',
    graphYear: 1987,
    cover: 'tourism-recreation-culture-1986',
    intro: 'The ministry’s mark under its only minister, Bill Reid: the flag symbol with its stripes run ' +
      'out to the left as three long bands between “Tourism” and “Recreation and Culture”, in one ' +
      'blue-violet ink. Rebuilt from the gallery’s own flag artwork (the Super, Natural sign’s) and ' +
      'italic serif outlines, fitted to a screenshot. The Province’s tourism marketing later went to ' +
      'Tourism BC.',
    eras: withMarks(COLLECTION_ERAS['tourism-recreation-culture'], {
      'trc-flag-stripes': specimenEntriesOf('tourism-recreation-culture')
    })
  },
  {
    id: 'reswest',
    shelf: 'bodies',
    label: 'ResWest',
    body: 'Provincewide tourism reservations service',
    years: 'Documented in 1985–1986',
    cover: 'reswest-badge',
    intro: 'ResWest took reservations by telephone and mail through a computerized booking service. Tourism Minister Claude Richmond reported in 1985 that the Province had franchised the system the previous year. In 1986 he described ResWest as the successful bidder and said the privately operated service was promoted in provincial tourism literature. Expo 86 named it the fair’s official accommodation agency.',
    eras: withMarks([resWestBadgeEra], {
      [resWestBadgeEra.id]: specimenEntriesOf('reswest').map((entry) => ({ ...entry, owner: 'reswest' }))
    })
  },
  {
    id: 'superhost',
    shelf: 'bodies',
    label: 'SuperHost',
    body: 'Ministry of Tourism’s hospitality-training program',
    years: 'Expo 86 years',
    graphNode: 'ministry-of-tourism-1980',
    graphYear: 1985,
    cover: 'superhost-1986',
    intro: 'The Ministry of Tourism’s training program for the people who served visitors in the Expo 86 ' +
      'years. Its mark is “Expect the most”: a spray of stars bursting up out of the flag symbol over ' +
      '“SUPERHOST”. Rebuilt on the gallery’s own flag artwork, with fitted stars and redrawn lettering, ' +
      'from a 1986 newspaper advertisement. The trademark specimen’s wider arrangement and colour ' +
      'interpretations are versions. The later SuperHost figure mark is in the Tourism BC & Destination BC ' +
      'initiative.',
    eras: withMarks(COLLECTION_ERAS.superhost, {
      'superhost-expect-the-most': specimenEntriesOf('superhost')
    })
  },
  {
    id: 'specimens-travel-industry',
    shelf: 'departmental',
    label: 'Department of Travel Industry',
    body: 'Departmental logo',
    years: 'Seen about 1970',
    intro: 'The map and dogwood in the department’s book This is British Columbia.',
    graphNode: 'department-of-travel-industry-1967',
    cover: 'bc-travel-industry-ca-1970',
    entries: specimenEntriesOf('travel-industry')
  },
  {
    id: 'bc-mark',
    shelf: 'bc-mark',
    label: 'On the BC mark',
    body: 'The Province’s one-off marks',
    years: '2005–present',
    cover: 'welcome-bc',
    aliases: [...BC_MARK_COLLECTED_ALIASES, ...BC_MARK_SPECIMEN_PROGRAMS.values()],
    intro: 'The June 2019 guidelines show how to pair program wordmarks with the BC mark. ' +
      'The collection also holds signatures created for individual bodies, programs and campaigns.',
    artworkSections: [BC_MARK_GUIDE_SECTION],
    entries: [
      ...BC_MARK_GUIDE_SECTION.entries,
      ...ONE_OFFS.filter((entry) => !PARKS_ONE_OFFS.includes(entry.id) && !LANDS_ONE_OFFS.includes(entry.id))
        .flatMap((entry) => BC_MARK_SPECIMEN_PROGRAMS.has(entry.id)
          ? [provincial(entry), ...specimenEntriesOf(entry.id, entry.id).map(withNode)]
          : [provincial(entry)]),
      ...specimenEntriesOf('bc-150-years'),
      ...collectedEntriesOf('government-communications-and-public-engagement'),
      // A service wordmark in the BC mark's Garamond, held as published.
      ...specimenEntriesOf('bceid'),
      // A service on the BC mark, as its website serves it.
      ...specimenEntriesOf('healthlink-bc').map(withNode),
      // An office's signature from before the BC mark: the arms in a rounded frame over its name, on
      // its 1991 letterhead, drawn once for it and held as found.
      ...collectedEntriesOf('office-of-the-premier')
    ]
  }
]

// Collections recovered by the acquisition pass use source files directly. Existing researched
// histories remain authoritative for bodies that already have a collection.
GALLERY_COLLECTIONS.push(...COLLECTED_COLLECTIONS.filter((candidate) => !BC_MARK_COLLECTED_ALIASES.includes(candidate.id) &&
  !GALLERY_COLLECTIONS.some((held) => nodesOf(held).includes(candidate.graphNode))))
// WorkSafeBC's specimens are folded into its collection above; the one-off programs keep theirs.
// Travel Industry opens in Departmental Logos and keeps its own register collection.
// A program's published specimens belong to the body its one-off stands for, so the body's panel
// finds the original files too.
GALLERY_COLLECTIONS.push(...SPECIMEN_COLLECTIONS.filter((collection) => !['specimens-health-program-signatures', 'specimens-worksafebc', 'specimens-bcts', 'specimens-travel-industry', 'specimens-justice-institute', 'specimens-auditor-general', 'specimens-sub-bc-online', 'specimens-bceid', 'specimens-shared-services-bc', 'specimens-sub-bc-cancer', 'specimens-healthlink-bc', 'specimens-bc-environment', 'specimens-tourism-recreation-culture', 'specimens-reswest', 'specimens-superhost', 'specimens-bc-150-years', ...BC_MARK_SPECIMEN_PROGRAMS.values()].includes(collection.id))
  .map((collection) => {
    if (collection.id === 'specimens-ecosystems-at-risk') {
      return { ...collection, label: 'Ecosystems at Risk', shelf: 'provincial-programs',
        body: 'B.C. Conservation Data Centre brochure series',
        cover: 'ecosystems-at-risk-badge', years: 'Seen in 1993 and 2006',
        intro: 'The B.C. Conservation Data Centre used this tilted badge on public brochures about threatened habitats. The brochures explained where each ecosystem occurs, what lives there, why it is vulnerable and how people can help protect it. The badge appears on Garry Oak Ecosystems in October 1993 and Estuaries in British Columbia in March 2006.' }
    }
    if (collection.id === bearAwareGalleryId) {
      return { ...collection, label: bearAwareTitle, fileCollection: false, shelf: 'initiatives',
        initiativeId: bearAwareId, cover: bearAwareMarkId, years: 'Artwork documented in 1997',
        entries: collection.entries.map((entry) => ({ ...entry, owner: bearAwareId })),
        body: 'Revelstoke wildlife education campaign',
        intro: 'The five-clawed paw and stacked Be Bear Aware lettering appear together on a checklist reproduced in the 1997 final report.' }
    }
    if (collection.id === environmentYouthCorpsGalleryId) {
      return { ...collection, label: 'Environment Youth Corps', fileCollection: false, shelf: 'initiatives',
        initiativeId: environmentYouthCorpsId, cover: environmentYouthCorpsScan.id, years: 'Seen in June 1990',
        entries: collection.entries.map((entry) => ({ ...entry, owner: environmentYouthCorpsId })),
        body: 'Provincial youth employment and training program',
        intro: 'The Corps used this mark in its June 1990 recruitment campaign. The newspaper scan and a vector reconstruction are available.' }
    }
    if (collection.id === 'specimens-firesmart-bc') {
      return { ...collection, label: 'FireSmart BC', fileCollection: false, shelf: 'initiatives', initiativeId: 'firesmart-bc',
        entries: collection.entries.map((entry) => ({ ...entry, owner: 'firesmart-bc' })),
        cover: 'firesmart-bc-signature', years: 'Artwork documented in July 2025',
        body: 'BC FireSmart Committee',
        intro: 'The provincial signature, four program and event identities, and Ember the FireSmart Fox, from the second edition of the FireSmart BC Brand Guidelines.' }
    }
    if (collection.id === 'specimens-buy-bc') {
      return { ...collection, label: 'Buy BC', fileCollection: false, graphNode: 'sub-buy-bc', body: 'Provincial food and beverage marketing program',
        shelf: 'initiatives', initiativeId: 'buy-bc', cover: 'buy-bc-vertical-colour',
        years: 'Artwork documented in 2023',
        intro: 'The Buy BC graphic standards show the program name below or beside its landscape emblem. The emblem also appears on its own as a digital icon.' }
    }
    if (collection.id === 'specimens-pacific-gateway') {
      return { ...collection, shelf: 'initiatives', initiativeId: 'pacific-gateway', showInGalleryIndex: false }
    }
    const node = GRAPH_NODES[collection.id.replace(/^specimens-/, '')]
    return node ? { ...collection, entries: collection.entries.map((entry) => ({ ...entry, graphNode: entry.graphNode ?? node })) } : collection
  }))

// PEP had its own provincial identity and administered federal JEPP funding in B.C.
const pepCollection = GALLERY_COLLECTIONS.find(({ id }) => id === 'specimens-provincial-emergency-program')
Object.assign(pepCollection, {
  shelf: 'bodies',
  label: 'Provincial Emergency Program',
  body: 'Provincial emergency preparedness and response',
  years: 'Logo documented in 1993, 1997 and 2003',
  cover: 'pep-striped-ink',
  initiativeId: 'jepp',
  intro: 'British Columbia’s Provincial Emergency Program processed applications and claims for JEPP. Its striped monogram appears on the 1993 guidelines. A provincial compliments slip received in October 1997 and a 2003 student safety guide show the heavier three-line lettering reconstructed here.',
  entries: specimenEntriesOf('provincial-emergency-program').map((entry) => ({ ...entry, owner: 'provincial-emergency-program' }))
})

// Public bodies outside the Crown corporations and health authorities the shelf collects for — a
// post-secondary institute and an officer of the Legislature — whose collections are placed there by hand.
const PLACED = {
  'justice-institute': {
    label: 'JIBC',
    body: 'Current public post-secondary institute',
    years: '1978–present',
    cover: 'jibc-logo',
    intro: 'The Justice Institute of British Columbia, established in 1978 to train police, corrections, sheriffs, ' +
      'paramedics, firefighters and emergency managers. Its blue griffin shield appears on letterhead in 2007 and on its 2008–09 and 2009–10 accountability reports. JIBC unveiled the eagle in September 2022. Its badge monogram also appears on shoulder patches.'
  },
  'sub-bc-online': {
    label: 'BC OnLine',
    body: 'The Province’s online registry access service',
    years: '1989–present',
    cover: 'bc-online-2011-logo',
    intro: 'BC OnLine, created in July 1989 and run at first by BC Systems, gives professional users online access to ' +
      'land titles, personal property, company and other registries. Its earlier logo (a hand reaching through a ' +
      'screen) is here; its later logo on the BC mark is under “On the BC mark”.'
  },
  // The historical body research/history/bodies-shared-services-2026-11-13.json adds.
  'shared-services-bc': {
    label: 'Shared Services BC',
    body: 'The government’s shared-services organization, as Solutions BC and Shared Services BC',
    years: '2003–?',
    cover: 'shared-services-bc-2015-rebuilt',
    intro: 'Solutions BC, launched on 1 April 2003 in the Ministry of Management Services, gathered the government’s ' +
      'common IT, payroll, accounting and procurement services. It was Shared Services BC by February 2006, and took in ' +
      'the former BC Buildings Corporation’s accommodation services that April. The name is last seen in 2015.'
  },
  'sub-bc-cancer': {
    label: 'BC Cancer',
    body: 'Agency of the Provincial Health Services Authority',
    years: '1974–present',
    cover: 'bc-cancer-phsa',
    intro: 'The BC Cancer Agency’s circular emblem and logo, seen from 2000 to 2015, and the stacked BC / CAN / CER of ' +
      'its identity as BC Cancer since November 2017: for BC Cancer, its Research Centre and Institute, and the BC Cancer ' +
      'Foundation, its fundraising charity, which shares the identity and has a newer logo of its own.'
  },
  'auditor-general': {
    label: 'Auditor General',
    body: 'Current officer of the Legislature',
    years: '1977–present',
    intro: 'The Office of the Auditor General of British Columbia, which audits the government’s accounts and ' +
      'programs and reports to the Legislative Assembly.'
  }
}
// A shared visual identity does not make the fundraising charity part of the agency. These
// design IDs retain their owner even while the collection shows the family together. The
// Foundation is not a node in the provincial-government graph.
const ENTRY_OWNERS = {
  'bc-cancer-foundation-2018': 'bc-cancer-foundation',
  'bc-cancer-foundation-2026': 'bc-cancer-foundation'
}
for (const [node, place] of Object.entries(PLACED)) {
  const held = SPECIMEN_COLLECTIONS.find((collection) => collection.id === `specimens-${node}`)
  if (!held) continue
  const cover = place.cover ?? held.entries[0]?.id
  GALLERY_COLLECTIONS.push({
    ...held,
    ...place,
    id: `collected-${node}`,
    shelf: 'bodies',
    graphNode: place.graphNode === undefined ? node : place.graphNode,
    cover,
    // A body's files, not a program's: they sit on no timeline.
    entries: coverFirst(held.entries, cover).map(({ timeline, ...entry }) => ({ ...entry, owner: ENTRY_OWNERS[entry.id] ?? node }))
  })
}

// Former departments, ministries and government branches open in Departmental Logos instead of
// the gallery's index (movedGalleryPlaces.js). They stay here, unlisted, so search, the register and
// any collection sharing their marks still find them; their links redirect.
for (const id of DEPARTMENTAL_COLLECTIONS) {
  const collection = GALLERY_COLLECTIONS.find((each) => each.id === id)
  if (!collection) throw new Error(`Unknown departmental collection: ${id}`)
  Object.assign(collection, { shelf: 'departmental', showInGalleryIndex: false })
}

// Every collection leads with its body's identity: anniversary, campaign, event, partner and
// decorative marks follow it, in sections of their own, and are never its cover while it holds an
// identity design (markRoles.js). Each collection object is kept, so later references still hold.
for (const collection of GALLERY_COLLECTIONS) Object.assign(collection, withMarkRoles(collection))

/**
 * Every collection holding a body's own designs. Its dedicated collection comes first, followed
 * by shared shelves such as the BC mark. Gallery placement and organization identity are separate.
 */
export const collectionsOfNode = (node) => {
  if (!node) return []
  const dedicated = GALLERY_COLLECTIONS.filter((collection) => nodesOf(collection).includes(node))
  return [...dedicated, ...GALLERY_COLLECTIONS.filter((collection) =>
    !dedicated.includes(collection) && entriesOfNode(collection, node).length > 0)]
}

/** The preferred collection: the body's own history where held, otherwise a shared shelf. */
export const collectionOfNode = (node) => collectionsOfNode(node)[0]

/** The collection a link names: by its id, or by the id one of its earlier names had on its own. */
export const collectionById = (id) => GALLERY_COLLECTIONS.find((collection) => collection.id === id || collection.aliases?.includes(id))

/**
 * A body's own logos in a collection that holds several names: the files collected under that name,
 * or for the collection's own body, those and every mark not collected for another.
 */
export const entriesOfNode = (collection, node) => entriesOf(collection)
  .filter((entry) => (entry.owner ?? entry.graphNode ?? collection.graphNode) === node)

// ── Related collections, under an organization's page ────────────────────────────────────────────
//
// A service brand, program or subsidiary with logos of its own keeps its own collection, but is
// shelved under the organization it belongs to rather than beside it as a body of its own: the
// gallery's first page lists them by organization, and the organization's page lists its own.
// The ties are the register's (identitySubjects.js) and were checked against each organization's
// own pages, reports and filings; a line's or service's operator is not its owner, so the Canada
// and Millennium lines sit under TransLink, whose services they are, not under BCRTC or the
// Canada Line's concessionaire. Umo is BC Transit's, licensed from Cubic, not TransLink's.
export const FOLDED_UNDER = [
  {
    parent: 'collected-translink',
    children: ['collected-translink-t-marker', 'collected-compass', 'collected-skytrain', 'collected-expo-line', 'collected-millennium-line',
      'collected-canada-line', 'collected-seabus', 'collected-b-line', 'collected-rapidbus', 'collected-nightbus', 'collected-handydart',
      'collected-quickpass', 'collected-aircare', 'collected-transit-security', 'collected-coast-mountain-bus-company',
      'collected-british-columbia-rapid-transit-company', 'collected-west-coast-express', 'collected-metro-vancouver-transit-police']
  },
  { parent: 'bc-transit', children: ['collected-umo'] },
  { parent: 'bc-ferries', children: ['collected-bc-ferries-travel'] },
  { parent: 'bc-hydro', children: ['collected-power-smart', 'collected-sub-powerex', 'collected-fish-wildlife-compensation-program'] },
  { parent: 'collected-bc-housing', children: ['collected-sub-bc-housing-licensing-and-consumer-services'] },
  // Chances venues each have their own owner, but run under BCLC service agreements (chancespr.ca, research
  // in northernTravelGuides.js), so their signatures sit with BCLC's.
  { parent: 'bclc', children: ['collected-gamesense', 'collected-sub-playnow', 'collected-chances-gaming'] },
  {
    parent: LIQUOR_DISTRIBUTION_COLLECTION,
    children: ['collected-sub-bcliquor', 'collected-bc-signature-liquor-store',
      'collected-sub-bc-cannabis-stores', 'collected-bc-cannabis-wholesale', 'collected-ldb-wholesale']
  },
  { parent: 'collected-land-title-and-survey-authority', children: ['collected-landsure-systems'] },
  { parent: 'collected-metro-vancouver', children: ['collected-metro-vancouver-regional-parks'] },
  { parent: 'collected-sub-british-columbia-geological-survey', children: ['collected-bcgs-mapplace', 'collected-bcgs-minfile'] },
  {
    parent: 'collected-provincial-health-services-authority',
    children: ['collected-sub-bc-childrens-hospital', 'collected-sub-bc-womens-hospital', 'collected-sub-bc-centre-for-disease-control', 'collected-sub-bc-cancer', 'collected-bc-emergency-health-services']
  },
  { parent: 'collected-bc-pavilion-corporation', children: ['collected-sub-bc-place', 'collected-sub-vancouver-convention-centre'] },
  // From the review in research/identity/gallery-hierarchy-2026-11-27: each tie is the register's own
  // part-of, service-of or operated-by relation. Earlier names of a continuing body are not folded
  // here, since this shelf is for programs, services and subsidiaries; their histories link them.
  { parent: 'collected-islands-trust', children: ['collected-islands-trust-conservancy', 'collected-islands-2050'] },
  { parent: 'collected-legislative-assembly', children: ['collected-legislative-library-bc'] },
  { parent: 'collected-university-of-british-columbia', children: ['collected-ubc-okanagan-campus'] },
  { parent: 'collected-4vi-group', children: ['collected-4tvi-stewardship', 'collected-4ever-strategies', 'collected-4good-social-impact-fund'] },
  { parent: 'tourism-bc-destination-bc', children: ['collected-vancouver-coast-mountains', 'collected-destination-brand', 'collected-visitor-centre'] },
  { parent: 'collected-bc-snowmobile-federation', children: ['collected-lets-ride-bc'] },
  { parent: 'collected-bc-association-farmers-markets', children: ['collected-bc-farmers-market-trail'] },
  { parent: 'collected-bc-regional-tourism-secretariat', children: ['collected-bc-tourism-sustainability-network'] },
  { parent: 'collected-bc-injury-research-and-prevention-unit', children: ['collected-concussion-awareness-training-tool', 'collected-active-safe-central', 'collected-cost-of-injury', 'collected-prevent-shaken-baby-syndrome-bc'] },
  // The second pass: each rests on a register tie that names the parent (operated-by, or a labelled
  // related-to such as "Based at the injury research unit" or "Coalition managed by"), checked against
  // the child's own intro. FWCP is BC Hydro's: BC Hydro funds it to meet its water licences (fwcp.ca).
  { parent: 'collected-bc-lodging-campgrounds-association', children: ['collected-camping-rving-bc-coalition'] },
  { parent: 'collected-bc-craft-brewers-guild', children: ['collected-bc-ale-trail'] },
  { parent: 'collected-rural-coordination-centre-bc', children: ['collected-real-time-virtual-support'] },
  { parent: 'collected-municipality-west-vancouver', children: ['collected-west-vancouver-blue-bus'] },
  { parent: 'collected-emergency-health-services-commission', children: ['collected-bc-ambulance-service'] }
]

// Program collections link to their histories in the initiatives register.
for (const program of ['gamesense', 'bc-youth', 'power-smart']) {
  GALLERY_COLLECTIONS.find((collection) => collection.id === 'collected-' + program).initiativeId = program
}

GALLERY_COLLECTIONS.find((collection) => collection.id === 'collected-bc-youth').shelf = 'initiatives'

for (const { parent, children } of FOLDED_UNDER) {
  if (!GALLERY_COLLECTIONS.some((collection) => collection.id === parent)) throw new Error(`Unknown parent collection: ${parent}`)
  for (const id of children) {
    const child = GALLERY_COLLECTIONS.find((collection) => collection.id === id)
    if (!child) throw new Error(`Unknown collection to fold under ${parent}: ${id}`)
    if (child.foldedUnder) throw new Error(`Collection folded twice: ${id}`)
    child.shelf = 'grouped'
    child.foldedUnder = parent
  }
}

/** The collections shelved under an organization's, in the order above. */
export const childCollectionsOf = (id) => (FOLDED_UNDER.find((group) => group.parent === id)?.children ?? [])
  .map((child) => GALLERY_COLLECTIONS.find((collection) => collection.id === child))

/** Each organization with its programs, services and subsidiaries, for the first page. */
export const FOLDED_GROUPS = FOLDED_UNDER.map(({ parent }) => ({
  parent: GALLERY_COLLECTIONS.find((collection) => collection.id === parent),
  children: childCollectionsOf(parent)
}))

export const COLLECTIONS_ON_SHELF = (shelf) => GALLERY_COLLECTIONS.filter((collection) => collection.shelf === shelf)

/** Every entry of a collection, across its eras. */
export const entriesOf = (collection) => collection.eras
  ? collection.eras.flatMap((each) => each.entries)
  : collection.entries

// Program marks published with no owning body (WelcomeBC, StrongerBC and the like) are owned by
// their program's register subject, so every held entry has an explicit owner.
for (const collection of GALLERY_COLLECTIONS) {
  for (const entry of entriesOf(collection)) {
    if (entry.owner === undefined && PROGRAM_ENTRY_OWNERS[entry.id]) entry.owner = PROGRAM_ENTRY_OWNERS[entry.id]
  }
}

export const findGalleryEntry = (id) => GALLERY_COLLECTIONS
  .flatMap(entriesOf)
  .find((entry) => entry.id === id || entry.aliases?.includes(id) ||
    entry.versions?.some((version) => version.id === id) ||
    entry.editorVersions?.some((version) => version.id === id) ||
    entry.paletteGroup?.palettes.some((palette) => palette.sourceIds?.includes(id)))

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
