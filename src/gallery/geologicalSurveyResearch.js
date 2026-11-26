// Publication dates identify the specimens. The Survey traces its institutional history to the Bureau of Mines.
const survey = 'sub-british-columbia-geological-survey'
const publisher = 'British Columbia Geological Survey'
const site = 'https://www2.gov.bc.ca/gov/content/industry/mineral-exploration-mining/british-columbia-geological-survey'
const catalogue = 'https://cmscontent.nrs.gov.bc.ca/geoscience/PublicationCatalogue/'
const paper = (title, path, page) => ({ title, url: catalogue + path + '.pdf#page=' + page })
const review1989 = paper('Mineral Exploration Review 1988, Information Circular 1989-1, cover', 'InformationCircular/BCGS_IC1989-01', 1)
const centennial = paper('Mineral Exploration Review 1994, Information Circular 1995-1, title page', 'InformationCircular/BCGS_IC1995-01', 2)
const survey2013 = paper('British Columbia Geological Survey, Information Circular 2013-4, cover', 'InformationCircular/BCGS_IC2013-04', 1)
const survey125 = paper('Geochronologic database, GeoFile 2020-10, cover', 'GeoFile/BCGS_GF2020-10', 1)
const survey2024 = paper('Surficial geology map index, Open File 2024-09, cover', 'OpenFile/BCGS_OF2024-09', 1)
const survey2026 = paper('Critical mineral study of the E&L deposit, GeoFile 2026-08, cover', 'GeoFile/BCGS_GF2026-08', 1)
const online2021 = paper('Online databases at the British Columbia Geological Survey, Information Circular 2021-5', 'InformationCircular/BCGS_IC2021-05', 1)
const program2014 = paper('Opportunities to Explore, Information Circular 2014-8, page 20', 'InformationCircular/BCGS_IC2014-08', 20)
const surveys2020 = paper('Committee of Provincial and Territorial Geologists, Canadian provincial and territorial geological surveys, BC profile', 'CPTG/2020_CPTG', 4)
const inventoryGuide = paper('Larry D. Jones, A Guide to Locating Mineral-Related Information in B.C., page E-9', 'GeologyExplorationMining/BCGS_EXP1998-00', 140)
const mapPage = { title: 'MapPlace, provincial service history', url: site + '/mapplace' }
const minfilePage = { title: 'MINFILE project history, from the card index to the web', url: site + '/mineralinventory/moreinfo' }
const oldSociety = { title: 'Geoscience BC 2017 Annual Report, cover and financial statements', url: 'https://cdn.geosciencebc.com/pdf/2017AnnualReport.pdf' }
const newSociety = { title: 'Geoscience BC quarterly update, January 24, 2019', url: 'https://www.geosciencebc.com/geoscience-bc-quarterly-update-new-logo-strategic-task-force-on-water-and-more/' }
const societyHomepage = { title: 'Geoscience BC homepage, three-colour header logo', url: 'https://www.geosciencebc.com/' }
const newsletter = { title: 'Quarterly newsletter announcing the mountain logo', url: 'https://mailchi.mp/657b79b0b5d2/geoscience-bc-quarterly-newsletter' }
const branchHistory = paper('Atholl Sutherland Brown, British Columbia’s Geological Surveys, 1895–1995 (1998)', 'Miscellaneous/BCGS_MP-77', 5)

