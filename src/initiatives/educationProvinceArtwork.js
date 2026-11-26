export const educationProvinceTitle = 'BC — The Education Province'
export const educationProvinceId = 'bc-the-education-province'
export const educationProvinceFolder = 'initiatives/' + educationProvinceId + '/'
export const educationProvinceReport = 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/283876'
export const educationProvinceReportPdf = 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/2e9d5e9b-0b8f-4c23-8300-d8418ec99d87/content'
export const educationProvinceNewspaper = 'https://princetonbcmuseum.com/wp-content/uploads/2023/11/SNL19981013.pdf'

export const educationProvinceWordmark = {
  id: 'education-province-wordmark',
  label: 'Horizontal annual report wordmark',
  file: educationProvinceFolder + 'education-province-wordmark.svg',
  format: 'svg',
  isVector: true,
  sourceGround: 'light',
  evidenceType: 'native-pdf-vector-extraction',
  sourceDate: '1999/2000',
  observedDate: '2026-11-25',
  publisher: 'Ministry of Advanced Education, Training and Technology',
  sourceUrl: educationProvinceReport,
  sourcePage: educationProvinceReportPdf + '#page=9',
  sourceLocator: 'Annual Report 1999/2000, PDF page 9 (printed page vii), right margin',
  notes: 'The annual report uses this horizontal wordmark as a 5% Pantone 287 CVU watermark. The provincial coat-of-arms signature appears elsewhere in the same publication.',
  extraction: { page: 9, method: 'Translated 22 native filled PDF paths into SVG, retaining coordinates, Bézier curves and fill rules. Sampled the PDF’s 5% spot-ink tint in sRGB.' },
  fidelityNote: 'Original paths with no embedded bitmap. The SVG represents the printed spot-ink tint in sRGB.',
  sha256: '475118c8893d8449e914c235cddac2c4f7410392d3cab179856636da284f458e'
}

export const educationProvinceBadge = {
  id: 'education-province-newspaper-badge',
  label: 'Circular newspaper badge',
  file: educationProvinceFolder + 'education-province-newspaper-badge.png',
  format: 'png',
  evidenceType: 'printed-source-crop',
  sourceDate: '1998-10-13',
  observedDate: '2026-11-25',
  publisher: 'Ministry of Advanced Education, Training and Technology and Premier’s Youth Office',
  sourceUrl: educationProvinceNewspaper,
  sourcePage: educationProvinceNewspaper + '#page=9',
  sourceLocator: 'The Similkameen News Leader, October 13, 1998, page 9, right side of the provincial advanced education ad',
  notes: 'The ad sets the slogan on three lines inside a dark circle, with a youth information phone number and website nearby.',
  extraction: { page: 9, method: 'Cropped the badge from the scanned newspaper page at 150 dpi.' },
  fidelityNote: 'Crop of the newspaper held by the Princeton Museum.',
  sha256: '569babed46fdc8e062230fde2fe08838e1bcbe3f5e993e181fb89edf84dba671'
}
