import { geoscienceBodies, geoscienceSubjects, surveyRegisterSubjects, surveyHistory, surveySources, surveySpecimens } from './geologicalSurveyResearch.js'
import { assemblyReport, legislativeAssemblyId } from './legislativeAssembly.js'

// Each design groups the particular print and web specimens we inspected.
const survey = 'sub-british-columbia-geological-survey'
const library = 'legislative-library-bc'
const handle = (id) => `https://digitalcollections.llbc.leg.bc.ca/handle/123456789/${id}`
const inventory1990 = { title: 'Geological Survey Branch 1990–91 Project Inventory, cover', url: handle(70474) }
const plan1991 = { title: 'Geological Survey Branch 1991–92 Plan, Information Circular 1991-12, cover', url: handle(67266) }
const plan1992 = { title: 'Geological Survey Branch 1992–93 Plan, Information Circular 1992-8, cover', url: 'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/InformationCircular/BCGS_IC1992-08.pdf#page=1' }
const geology2017 = { title: 'British Columbia Digital Geology, Open File 2017-8, cover', url: 'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/OpenFile/BCGS_OF2017-08.pdf#page=1' }
const annualReport = { title: 'Annual Report of the British Columbia Legislative Library for 1985, cover and “Our Cover Story”, PDF pages 2 and 5', url: handle(272748) }
const directors = { title: 'Provincial Library Directors: A History and Timeline, March 2011, PDF page 2', url: handle(62621) }
const history = { title: 'Legislative Assembly of British Columbia, History of the Legislative Library', url: 'https://www.leg.bc.ca/learn/legislative-library/library-history' }
const digitalCollections = {
  title: 'BC Government Publications, Legislative Library Digital Collections',
  url: 'https://digitalcollections.llbc.leg.bc.ca/collections/8ed826b2-66c8-41d7-9cb0-b2eb104159a2'
}
const digitalMark = 'legislative-library-digital-collections'
const digitalSource = {
  publisher: 'Legislative Library of British Columbia', sourcePage: digitalCollections.url,
  sourceLocator: 'Site header on the BC Government Publications collection page.',
  sourceUrl: 'https://digitalcollections.llbc.leg.bc.ca/assets/custom/images/LibraryLogo.png'
}
const linocutSightings = [
  { title: '1986 Library annual report, brown linocut on the cover, PDF page 2', url: handle(272773), date: '1987-05-07' },
  { title: '1992 Library annual report, white linocut on a burgundy cover, PDF page 2', url: handle(272755), date: '1993-06-09' },
  { title: 'A Guide to Newspaper Holdings at the BC Legislative Library, cover, PDF page 2', url: handle(334131), date: '2009-07' },
  { title: '2011 Library annual report, cover, PDF page 2', url: handle(272759), date: '2012-06-15' }
]
const publicationsChecklist = {
  title: 'BC Government Publications Monthly Checklist, September 2026, PDF page 3',
  url: handle(344221),
  citation: 'The cover pairs the dome with the shorter “Legislative Library of British Columbia” wordmark in teal.'
}
const shared = { current: true, status: 'asset-collected' }
const raster = { observedDate: '2026-11-25', format: 'png', isVector: false, fidelity: 'source compared' }

