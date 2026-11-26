export const ASI_ID = 'advanced-systems-institute-of-bc'
const name = 'Advanced Systems Institute of BC'
const dir = `identity-collected/${ASI_ID}/`
const archived = (title, timestamp, file) => ({
  title, url: `https://web.archive.org/web/${timestamp}id_/http://${file}`
})
export const ASI_SOURCES = {
  exchange2000: archived('ASI Exchange registration form, March 2000', '20000302125223', 'www.asi.bc.ca/asi/exchange/2000Reg.pdf'),
  website2000: archived('BC Advanced Systems Institute website, May 2000', '20000520123823', 'www.asi.bc.ca/asi/graphics/asi-small.gif'),
  guidelines: archived('ASI Germination Family of Funds program guide', '20030721000541', 'asi.bc.ca/pdfs/PDF__ATIF_Guidelines.pdf'),
  anniversary: archived('ASI website, fifteenth-anniversary graphic, June 2001', '20010603175738', 'www.asi.bc.ca/home/logo.gif'),
  press: archived('ASI Exchange news release, January 14, 2003', '20030717142211', 'asi.bc.ca/news/press_releases/ASI_Jan1403_Exchange.pdf'),
  exchange2003: archived('Guide to the ASI Exchange 2003', '20030310134643', 'asiexchange.com/guide_2003.pdf'),
  board: archived('ASI board appointments, June 23, 2003', '20030718064936', 'asi.bc.ca/news/press_releases/ASI_Jun1903_Brd.pdf'),
  newsletter: archived('ASI LINX, issue 42, July 2003', '20030809013335', 'www.asi.bc.ca/pdfs/LINX_42.pdf'),
  header: archived('ASI website masthead, November 2003', '20031112105514', 'www.asi.bc.ca/images/asilogo.jpg'),
  logoPage: archived('ASI’s corporate logo page, December 2003', '20031222134747', 'www.asi.bc.ca/logos.html'),
  merger: {
    title: 'Province announces the merger, April 23, 2004',
    url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2004sbed0012-000273.htm'
  },
  letter: {
    title: 'ASI letter to the University of Victoria, October 29, 2002',
    url: 'https://webhome.cs.uvic.ca/~hausi/sedp/BSENG-DPRC-Nov8.pdf#page=38'
  },
  report: {
    title: 'Rocket Builders, Commercialization Success in Early Stage Technology Companies, credits',
    url: 'https://static1.squarespace.com/static/528292afe4b09330e9751c95/t/52ab35dce4b00ea3a8f3bec5/1386952156282/RB_Commercialization_June2004-FInal.pdf#page=2'
  },
  studio: {
    title: 'NextPhase Strategy, ASI identity portfolio',
    url: 'https://nextphasestrategy.com/advanced-systems-institute-of-bc/'
  }
}
const note = 'Founded in 1986, ASI was a nonprofit foundation that funded technology development, mentored early-stage companies and brought researchers and industry together. In 2004 it merged with the Innovation and Science Council of British Columbia to form the BC Innovation Council.'
const nextAction = 'Seek source vectors for the widely spaced letterhead initials, anniversary lettering and full-name three-figure signature. The redesign date is still open.'
export const ASI_SUBJECT = {
  id: ASI_ID, label: name, name, kind: 'nonprofit-agency', graphNode: null,
  family: 'innovation-training', scope: 'core', priority: 2, salaryEmployers: [],
  aliases: ['ASI', 'BC Advanced Systems Institute', 'Advanced Systems Institute of British Columbia'],
  collectionIds: [`collected-${ASI_ID}`], sources: Object.values(ASI_SOURCES), note, nextAction,
  relations: [{ subject: 'bc-innovation-council', type: 'predecessor-of', label: 'Merger partner in October 2004' }]
}

