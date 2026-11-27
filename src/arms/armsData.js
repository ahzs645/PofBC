// Coats of arms: the Province's, and those of the public bodies around it.
//
// The Province's entry is built from the arms-variants catalogue
// (research/identity/arms-variants-2026-11-14/catalogue.json): its design stages, then every dated
// specimen in catalogue order with its credit and sources. The other holders are plain records in
// holders.js, each with its register entry and the artwork acquired for it. Nothing here imports an
// image, so it can be tested without a browser; ArmsView.jsx resolves the image files.

import catalogue from '../../research/identity/arms-variants-2026-11-14/catalogue.json' with { type: 'json' }
import { ACQUISITION_DIR, ADDITIONAL_HOLDERS, HOLDERS as REGISTER_HOLDERS, MUNICIPAL_HOLDERS, PROVINCE_REGISTER, artworkOf } from './holders.js'

export const CATALOGUE_DIR = 'research/identity/arms-variants-2026-11-14'
export { ACQUISITION_DIR }

export const GROUPS = [
  { id: 'province', title: 'The Province', description: 'The arms of British Columbia, from the 1895 design to the 1987 grant.' },
  { id: 'crown', title: 'The Crown', description: 'The Lieutenant Governor’s flag of office. The Legislative Assembly, the Great Seal and the courts have no entry in the register.' },
  { id: 'post-secondary', title: 'Universities and colleges', description: 'Public post-secondary institutions with arms: those in the register, and Douglas College, whose arms the College documents itself.' },
  { id: 'public-body', title: 'Public bodies', description: 'Police, agencies, Crown corporations and other public bodies with registered arms.' },
  { id: 'municipal', title: 'Municipalities', description: 'Local governments whose arms, flags or badges are in the public register.' }
]

const sourcesById = new Map(catalogue.sources.map((source) => [source.id, source]))

/** The catalogue's sections ("02 · The 1895 arms") without their numbers, in catalogue order. */
const sectionTitle = (section) => section.replace(/^\d+\s*·\s*/, '')