const surveyAndLibrary = [
  {
    ...shared, id: survey, name: 'British Columbia Geological Survey', kind: 'government-branch', graphNode: survey,
    notes: surveyHistory,
    artworkSections: [
      { id: 'bcgs-current-seal', label: 'Current seal', marks: ['bcgs-founding-year-seal'] },
      { id: 'bcgs-earlier-seal', label: 'Earlier seal', marks: ['bcgs-survey-seal'] },
      { id: 'bcgs-anniversary-variants', label: 'Anniversary variants', marks: ['bcgs-anniversary-2020', 'bcgs-centennial-1995'] }
    ],
    assets: [
      {
        ...raster, id: 'bcgs-survey-seal', label: 'Geological Survey seal in colour', designLabel: 'Geological Survey seal',
        versionLabel: '2017 colour', file: 'identity-collected/bc-geological-survey/seal-2017.png',
        sha256: 'fe00daf024ac69c7410b101ff9c2786e2c422a9e842f53230d0f90e67c8260e4',
        publisher: 'British Columbia Geological Survey', sourceDate: '2017', sourcePage: geology2017.url, sourceLocator: geology2017.title,
        alsoSeen: [{ label: inventory1990.title, source: inventory1990.url, date: '1990' }, { label: plan1991.title, source: plan1991.url, date: '1991' }],
        downloads: [{ label: 'Download the 1999 hammer-seal vector (SVG)', file: 'identity-collected/bc-geological-survey/hammer-seal-1999.svg' }],
        notes: 'The colour seal on the cover of British Columbia Digital Geology has a blue field and coloured bands within the provincial outline.',
        fidelityNote: 'The 360 × 360 pixel image embedded in the published PDF retains its original transparency mask.'
      },
      {
        ...raster, id: 'bcgs-plan-seal-1992', variantOf: 'bcgs-survey-seal', label: 'Geological Survey seal on the June 1992 plan',
        versionLabel: '1992 monochrome', file: 'identity-collected/bc-geological-survey/seal-1992.png',
        sha256: '38b57d4e9324394fc23e4490320fbb666a2cbacd39954b4b6f8ad72b64957878',
        publisher: 'Ministry of Energy, Mines and Petroleum Resources, Geological Survey Branch', sourceDate: '1992-06',
        sourcePage: plan1992.url, sourceLocator: 'Cover, with place and date of issue on PDF page 2.',
        notes: 'The earlier specimen has outlined bands, wider letterspacing and different hammer heads.',
        fidelityNote: 'A crop at the scan’s native resolution retains the paper and ink of the ministry copy.'
      },
      ...surveySpecimens
    ]
  },
  {
    ...shared, id: library, name: 'Legislative Library of British Columbia', kind: 'legislative-institution', graphNode: null,
    cover: digitalMark,
    notes: 'The Library identifies a linocut of its entrance as its logo. Its 1985 report dates the recovery of the block to November 1985 and identifies an earlier printing in the January 1955 B.C.L.A. Bulletin, volume 18, number 3. The Library’s Digital Collections site uses a dome and crown beside the Library and Legislative Assembly names.',
    assets: [
      {
        ...raster, id: 'legislative-library-entrance', label: 'Library entrance linocut', designLabel: 'Library entrance linocut',
        versionLabel: '2011 publication', file: 'identity-collected/legislative-library-bc/entrance-2011.png',
        sha256: '0b14fd362c90baecf648490019d41ca00ba2d7a73743f561abc4c46f31b52aec',
        publisher: 'Legislative Library of British Columbia', sourceDate: '2011-03', sourcePage: directors.url, sourceLocator: directors.title,
        alsoSeen: linocutSightings.map(({ title, url, date }) => ({ label: title, source: url, date })),
        notes: 'The Library reproduced the print on the cover of its history of provincial library directors.',
        fidelityNote: 'Original 275 × 413 pixel cover illustration extracted from the Library’s PDF.'
      },
      {
        ...raster, id: 'legislative-library-1985-report', variantOf: 'legislative-library-entrance', label: 'Library entrance on the 1985 report',
        versionLabel: '1985 annual report', file: 'identity-collected/legislative-library-bc/entrance-1985-report.png',
        sha256: '7db4c2065246157494596f5187a6baf888fc12e425ed76a320a939652294a356',
        publisher: 'British Columbia Legislative Library', sourceDate: '1986', sourcePage: annualReport.url, sourceLocator: annualReport.title,
        dateNote: 'The report covers 1985. Its letter of submission is dated May 15, 1986 (PDF page 6).',
        notes: 'The report reproduces the print on the cover and gives its history on PDF page 5.',
        fidelityNote: 'Cropped directly from the native cover scan, including the screened paper around the woodwork and entrance.'
      },
      {
        ...raster, id: 'legislative-library-web-entrance', variantOf: 'legislative-library-entrance', label: 'Library entrance on the Assembly website',
        versionLabel: 'Assembly website', file: 'identity-collected/legislative-library-bc/entrance.png',
        sha256: '3f95c1ea0c301b0d4ffc0fc141e64fb8b7fa1b8ef547d438de9f61ef2455d94f',
        publisher: 'Legislative Assembly of British Columbia', sourcePage: history.url, sourceLocator: history.title,
        sourceUrl: 'https://www.leg.bc.ca/sites/default/files/images/learn-about-us/image_56.png',
        notes: 'The Assembly credits the linocut to an unknown artist. James G. Mitchell edited the 1955 bulletin.',
        fidelityNote: 'The 174 × 290 transparent PNG served by the Assembly’s history page.'
      },
      {
        ...raster, ...digitalSource, id: digitalMark, label: 'Digital Collections header logo', versionLabel: 'Published image',
        file: 'identity-collected/legislative-library-bc/digital-collections-header.png', darkBackground: true,
        sha256: 'd0776ecf1d0f6517e5dc5d03b09af8bf34fa84bedcb69ded637a978a95437088',
        notes: 'The Digital Collections header pairs a white dome and crown with the Library and Legislative Assembly names.',
        fidelityNote: 'The 1082 × 344 transparent PNG supplied to the project matches the file served by the Library byte for byte.'
      },
      {
        ...digitalSource, id: `${digitalMark}-rebuilt`, variantOf: digitalMark, reconstructionOf: digitalMark,
        label: 'Digital Collections header logo', versionLabel: 'Vector reconstruction',
        file: 'identity-collected/legislative-library-bc/digital-collections-header-rebuilt.svg', darkBackground: true,
        sha256: '7d760ebc25bb3715f4ce319c0b13bf71c9e9ebfbc5df38789018fcf0a6beda62',
        format: 'svg', isVector: true, reconstruction: true, evidenceType: 'vector-reconstruction',
        observedDate: raster.observedDate, fidelity: 'source compared',
        sourcePage: assemblyReport.url, sourceLocator: 'February 2024 report cover, source of the dome and crown paths.',
        notes: 'This reconstruction follows the three-line lettering and layout of the Library’s Digital Collections header.',
        fidelityNote: 'The dome geometry comes from the Assembly’s February 2024 report. The letter outlines were traced from the published PNG and retain its line positions and spacing.'
      },
      {
        // The Provincial Library and Archives' own emblem: the 1906 arms engraved under its name.
        id: 'provincial-library-archives-emblem-rebuilt', label: 'Provincial Library & Archives emblem',
        designLabel: 'Provincial Library & Archives emblem', versionLabel: 'Vector reconstruction',
        file: 'identity-collected/legislative-library-bc/provincial-library-archives-emblem-rebuilt.svg',
        sha256: '2434c9b39fac9865fee3976282b1ebcf705255c470bf9f7f51eb1bbf7cec3e7e',
        format: 'svg', isVector: true, reconstruction: true, supplied: true, evidenceType: 'supplied-vector-reconstruction',
        observedDate: '2026-11-27', fidelity: 'partially compared',
        publisher: 'Provincial Library and Archives, Victoria',
        sourceLocator: 'An undated engraving supplied to the project as a raster (research/identity/provincial-library-archives-2026-11-27/reference/source-reference.png); the publication it came from is not recorded.',
        dateNote: 'Undated. The emblem names the Provincial Library and the Archives together; when it was drawn and used is not established here. Letterheads of 1941 and 1944 use the government’s arms device instead. An undated UBC bookplate with text on scrolls above and below the arms may be this design.',
        notes: 'The Provincial Library & Archives, Victoria B.C., on two scrolls above the Province’s arms as granted in 1906: the Union Flag over the setting sun, the lion on the crown, a stag and a ram, and “SPLENDOR SINE OCCASU.” The Library is now the Legislative Library; the Archives are the BC Archives at the Royal BC Museum.',
        fidelityNote: 'A supplied vector reconstruction of the engraving: source-derived Bézier contours with selective cleanup, the lettering kept as outlines of the original, and three white backing paths restoring the crown’s enclosed interiors. Not original artwork.'
      }
    ]
  }
]

