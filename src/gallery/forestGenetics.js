const council = 'forest-genetics-council'
const society = 'bc-forest-genetics-society'
const company = 'select-seed'
const councilName = 'Forest Genetics Council of British Columbia'
const companyName = 'Select Seed Company Ltd.'
const home = 'https://forestgeneticsbc.ca/'
const newsletter = home + 'wp-content/uploads/2020/07/TICtalk-1999.pdf'
const earlyReport = home + 'wp-content/uploads/2020/07/FGCAR_2001_02_Abbr.pdf'
const terms = home + 'wp-content/uploads/2022/06/Terms-of-Reference-for-the-Forest-Genetics-Council-May-12-2022.pdf'
const governance = home + 'wp-content/uploads/2020/08/FGC-Genetics-Society-SelectSeed-Governance-Dec-2019-v3.pdf'
const companySite = 'https://www.selectseed.ca/'
const folder = 'identity-collected/'
const source = { title: 'Office of the Chief Forester, May 2022 terms of reference', url: terms }
const councilNote = 'The Chief Forester appoints this advisory council. The coastal and interior tree improvement councils were brought together in 1997. The Chief Forester endorsed the permanent council’s name and plans in July 1998. Its spring 1999 newsletter already carries the FGC initials and seven trees.'
const companyNote = 'SelectSeed was established in 1999. The BC Forest Genetics Society is its sole shareholder. The company helps supply seed for reforestation and provides program management to the Forest Genetics Council.'
const subject = { graphNode: null, priority: 2, salaryEmployers: [], family: 'institutions', scope: 'institution', collectionIds: [], relations: [] }