const review1999 = paper('British Columbia Mineral Exploration Review 1998, Information Circular 1999-1, cover', 'InformationCircular/BCGS_IC1999-01', 1)
const poster2020 = paper('Catching the tail of a golden dragon plus 60 elements in British Columbia, GeoFile 2020-4, upper left', 'GeoFile/BCGS_GF2020-04', 1)
const map1995 = paper('Porphyry deposits in British Columbia, Open File 1995-23, upper right title block', 'OpenFile/BCGS_OF1995-23', 1)
const map2022 = paper('Bedrock geology of the Dease Lake area, Geoscience Map 2022-1, title block', 'GeoscienceMap/BCGS_GM2022-01', 1)
const division1973 = paper('Minister of Mines and Petroleum Resources, 1973 annual report, page A58', 'AnnualReport/BCGS_AR1973', 58)
const branch1981 = paper('1981 annual report, organization chart at December 31, 1981', 'AnnualReport/BCGS_AR1981', 6)
const workshop2017 = paper('MapPlace 2 (beta) workshop, Information Circular 2017-3, cover', 'InformationCircular/BCGS_IC2017-03', 1)
const mapTour = { title: 'Tour of the MapPlace, slide 3, website screenshot', url: 'https://cmscontent.nrs.gov.bc.ca/geoscience/MapPlace1/MapPlaceTour.ppt' }
const manual = { title: 'MINFILE/pc and MINFILE/www 5.0 User’s Manual, Information Circular 2007-5, PDF pages 9–10', url: 'https://cmscontent.nrs.gov.bc.ca/geoscience/MINFILE/MINFILE_usermanual.pdf#page=10' }
const society2022 = { title: 'Geoscience BC 2021–2022 Annual Report, back cover', url: 'https://cdn.geosciencebc.com/pdf/Geoscience%20BC%20Annual%20Report%202021-22%20-%20Web.pdf#page=24' }
const vector = { format: 'svg', isVector: true, evidenceType: 'native-pdf-vector-extraction' }

