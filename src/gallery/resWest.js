const directory = 'identity-collected/reswest'
const brochure = 'https://www.worldsfairphotos.com/expo86/booklets/1985-brochure-us.pdf'
const advertisement = `${import.meta.env?.BASE_URL ?? '/'}${directory}/reswest-advertisement.png`
const design = 'reswest-badge'

export const RESWEST_SOURCES = [
  { title: 'B.C. Hansard, June 18, 1985, pp. 6709–6710', url: 'https://lims.leg.bc.ca/hdms/file/Debates/33rd3rd/33p_03s_850618p.htm#06709' },
  { title: 'Expo 86 Corporation, 1985 U.S. brochure, accommodation information', url: `${brochure}#page=3` },
  { title: 'B.C. Hansard, April 29, 1986, pp. 8015–8016', url: 'https://lims.leg.bc.ca/hdms/file/Debates/33rd4th/33p_04s_860429p.htm#08015' },
  { title: 'B.C. Hansard, June 17, 1986, p. 8780', url: 'https://lims.leg.bc.ca/hdms/file/Debates/33rd4th/33p_04s_860617p.htm#08780' }
]

const adEvidence = {
  label: 'ResWest badge',
  publisher: 'Publisher unidentified',
  sourceFile: 'Supplied screenshot of a ResWest booking advertisement',
  sourcePage: advertisement,
  sourceLocator: 'Centre badge, between the provincial BC signature and the stacked Expo 86 mark.',
  sourceDate: 'Expo 86 era',
  observedDate: '2026-11-25',
  dateNote: 'The advertisement’s publication and issue are still unidentified. The cited 1985 date is for the brochure specimen.'
}

const brochureEvidence = {
  label: 'ResWest badge',
  publisher: 'Expo 86 Corporation',
  sourceFile: 'The 1986 World Exposition, U.S. edition, D406-885 UST-1K',
  sourcePage: `${brochure}#page=4`,
  sourceUrl: brochure,
  sourceLocator: 'PDF page 4, lower-right accommodation reservation block, between the caption and the phone number.',
  sourceDate: '1985',
  observedDate: '2026-11-25',
  alsoSeen: [
    { date: '1985', label: 'Canadian English brochure, PDF page 4', source: 'https://www.worldsfairphotos.com/expo86/booklets/1985-brochure-english.pdf#page=4' },
    { date: '1985', label: 'Canadian French brochure, PDF page 4', source: 'https://www.worldsfairphotos.com/expo86/booklets/1985-brochure-french.pdf#page=4' }
  ]
}

const rebuilt = {
  variantOf: design,
  format: 'svg',
  isVector: true,
  reconstruction: true,
  provenance: 'reconstructed',
  reconstructionDate: '2026-11-25',
  evidenceType: 'vector-reconstruction',
  sourceGround: 'light'
}

export const resWestSpecimens = {
  program: 'reswest',
  assets: [
    {
      ...adEvidence,
      id: design,
      designLabel: 'ResWest badge',
      preferredReconstruction: 'reswest-colour-rebuilt',
      file: `${directory}/reswest-badge-advertisement.png`,
      format: 'png',
      isVector: false,
      evidenceType: 'publication-raster-crop',
      versionLabel: 'Colour scan',
      notes: 'The two-colour badge as printed in the booking advertisement. The provincial BC and Expo 86 marks appear on either side.',
      fidelityNote: 'Cropped from the supplied screenshot at its original resolution and colours.',
      extraction: { method: 'Cropped the 930 × 697 screenshot at pixel bounds (352, 382) to (513, 471).' },
      sha256: '280ebfc31138bce59873d52ebb595f3638c80ec4ac74fa85ec9c100889b28caf'
    },
    {
      ...adEvidence,
      ...rebuilt,
      id: 'reswest-colour-rebuilt',
      file: `${directory}/reswest-badge-colour.svg`,
      versionLabel: 'Colour reconstruction',
      notes: 'White serif lettering with an enlarged W crosses the rule between the green and blue halves of the rounded badge.',
      fidelityNote: 'The badge and lettering were redrawn as Bézier paths, fitted to the advertisement crop. The colours are sampled approximations from the scan. The original typeface, artwork and ink specifications remain unknown.',
      sha256: '73b848183a4777bb225222801352988fee45552814438725c66ffc79666fd81f'
    },
    {
      ...brochureEvidence,
      ...rebuilt,
      id: 'reswest-one-colour-rebuilt',
      file: `${directory}/reswest-badge-one-colour.svg`,
      versionLabel: 'One-colour reconstruction',
      notes: 'The 1985 Expo 86 brochure uses the badge in one ink with the lettering and rule reversed out.',
      fidelityNote: 'Uses the colour redraw’s outlines with both badge halves in a dark ink, following the dated brochure scan. The scan preserves the printed specimen.',
      sha256: 'd4726b7a124a10ea881c61c2f22300bd8a5b70d0cc288db1e0641c7314652d53'
    },
    {
      ...brochureEvidence,
      id: 'reswest-brochure-print',
      variantOf: design,
      file: `${directory}/reswest-badge-brochure.png`,
      format: 'png',
      isVector: false,
      evidenceType: 'publication-raster-crop',
      versionLabel: '1985 brochure scan',
      notes: 'The one-colour badge printed beside the booking caption and Vancouver telephone number on the 1985 Expo brochure.',
      fidelityNote: 'Crop from the PDF scan at native resolution.',
      extraction: { method: 'Extracted JPEG object 15 with pdfimages, then cropped at pixel bounds (360, 905) to (412, 935).' },
      sha256: '3825ba5ac1b12318d7189c75a807f9f82a236c416ed5bf936d9d26ecfd08b0d2'
    }
  ]
}

export const resWestBadgeEra = {
  id: 'reswest-reservation-service',
  status: 'held',
  years: '1985 brochure · Expo 86-era advertisement',
  label: 'A single booking service for B.C.',
  note: 'The fair’s brochure directed travellers to ResWest for accommodation reservations across B.C. for a single $5 charge. The service also handled Expo’s Host Home bookings. The colour advertisement shows the ResWest badge alongside the provincial BC flag signature and Expo 86 mark.',
  applicability: {
    kind: 'dated_specimen',
    years: '1985',
    note: 'The dated brochure establishes the badge in print. The colour advertisement’s issue and the badge’s adoption date remain unknown.'
  },
  sources: [...RESWEST_SOURCES, { title: 'ResWest booking advertisement, supplied screenshot', url: advertisement }]
}
