// Specimens from the Legislative Library reports supplied with the collection.
const handbook = 'https://www.obwb.ca/fileadmin/docs/drought_handbook.pdf'
const universityReport = 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/46d7b367-89cb-4fa5-8e03-c0de215434d9/content'
const universityRecord = 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/50723'
const lwbcDesign = 'land-and-water-bc-2004-rebuilt'
const lwbcVector = 'lwbc-handbook-2004-black'

const universitySource = {
  publisher: 'University of the Fraser Valley',
  sourceUrl: universityReport,
  sourcePage: universityRecord,
  sourceDate: '2014',
  role: 'historical',
  sourceGround: 'dark',
  dateNote: 'The university reproduced the mark in its 2014 retrospective.',
}

const artwork = {
  'bc-human-rights-commission': [{
    id: 'bchrc-2000-01-cover-colour',
    variantOf: 'historical-source-human-rights-2001-lockup',
    label: 'Commission signature on the 2000/01 annual report',
    versionLabel: 'Blue cover · 2000/01 annual report',
    publisher: 'British Columbia Human Rights Commission',
    sourcePage: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/273922',
    sourceDate: '2000/2001',
    role: 'historical',
    sourceLocator: '2000/01 Annual Report, Equality Through Access, Legislative Library PDF p. 2, top right.',
    notes: 'The original blue cover carries the two-line black commission name alongside the black-and-white provincial sun. The same publication also survives as a grey ERIC scan.',
    fidelityNote: 'Cropped the original colour cover at four pixels per PDF point. The PDF outlines the letters and combines paths with five bitmap components in the sun. The PNG preserves the printed background.',
    format: 'png',
    isVector: false,
    containsRaster: true,
    evidenceType: 'faithful-crop-of-primary-document',
    sha256: '13f4d0be802dde88a8d3476511619af2279c3080aa25878d49889917b3b1047d',
    bytes: 26851,
  }],
  'land-and-water-bc': [{
    id: lwbcVector,
    label: 'LWBC initials and full name',
    versionLabel: 'Black · June 2004 handbook',
    variantOf: lwbcDesign,
    publisher: 'Land and Water British Columbia Inc.',
    sourceUrl: handbook,
    sourcePage: handbook + '#page=3',
    sourceLocator: 'Dealing with Drought, June 2004, title page. PDF p. 3 in the Okanagan Basin Water Board copy, p. 4 in the Legislative Library copy.',
    sourceDate: '2004-06',
    dateNote: 'The handbook dates this printed example to June 2004.',
    sourceGround: 'light',
    notes: 'The black printed signature pairs the mountain, sun and water emblem with the LWBC initials and full corporate name.',
    fidelityNote: 'Extracted the title page’s original logo path group, including the outlined letters. The monochrome emblem and both lines of lettering match the financial-statement specimen.',
    sha256: 'bc181987e2a1a1c639cdf5981ae1ce2749ad62bc991a6f7b3115e756bed99734',
    bytes: 26540,
  }],
  'university-college-of-the-fraser-valley': [{
    ...universitySource,
    id: 'ucfv-initials-white-2014',
    label: 'UCFV initials and landscape emblem in white',
    sourceLocator: 'Institutional Accountability Report and Plan 2014–15 to 2016–17, Legislative Library PDF p. 5, middle of the three logos.',
    sourceReproduction: true,
    historicalDateLabel: 'University college era',
    notes: 'The emblem sits beside four white initials. The 2007 calendar also prints the full college name below the initials in a separate design.',
    fidelityNote: 'Isolated five white paths from the report’s logo column, keeping the original coordinates, ink and lettering.',
    sha256: '1c57b5c6f67487fdb34bb0caa4e8905e2c5231f01a2add77fa6a3d025563c730',
    bytes: 3978,
  }],
  'university-of-the-fraser-valley': [{
    ...universitySource,
    id: 'ufv-wave-wordmark-white-2014',
    label: 'University of the Fraser Valley wave and leaf wordmark',
    sourceLocator: 'Institutional Accountability Report and Plan 2014–15 to 2016–17, Legislative Library PDF p. 5, bottom of the three logos.',
    notes: 'The university reproduced its white two-line serif name under a leaf and two curved strokes. The report also shows the university’s 40th-anniversary treatment on its cover.',
    fidelityNote: 'Isolated the seven white paths that draw the entire signature, retaining both strokes, the leaf and the outlined lettering.',
    sha256: '6d98681b7f4ca0b0186f45a646e6dfb4447e5a2420d6c28be4f6a7764bf969c9',
    bytes: 14700,
  }, {
    ...universitySource,
    id: 'ufv-40-years-2014',
    label: 'University of the Fraser Valley · 40 years',
    dateNote: 'UFV used this signature on the cover of its 2014 anniversary-year accountability report.',
    sourceLocator: 'Institutional Accountability Report and Plan 2014–15 to 2016–17, Legislative Library PDF p. 2, lower-right corner of the cover.',
    notes: 'White “40 YEARS” lettering appears above the university’s white and lime-green serif signature and leaf. The anniversary commemorates the founding of Fraser Valley College in 1974.',
    fidelityNote: 'Retained all 14 native outline paths, both source inks and original positioning. The separate dark-green background rectangle and cover photograph are omitted.',
    sha256: '30555431c5b6b8b2b98801c084d3866425633fd503660b713e04786546647bb7',
    bytes: 18025,
  }, {
    ...universitySource,
    id: 'ufv-cascades-30-years-2013',
    label: 'UFV Cascades athletics · 30 years',
    historicalDateLabel: '2013 athletics anniversary',
    dateNote: 'The ribbon dates the anniversary to 1983–2013. UFV printed the design in its 2014 retrospective.',
    sourceLocator: 'Institutional Accountability Report and Plan 2014–15 to 2016–17, Legislative Library PDF p. 7, above the 2013 athletics caption.',
    notes: 'A green 1983–2013 ribbon wraps around a white-outlined 30 above the Cascades mountain and UFV initials. The university identifies this as the athletic department’s 30th anniversary.',
    fidelityNote: 'Isolated the 44 native filled paths for the numerals, ribbon, mountain, lettering and trademark from the 2014 report.',
    sha256: '4ab6473e8af1d764ece1b84064c0a01afbd0fc8e68f4868ef731ab2c00ef775d',
    bytes: 24411,
  }],
}

export function withArchivalReportArtwork(body) {
  const specimens = artwork[body.id]
  if (!specimens) return body
  const assets = body.assets.map((asset) => asset.id === lwbcDesign
    ? { ...asset, label: 'Land and Water British Columbia Inc. · LWBC initials and full name', preferredVector: lwbcVector }
    : asset)
  return {
    ...body,
    assets: [...assets, ...specimens.map((specimen) => ({
      format: 'svg', isVector: true, containsRaster: false, reconstruction: false,
      evidenceType: 'native-pdf-vector-extraction', observedDate: '2026-11-27',
      ...specimen, file: 'identity-archival-reports/' + specimen.id + '.' + (specimen.format || 'svg'),
    }))],
  }
}
