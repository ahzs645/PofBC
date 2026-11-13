// How the printed pieces connect to the rest of the site, and why.
//
// One registry rather than links scattered through panels: each entry says which piece it starts
// from, where it leads, what kind of relationship that is, and how firmly it is known. A piece's
// overview lists its own entries (ui/Connections.jsx); the logo and patch views read the same
// entries backwards, so a mark or a patch can say which printed pieces it is tied to.
//
// Data only, and nothing here imports a drawing, so it can be read and tested without a browser.
//
// `to` is a place on the site (see site/navigation.jsx); `href` is a page elsewhere. `certainty`
// is one of CERTAINTY's keys: what the relationship rests on, not how interesting it is.

import { POSTERS } from './catalogue.js'

/** The overview's sections, in the order shown. */
export const GROUPS = [
  { id: 'issuer', title: 'Issuer' },
  { id: 'marks', title: 'Marks used' },
  { id: 'objects', title: 'Related objects' },
  { id: 'context', title: 'Historical context' }
]

/** What a connection rests on. */
export const CERTAINTY = {
  printed: 'As printed',
  documented: 'Documented',
  inferred: 'Inferred',
  thematic: 'Thematic'
}

const logo = (id) => ({ view: 'internal', internal: 'forests', 'internal-logo': id })
const body = (node, year) => ({ view: 'government', year, node })
const piece = (poster, part) => ({ view: 'posters', poster, ...(part ? { part } : {}) })

/**
 * A mark that is also a made object in the Patches or Badges view. Stored once: every piece that
 * uses the mark is connected to the object, and the object back to every piece.
 */
export const MARK_OBJECTS = [
  {
    logo: 'forest-service-emblem',
    to: { view: 'patches', patch: 'S48-O01' },
    label: 'The same emblem on a cloth patch',
    note: 'Patches · S48-O01, the evergreen emblem as a cloth square. Whether the patch and the printed pieces were issued together is not known.',
    certainty: 'documented'
  },
  {
    logo: 'forest-service',
    to: { view: 'patches', patch: 'FO-forest-service' },
    label: 'The tree oval in the patch collection',
    note: 'Patches · FO-forest-service. That record is a digital emblem drawn from the same artwork, not a photographed cloth patch.',
    certainty: 'documented'
  }
]

// ── Shared targets ──────────────────────────────────────────────────────────────────────────────

const SERVICE_COLLECTION = {
  group: 'issuer',
  rel: 'Issued by',
  label: 'British Columbia Forest Service',
  note: 'Patches · the service’s cloth patches and emblems. The credit on the piece names the service, not a department.',
  to: { view: 'patches', org: 'bc-forest-service' },
  certainty: 'printed'
}
const EVERGREEN = {
  group: 'marks',
  rel: 'Uses mark',
  label: 'The evergreen emblem',
  note: 'Internal Logos · Forests: printed beside the service’s name. When the emblem was introduced or replaced is not confirmed.',
  to: logo('forest-service-emblem'),
  certainty: 'printed'
}
const DEPARTMENT = {
  group: 'context',
  rel: 'Historical context',
  label: 'Department of Lands, Forests and Water Resources',
  note: 'Government · 1970: where the Forest Service sat from 1962 to 1975. The piece is undated, so this is one possible setting, not its date.',
  to: body('department-of-lands-forests-and-water-resources-1962', 1970),
  certainty: 'inferred'
}
const FIRE_CONTROL_PATCH = {
  group: 'objects',
  rel: 'Related service function',
  label: 'Forest Service Fire Control patch',
  note: 'Patches · FO-fire-control: what the people who fought the fires wore. No record ties it to this design or to one campaign.',
  to: { view: 'patches', patch: 'FO-fire-control' },
  certainty: 'thematic'
}
const PREVENTION_BADGE = {
  group: 'objects',
  rel: 'Related service function',
  label: 'Forest Fire Prevention Officer badge',
  note: 'Badges · S51-O01, a metal shield. The same work, worn; not evidence of a shared designer or date.',
  to: { view: 'badges', patch: 'S51-O01' },
  certainty: 'thematic'
}
const firePiece = (poster, note) => ({
  group: 'objects',
  rel: 'Related fire-prevention material',
  label: POSTERS[poster].title,
  note,
  to: piece(poster),
  certainty: 'thematic'
})
const MINISTRY_OF_FORESTS = (year, note) => ({
  group: 'context',
  rel: 'Historical context',
  label: `Ministry of Forests, in ${year}`,
  note,
  to: body('ministry-of-forests-1988', year),
  certainty: 'documented'
})
const BRANCH_NOTE = 'The Forest Practices Branch, a unit of the ministry, is the printed issuer. It is not the Forest Practices Board, a separate body; the site has no record for the Branch yet.'
const companion = (poster, note) => ({
  group: 'objects',
  rel: 'Companion piece',
  label: POSTERS[poster].title,
  note,
  to: piece(poster),
  certainty: 'printed'
})
const credits = (note) => ({
  group: 'context',
  rel: 'Made by',
  label: 'Credits, as printed',
  note,
  certainty: 'printed'
})