export const FOREST_GENETICS_SUBJECTS = [
  { ...subject, id: council, name: councilName, label: councilName, kind: 'advisory-council', scope: 'core',
    aliases: ['FGC'], collectionIds: ['collected-' + council],
    sources: [{ title: 'TICtalk, Spring 1999', url: newsletter }, source, { title: 'Council membership and technical committees', url: home + 'about/who-we-are/' }],
    note: councilNote, relations: [{ type: 'related-to', subject: society }],
    nextAction: 'Locate a design credit or dated adoption record for the seven-tree emblem.' },
  { ...subject, id: society, name: 'BC Forest Genetics Society', label: 'BC Forest Genetics Society', kind: 'nonprofit-society',
    aliases: ['British Columbia Forest Genetics Society'], sources: [source], identityStatus: 'distinct-unconfirmed',
    note: 'The Society was incorporated in 1999 so assets could be held and business undertaken in support of the council. It owns the shares of SelectSeed. The governance documents identify the council and the company visually. A separate Society mark remains unverified.',
    relations: [{ type: 'related-to', subject: council }], nextAction: 'Check signed annual statements and society letterhead for a distinct identity.' },
  { ...subject, id: company, name: companyName, label: 'SelectSeed', kind: 'corporate-subsidiary',
    aliases: ['Select Seed', 'Select Seed Co. Ltd.'], collectionIds: ['collected-' + company],
    sources: [source, { title: 'SelectSeed company profile', url: companySite }, { title: 'Governance paper, December 2019, PDF page 2', url: governance + '#page=2' }],
    relations: [{ type: 'owned-by', subject: society }], note: companyNote, nextAction: 'Find the first dated use of the pine-cone wordmark.' },
  { ...subject, id: 'forest-and-range-practices-advisory-council', name: 'Forest and Range Practices Advisory Council', label: 'Forest and Range Practices Advisory Council',
    kind: 'advisory-council', scope: 'core', aliases: ['Forest Practices Advisory Council'], identityStatus: 'distinct-unconfirmed',
    sources: [{ title: 'Forest and Range Practices Act, section 170', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/02069_01#section170' }],
    note: 'Section 170 continues and renames the Forest Practices Advisory Council. The Act establishes an institutional lead. A distinct logo has yet to be verified.',
    nextAction: 'Find council-authored advice or letterhead under either statutory name.' }
]

const shared = { observedDate: '2026-11-25', reconstruction: false }
const vector = { ...shared, format: 'svg', isVector: true, publisher: councilName }
const horizontal = {
  ...vector, evidenceType: 'official-inline-vector-extraction', sourcePage: home, sourceFile: 'Council website header',
  designLabel: 'FGC and seven trees with the council name',
  dateNote: 'The annual report dates the horizontal design. The recovered website vectors have no separate publication date.',
  alsoSeen: [{ label: 'Annual report 2001/2002, cover', source: earlyReport }],
  fidelityNote: 'The Council’s website supplies 41 original paths and seven tree polygons. The artwork contains no embedded picture, external font or live text.'
}

export const FOREST_GENETICS_BODIES = [
  { id: council, name: councilName, from: 1998, current: true, kind: 'advisory-council', graphNode: null, status: 'asset-collected', notes: councilNote,
    assets: [
      { ...horizontal, id: 'fgc-horizontal-green', label: 'FGC horizontal signature in dark green', versionLabel: 'Dark green', file: folder + council + '/horizontal-green.svg',
        notes: 'Dark green FGC initials and seven tapered trees sit beside the two-line council name.' },
      { ...horizontal, id: 'fgc-horizontal-white', specimenDate: '2001/02', label: 'FGC horizontal signature in white', versionLabel: 'White', variantOf: 'fgc-horizontal-green', darkBackground: true,
        file: folder + council + '/horizontal-white.svg', notes: 'The white-on-blue version shown on the 2001/02 report cover also appears as white artwork on the Council’s website.',
        downloads: [{ label: 'Download the 2001/02 cover detail (PNG)', file: folder + council + '/cover-2001-02.png' }] },
      { ...vector, id: 'fgc-stacked-white', label: 'Stacked FGC signature in white', file: folder + council + '/stacked-white.svg', darkBackground: true,
        sourcePage: home, sourceUrl: home + 'wp-content/themes/enfold-child/img/fgc-logo-stacked-white.svg', evidenceType: 'published-vector',
        notes: 'The Council also uses a compact layout with the name below the initials and trees.', fidelityNote: 'Standalone SVG from the Council’s website theme, retained as served.' },
      { ...vector, id: 'fgc-1999-tictalk', label: 'FGC in a black panel, Spring 1999', file: folder + council + '/tictalk-1999.svg', specimenDate: 'Spring 1999',
        sourcePage: newsletter, sourceLocator: 'Volume 2, number 1, page 1, masthead.', evidenceType: 'native-pdf-vector-extraction',
        downloads: [{ label: 'Download the 1999 print specimen (PNG)', file: folder + council + '/tictalk-1999.png' }],
        notes: 'A black panel encloses the white initials and trees. The full name sits to the right in black.',
        fidelityNote: 'The panel, trees and initials retain the native PDF paths. The PDF names unembedded Helvetica Bold for the two lines of type. MuPDF supplied its standard-font outlines. Ink overlap against the source rendering measured 96.5–97.9%.' }
    ] },
  { id: company, name: companyName, shortName: 'SelectSeed', from: 1999, current: true, kind: 'nonprofit-company', graphNode: null, status: 'asset-collected', notes: companyNote,
    assets: [
      { ...shared, id: 'selectseed-pinecone', label: 'SelectSeed pine-cone wordmark', designLabel: 'SelectSeed pine-cone wordmark', versionLabel: 'Published transparent PNG',
        file: folder + company + '/website.png', format: 'png', isVector: false, publisher: companyName, sourcePage: companySite, sourceUrl: companySite + 'wp-content/uploads/2020/09/select-seed-logo-1.png',
        evidenceType: 'published-raster', notes: 'The company’s blue wordmark ends in a stylized pine cone.', fidelityNote: 'Original 600 × 158 pixel transparent PNG served by the company.' },
      { ...shared, id: 'selectseed-2019-print', label: 'SelectSeed on the 2019 governance paper', versionLabel: 'December 2019 letterhead', variantOf: 'selectseed-pinecone',
        file: folder + company + '/letterhead-2019.jpg', format: 'jpg', isVector: false, specimenDate: '2019-12-08', publisher: 'Forest Genetics Council of BC',
        sourcePage: governance, sourceLocator: 'Draft v3, PDF page 2, upper-right letterhead.', evidenceType: 'published-raster',
        notes: 'The governance paper prints the company’s pine cone beside the Council’s separate FGC mark.', fidelityNote: 'The source PDF embeds the logo as a 333 × 83 pixel JPEG. The original JPEG stream is preserved.' }
    ] }
]
