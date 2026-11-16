// Coats of arms: the Province's, and those of the public bodies around it.
//
// The Province's entry is built from the arms-variants catalogue
// (research/identity/arms-variants-2026-11-14/catalogue.json): its design stages, then every dated
// specimen in catalogue order with its credit and sources. The other holders are plain records in
// holders.js, each with its register entry. Nothing here imports an image, so it can be tested
// without a browser; ArmsView.jsx resolves the image files.

import catalogue from '../../research/identity/arms-variants-2026-11-14/catalogue.json' with { type: 'json' }
import { HOLDERS as OTHER_HOLDERS, MUNICIPAL_HOLDERS } from './holders.js'

export const CATALOGUE_DIR = 'research/identity/arms-variants-2026-11-14'

export const GROUPS = [
  { id: 'province', title: 'The Province', description: 'The arms of British Columbia, from the 1895 design to the 1987 grant.' },
  { id: 'crown', title: 'The Crown and the Legislature', description: 'Arms and badges for the offices of the Crown in British Columbia and the Assembly.' },
  { id: 'post-secondary', title: 'Universities and colleges', description: 'Public post-secondary institutions with registered arms.' },
  { id: 'public-body', title: 'Public bodies', description: 'Police, agencies, Crown corporations and other public bodies with registered arms.' },
  { id: 'municipal', title: 'Municipalities and regional districts', description: 'Local governments whose arms are in the public register.' }
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
  registered: ['Arms', 'Crest', 'Supporters', 'Motto', 'Flag'],
  granted: 'Shield and motto 31 March 1906; crest, supporters and compartment 15 October 1987',
  motto: { text: 'Splendor sine occasu', translation: 'Splendour without diminishment' },
  description: 'The Union Flag with an antique crown at its centre, over the sun setting into the sea between wavy bars of blue and silver. The 1987 augmentation added the crowned lion crest with its dogwood collar, the wapiti and bighorn ram supporters, and a compartment of Pacific dogwood.',
  image: { kind: 'vector' },
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

export const HOLDERS = [PROVINCE, ...OTHER_HOLDERS]
export const MUNICIPALITIES = MUNICIPAL_HOLDERS

export const holderById = (id) => HOLDERS.find((holder) => holder.id === id) ?? null

export const holdersInGroup = (group) => HOLDERS.filter((holder) => holder.group === group)
