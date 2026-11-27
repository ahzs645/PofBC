 count: 22206)
Total output lines: 1699

566a7fb58508aa770a60df033b822cd77b989fd6
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
import { LIQUOR_DISTRIBUTION_COLLECTION } from './liquorHistory.js'
import { ENDORSED_2019 } from './endorsed2019.js'
import { bearAwareGalleryId, bearAwareId, bearAwareMarkId, bearAwareTitle } from '../initiatives/bearAwareArtwork.js'
import { environmentYouthCorpsGalleryId, environmentYouthCorpsId, environmentYouthCorpsScan } from '../initiatives/environmentYouthCorpsArtwork.js'
import { resWestBadgeEra } from './resWest.js'

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
…12206 tokens truncated…ervice. Tourism Minister Claude Richmond reported in 1985 that the Province had franchised the system the previous year. In 1986 he described ResWest as the successful bidder and said the privately operated service was promoted in provincial tourism literature. Expo 86 named it the fair’s official accommodation agency.',
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
  { parent: 'bc-hydro', children: ['collected-power-smart', 'collected-sub-powerex'] },
  { parent: 'collected-bc-housing', children: ['collected-sub-bc-housing-licensing-and-consumer-services'] },
  { parent: 'bclc', children: ['collected-gamesense', 'collected-sub-playnow'] },
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
  { parent: 'collected-bc-pavilion-corporation', children: ['collected-sub-bc-place', 'collected-sub-vancouver-convention-centre'] }
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
