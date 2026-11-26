const designId = 'ecosystems-at-risk-badge'
const label = 'Ecosystems in British Columbia at Risk'
const directory = 'identity-collected/ecosystems-at-risk'
const estuaries = 'https://www.env.gov.bc.ca/wld/documents/Estuaries_brchr06.pdf'
const garryOak = 'https://www.env.gov.bc.ca/wld/documents/garryoak.pdf'

const badge = {
  label,
  designLabel: label,
  format: 'svg',
  isVector: true,
  evidenceType: 'native-pdf-vector-extraction',
  sourceGround: 'light',
  observedDate: '2026-11-25',
  fidelityNote: 'The angled frame, ink colours and lettering come from the original PDF artwork. The SVG preserves the paths and the outlined letters.'
}

export const ecosystemsAtRiskSpecimens = {
  program: 'ecosystems-at-risk',
  assets: [
    {
      ...badge,
      id: designId,
      file: `${directory}/estuaries-2006.svg`,
      versionLabel: 'Estuaries · 2006',
      publisher: 'British Columbia Ministry of Environment',
      sourceDate: '2006-03',
      sourceFile: 'Estuaries_brchr06.pdf',
      sourceUrl: estuaries,
      sourcePage: `${estuaries}#page=1`,
      sourceLocator: 'Estuaries in British Columbia, front panel at upper right. PDF page 1 in the ministry copy and page 2 in the Legislative Library copy.',
      extraction: {
        page: 1,
        pdfBounds: [1617.5, 645, 1743, 770],
        method: 'Cropped the cover in PDF page coordinates and converted it with pdftocairo -svg. Removed a white shape outside the badge.'
      },
      notes: 'Tall orange-red “AT RISK” lettering dominates the tilted badge, with the series name above it. The B.C. Conservation Data Centre used it on public brochures about vulnerable habitats, including Garry oak ecosystems in 1993 and estuaries in 2006. The estuaries brochure says they account for just 2.3 per cent of B.C.’s coastline and explains how development, invasive species and changes to river flows threaten habitat for fish and migratory birds.',
      sha256: 'fdc99400ebd95593d46e258b171fc84635f78599ed5c2e450e3d108dc7b90744'
    },
    {
      ...badge,
      id: 'ecosystems-at-risk-garry-oak-1993',
      variantOf: designId,
      file: `${directory}/garry-oak-1993.svg`,
      versionLabel: 'Garry oak · 1993',
      publisher: 'British Columbia Ministry of Environment, Lands and Parks',
      sourceDate: '1993-10',
      sourceFile: 'garryoak.pdf',
      sourceUrl: garryOak,
      sourcePage: `${garryOak}#page=1`,
      sourceLocator: 'Garry Oak Ecosystems, front cover at upper right. The colophon is dated October 1993.',
      extraction: {
        page: 1,
        pdfBounds: [466, 645, 564.5, 751],
        method: 'Cropped the cover in PDF page coordinates and converted it with pdftocairo -svg.'
      },
      notes: 'The October 1993 Garry Oak Ecosystems brochure uses the same lettering and arrangement, with a redder “AT RISK” and a slightly steeper tilt. It explains how agriculture and urban development had already reduced the Garry oak landscapes of southwestern B.C.',
      sha256: 'ffc258fa4c40f7963b313ade2731456ae4d984505ca882c65d5c9dff0104b80c'
    }
  ]
}