export const SURVEY_AND_LIBRARY_BODIES = [...surveyAndLibrary, ...geoscienceBodies]
export const SURVEY_AND_LIBRARY_SUBJECTS = [...surveyAndLibrary.map((body) => ({
  id: body.id, name: body.name, label: body.name, kind: body.kind, graphNode: body.graphNode,
  priority: 2, salaryEmployers: [], relations: [], collectionIds: [`collected-${body.id}`], note: body.notes,
  ...(body.id === survey ? {
    scope: 'core', family: 'provincial-programs', aliases: ['Geological Survey Branch', 'BC Geological Survey', 'BCGS', 'Geological Branch', 'Geological Division', 'Mineralogical Branch'],
    relations: [...geoscienceSubjects, ...surveyRegisterSubjects].map(({ id }) => ({ type: 'related-to', subject: id })),
    sources: [...surveySources, inventory1990, plan1991, plan1992, geology2017], nextAction: 'Identify a dated introduction of the seal or a contemporary design credit.'
  } : {
    scope: 'institution', family: 'historical-research', aliases: ['British Columbia Legislative Library', 'Provincial Library', 'Provincial Library and Archives'],
    relations: [{ type: 'part-of', subject: legislativeAssemblyId }],
    sources: [digitalCollections, publicationsChecklist, annualReport, directors, history, ...linocutSightings],
    nextAction: 'Examine the January 1955 bulletin cover and seek a record of formal logo adoption.'
  })
})), ...geoscienceSubjects, ...surveyRegisterSubjects]
