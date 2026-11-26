// How the printed pieces connect to the rest of the site, and why.
//
// One registry rather than links scattered through panels: each entry says which piece it starts
// from, where it leads, what kind of relationship that is, and how firmly it is known. A piece's
// overview lists its own entries (ui/Connections.jsx); the logo and patch views read the same
// entries backwards, so a mark or a patch can say which printed pieces it is tied to.
//
// Data only, and nothing here imports a drawing, so it can be read and tested without a browser.
//
// `to` is a place on the site (see site/navigation.jsx); `href` is a page elsewhere; `record` is
// one of this collection's own records (records.js), opened in place. `certainty` is one of
// CERTAINTY's keys: what the relationship rests on, not how interesting it is.

import { ASHTRAY_REGULATIONS, ASHTRAY_ROAD_MARKER } from './forest-service/ashtray.js'
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
  note: 'Departmental Logos · Forests: printed beside the service’s name. When the emblem was introduced or replaced is not confirmed.',
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
const BRANCH_NOTE = 'The Forest Practices Branch, a unit of the ministry, is the printed issuer; its record is below.'
const companion = (poster, note) => ({
  group: 'objects',
  rel: 'Companion piece',
  label: POSTERS[poster].title,
  note,
  to: piece(poster),
  certainty: 'printed'
})
const EXPO_MARKS = {
  group: 'marks',
  rel: 'Uses mark',
  label: 'Expo 86’s marks',
  note: 'Logos · Expo 86 Corporation: the stacked EXPO and three-ring 86 at the poster’s foot',
  to: { view: 'gallery', logos: 'collected-expo-86-corporation' },
  certainty: 'printed'
}
const expoPiece = (poster, note, certainty) => ({ ...companion(poster, note), rel: 'Also from Expo 86', certainty })
const CREDITS = {
  group: 'context',
  rel: 'Made by',
  label: 'Who made the weed posters',
  note: 'Record · the writers, art directors, designer, photographer, illustrator and lithographer, as the posters print them',
  record: 'noxious-weeds-credits',
  certainty: 'printed'
}
const BRANCH = {
  group: 'issuer',
  rel: 'Printed unit',
  label: 'Forest Practices Branch',
  note: 'Record · the unit named under the ministry in the signature. Not the Forest Practices Board.',
  record: 'forest-practices-branch',
  certainty: 'printed'
}

// ── The connections, by piece ───────────────────────────────────────────────────────────────────

