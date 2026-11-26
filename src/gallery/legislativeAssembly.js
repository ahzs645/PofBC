export const legislativeAssemblyId = 'legislative-assembly'
const name = 'Legislative Assembly of British Columbia'
const kind = 'legislative-institution'
const observedDate = '2026-11-25'
const folder = 'identity-collected/legislative-assembly/'
const webMark = 'legislative-assembly-website-signature'
const website = { title: 'Legislative Assembly of British Columbia, website header', url: 'https://www.leg.bc.ca/' }
const webAsset = 'https://www.leg.bc.ca/sites/default/files/LABC%20Logo.png'
const identityGuide = {
  title: 'Legislative Assembly Visual Identity',
  url: 'https://members.leg.bc.ca/home/gettingstarted/legislative-assembly-visual-identity/'
}
export const assemblyReport = {
  title: 'Working Together to Build a Better Parliamentary Culture, February 2024, cover',
  url: 'https://www.leg.bc.ca/sites/default/files/images/pdf/clerk/WGPC-Report_February-2024.pdf#page=1'
}
const notes = 'The Assembly’s signature combines the Parliament Buildings dome, St. Edward’s Crown and a serif wordmark. The February 2024 report uses teal and grey. The website header sets its white lettering larger relative to the emblem.'
const source = { observedDate, publisher: name, fidelity: 'source compared' }
const webSource = {
  ...source, sourcePage: website.url, sourceUrl: webAsset, sourceLocator: 'Header logo on the Assembly website.'
}

export const LEGISLATIVE_ASSEMBLY_BODY = {
  id: legislativeAssemblyId, name, kind, graphNode: legislativeAssemblyId,
  status: 'asset-collected', current: true, notes,
  assets: [
    {
      ...source, id: 'legislative-assembly-dome-signature', label: 'Dome and crown signature',
      format: 'svg', isVector: true, evidenceType: 'native-pdf-vector-extraction',
      file: `${folder}dome-signature-2024.svg`, sha256: '7e4c3590ef72a09373615cca571e5d4045dbae79eb3afb13b72839cb93598bfe',
      sourceDate: '2024-02', sourcePage: assemblyReport.url, sourceLocator: assemblyReport.title,
      notes: 'The report cover pairs the teal dome and crown with teal Assembly lettering and a grey provincial name.',
      fidelityNote: 'The native cover paths for the emblem and both lines of lettering were isolated in SVG with their original colours, clipping and positions.'
    },
    {
      ...webSource, id: webMark, label: 'Assembly website header logo', versionLabel: 'Published image',
      format: 'png', isVector: false, darkBackground: true, evidenceType: 'official-website-raster',
      file: `${folder}website-signature.png`, sha256: 'd21e7a1bb0b69a692e7da761838da8fb6a98544e8788a3deed131cfe3f06f599',
      notes: 'The Assembly’s white website header signature has two lines of lettering beside the dome and crown.',
      fidelityNote: 'The official 484 × 60 transparent PNG matches the supplied image wherever the artwork is visible.'
    },
    {
      ...webSource, id: `${webMark}-rebuilt`, variantOf: webMark, reconstructionOf: webMark,
      label: 'Assembly website header logo', versionLabel: 'Vector reconstruction',
      format: 'svg', isVector: true, reconstruction: true, evidenceType: 'vector-reconstruction', darkBackground: true,
      file: `${folder}website-signature-rebuilt.svg`, sha256: '91db3913af8eeb8f162d1a9c616193b14821dea6417cc6c2732ebf9127ae322e',
      sourcePage: assemblyReport.url, sourceLocator: 'February 2024 report cover, source of the emblem and letter paths.',
      notes: 'This reconstruction follows the proportions and spacing of the Assembly’s white website logo.',
      fidelityNote: 'The dome and lettering paths come from the February 2024 report. They were scaled, repositioned and filled in white against the website PNG.'
    }
  ]
}

export const LEGISLATIVE_ASSEMBLY_SUBJECT = {
  id: legislativeAssemblyId, name, label: name, kind, graphNode: legislativeAssemblyId,
  scope: 'institution', family: 'historical-research', priority: 2,
  aliases: ['Legislative Assembly', 'BC Legislature', 'B.C. Legislature'], salaryEmployers: [], relations: [],
  collectionIds: [`collected-${legislativeAssemblyId}`], note: notes,
  sources: [identityGuide, assemblyReport, website],
  nextAction: 'Locate the source vector for the white website signature and a dated record of its introduction.'
}