const specimen = (entry) => ({
  id: entry.id,
  number: entry.catalogueNumber,
  title: entry.title,
  section: sectionTitle(entry.section),
  date: entry.dateLabel,
  classification: entry.classification,
  description: entry.description,
  dating: entry.datingNote ?? null,
  credit: entry.credit ?? null,
  image: entry.imagePath.replace(/^reference\//, ''),
  sources: (entry.sources ?? []).map((id) => sourcesById.get(id)).filter(Boolean)
})

export const PROVINCE_SPECIMENS = [...catalogue.entries]
  .sort((a, b) => a.catalogueNumber - b.catalogueNumber)
  .map(specimen)

/** The specimens grouped under their catalogue sections, in order. */
export const provinceSections = () => {
  const sections = []
  for (const item of PROVINCE_SPECIMENS) {
    const last = sections.at(-1)
    if (last?.title === item.section) last.specimens.push(item)
    else sections.push({ title: item.section, specimens: [item] })
  }
  return sections
}

const source = (id) => sourcesById.get(id)

export const PROVINCE = {
  id: 'british-columbia',
  name: 'Province of British Columbia',
  group: 'province',
  year: '1906',
  registered: ['Arms', 'Flag'],
  granted: 'Shield and motto 31 March 1906; crest, supporters and compartment 15 October 1987 (College of Arms, London)',
  registeredInCanada: PROVINCE_REGISTER?.granted ?? null,
  register: PROVINCE_REGISTER?.register ?? null,
  blazon: PROVINCE_REGISTER?.blazon ?? null,
  symbolism: PROVINCE_REGISTER?.symbolism ?? null,
  motto: { text: 'Splendor sine occasu', translation: 'Splendour without diminishment' },
  description: 'The Union Flag with an antique crown at its centre, over the sun setting into the sea between wavy bars of blue and silver. The 1987 augmentation added the crowned lion crest with its dogwood collar, the wapiti and bighorn ram supporters, and a compartment of Pacific dogwood.',
  image: { kind: 'vector' },
  artwork: artworkOf('british-columbia'),
  stages: [
    {
      year: '1895',
      title: 'The Beanlands arms',
      text: 'Sun and waves above the Union Flag, with the royal crest, a stag and a ram, and the motto. Adopted by the Province on 19 July 1895.',
      sources: [source('S01')].filter(Boolean)
    },
    {
      year: '1906',
      title: 'The granted shield and motto',
      text: 'The Union Flag moved to the top with an antique crown at its centre, the waves and setting sun below. Granted on 31 March 1906; the earlier crest and supporters stayed in use without being part of the grant.',
      sources: [source('S02'), source('S16')].filter(Boolean)
    },
    {
      year: '1987',
      title: 'The complete achievement',
      text: 'Crest and supporters made formal, with the helmet and mantling, the dogwood collar and the floral compartment. Granted on 15 October 1987 and unchanged since.',
      sources: [source('S21'), source('S02')].filter(Boolean)
    }
  ],
  links: [
    { label: 'The coat of arms lockup, in the generator (choose Arms)', to: { view: 'generator' } },
    { label: 'The 1919 cardboard licence plate, which carries the arms', to: { view: 'plates', plate: '1919-cardboard' } }
  ],
  sources: [source('S01'), source('S02')].filter(Boolean),
  catalogue: {
    readme: `${CATALOGUE_DIR}/README.md`,
    pdf: `${CATALOGUE_DIR}/catalogue.pdf`
  }
}

// The Province's page is one account of the arms, oldest first. Each design, object or treatment is
// one entry: a catalogue specimen or an acquired rendering, with every other copy of the same
// drawing or object gathered into it. A copy names the entry it belongs to in its own record
// (`sameAs`: a catalogue entry's, or an acquisition record's, both pointing at a catalogue id), so
// the merges live in the research data and survive a rebuild; this list only orders the entries
// and says which section each belongs to. Anything listed here or gathered by `sameAs` is shown
// once, and the tests check that nothing is left out.

const entriesById = new Map(PROVINCE_SPECIMENS.map((item) => [item.id, item]))
const rawEntriesById = new Map(catalogue.entries.map((entry) => [entry.id, entry]))
const provinceArtworkById = new Map(PROVINCE.artwork.map((item) => [item.id, item]))

const catalogueFile = (item) => {
  const raw = rawEntriesById.get(item.id)
  return {
    id: item.id,
    from: 'catalogue',
    number: item.number,
    title: item.title,
    date: item.date,
    credit: item.credit,
    image: item.image,
    vector: /\.svg$/i.test(item.image),
    format: item.image.split('.').at(-1).toUpperCase(),
    sources: item.sources,
    sameAs: raw?.sameAs ?? null
  }
}

const artworkFile = (item) => ({
  id: item.id,
  from: 'artwork',
  title: item.title,
  date: item.date,
  credit: [item.author, item.licence].filter(Boolean).join(' · '),
  author: item.author,
  licence: item.licence,
  licenceUrl: item.licenceUrl ?? null,
  page: item.page,
  original: item.original,
  alternates: item.alternates ?? [],
  format: item.format,
  vector: Boolean(item.vector),
  item,
  sameAs: item.sameAs ?? null
})

/** Every copy that names `id` as the entry it belongs to, catalogue specimens first. */
const copiesOf = (id) => [
  ...PROVINCE_SPECIMENS.filter((item) => rawEntriesById.get(item.id)?.sameAs === id).map(catalogueFile),
  ...PROVINCE.artwork.filter((item) => item.sameAs === id).map(artworkFile)
]

/**
 * One entry of the account. Its words (title, dates, description) are the catalogue's where the
 * catalogue holds it; its picture is the best file: a source vector first (AGENTS.md), then the
 * one `lead` names, else the catalogue's own. The rest are listed as further copies.
 */
const storyEntry = ({ id, lead }) => {
  const specimen = entriesById.get(id)
  const artwork = provinceArtworkById.get(id)
  if (!specimen && !artwork) throw new Error(`Unknown arms entry ${id}`)
  const own = specimen ? catalogueFile(specimen) : artworkFile(artwork)
  const files = [own, ...copiesOf(id)]
  const chosen = files.find((file) => file.vector) ?? files.find((file) => file.id === lead) ?? own
  const ordered = [chosen, ...files.filter((file) => file !== chosen)]
  const sources = []
  for (const source of ordered.flatMap((file) => file.sources ?? [])) {
    if (!sources.some(({ url }) => url === source.url)) sources.push(source)
  }
  return {
    id,
    number: specimen?.number ?? null,
    title: specimen?.title ?? artwork.title,
    date: specimen?.date ?? artwork.date,
    classification: specimen?.classification ?? null,
    kind: artwork?.kind ?? null,
    historical: artwork?.historical ?? null,
    description: specimen?.description ?? null,
    dating: specimen?.dating ?? null,
    credit: specimen?.credit ?? null,
    // A reconstruction names the specimen it was redrawn from; it is not a copy of it.
    follows: entriesById.get(rawEntriesById.get(id)?.follows)?.number ?? null,
    sources,
    lead: ordered[0],
    files: ordered
  }
}

const stage = (year) => PROVINCE.stages.find((item) => item.year === year)

const STORY = [
  {
    id: 'precursors',
    title: 'Precursors and proposals',
    period: '1850–1882',
    from: 1850,
    text: 'Before the Province had arms of its own: the colonial seal of Vancouver Island, the lion-and-crown badge approved for the colony’s flag in 1870, and the trial shields the Marquess of Lorne drew about 1882. None of them was adopted as the provincial arms.',
    sources: ['S03', 'S06', 'S08'],
    groups: [{ entries: [{ id: 'vancouver-island-seal' }, { id: 'royal-crest-bc-badge' }, { id: 'lorne-proposals' }, { id: 'crest-wreath-motto' }] }]
  },
  {
    id: 'beanlands',
    title: 'The 1895 Beanlands arms',
    period: '1895–1906',
    from: 1895,
    stage: '1895',
    groups: [{
      entries: [
        { id: 'beanlands-web-drawing' },
        { id: 'beanlands-seal' },
        // The higher-resolution photograph shows the whole window, motto included.
        { id: 'diamond-jubilee-window', lead: 'province-older-arms-window-makaristos' },
        { id: 'speakers-chair' },
        { id: 'foley-china' }
      ]
    }]
  },
  {
    id: 'grant-1906',
    title: 'The 1906 grant and the printed full achievement',
    period: '1906–1987',
    from: 1906,
    stage: '1906',
    text: 'Until 1987 the granted shield was printed with the older crest and supporters, which the grant did not include. The drawings varied; a printing dates when its drawing was in use, not when it was made.',
    groups: [
      {
        title: 'Dated printings and undated illustrations',
        entries: ['museum-report-1915', 'museum-report-1935', 'canada-year-book-1943-44', 'museum-report-1952', 'museum-report-1960', 'recreation-conservation-report-1970-cover', 'recreation-conservation-report-1970-title', 'old-full-arms-government', 'old-full-arms-colour'].map((id) => ({ id }))
      },
      {
        title: 'Document headings',
        entries: [{ id: 'supplied-split-serif' }, { id: 'supplied-government-caption' }, { id: 'supplied-blackletter' }]
      }
    ]
  },
  {
    id: 'augmentation-1987',
    title: 'The 1987 augmentation and the 1990 registration',
    period: '1987–1990',
    from: 1987,
    stage: '1987',
    text: 'The Canadian Heraldic Authority registered the arms and the flag on 17 April 1990. The registration recorded the existing arms; it was not another redesign.',
    sources: ['S02'],
    groups: [{
      entries: [{ id: 'full-1987-sculpture' }, { id: 'full-1987-period-report' }, { id: 'full-1990-cha-registration' }, { id: 'cha-1406-flag-2' }]
    }],
    letters: [{ id: 'cha-1406-letters-patent-3' }, { id: 'cha-1406-letters-patent-4' }]
  },
  {
    id: 'current',
    title: 'Current official reproduction',
    period: 'Guide undated · in use today',
    from: 2017,
    text: 'The Province’s guide, The Emblems of British Columbia, sets the 1987 drawing out in colour, in one colour and in reverse, alone and above the English or French name. It is undated (its PDF was made in 2017 and changed in 2021), and its reproduction masters are not published: the copies here keep the guide’s SAMPLE mark.',
    sources: ['S25'],
    groups: [{
      entries: [{ id: 'guide-colour-lockups' }, { id: 'guide-monochrome' }, { id: 'guide-reverse' }, { id: 'guide-shield-only' }, { id: 'full-legislature-factsheet-2025' }]
    }]
  },
  {
    id: 'seal',
    title: 'Related seal',
    period: '2023',
    from: 2023,
    text: 'The Great Seal changes with the sovereign. The 2023 seal for Charles III changes the legend around the Province’s arms, not the arms.',
    groups: [{ entries: [{ id: 'great-seal-2023' }] }]
  },
  {
    id: 'renderings',
    title: 'Modern renderings and reconstructions',
    period: 'Drawn 2009–2026',
    renderings: true,
    text: 'Drawings of the designs above made since 2009: SVGs from Wikimedia Commons and vector reconstructions supplied to this project. They are not specimens of the arms in use, and each date is the drawing’s own.',
    groups: [
      {
        title: 'Wikimedia Commons',
        entries: [{ id: 'province-1895-fenn-o-manic' }, { id: 'province-shield-zorlot' }, { id: 'province-shield-fry1989' }, { id: 'province-current-leonid2' }]
      },
      {
        title: 'Supplied vector reconstructions',
        entries: [{ id: 'reconstruction-colour-ornate' }, { id: 'reconstruction-monochrome-engraved' }, { id: 'reconstruction-monochrome-line' }]
      }
    ]
  }
]

/** The Province's account: sections oldest first, each with its entries, merged copies gathered. */
export const PROVINCE_STORY = STORY.map((section) => {
  const designStage = section.stage ? stage(section.stage) : null
  return {
    id: section.id,
    title: section.title,
    period: section.period,
    from: section.from ?? null,
    renderings: Boolean(section.renderings),
    stage: designStage ? { year: designStage.year, title: designStage.title, text: designStage.text } : null,
    text: section.text ?? null,
    sources: [...new Map([...(designStage?.sources ?? []), ...(section.sources ?? []).map(source)].filter(Boolean).map((item) => [item.url, item])).values()],
    groups: section.groups.map((group) => ({ title: group.title ?? null, entries: group.entries.map(storyEntry) })),
    letters: (section.letters ?? []).map(storyEntry)
  }
})

export const provinceStoryEntries = () => PROVINCE_STORY.flatMap((section) => [...section.groups.flatMap(({ entries }) => entries), ...section.letters])

const GROUP_ORDER = GROUPS.map(({ id }) => id)
const OTHER_HOLDERS = [...REGISTER_HOLDERS, ...ADDITIONAL_HOLDERS]
  .sort((a, b) => GROUP_ORDER.indexOf(a.group) - GROUP_ORDER.indexOf(b.group) || a.name.localeCompare(b.name))

export const HOLDERS = [PROVINCE, ...OTHER_HOLDERS, ...MUNICIPAL_HOLDERS]

export const holderById = (id) => HOLDERS.find((holder) => holder.id === id) ?? null

export const holdersInGroup = (group) => HOLDERS.filter((holder) => holder.group === group)