// ── The connections, by piece ───────────────────────────────────────────────────────────────────

const BY_POSTER = {
  'coastal-forest': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Ministry of Environment',
      note: 'Government · 1980: the wording on the poster. The ministry held exactly this name twice, in 1979–86 and again in 1988–91.',
      to: body('ministry-of-environment-1979', 1980),
      certainty: 'printed'
    },
    {
      group: 'marks',
      rel: 'Uses mark',
      label: 'The crest lockup',
      note: 'This poster · the Province’s arms in a rounded square beside its name, with a studio to redraw it',
      to: piece('coastal-forest', 'logo'),
      certainty: 'printed'
    },
    {
      group: 'context',
      rel: 'Historical context',
      label: 'Ministry of Environment, in 1989',
      note: 'Government · 1989: the second span of years the same wording fits',
      to: body('ministry-of-environment-1988', 1989),
      certainty: 'documented'
    },
    {
      group: 'objects',
      rel: 'Compare',
      label: POSTERS['wildlife-trees'].title,
      note: 'Posters · the forest as habitat again, as a practical lesson about which trees to leave',
      to: piece('wildlife-trees'),
      certainty: 'thematic'
    },
    {
      group: 'objects',
      rel: 'Compare',
      label: POSTERS['go-bc-ferries'].title,
      note: 'Posters · the same coast sold as a destination rather than explained as a habitat',
      to: piece('go-bc-ferries'),
      certainty: 'thematic'
    }
  ],
  'reward-living-forest': [
    SERVICE_COLLECTION,
    EVERGREEN,
    { ...companion('enjoy-protect-forests', 'Posters · the sign that carries the same emblem'), rel: 'Same mark appears on', to: piece('enjoy-protect-forests', 'emblem') },
    firePiece('dont-drop-it', 'Posters · one cause of fire, a dropped cigarette, as a badge'),
    firePiece('dont-gamble-with-fire', 'Posters · the same warning as a joke about dice'),
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    DEPARTMENT
  ],
  'enjoy-protect-forests': [
    SERVICE_COLLECTION,
    EVERGREEN,
    { ...companion('reward-living-forest', 'Posters · the campfire poster that carries the same emblem'), rel: 'Same mark appears on', to: piece('reward-living-forest', 'emblem') },
    DEPARTMENT
  ],
  'dont-drop-it': [
    { ...SERVICE_COLLECTION, label: 'B. C. Forest Service' },
    firePiece('dont-gamble-with-fire', 'Posters · the other fire-prevention badge. The two were photographed in different colours; nothing establishes that they were issued as a pair.'),
    firePiece('reward-living-forest', 'Posters · the same care asked for as a bargain: observe the campfire regulations'),
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    DEPARTMENT
  ],
  'dont-gamble-with-fire': [
    { ...SERVICE_COLLECTION, label: 'B. C. Forest Service' },
    firePiece('dont-drop-it', 'Posters · the other fire-prevention badge, printed green where this one is blue'),
    firePiece('reward-living-forest', 'Posters · the same care asked for as a bargain: observe the campfire regulations'),
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    DEPARTMENT
  ],
  'wildlife-trees': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Ministry of Forests, Forest Practices Branch',
      note: `Government · 2001: the ministry in the signature. ${BRANCH_NOTE}`,
      to: body('ministry-of-forests-1988', 2001),
      certainty: 'printed'
    },
    {
      group: 'marks',
      rel: 'Uses mark',
      label: 'The Forest Service tree oval',
      note: 'Internal Logos · Forests: printed beside the ministry’s arms signature',
      to: logo('forest-service'),
      certainty: 'printed'
    },
    {
      group: 'objects',
      rel: 'Same signature appears on',
      label: POSTERS['shattering-the-environment'].title,
      note: 'Posters · the branch’s weed poster, signed the same way in black',
      to: piece('shattering-the-environment', 'signature'),
      certainty: 'printed'
    },
    {
      group: 'objects',
      rel: 'Official copy',
      label: 'Stand-level Biodiversity Brochure, Side 2',
      note: 'gov.bc.ca · the Province still hosts a scan of this sheet under that name (a PDF made in 2012): the same tree, six portraits, copy and signatures. Not yet compared with the reconstruction line by line.',
      href: 'https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/conservation-habitat-management/wildlife-conservation/wildlife-tree-committee/stand_level_biodiversity_brochure_side_2.pdf',
      certainty: 'documented'
    },
    {
      group: 'objects',
      rel: 'Companion piece',
      label: 'Stand-level Biodiversity Brochure, Side 1',
      note: 'gov.bc.ca · the other side of the same publication, listed beside it by the Wildlife Tree Committee. Not in this collection.',
      href: 'https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/conservation-habitat-management/wildlife-conservation/wildlife-tree-committee/stand_level_biodiversity_brochure_side_1.pdf',
      certainty: 'documented'
    },
    {
      group: 'context',
      rel: 'Policy context',
      label: 'Wildlife tree policy, 1985 to 2002',
      note: 'gov.bc.ca · the Province’s 2006 guidance records a first wildlife-tree policy in 1985, an update in February 2000 and an evaluation released in 2002. Context only: nothing here shows that a policy commissioned the poster.',
      href: 'https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/conservation-habitat-management/wildlife-conservation/wildlife-tree-committee/wt-guidance-05-2006.pdf',
      certainty: 'documented'
    }
  ],
  'beware-these-alien-invaders': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Ministry of Forests',
      note: 'Government · 1999: named on the cover; the file gives its author as MOF',
      to: body('ministry-of-forests-1988', 1999),
      certainty: 'printed'
    },
    companion('shattering-the-environment', 'Posters · the landscape poster, under the same Noxious Weeds wordmark'),
    companion('explosion-in-slow-motion', 'Posters · the specimen poster, with the same four weeds among its ten'),
    {
      group: 'context',
      rel: 'Date evidence',
      label: 'A PDF made on 25 March 1999',
      note: 'The date the supplied file was created. It does not establish when the leaflet was first published.',
      certainty: 'documented'
    }
  ],
  'shattering-the-environment': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Ministry of Forests, Forest Practices Branch',
      note: `Government · 2000: the ministry in the signature. ${BRANCH_NOTE}`,
      to: body('ministry-of-forests-1988', 2000),
      certainty: 'printed'
    },
    companion('beware-these-alien-invaders', 'Posters · the screen leaflet, with the same four weeds'),
    companion('explosion-in-slow-motion', 'Posters · the specimen poster, credited to the same writers, art directors and photographer'),
    {
      group: 'objects',
      rel: 'Same signature appears on',
      label: POSTERS['wildlife-trees'].title,
      note: 'Posters · the branch’s habitat-tree poster, signed the same way in green',
      to: piece('wildlife-trees', 'ministry'),
      certainty: 'printed'
    },
    credits('Copy, Susan Turner and Dwaine Brooke. Art direction, Paul Nystedt and Denton Pendergast. Design, Rocket Science Design. Weed photography, Dion Manastyrski. Background photograph, Gunter Marx Photography. Compositing and film, Watermark Lithography. Names as the poster prints them; none has been identified independently.'),
    {
      group: 'context',
      rel: 'Date evidence',
      label: 'A PDF made on 31 March 2000',
      note: 'The date the supplied file was created. It does not establish when the poster was printed or first shown.',
      certainty: 'documented'
    }
  ],
  'explosion-in-slow-motion': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Ministry of Forests, Forest Practices Branch',
      note: `Government · 2000: the ministry in the signature. ${BRANCH_NOTE}`,
      to: body('ministry-of-forests-1988', 2000),
      certainty: 'printed'
    },
    companion('beware-these-alien-invaders', 'Posters · the screen leaflet, whose four weeds are all here'),
    companion('shattering-the-environment', 'Posters · the landscape poster, credited to the same writers, art directors and photographer'),
    credits('Copy, Susan Turner and Dwaine Brooke. Art direction, Paul Nystedt and Denton Pendergast. Design, Denton Pendergast. Photography, Dion Manastyrski. Illustration, Soren Henrich. Photo-compositing, Watermark Lithography. Names as the poster prints them; none has been identified independently.'),
    {
      group: 'context',
      rel: 'Date evidence',
      label: 'A PDF made on 31 March 2000',
      note: 'The date the supplied file was created. It does not establish when the poster was printed or first shown.',
      certainty: 'documented'
    }
  ],
  'go-bc-ferries': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'British Columbia Toll Authority Ferry Systems',
      note: 'Government · 1962: the subtitle names the Toll Highways and Bridges Authority’s ferry system, which ran the ferries until 1964',
      to: body('bc-toll-highways-and-bridges-authority', 1962),
      certainty: 'printed'
    },
    {
      group: 'marks',
      rel: 'Uses mark',
      label: 'BC Ferries’ marks',
      note: 'Logos · BC Ferries: the Toll Authority wordmark and the dogwood flag on the decal',
      to: { view: 'gallery', logos: 'bc-ferries' },
      certainty: 'printed'
    },
    { ...companion('queen-of-sidney', 'Posters · one ship’s own sticker, from the same fleet'), rel: 'Also a decal', certainty: 'thematic' },
    {
      group: 'objects',
      rel: 'Compare',
      label: POSTERS['coastal-forest'].title,
      note: 'Posters · the same coast explained as a habitat rather than sold as a destination',
      to: piece('coastal-forest'),
      certainty: 'thematic'
    }
  ],
  'queen-of-sidney': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'British Columbia Ferries',
      note: 'Government · 1970: the name in the lettering. The ferries had an authority of their own from 1 April 1964, but the wording alone does not say which body printed the sticker, or when.',
      to: body('bc-ferry-authority', 1970),
      certainty: 'inferred'
    },
    {
      group: 'marks',
      rel: 'Uses mark',
      label: 'BC Ferries’ marks',
      note: 'Logos · BC Ferries: the dogwood house flag above the ship',
      to: { view: 'gallery', logos: 'bc-ferries' },
      certainty: 'printed'
    },
    { ...companion('go-bc-ferries', 'Posters · the Toll Authority’s sticker for the whole system'), rel: 'Also a decal', certainty: 'thematic' }
  ]
}

