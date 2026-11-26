export const buyBCStandards = 'https://buybc.gov.bc.ca/app/uploads/sites/386/2024/03/BuyBC-Logo-Graphic-Standards.pdf'

const colours = { colour: 'Full colour', blue: 'Blue', black: 'Black', white: 'White' }
export const buyBCDesigns = [
  {
    layout: 'vertical', title: 'Vertical logo', page: 3, usagePage: 6,
    description: 'Yellow rays rise above green land and blue water. The red buyBC lettering sits below the emblem. The guide sets a minimum width of ¼ inch and uses the height of the lettering to measure clear space on each side.',
    versions: {
      colour: { sha256: '620bf8535132ba64c633281c18c4cae82eb552da09f3fea7c419f2195118263d', pdfBounds: [120.5, 111.625, 174.625, 188.875] },
      blue: { sha256: '73b4776860650883f29c86927ed76e7ab5678ad8a76d987bf63345f37528bed2', pdfBounds: [120.5, 224.0, 174.625, 301.375] },
      black: { sha256: '87578820e2f42b0dc04ce0167483a7afee9f68bf4e25292ce47c6ad26cb886fc', pdfBounds: [120.5, 332.375, 174.625, 409.75] },
      white: { sha256: '5401c363a7633c2018b89d384a1aa2fd7148ac06890c9a28d2391bcfd1bd0bfd', pdfBounds: [121.0, 441.0, 175.125, 518.375] }
    }
  },
  {
    layout: 'horizontal', title: 'Horizontal logo', page: 4, usagePage: 7,
    description: 'The lettering sits to the right of the emblem, with an italic lowercase buy beside a heavier uppercase BC. The guide sets a minimum width of ½ inch and measures clear space by the height of the capital letters.',
    versions: {
      colour: { sha256: '523ba0fcfe25f35362ed931dd17acadbe3270e7cbd154adf753370f4406c1dfc', pdfBounds: [89.75, 112.5, 223.0, 160.625] },
      blue: { sha256: 'ca5cedb7358fe315685805443a8fa370e6d887171758096aa272c35ca01c180e', pdfBounds: [89.75, 236.75, 223.0, 284.875] },
      black: { sha256: '8e10bb7143bfc5e81f381204741db4f84e1ba75d85750d32801c1b6c23c27437', pdfBounds: [89.75, 343.75, 223.0, 391.875] },
      white: { sha256: 'cfd6f762d3584c1e84e55a09e4c2d37a97ef5b209d3ea2c95b5a20a077d7e768', pdfBounds: [90.75, 456.625, 224.0, 504.75] }
    }
  },
  {
    layout: 'icon', title: 'Digital icon', page: 8,
    description: 'The sun, land and water appear without lettering at small sizes. The guide shows a 16-pixel browser icon and examples for Facebook, Instagram and Twitter. This vector comes from the Twitter example.',
    versions: { colour: { sha256: 'b1016153f837ab86d6c5e33fdb044cf7e0bcea4592e149a357a64e19e39e0623', pdfBounds: [71.875, 502.0, 122.0, 552.125] } }
  }
]

export const buyBCSpecimens = {
  program: 'buy-bc',
  assets: buyBCDesigns.flatMap(({ layout, title, page, description, versions }) =>
    Object.entries(versions).map(([colour, { sha256, pdfBounds }]) => ({
      id: `buy-bc-${layout}-${colour}`,
      ...(colour === 'colour' ? {} : { variantOf: `buy-bc-${layout}-colour` }),
      designLabel: title, label: title, versionLabel: colours[colour], darkBackground: colour === 'white',
      file: `identity-collected/buy-bc/${layout}-${colour}.svg`, format: 'svg', isVector: true, sha256,
      publisher: 'Province of British Columbia, Buy BC', evidenceType: 'native-pdf-vector-extraction',
      sourceDate: '2023-04-12', dateNote: 'Creation date embedded in the supplied PDF.',
      observedDate: '2026-11-25', sourceUrl: buyBCStandards, sourcePage: `${buyBCStandards}#page=${page}`,
      sourceLocator: `Buy BC Graphic Standards, PDF page ${page}, ${layout === 'icon' ? 'Twitter icon' : colours[colour] + ' example'}.`,
      extraction: { page, pdfBounds, method: 'Filled clipping paths isolated from the PyMuPDF SVG export.' },
      fidelity: 'source compared', notes: description,
      fidelityNote: 'The SVG uses the PDF’s native clipping paths as filled outlines in their original positions and colours. Each extraction was rendered and compared with its example in the guide.'
    })))
}
