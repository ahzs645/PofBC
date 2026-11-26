import { strongerPlacement } from './programPlacement.js'
import guideFiles from './strongerBCSources.json' with { type: 'json' }
import { programMarkVersion } from './programMarkVersions.js'

const root = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/web-content-development-guides/corporate-identity-assets/'
export const strongerBCGuide = root + 'visid-pdfs/strongerbc_guidelinesforuse.pdf'
export const strongerBCMatrix = root + 'visid-files/strongerbc_brandmatrix.pdf'
const generalGuide = root + 'visid-pdfs/strongerbc_generalbrandinfo_v3.pdf'
const folder = 'identity-collected/stronger-bc/'

const guideVersions = guideFiles.map(({ form, treatment, pdfBounds, sha256 }) => {
  const design = 'strongerbc-for-everyone-' + form
  const endorsed = form === 'endorsed'
  const label = 'StrongerBC for everyone ' + (endorsed ? 'endorsed mark' : 'wordmark')
  return {
    ...programMarkVersion(treatment === 'positive' ? design : design + '-' + treatment, design, treatment, design + '-reverse'),
    placement: strongerPlacement(endorsed ? 'C' : 'D', strongerBCGuide),
    label, designLabel: label, file: folder + 'for-everyone-' + form + '-' + treatment + '.svg',
    sha256, format: 'svg', isVector: true, publisher: 'Province of British Columbia',
    observedDate: '2026-11-25', specimenDate: '2024-03', timelineEra: 'strongerbc-2022',
    sourcePage: strongerBCGuide + '#page=3', sourceLocator: 'Page 3, ' + (endorsed ? 'column C' : 'column D') + ', ' + treatment,
    ...(treatment === 'positive' ? { alsoSeen: [{ label: 'General Brand Information, layout examples on page 8', source: generalGuide + '#page=8' }] } : {}),
    evidenceType: 'native-pdf-vector-extraction', extraction: { pdfBounds },
    fidelityNote: 'The native logo paths were isolated from the public guide with PyMuPDF. The print sample’s frame and background were removed.',
    notes: 'The guide reserves the “for everyone” signature for government communications. ' + (endorsed
      ? 'The preferred endorsed arrangement includes the provincial signature. Its minimum height is 50 px on screen or 0.46 in in print.'
      : 'The wordmark may appear separately when the BC mark is visible elsewhere. Its minimum height is 40 px on screen or 0.35 in in print.')
  }
})

function kitVersion(asset) {
  const endorsed = asset.id.startsWith('vector-BCID_')
  const solid = asset.id.includes('_Solid_')
  const reversed = asset.id.endsWith('_rev')
  const treatment = solid ? (reversed ? 'white' : 'black') : (reversed ? 'reverse' : 'positive')
  // The two standalone masters have separately verified geometry and palette editors.
  const design = endorsed ? 'vector-BCID_StrongerBC_RGB_pos' : asset.id.replace(/_rev$/, '_pos')
  const label = endorsed ? 'StrongerBC endorsed mark' : asset.label
  return {
    ...asset, ...programMarkVersion(asset.id, design, treatment, design.replace(/_pos$/, '_rev')),
    placement: strongerPlacement(endorsed ? 'A' : 'B', strongerBCGuide),
    publisher: 'Province of British Columbia', designLabel: label, label, specimenDate: '2024-03',
    alsoSeen: [{ label: 'March 2024 guide, page 2', source: strongerBCGuide + '#page=2' }],
    notes: endorsed
      ? 'The guide prefers the endorsed arrangement. Minimum height is 50 px on screen or 0.46 in in print. Third-party use is subject to provincial approval.'
      : 'The plain wordmark may appear separately when the BC mark is visible elsewhere. Minimum height is 25 px on screen or 0.23 in in print.',
    ...(!solid ? { printMember: asset.sourceLocator.replace('_RGB_', '_CMYK_').replace(/\.svg$/, '.eps'), downloads: [{ label: 'Download CMYK ' + treatment + ' PDF', file: asset.file.replace('_RGB_', '_CMYK_').replace(/\.svg$/, '.pdf') }] } : {})
  }
}

export function withStrongerBCGuide(record) {
  return { ...record, assets: [...record.assets.map(kitVersion), ...guideVersions] }
}