const sameLogo = (to, id) => to?.view === 'internal' && to['internal-logo'] === id

/** A piece's connections, the made objects of its marks among them, in group order. */
export const connectionsOf = (posterId) => {
  const own = BY_POSTER[posterId] ?? []
  const derived = own
    .filter((entry) => entry.group === 'marks')
    .flatMap((entry) => MARK_OBJECTS.filter((object) => sameLogo(entry.to, object.logo)))
    .map(({ logo: _logo, ...object }) => ({ group: 'objects', rel: 'Same mark appears on', ...object }))
  const all = [...own, ...derived]
  return GROUPS.flatMap(({ id }) => all.filter((entry) => entry.group === id))
}

/** A piece's connections as the overview shows them: [{ id, title, entries }], empty groups left out. */
export const groupedConnections = (posterId) => {
  const all = connectionsOf(posterId)
  return GROUPS.map((group) => ({ ...group, entries: all.filter((entry) => entry.group === group.id) })).filter(({ entries }) => entries.length)
}

/** Every piece with connections. */
export const connectedPosters = () => Object.keys(BY_POSTER)

const backLink = (posterId, entry) => ({
  poster: posterId,
  title: POSTERS[posterId].title,
  rel: entry.rel,
  certainty: entry.certainty,
  to: piece(posterId)
})

/** The printed pieces connected to a patch or badge, read backwards from the registry. */
export const postersForPatch = (patchId) => connectedPosters().flatMap((posterId) => connectionsOf(posterId)
  .filter((entry) => entry.to?.patch === patchId)
  .map((entry) => backLink(posterId, entry)))

/** The made objects (patches, badges) that carry one of the Internal Logos. */
export const objectsForLogo = (logoId) => MARK_OBJECTS.filter((object) => object.logo === logoId)

/** The printed pieces that use one of the Internal Logos. */
export const postersForLogo = (logoId) => connectedPosters().filter((posterId) => (BY_POSTER[posterId] ?? [])
  .some((entry) => entry.group === 'marks' && sameLogo(entry.to, logoId)))
