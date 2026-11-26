import { foundationStudyAssets, foundationStudySections } from './foundationDesignStudies.js'

const id = 'bc-parks-foundation'
const name = 'BC Parks Foundation'
const directory = 'identity-collected/bc-parks-foundation'
const site = 'https://bcparksfoundation.ca'
export const foundationSources = {
  partnership: 'https://bcparks.ca/get-involved/donate/',
  board: 'https://archive.news.gov.bc.ca/releases/news_releases_2013-2017/2017ENV0028-000886.htm',
  faq: site + '/faq/',
  agreement: 'https://docs.openinfo.gov.bc.ca/Environment_and_Parks_Estimates_Notes_2025.pdf#page=89',
  endowment: 'https://archive.news.gov.bc.ca/releases/news_releases_2020-2024/2023ENV0036-000857.pdf',
  conservation: 'https://news.gov.bc.ca/releases/2023FOR0061-001662',
  earlier: 'https://nrs.objectstore.gov.bc.ca/kuwyyf/connecting_with_place_973426eb63.pdf#page=11',
  loki: 'https://www.weareloki.com/portfolio/bc-parks-foundation/',
  launch: site + '/updates/bc-parks-foundation-launches-a-bold-new-visual-identity/',
  designer: 'https://burnkit.com/featured-work/bc-parks-foundation/',
  press: site + '/press-room/',
  kit: 'https://cdn.sanity.io/files/p3hjnjl0/production/a9612767a2b12c06c15ae9161f2615ad1f03fc8b.zip',
  contact: site + '/contact/'
}
const s = foundationSources
const note = 'BC Parks Foundation is the independent registered charity that serves as BC Parks’ official charitable partner. BC Parks manages provincial parks and protected areas. The Foundation raises funds, helps protect land and runs public programs with its partners.'

export const PARKS_FOUNDATION_SUBJECT = {
  id, label: name, name, kind: 'charitable-institution', family: 'affiliated-organizations', scope: 'institution',
  aliases: ['BCPF', 'British Columbia Parks Foundation'], priority: 2, graphNode: null,
  collectionIds: ['collected-' + id], salaryEmployers: [],
  relations: [{ type: 'charitable-partner-of', subject: 'sub-bc-parks' }],
  sources: [
    { title: 'BC Parks on its charitable partner', url: s.partnership },
    { title: 'Province announces the founding board, 2017', url: s.board },
    { title: 'Foundation FAQ and operational history', url: s.faq },
    { title: 'Charitable registration 731307492RR0001', url: s.contact },
    { title: 'Foundation visual identity launch, September 18, 2025', url: s.launch }
  ],
  note, nextAction: 'Locate the original full-colour artwork for the pre-2025 partner signature shown in the BC Parks brand guide.'
}

const shared = { publisher: name, format: 'svg', isVector: true, reconstruction: false, observedDate: '2026-11-25' }
const artworkDigests = {
  "charcoal": "5bfe75b27ca89dc9c5078494626da17c58d73027a69f8483364fbfc9796d48db",
  "connecting-with-place": "feeb0f95536c288aafbcbe3219f5dfeebd707ec87ffeb4937e6b25012336dcce",
  "midnight": "1884330c42bb7affdb96fad6acb4a20fb6889afa800cd0a2ce331483721f9120",
  "mist": "6ace32d35a97292f6bb177f8aeb7298fc5e816cf159db25ea8a34185f1b4677c",
  "moss": "1dc6a6bce6401716f45c3717d12f91764f7361c43ab77d7d4eb8fefb8ab88727",
  "sunset": "30dbcd350b8cfeaa7119b48b19268f8c03d40853d2a76ff4d6a948ef221adeaf",
  "umber": "be21b901537554c68908d93bbf907a1e6cc7a2bf04ed11570b870a8f5d1d75f1",
  "white": "d2569f1c3fa51f7253aff17d60e16a3bd250de0e63dada17af659e0a18e04c7f"
}
const design = 'bcpf-full-logo-charcoal'
const colours = ['Charcoal', 'Moss', 'Umber', 'Sunset', 'Midnight', 'Mist', 'White']

export const PARKS_FOUNDATION_BODY = {
  id, name, kind: 'charitable-institution', graphNode: null, current: true, from: 2017,
  shelf: 'partners', status: 'asset-collected', cover: design, notes: note,
  artworkSections: [
    { id: 'foundation-signature', label: 'Foundation signature', marks: [design] },
    ...foundationStudySections
  ],
  assets: [
    ...colours.map((colour) => {
      const key = colour.toLowerCase()
      const file = 'BC_Parks_Foundation_Full_Logo_' + (colour === 'White' ? 'W' : colour + '_RGB') + '.eps'
      const ground = ['Charcoal', 'Midnight', 'Umber'].includes(colour) ? 'light' : 'dark'
      return {
        ...shared, id: 'bcpf-full-logo-' + key, label: 'Foundation signature in ' + colour,
        designLabel: 'BC Parks Foundation signature', versionLabel: colour,
        ...(key === 'charcoal' ? { darkVariant: 'bcpf-full-logo-moss', specimenDate: '2025-09-18' } : { variantOf: design }),
        file: directory + '/' + key + '.svg', sha256: artworkDigests[key], sourceFile: file, sourceGround: ground, darkBackground: ground === 'dark',
        sourcePage: s.press, sourceUrl: s.kit, sourceLocator: 'BCPF Logos / Full Logo - RGB / ' + file,
        role: 'current', evidenceType: 'native-eps-vector-extraction',
        extraction: { method: 'Native Illustrator EPS paths converted to SVG' },
        notes: 'The open outline of British Columbia wraps around three lines of lettering. Burnkit retained this signature when it refreshed the Foundation’s visual identity in 2025.',
        fidelityNote: 'All 18 filled paths come from the Foundation’s EPS. The screen colour comes from its companion RGB PNG. The lettering is outlined in the source.',
        alsoSeen: [{ label: 'Foundation launch and playbook', source: s.launch }]
      }
    }),
    {
      ...shared, id: 'bcpf-connecting-with-place', variantOf: design,
      label: 'Foundation signature in Connecting with Place', versionLabel: '2019 activity book',
      file: directory + '/connecting-with-place.svg', sha256: artworkDigests['connecting-with-place'], sourceGround: 'dark', darkBackground: true,
      role: 'historical', sourcePage: s.earlier, sourceFile: 'Connecting with Place',
      sourceLocator: 'Printed page 10, PDF page 11, upper left', specimenDate: '2019',
      evidenceType: 'native-pdf-vector-extraction', extraction: { method: 'Isolated 18 white filled paths from the activity page' },
      notes: 'A page credited to the Foundation in 2019 prints the white signature beside four illustrated park patches and a patch for readers to colour.',
      fidelityNote: 'The white lettering and provincial outline are native PDF paths. The surrounding activity page is visible in the source publication.'
    },
    ...foundationStudyAssets
  ]
}