export const surveyHistory = 'The Survey traces its origins to the Bureau of Mines, established in 1895. A district Mineral Survey began work alongside the Bureau in 1917. The department renamed its Mineralogical Branch the Geological Division in 1973. Its December 1981 organization chart names the Geological Branch. In 1986 the province renamed the Geological Branch the Geological Survey Branch. The hammer-and-map seal appears on a 1989 title page. Special designs marked the centennial in 1995 and the 125th anniversary in 2020.'
export const surveySources = [
  { title: 'British Columbia Geological Survey', url: site },
  { title: 'Bureau of Mines Act, 1895, chapter 3, sections 3–7', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/1221491311' },
  branchHistory, division1973, branch1981, review1989, centennial, map1995, review1999, survey2013, survey125, poster2020, online2021, map2022, survey2024, survey2026
]
const image = (id, label, file, source, sha256) => ({
  id, label, file: 'identity-collected/' + file, observedDate: '2026-11-25', sha256,
  format: 'png', isVector: false, publisher, fidelity: 'source compared', sourcePage: source.url, sourceLocator: source.title
})
const seen = (source, date) => ({ label: source.title, source: source.url, date })
export const surveySpecimens = [
  { ...image('bcgs-seal-1989', 'Geological Survey seal on the 1989 circular', 'bc-geological-survey/seal-1989.png', review1989, '48320c9599d1a0a754317956b0be5c36850673329d161f87121201a6cf552305'),
    sourceDate: '1989', versionLabel: '1989 monochrome', variantOf: 'bcgs-survey-seal',
    notes: 'Two rock hammers flank an outline map of the province. The circular reports on exploration during 1988.',
    fidelityNote: 'Cropped from the original title-page scan at its native resolution.' },
  { ...image('bcgs-centennial-1995', '100 years of geological surveying', 'bc-geological-survey/centennial-1995.png', centennial, 'e95ea44e8bfd32dcd6e77c5141ba6ae2f49f870cb0822a7b3377642ddb1c27cf'),
    sourceDate: '1995-01', designLabel: '100 years of geological surveying', versionLabel: '1995 title-page scan',
    downloads: [{ label: 'Download the 1995 centennial map vector (SVG)', file: 'identity-collected/bc-geological-survey/centennial-1995.svg' }],
    notes: 'The centennial signature places the Survey seal beside a large 100, below the years 1895–1995.',
    fidelityNote: 'Native-resolution crop of the black title-page printing. The following page explains the anniversary.' },
  { ...image('bcgs-seal-2013', 'Geological Survey seal on the 2013 profile', 'bc-geological-survey/seal-2013.png', survey2013, 'f5a0a35a13e834ee26a0ec34e735c844cc802a19ed05878783b829a553360006'),
    sourceDate: '2013', versionLabel: '2013 flat colour', variantOf: 'bcgs-survey-seal',
    notes: 'Curved rock picks flank the provincial outline on a flat cyan field.',
    fidelityNote: 'The cover embeds a 769 × 769 pixel CMYK image. Converted to sRGB with its original transparency mask.' },
  { ...image('bcgs-anniversary-2020', '125th anniversary seal', 'bc-geological-survey/anniversary-2020.png', survey125, 'a712781b07dc6efc59dffb4442d890544ce2d3a58ac4ae2b77fdc744aa73542f'),
    sourceDate: '2020', designLabel: '125th anniversary seal', versionLabel: '2020 report cover',
    preferredVector: 'bcgs-anniversary-vector-2020',
    alsoSeen: [seen(surveys2020, '2020')], notes: 'The white number 125 crosses the coloured geological bands. The founding year appears inside the ring.',
    fidelityNote: 'Original 533 × 521 pixel PDF image with its embedded transparency mask.' },
  { ...image('bcgs-founding-year-seal', 'Geological Survey seal with founding year', 'bc-geological-survey/est-1895-seal-2024.png', survey2024, 'b1e8f5075e4cb898e4e12aa905efde7aad35a4f5db48aadb733a6b9188daf13e'),
    sourceDate: '2024', designLabel: 'Geological Survey seal with founding year', versionLabel: '2024 report cover',
    role: 'current', preferredVector: 'bcgs-founding-year-vector-2022',
    alsoSeen: [seen(online2021, '2021'), seen(survey2026, '2026')],
    notes: 'A coloured map sits on pale blue between the words “est.” and “1895”. Earlier seals placed hammers on either side of the map.',
    fidelityNote: 'Original 533 × 533 pixel PDF image with its embedded transparency mask.' },
  { ...image('bcgs-centennial-vector-1995', 'Centennial emblem on the porphyry deposits map', 'bc-geological-survey/centennial-1995.svg', map1995, '21a97c3e411df6da8adc6e7a24fe45c81ff2c1997be161a97d0c2764d9eb7c2a'),
    ...vector, variantOf: 'bcgs-centennial-1995', versionLabel: '1995 map vector', sourceDate: '1995',
    notes: 'The map title block places the Survey seal beside a hatched 100 between the anniversary dates and the words “Years of Geological Surveying”.',
    fidelityNote: 'All 544 filled and stroked paths come from the original plotted map. The SVG reproduces the paper’s linework, lettering and hatching.' },
  { ...image('bcgs-hammer-seal-1999', 'Hammer-and-map seal in the 1999 exploration review', 'bc-geological-survey/hammer-seal-1999.svg', review1999, '4417e63b071e9d6eb4f50dcfcb0e458dbcddaa7c0e1963c7ed8fa216b4bf008a'),
    ...vector, variantOf: 'bcgs-survey-seal', versionLabel: '1999 vector', sourceDate: '1999',
    notes: 'Two black hammers sit in the white outer ring. Coloured geological bands cross the map on a blue field.',
    fidelityNote: 'All 56 paths come from the cover artwork, including letter outlines from the embedded font.' },
  { ...image('bcgs-anniversary-vector-2020', '125th anniversary seal on the 2020 geochemistry poster', 'bc-geological-survey/anniversary-2020.svg', poster2020, '0102f4c6f33180b979d5f8f2ae47d32fdeebd79d85d15bcc3aafbd22b39febfa'),
    ...vector, variantOf: 'bcgs-anniversary-2020', versionLabel: '2020 poster vector', sourceDate: '2020',
    notes: 'The poster sets a white 125 with a black outline across the geological map.',
    fidelityNote: 'All 26 emblem paths retain their fills and strokes. The surrounding blue poster field is omitted.' },
  { ...image('bcgs-founding-year-vector-2022', 'Founding-year seal on the Dease Lake map', 'bc-geological-survey/est-1895-seal-2022.svg', map2022, '8b0b84a9e502b1fb1098e1300082e67c7f8f82d5095a62c3556987e46f113c1a'),
    ...vector, variantOf: 'bcgs-founding-year-seal', versionLabel: '2022 map vector', sourceDate: '2022',
    alsoSeen: [seen(survey2026, '2026')], notes: 'The founding-year seal appears in the Dease Lake map title block and on the cover of GeoFile 2026-08.',
    fidelityNote: 'The 22 filled and stroked paths include the lettering and founding year.' }
]

const shared = { current: true, graphNode: null, status: 'asset-collected' }
export const geoscienceBodies = [
  { ...shared, id: 'bcgs-mapplace', name: 'MapPlace', kind: 'service-brand', from: 1995,
    notes: 'The Geological Survey developed MapPlace in 1995 so users could query provincial geoscience databases and make their own maps. The Survey credits W. Kilby with its initial development. A preserved web page last updated in November 2001 shows “The Map Place” across a map of Canada. Its 2014 signature includes a wired mouse. By 2017 its signature paired a simplified geological map with the words “digital geoscience for British Columbia”.',
    assets: [
      { ...image('mapplace-web-panel-2001', 'The Map Place over a map of Canada', 'bcgs-mapplace/web-panel-2001.png', mapTour, '34b24f53a9aeb9c767fc9d08190c17474ecbcc350165f22890c59ccc350ba101'),
        specimenDate: '2001-11-28', dateNote: 'The captured page gives November 28, 2001 as its last update. The archived presentation was last saved in 2009.',
        notes: 'Blue lettering spans a yellow map of Canada in the program’s early web graphic.',
        fidelityNote: 'A 220 × 145 pixel crop of the 1024 × 768 Netscape screenshot on slide 3, including its purple border.' },
      { ...image('mapplace-wired-mouse', 'MapPlace.ca with wired mouse', 'bcgs-mapplace/mapplace-ca.png', program2014, '132599493fddcb93e3db38981771ba0e0c2cb5ecb5b9d6793abbe9e9e975f40e'),
        sourceDate: '2014-05', notes: 'A crosshair sits in the wordmark and a mouse cord runs beneath it.', fidelityNote: 'Original 1148 × 310 pixel image and transparency mask embedded on page 20.' },
      { ...image('mapplace-digital-geoscience', 'MapPlace digital geoscience signature', 'bcgs-mapplace/mapplace-2020.png', surveys2020, 'c78a4f9b176af4fd596e852b481777a644211442df82586352656fe0e5dfde29'),
        sourceDate: '2020', alsoSeen: [seen(workshop2017, '2017')], publisher: 'Committee of Provincial and Territorial Geologists', notes: 'Bright geological bands sit beside the MapPlace name and a one-line description.', fidelityNote: 'Original 918 × 275 pixel image from the British Columbia profile.' }
    ] },
  { ...shared, id: 'bcgs-minfile', name: 'MINFILE', kind: 'service-brand', from: 1976,
    notes: 'The provincial inventory began as a card file in 1967. UBC incorporated it into MINDEP in 1973. The system took the name MINFILE in 1976 when it moved to the BC Systems Corporation. The Survey records a web rewrite in 2005. Its 2007 manual reproduces the MINFILE/pc search menu and title screen on page 10.',
    assets: [
      { ...image('minfile-early-web', 'MINFILE mineral inventory web mark', 'bcgs-minfile/web-inventory.png', inventoryGuide, '9d26f0c6d8f6f19e50a73a9244c843ddfee61cb7069c92bf26a33cef92243938'),
        publisher: 'Ministry of Energy and Mines', sourceDate: '1998 reporting volume', versionLabel: 'Early web interface',
        dateNote: 'The volume covers 1998. The article cites January 1999 data. The original screen capture has no date.',
        notes: 'A ministry geologist reproduced the boxed MINFILE wordmark in a screenshot of the mineral inventory website.',
        downloads: [{ label: 'Download the 2007 MINFILE/pc title screen (JPEG)', file: 'identity-collected/bcgs-minfile/desktop-2007.jpeg' }],
        fidelityNote: 'Native-resolution crop of the printed screenshot on page E-9. The stippled fill and small lettering survive at the resolution of the scan.' }
    ] },
  { ...shared, id: 'geoscience-bc', name: 'Geoscience BC', kind: 'nonprofit-society', from: 2005,
    notes: 'Geoscience BC Society incorporated on April 26, 2005. This independent research society publishes projects alongside the provincial Survey. In January 2019 it announced a new mountain logo representing its minerals, energy and water research.',
    assets: [
      { ...image('geoscience-bc-green-ridges', 'Geoscience BC green ridges and crosshair', 'geoscience-bc/mountains-2017.svg', oldSociety, 'd5905ea8113c3dc6391bf5d0a8f176ab42772638e21f7b9d0480d5df622524f1'),
        format: 'svg', isVector: true, publisher: 'Geoscience BC', sourceDate: '2017', evidenceType: 'native-pdf-vector-extraction',
        notes: 'Two green ridges rise above dark blue lettering. A green crosshair marks the first o.', fidelityNote: 'The 15 filled paths from the annual report cover preserve the outlined type and both ridgelines.' },
      { ...image('geoscience-bc-three-colours', 'Geoscience BC three-colour mountain logo', 'geoscience-bc/mountains-web.png', newSociety, '1e212150300654c9a36dab20c731bbd12d65f8f302178fab6673b80dabc8c7f2'),
        publisher: 'Geoscience BC', designLabel: 'Three-colour mountain signature', versionLabel: 'Website PNG', specimenDate: '2019-01', sourceUrl: 'https://www.geosciencebc.com/wp-content/uploads/2018/12/geoscience_logo.png',
        role: 'current', sourcePage: societyHomepage.url, sourceLocator: societyHomepage.title,
        notes: 'Orange, green and blue ridges sit above the society’s name.', dateNote: 'The January newsletter dates the launch. The homepage still served the same PNG when checked in November 2026.',
        preferredVector: 'geoscience-bc-three-colours-vector',
        fidelityNote: 'Original transparent PNG served by Geoscience BC.' },
      { ...image('geoscience-bc-three-colours-vector', 'Three-colour mountain signature on the annual report', 'geoscience-bc/mountains-2022.svg', society2022, '6a633f3767f09526a9dd000c537680541a0e1ccb24df66fa4a6c6d1f93139454'),
        ...vector, publisher: 'Geoscience BC', sourceDate: '2022', versionLabel: '2022 back-cover vector', variantOf: 'geoscience-bc-three-colours',
        notes: 'Three coloured ridges sit above the society’s full name on the back cover.',
        fidelityNote: 'The mountain paths and outlined glyphs from the embedded typeface reproduce all 15 visible elements.' }
    ] }
]

const sources = {
  'bcgs-mapplace': [mapPage, mapTour, paper('Jones and colleagues, Update of British Columbia Geological Survey Geospatial Databases and Applications, PDF page 9', 'Paper/BCGS_P2007-01-05_Jones', 9), program2014, workshop2017, surveys2020],
  'bcgs-minfile': [minfilePage, inventoryGuide, manual],
  'geoscience-bc': [societyHomepage, oldSociety, newSociety, newsletter, society2022, { title: 'Geoscience BC releases in the provincial catalogue', url: site + '/publications/geoscience-bc-releases' }]
}
export const geoscienceSubjects = geoscienceBodies.map(({ id, name, kind, notes }) => ({
  id, name, label: name, kind, graphNode: null, priority: 2, salaryEmployers: [], note: notes,
  scope: id === 'geoscience-bc' ? 'institution' : 'core', family: id === 'geoscience-bc' ? 'institutions' : 'provincial-programs',
  aliases: { 'bcgs-mapplace': ['MapPlace.ca', 'MapPlace 2'], 'bcgs-minfile': ['MINFILE/pc', 'MINFILE/www'], 'geoscience-bc': ['Geoscience BC Society'] }[id],
  relations: [{ type: id === 'geoscience-bc' ? 'related-to' : 'service-of', subject: survey }],
  collectionIds: ['collected-' + id], sources: sources[id],
  nextAction: { 'bcgs-mapplace': 'Locate an original MapPlace launch screen from the 1990s.', 'bcgs-minfile': 'Locate the standalone boxed web graphic shown in the early inventory guide.', 'geoscience-bc': 'Identify the designers of the two mountain signatures.' }[id]
}))

const directory = { title: 'Survey staff and sections', url: site + '/aboutbcgs' }
const chart = paper('British Columbia Geological Survey, 2013 organization chart, page 2', 'InformationCircular/BCGS_IC2013-04', 2)
const assessments = { title: 'Survey assessment report collections', url: site + '/assessmentreports' }
const office2020 = paper('Mineral Development Office, Information Circular 2020-4, cover', 'InformationCircular/BCGS_IC2020-04', 1)
const office2024 = paper('Mineral Development Office, Information Circular 2024-3, cover', 'InformationCircular/BCGS_IC2024-03', 1)

export const surveyRegisterSubjects = [
  { id: 'sub-mineral-development-office', name: 'Mineral Development Office', aliases: ['MDO'],
    graphNode: 'sub-mineral-development-office', kind: 'government-branch',
    note: 'The Vancouver office uses the Survey’s anniversary seal on its 2020 circular and the founding-year seal on its 2024 circular.',
    sources: [{ title: 'Mineral Development Office', url: site + '/mineral-development-office' }, office2020, office2024],
    nextAction: 'Check earlier office letterhead for a separate emblem.' },
  { id: 'bcgs-cordilleran-section', name: 'Cordilleran Section', aliases: ['Cordilleran Geoscience Section'], kind: 'government-branch',
    sources: [directory, chart], note: 'The staff directory lists the section. The 2013 chart uses the longer name Cordilleran Geoscience Section.',
    nextAction: 'Locate a section-issued publication carrying a distinct signature.' },
  { id: 'bcgs-resource-information-section', name: 'Resource Information Section', kind: 'government-branch',
    sources: [directory, chart], note: 'The Survey identifies the section in its staff directory and its 2013 organization chart.',
    nextAction: 'Check section publications and letterhead for a distinct mark.' },
  { id: 'bcgs-aris', name: 'Assessment Report Indexing System', aliases: ['ARIS'], kind: 'service-brand',
    sources: [assessments, { title: 'ARIS search service', url: 'https://apps.nrs.gov.bc.ca/pub/aris' }, online2021],
    note: 'ARIS indexes mineral and placer exploration assessment reports. The Survey identifies the service by name in its database guide.',
    nextAction: 'Check early database guides for a separately identifiable ARIS mark.' },
  { id: 'bcgs-coalfile', name: 'COALFILE', kind: 'service-brand', sources: [assessments, online2021],
    note: 'The Survey’s coal assessment report collection supplies exploration reports and supporting data.',
    nextAction: 'Examine historical COALFILE screens for a program signature.' },
  { id: 'bcgs-property-file', name: 'Property File', aliases: ['PropertyFile'], kind: 'service-brand',
    sources: [{ title: 'Survey Property File collection', url: site + '/propertyfile' }, { title: 'Property File search portal', url: 'https://propertyfile.gov.bc.ca/' }],
    note: 'The Survey preserves donated exploration documents in Property File. The search portal uses the provincial identity.',
    nextAction: 'Check printed Property File indexes for a distinct historical mark.' }
].map((subject) => ({
  graphNode: null, priority: 2, salaryEmployers: [], collectionIds: [], identityStatus: 'distinct-unconfirmed',
  scope: 'core', family: 'provincial-programs', label: subject.name, aliases: [],
  relations: [{ type: subject.kind === 'service-brand' ? 'service-of' : 'part-of', subject: survey }],
  ...subject
}))