const BY_POSTER = {
  'super-natural-spring': [
    {
      group: 'issuer', rel: 'Advertises', label: 'Province of British Columbia',
      note: 'Concordia University’s account identifies the advertisement with the Province’s Super, Natural tourism campaign.',
      href: 'https://www.concordia.ca/cunews/offices/advancement/2021/12/02/-concordia-very-formative--in-lives-of-ad-agency-founder-and-chi.html',
      certainty: 'documented'
    },
    {
      group: 'marks', rel: 'Campaign identity', label: 'Super, Natural British Columbia',
      note: 'Logos · the wider tourism identity collection. This 1984 signature is not identified as one of its later source-vector marks.',
      to: { view: 'gallery', logos: 'tourism-bc-destination-bc' },
      certainty: 'printed'
    },
    {
      group: 'objects', rel: 'Related tourism wording', label: 'Super, Natural British Columbia welcomes you',
      note: 'Signs · the tourism phrase on a provincial welcome sign, in a different arrangement.',
      to: { view: 'signs', sign: 'super-natural' },
      certainty: 'thematic'
    },
    {
      group: 'context', rel: 'Date and creative credits', label: 'McKim Advertising Vancouver, 1984',
      note: 'BCBusiness credits copywriter Alvin Wasserman and art director Bill Cozens and dates the whale advertisement to 1984.',
      href: 'https://bcbusiness.ca/lifestyle/tourism/the-bcbusiness-2018-tourism-status-report-branding/',
      certainty: 'documented'
    },
    {
      group: 'context', rel: 'Award and full credits', label: 'ADCC Gold, Consumer Magazine Ad, 1985',
      note: 'The award archive names client Tourism B.C., company McKim Advertising, writer and creative director Alvin Wasserman, designer and art director Bill Cozens, and original photographer Peter Thomas. The award year is distinct from the ad’s reported 1984 appearance.',
      href: 'https://theadcc.ca/archive/so-many-of-our-visitors_1985_gold_consumer-magazine-ad',
      certainty: 'documented'
    }
  ],
  'use-your-ashtray': [
    {
      group: 'issuer', rel: 'Printed publication', label: 'Fish and Game Branch',
      note: 'The branch names itself on the adjacent cover of the 1961–62 game regulations.',
      href: ASHTRAY_REGULATIONS.href, certainty: 'printed'
    },
    {
      group: 'context', rel: 'Roadside campaign', label: 'British Columbia Forest Service',
      note: 'The July 1962 newspaper account describes the same wording stencilled on the Victoria–Sidney Highway.',
      href: ASHTRAY_ROAD_MARKER.href, certainty: 'documented'
    },
    firePiece('dont-drop-it', 'A related Forest Service badge warns smokers about discarded cigarettes.')
  ],
  'new-carecard': [{
    group: 'issuer', rel: 'Issued by', label: 'Ministry of Health',
    note: 'The ministry signs the advertisement beneath the Gold CareCard.',
    to: body('ministry-of-health-1976', 1989), certainty: 'printed'
  }],
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
    firePiece('dont-gamble-with-fire', 'Posters · the other fire-prevention badge, in the same green. No record says whether the two were issued as a pair.'),
    firePiece('reward-living-forest', 'Posters · the same care asked for as a bargain: observe the campfire regulations'),
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    DEPARTMENT
  ],
  'dont-gamble-with-fire': [
    { ...SERVICE_COLLECTION, label: 'B. C. Forest Service' },
    firePiece('dont-drop-it', 'Posters · the other fire-prevention badge, in the same green'),
    firePiece('reward-living-forest', 'Posters · the same care asked for as a bargain: observe the campfire regulations'),
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    DEPARTMENT
  ],
  'be-careful': [
    { ...SERVICE_COLLECTION, label: 'BC Forest Service' },
    firePiece('dont-drop-it', 'Posters · the fire-prevention badge with a cigarette. No record ties the two together.'),
    firePiece('dont-gamble-with-fire', 'Posters · the fire-prevention badge with the dice'),
    {
      group: 'objects',
      rel: 'Related fire-prevention material',
      label: 'LOOKOUT',
      note: 'Signs · the Forest Service’s fire-protection sign',
      to: { view: 'signs', sign: 'lookout' },
      certainty: 'thematic'
    },
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    {
      group: 'context',
      rel: 'Historical context',
      label: 'Department of Lands and Forests',
      note: 'Government · 1960: where the Forest Service sat from 1945 to 1962',
      to: body('department-of-lands-and-forests-1945', 1960),
      certainty: 'documented'
    },
    {
      group: 'context',
      rel: 'Date evidence',
      label: 'Protection Bulletin No. 3, 1960',
      note: 'The service’s bulletin pictures the same design on p. 5, as new decals for vehicle windows and hard hats',
      href: 'https://a100.gov.bc.ca/pub/eirs/finishDownloadDocument.do?subdocumentId=21448',
      certainty: 'documented'
    }
  ],
  'coons-age': [
    SERVICE_COLLECTION,
    EVERGREEN,
    { ...companion('reward-living-forest', 'Posters · the campfire poster, with the same emblem in colour'), rel: 'Same mark appears on', to: piece('reward-living-forest', 'emblem') },
    { ...companion('enjoy-protect-forests', 'Posters · the sign, with the same emblem'), rel: 'Same mark appears on', to: piece('enjoy-protect-forests', 'emblem') },
    {
      group: 'objects',
      rel: 'Compare',
      label: POSTERS['coastal-forest'].title,
      note: 'Posters · the managed forest argued again, by the Ministry of Environment',
      to: piece('coastal-forest'),
      certainty: 'thematic'
    },
    {
      group: 'context',
      rel: 'Historical context',
      label: 'Department of Lands, Forests and Water Resources',
      note: 'Government · 1971: where the Forest Service sat when the advertisement ran',
      to: body('department-of-lands-forests-and-water-resources-1962', 1971),
      certainty: 'documented'
    },
    {
      group: 'context',
      rel: 'Date evidence',
      label: 'Gulf Islands Driftwood, 2 December 1971',
      note: 'Printed on p. 11 of that issue. Whether it ran elsewhere, or earlier, is not known.',
      href: 'https://saltspringarchives.com/driftwood/1971/v12n47Dec2-1971.pdf#page=11',
      certainty: 'documented'
    }
  ],
  'prevent-forest-fires': [
    SERVICE_COLLECTION,
    { ...companion('reward-living-forest', 'Posters · the campfire poster, signed in full the same way'), certainty: 'thematic' },
    { ...companion('enjoy-protect-forests', 'Posters · the sign, signed in full the same way'), certainty: 'thematic' },
    {
      group: 'objects',
      rel: 'Related fire-prevention material',
      label: 'B. C. Forest Service badges and decals',
      note: 'Posters · DON’T DROP IT!, Don’t gamble with FIRE and Be Careful, the fire-prevention series',
      to: piece('dont-drop-it'),
      certainty: 'thematic'
    },
    firePiece('be-careful', 'Posters · the 1960 decal, PREVENT FOREST FIRES across its base. No record ties the two together.'),
    firePiece('matches-not-for-children', 'Posters · the service’s matches poster, F. P. 19, from about 1966–67'),
    {
      group: 'objects',
      rel: 'Compare',
      label: POSTERS['coons-age'].title,
      note: 'Posters · the forest as lasting wealth again, argued in a 1971 newspaper advertisement',
      to: piece('coons-age'),
      certainty: 'thematic'
    },
    {
      group: 'objects',
      rel: 'Related fire-prevention material',
      label: 'England Expects: Prevent Forest Fires',
      note: 'Cards · the same plea as a call to duty, under the Lands Department seal',
      to: { view: 'cards', card: 'england-expects' },
      certainty: 'thematic'
    },
    {
      group: 'objects',
      rel: 'Related fire-prevention material',
      label: 'Prevent Forest Fires: Put Your Campfires Out',
      note: 'Pins · the Forest Branch’s yellow campfire oval, with the same three words over the top',
      to: { view: 'pins', pin: 'forest-branch-campfires' },
      certainty: 'thematic'
    },
    {
      group: 'objects',
      rel: 'Related fire-prevention material',
      label: 'LOOKOUT',
      note: 'Signs · the Forest Service’s fire-protection sign',
      to: { view: 'signs', sign: 'lookout' },
      certainty: 'thematic'
    },
    {
      group: 'objects',
      rel: 'Related fire-prevention material',
      label: 'FOREST CLOSURE, Zone 3',
      note: 'Signs · the Forest Service’s closure sign, its strip reading OPEN or CLOSED',
      to: { view: 'signs', sign: 'forest-closure' },
      certainty: 'thematic'
    }
  ],
  'matches-not-for-children': [
    SERVICE_COLLECTION,
    {
      group: 'marks',
      rel: 'Uses mark',
      label: 'The one-ink oval seal',
      note: 'Departmental Logos · Forests: printed bottom right, beside the headline. When the seal was introduced or replaced is not known.',
      to: logo('forest-service-one-ink-oval'),
      certainty: 'printed'
    },
    firePiece('prevent-forest-fires', 'Posters · another Forest Service poster, its case made as a loss of timber and wages'),
    firePiece('be-careful', 'Posters · the 1960 decal. No record ties the two together.'),
    firePiece('dont-drop-it', 'Posters · one cause of fire, a dropped cigarette, as a badge'),
    FIRE_CONTROL_PATCH,
    PREVENTION_BADGE,
    {
      group: 'context',
      rel: 'Historical context',
      label: 'Department of Lands, Forests and Water Resources',
      note: 'Government · 1967: where the Forest Service sat in the centennial years the captions name',
      to: body('department-of-lands-forests-and-water-resources-1962', 1967),
      certainty: 'inferred'
    }
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
    BRANCH,
    {
      group: 'context',
      rel: 'Made by',
      label: 'd.g., from the artist’s mark',
      note: 'Record · the one signature on the sheet, “d.g.01”',
      record: 'wildlife-trees-artist',
      certainty: 'inferred'
    },
    {
      group: 'marks',
      rel: 'Uses mark',
      label: 'The Forest Service tree oval',
      note: 'Departmental Logos · Forests: printed beside the ministry’s arms signature',
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
    companion('explosion-in-slow-motion', 'Posters · the specimen poster: ten weeds, under the same wordmark'),
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
    BRANCH,
    companion('beware-these-alien-invaders', 'Posters · the screen leaflet, four weeds under the same wordmark'),
    companion('explosion-in-slow-motion', 'Posters · the specimen poster, credited to the same writers, art directors and photographer'),
    {
      group: 'objects',
      rel: 'Same signature appears on',
      label: POSTERS['wildlife-trees'].title,
      note: 'Posters · the branch’s habitat-tree poster, signed the same way in green',
      to: piece('wildlife-trees', 'ministry'),
      certainty: 'printed'
    },
    CREDITS,
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
    BRANCH,
    companion('beware-these-alien-invaders', 'Posters · the screen leaflet, four weeds under the same wordmark'),
    companion('shattering-the-environment', 'Posters · the landscape poster, credited to the same writers, art directors and photographer'),
    CREDITS,
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
    {
      group: 'objects',
      rel: 'Depicts',
      label: 'Queen of Sidney, the ship',
      note: 'Record · built as Sidney, in service from 1960, given this name in 1963',
      record: 'queen-of-sidney-vessel',
      certainty: 'documented'
    },
    { ...companion('go-bc-ferries', 'Posters · the Toll Authority’s sticker for the whole system'), rel: 'Also a decal', certainty: 'thematic' }
  ],
  // Unlisted on the shelf (catalogue.js): the Expo 86 pieces point only to one another.
  'expo-86-davidson': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Expo 86 Corporation',
      note: 'Government · 1986: “© The Expo 86 Corporation” in the credit line, the Crown corporation that ran the fair',
      to: body('expo-86-corporation', 1986),
      certainty: 'printed'
    },
    EXPO_MARKS,
    expoPiece('expo-86-fiorucci', 'Posters · another of the fair’s art posters, with the same mark and event text', 'printed'),
    expoPiece('our-british-columbia', 'Posters · the British Columbia Pavilion’s poster for its film', 'thematic')
  ],
  'expo-86-fiorucci': [
    {
      group: 'issuer',
      rel: 'Issued by',
      label: 'Expo 86 Corporation',
      note: 'Government · 1986: the publisher a dealer’s listing gives for a matching copy; the sheet carries no credit line',
      to: body('expo-86-corporation', 1986),
      certainty: 'documented'
    },
    EXPO_MARKS,
    expoPiece('expo-86-davidson', 'Posters · another of the fair’s art posters, with the same mark and event text', 'printed'),
    expoPiece('our-british-columbia', 'Posters · the British Columbia Pavilion’s poster for its film', 'thematic')
  ],
  'our-british-columbia': [
    {
      group: 'issuer',
      rel: 'Presented by',
      label: 'B.C. Pavilion Corporation',
      note: 'Government · 1986: the credit line names THE BRITISH COLUMBIA PAVILION, not a body; this is the Crown corporation incorporated in 1984 under its name. The copyright is International Media Distribution’s.',
      to: body('bc-pavilion-corporation', 1986),
      certainty: 'inferred'
    },
    {
      group: 'context',
      rel: 'Historical context',
      label: 'Expo 86 Corporation',
      note: 'Government · 1986: the Crown corporation that ran the fair the pavilion’s badge names',
      to: body('expo-86-corporation', 1986),
      certainty: 'printed'
    },
    expoPiece('expo-86-davidson', 'Posters · one of the fair’s art posters', 'thematic'),
    expoPiece('expo-86-fiorucci', 'Posters · another of the fair’s art posters', 'thematic')
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

/** The made objects (patches, badges) that carry one of the Departmental Logos. */
export const objectsForLogo = (logoId) => MARK_OBJECTS.filter((object) => object.logo === logoId)

/** The printed pieces that use one of the Departmental Logos. */
export const postersForLogo = (logoId) => connectedPosters().filter((posterId) => (BY_POSTER[posterId] ?? [])
  .some((entry) => entry.group === 'marks' && sameLogo(entry.to, logoId)))
