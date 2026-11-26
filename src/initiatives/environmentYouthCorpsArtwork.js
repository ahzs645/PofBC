export const environmentYouthCorpsId = 'environment-youth-corps'
export const environmentYouthCorpsGalleryId = `specimens-${environmentYouthCorpsId}`

const directory = `initiatives/${environmentYouthCorpsId}/`
const markLabel = 'Environment Youth Corps of British Columbia'

export const environmentYouthCorpsAd = {
  id: 'driftwood-1990-06-13',
  title: '“Working for a better world,” Gulf Islands Driftwood',
  shortTitle: 'Gulf Islands Driftwood',
  publisher: 'Gulf Islands Driftwood, via Salt Spring Archives',
  date: '1990-06-13',
  url: 'https://saltspringarchives.com/driftwood/1990/v31n24June13-1990A.pdf',
  note: 'The provincial recruitment ad directs applicants to the Canada Employment Centre. It credits John Reynolds, Minister of Environment.'
}

export const environmentYouthCorpsReprint = {
  id: 'driftwood-1990-06-20',
  title: '“Working for a better world,” second Driftwood printing',
  shortTitle: 'Gulf Islands Driftwood reprint',
  publisher: 'Gulf Islands Driftwood, via Salt Spring Archives',
  date: '1990-06-20',
  url: 'https://saltspringarchives.com/driftwood/1990/v31n25June20-1990B.pdf',
  note: 'The same recruitment mark appears one week later on p. B11.'
}

const source = {
  label: markLabel,
  publisher: 'British Columbia Ministry of Environment',
  sourceFile: 'Gulf Islands Driftwood recruitment advertisement',
  sourceId: environmentYouthCorpsAd.id,
  sourceUrl: environmentYouthCorpsAd.url,
  sourcePage: `${environmentYouthCorpsAd.url}#page=10`,
  sourceLocator: 'June 13, 1990, p. A10, logo in the right-column advertisement',
  sourceDate: environmentYouthCorpsAd.date,
  observedDate: '2026-11-25',
  alsoSeen: [{ label: 'June 20, 1990, p. B11', source: `${environmentYouthCorpsReprint.url}#page=11`, date: environmentYouthCorpsReprint.date }],
  alt: 'Waving British Columbia flag above the rounded youth corps lettering and two lines of script',
  notes: 'The provincial waving flag sits above the rounded youth corps lettering, with Environment and of British Columbia in script.'
}

export const environmentYouthCorpsScan = {
  ...source,
  id: 'environment-youth-corps-lockup', designLabel: markLabel, versionLabel: 'Newspaper scan',
  file: `${directory}driftwood-1990-06-13.png`, format: 'png', isVector: false,
  width: 328, height: 319, evidenceType: 'printed-source-crop',
  caption: 'Crop of the June 13, 1990 recruitment ad',
  fidelityNote: 'Unretouched crop of the page bitmap archived by Salt Spring Archives.',
  sha256: 'db2bba1f512bdca5be66816a7c54eacdf821353863f478c65e915680b8ef31af'
}

export const environmentYouthCorpsVector = {
  ...source,
  id: 'environment-youth-corps-reconstruction', variantOf: environmentYouthCorpsScan.id,
  versionLabel: 'SVG reconstruction',
  file: `${directory}environment-youth-corps-reconstruction.svg`, format: 'svg', isVector: true,
  width: 742, height: 749, evidenceType: 'vector-reconstruction', sourceGround: 'light', reconstruction: true,
  caption: 'Vector reconstruction of the mark printed in June 1990',
  fidelityNote: 'Cleaned outlines from the supplied crop, compared with the June 1990 advertisement. The flag reuses the repository’s Spirit of BC vector in one ink. The original typefaces remain unconfirmed.',
  sha256: '4af78203f90e472c30122cf360e4e8694d7f7d53d45e3696d05305aedf4cf966'
}

export const environmentYouthCorpsCover = {
  file: environmentYouthCorpsVector.file,
  displayId: environmentYouthCorpsVector.id,
  alt: environmentYouthCorpsVector.alt,
  caption: environmentYouthCorpsVector.caption
}

export const environmentYouthCorpsSpecimens = {
  program: environmentYouthCorpsId,
  assets: [environmentYouthCorpsScan, environmentYouthCorpsVector]
}