const raster = { format: 'png', isVector: false, reconstruction: false, observedDate: '2026-11-25' }
const letter = {
  ...raster, publisher: 'BC Advanced Systems Institute', sourceDate: '2002-10-29',
  sourcePage: ASI_SOURCES.letter.url, evidenceType: 'published-raster-extraction',
  downloads: [{ file: dir + '2002-letter.pdf', label: 'Download ASI letter (PDF)' }]
}
const institute = 'Advanced Systems Institute of BC'
const published = { ...raster, publisher: institute, evidenceType: 'published-raster-extraction' }
const vector = { ...published, format: 'svg', isVector: true, evidenceType: 'native-pdf-vector-extraction', sourceGround: 'light' }
export const ASI_COLLECTION = {
  id: ASI_ID, name, graphNode: null, historyId: ASI_ID, kind: 'nonprofit-agency',
  current: false, from: 1986, to: 2004, status: 'asset-collected', notes: note, nextAction,
  cover: 'asi-nextphase',
  assets: [
    {
      ...vector, id: 'asi-exchange-square', label: 'Square emblem over tall ASI initials', designLabel: 'Square emblem over tall ASI initials',
      versionLabel: 'Black and grey (SVG)', file: dir + 'exchange-square-2000.svg', sourceDate: '2000-03',
      sourcePage: ASI_SOURCES.exchange2000.url, sourceLocator: 'Page 1, presenter panel to the right of the ASI Exchange 2000 banner',
      notes: 'A black square breaks into triangles above three tall initials. The registration form for the March 14, 2000 Exchange prints the triangles in grey. The 2003 event guide uses magenta.',
      fidelityNote: 'Eight original filled paths include the lettering. The surrounding registration form is omitted.',
      extraction: { method: 'MuPDF SVG export of the eight emblem and letter paths', page: 1, pdfBounds: [440, 35, 460, 69] },
      downloads: [{ file: dir + 'exchange-registration-2000.pdf', label: 'Download registration form (PDF)' }],
      sha256: '3de328f1e8068e691939a022c8b21601fc9c7c13b9d4c8dbfdd2fa8606d7df04'
    },
    {
      ...published, id: 'asi-exchange-square-magenta', variantOf: 'asi-exchange-square', label: 'ASI Exchange presenter in colour',
      versionLabel: 'Black and magenta (PNG)', file: dir + 'exchange-square-colour.png', sourceDate: '2003-03',
      sourcePage: ASI_SOURCES.exchange2003.url, sourceLocator: 'Page 2, Presented by header, right end of the embedded banner',
      notes: 'The guide for the March 11 Exchange prints both the triangles and the tall ASI initials in magenta.',
      extraction: { method: 'Original embedded RGB image cropped at native resolution', page: 2, pixelBounds: [550, 0, 655, 181] },
      sha256: 'bc4b64834c37113392930c6db1bef2ebd7fe480c9bf6768c74e014118bfc2c44'
    },
    {
      ...published, id: 'asi-stepped-name', label: 'BC Advanced Systems Institute with stepped name',
      file: dir + 'stepped-name-2000.gif', format: 'gif', sourceDate: '2000-05-20', sourcePage: ASI_SOURCES.website2000.url,
      sourceLocator: 'ASI website, asi/graphics/asi-small.gif', evidenceType: 'official-website-raster',
      notes: 'The three lines step down from left to right, with A, S and I emphasized. A magenta rule underlines the name beside the square emblem.',
      fidelityNote: 'Original 177 × 75 pixel GIF from the institute’s website.', dateNote: 'The date is the archived capture.',
      sha256: '42b6dc4710fe8b93def66bfebd0b9ca310d04f08052f3aca3fe6aee6cb362e14'
    },
    {
      ...published, id: 'asi-letterhead', label: 'Square emblem over widely spaced ASI initials', designLabel: 'Square emblem over widely spaced ASI initials',
      versionLabel: 'Program guide in colour (PNG)', file: dir + 'letterhead-colour.png', sourceDate: '2000-12',
      sourcePage: ASI_SOURCES.guidelines.url, sourceLocator: 'ASI Guide to the Programs, Germination Family of Funds, page 1, upper right',
      notes: 'Magenta triangles break away from the upper-right corner of the black square. The small, widely spaced initials identify the same layout on the October 2002 letter.',
      extraction: { method: 'Original embedded 77 × 104 pixel colour image, PDF object 37', page: 1 },
      dateNote: 'The PDF creation date is December 19, 2000. The archived copy was captured in July 2003.',
      sha256: '81b7fb5e1a56c654c23dbf64572ad72310d64015ffd10f9d5868c2e4dbf80998'
    },
    {
      ...letter, id: 'asi-letterhead-scan', variantOf: 'asi-letterhead', versionLabel: 'October 2002 letter (PNG)',
      label: 'ASI letterhead emblem', file: dir + 'letterhead.png',
      sourceLocator: 'University of Victoria software engineering proposal, PDF page 38, upper left',
      notes: 'The monochrome letter reproduces the square-and-triangles emblem above small, widely spaced initials.',
      extraction: { method: 'Embedded page image cropped at original resolution', pixelBounds: [322, 218, 447, 417] },
      fidelityNote: 'Original grayscale pixels from the 300 dpi letter scan. The fine pattern is faint in the source.',
      sha256: '037c5d4073594fb9d0dc1e260191a289a434a9c2880d31e876f82149c3b917c0'
    },
    {
      ...published, id: 'asi-anniversary-web', label: 'ASI 15th anniversary, 1986–2001', file: dir + 'anniversary-web.gif', format: 'gif',
      preview: dir + 'anniversary-web.png', sourceDate: '2001-06-03', sourcePage: ASI_SOURCES.anniversary.url,
      sourceLocator: 'ASI website, home/logo.gif', evidenceType: 'official-website-raster',
      notes: 'The outlined number 15 surrounds ASI and the years 1986 and 2001. Pink triangles fill the top of the 5. The October 2002 letter pairs the anniversary emblem with a separate caption.',
      fidelityNote: 'The original GIF is available to download. The preview crops a horizontal page rule below the emblem.',
      dateNote: 'The date is the archived capture.', sha256: '4771f6417f458c94cd5f1b89232ce5a8df649667deea4785505e07b2d873664b'
    },
    {
      ...letter, id: 'asi-fifteen-years', label: 'ASI fifteenth anniversary signature', file: dir + 'anniversary.png',
      sourceLocator: 'University of Victoria software engineering proposal, PDF page 38, lower right',
      notes: 'The footer pairs the initials and the years 1986 and 2001 with the words “Fifteen years building BC’s high technology sector.” The letter is dated October 2002.',
      extraction: { method: 'Embedded page image cropped at original resolution', pixelBounds: [1777, 2961, 2531, 3198] },
      fidelityNote: 'Original grayscale pixels from the letter scan, including the anniversary caption.',
      sha256: 'fbfdc36c2d232f1a18dd4a4132ca0e03cd529eadc5ad2e2245a2c05fd67aec99'
    },
    {
      ...published, id: 'asi-press-square', label: 'Magenta ASI initials beside the square emblem',
      file: dir + 'press-square.png', sourceDate: '2003-01-14', sourcePage: ASI_SOURCES.press.url,
      sourceLocator: 'Page 1, left end of news release masthead',
      notes: 'Magenta initials appear to the left of the black square and its dispersing triangles on ASI’s January 14 news release.',
      extraction: { method: 'Original embedded 100 × 43 pixel RGB image, PDF object 20', page: 1 },
      sha256: 'df525913cee641c4ddacb1b6289715010f8b0223cb0ed1700fcf93d7369d3c42'
    },
    {
      ...raster, id: 'asi-nextphase', preferredVector: 'asi-nextphase-linx-vector', designLabel: 'ASI three-figure logo',
      versionLabel: 'NextPhase portfolio (JPEG)', label: 'ASI three-figure logo', file: dir + 'asi-logo.jpg',
      format: 'jpg', preview: dir + 'asi-logo-preview.png', publisher: 'NextPhase Strategy', creator: 'NextPhase Strategy',
      sourcePage: ASI_SOURCES.studio.url, sourceUrl: 'https://nextphasestrategy.com/dexx/user_images/portfolio/asi_logo.jpg',
      sourceLocator: 'ASI client portfolio, first image, titled Logo', evidenceType: 'designer-published-raster',
      notes: 'Three figures form a triangular emblem beside the initials ASI. NextPhase identifies this design as part of its rebranding work for the institute.',
      dateNote: 'The design studio does not date this portfolio specimen. ASI published the initials-only design in June and July 2003.',
      fidelityNote: 'The download preserves the JPEG published by the design studio. The preview crops only the surrounding white margin.',
      sha256: '00bfa9546b7f9b2b483f264133df010b47b782bda9469880cea1867183d8f17d'
    },
    {
      ...vector, id: 'asi-nextphase-linx-vector', variantOf: 'asi-nextphase', label: 'ASI three-figure logo',
      versionLabel: 'ASI LINX newsletter (SVG)', file: dir + 'three-figure-2003.svg', creator: 'NextPhase Strategy',
      sourceDate: '2003-07', sourcePage: ASI_SOURCES.newsletter.url, sourceLocator: 'Issue 42, cover, below the institute’s mission statement',
      alsoSeen: [{ ...ASI_SOURCES.board, date: '2003-06-23' }],
      notes: 'Three figures form a triangular emblem beside the initials ASI. The institute printed this flat-colour design on its June 23 news release and on the cover of its July newsletter.',
      fidelityNote: 'Ten filled paths preserve the figures and outlined initials in the newsletter’s blue, green and lavender inks.',
      extraction: { method: 'MuPDF SVG export of the ten logo paths', page: 1, pdfBounds: [32, 290, 87, 314] },
      downloads: [{ file: dir + 'linx-42-2003.pdf', label: 'Download LINX issue 42 (PDF)' }],
      sha256: 'f8b56deb86e6030d4c64b5aa408d2a5f475faf85c5ea6437bc58b755cc120e6d'
    },
    {
      ...published, id: 'asi-full-name-2004', label: 'ASI with Advanced Systems Institute of BC', designLabel: 'ASI with Advanced Systems Institute of BC',
      versionLabel: 'ASI website masthead (PNG)', file: dir + 'full-name-web.png', sourceDate: '2003-11-12',
      sourcePage: ASI_SOURCES.header.url, sourceLocator: 'ASI website, images/asilogo.jpg, below the slogan band',
      notes: 'The institute’s full name runs beneath the blue initials, with a shadow behind the lettering and figures. The same layout appears in the June 2004 Rocket Builders report.',
      fidelityNote: 'Native-resolution crop of the archived JPEG masthead.', dateNote: 'The date is the archived capture.',
      extraction: { method: 'Crop from the original 278 × 92 pixel website masthead', pixelBounds: [4, 41, 235, 92] },
      downloads: [{ file: dir + 'website-header-2003.jpg', label: 'Download original masthead (JPEG)' }],
      sha256: '6bd2d4ef33086f65ed3121fee6568c317254a9298a09cb014a5f738dfedcddcf'
    },
    {
      ...raster, id: 'asi-full-name-report', variantOf: 'asi-full-name-2004', versionLabel: 'Rocket Builders report (PNG)',
      label: 'ASI with Advanced Systems Institute of BC', file: dir + 'asi-full-name.png',
      publisher: 'Rocket Builders', sourceDate: '2004-06-25', sourcePage: ASI_SOURCES.report.url,
      sourceLocator: 'Final Summary, June 25, 2004, PDF page 2, Guidance and Direction credit',
      notes: 'The report credits ASI for directing the research. Its signature places the institute’s full name below the blue initials.',
      evidenceType: 'published-raster-extraction', extraction: { method: 'MuPDF raster crop at 144 dpi', page: 2, pdfBounds: [175, 334, 351, 379] },
      fidelityNote: 'The PDF stores the logo in small raster strips. The PNG renders those strips in place, including the full-name lettering.',
      downloads: [{ file: dir + '2004-credits.pdf', label: 'Download report credits (PDF)' }],
      sha256: 'c5ce364498c0ea1b07f72a59083169c93f3d7e922e329fe03879127e47db514b'
    }
  ]
}
