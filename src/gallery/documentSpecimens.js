// Page numbers count the Legislative Library cover sheet. Dates describe the printed specimen.
const report = (handle, title, publisher, sourceDate) => ({
  sourcePage: 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/' + handle,
  publisher, title, sourceDate
})
export const reports = {
  boards: {
    title: 'Islands 2050 public open-house storyboards', publisher: 'Islands Trust', sourceDate: '2019-11',
    pageLabel: 'publisher PDF', sourcePage: 'https://webfiles.islandstrust.bc.ca/islands/local-trust-areas/01-Islands%202050/Public%20Engagement%20Phase%201%202019/2.Open-House-Storyboards_Islands-Trust-Area.pdf'
  },
  leading: report(311041, 'Annual Report 2004/05', 'Leading Edge British Columbia', '2004/05'),
  trust: report(284236, 'Annual Report 2005–2006', 'Islands Trust', '2005/06'),
  well: report(317668, 'Pumphandle Well Protection Plan', 'British Columbia, Environment Canada and the British Columbia Ground Water Association', '2005-12'),
  columbia: report(272585, 'Program Update, issue 14', 'Columbia Basin Fish & Wildlife Compensation Program', 'Spring 2006'),
  columbiaAnnual: report(218175, 'FWCP Annual Report, Columbia Region', 'Fish & Wildlife Compensation Program', '2013/14'),
  peace: report(218154, 'FWCP Annual Report, Peace Region', 'Fish & Wildlife Compensation Program', '2014/15'),
  injury: report(214409, 'BCIRPU Annual Report 2023–2024', 'BC Injury Research and Prevention Unit', '2023/24')
}

const specimen = (id, label, publication, page, locator, fidelityNote, sha256, options = {}) => {
  const { title, pageLabel = 'library PDF', ...source } = reports[publication]
  const { format = 'svg', containsRaster = format === 'png', ...details } = options
  return {
    id, label, file: 'identity-archival-reports/' + id + '.' + format, ...source, sourceUrl: source.sourcePage,
    sourceLocator: title + ', ' + pageLabel + ' p. ' + page + ', ' + locator + '.',
    format, containsRaster, isVector: format === 'svg' && !containsRaster,
    evidenceType: containsRaster ? (format === 'png' ? 'published-raster-extraction' : 'published-mixed-artwork') : 'native-pdf-vector-extraction',
    sourceGround: 'light', reconstruction: false, observedDate: '2026-11-27', sha256, fidelityNote,
    notes: label + '. ' + fidelityNote, ...details
  }
}

export const documentSpecimens = {
  leading: [
    specimen('leading-edge-2005', 'Orange frame around the Leading Edge British Columbia wordmark', 'leading', 37,
      'back cover, above the corporate office address', 'The original outlines carry the orange frame, white inset and two-colour lettering.', '9c6f00b83525dbbccc71c05a11151c053023270a4bc39fb01ea6ebf0507c4d16'),
    specimen('leading-edge-cover-2005', 'White Leading Edge wordmark with British Columbia below', 'leading', 2,
      'lower right of the front cover', 'The front cover uses white lettering without the frame. All 26 outlines come from the report.', 'e20334b22cbd5b60e00503bfcbbef7c5898c7a679f4349f1ecb1e21ce5a904b3', { sourceGround: 'dark' })
  ],
  trust: [
    specimen('islands-trust-2019', 'Islands Trust tree and shoreline on the Islands 2050 boards', 'boards', 3,
      'footer, beside the project signature', 'The November 2019 boards reproduce the Trust landscape in 26 native paths alongside a separate project identity.', '995db89d3ac5935ec2a3c4ac5c78f47a0961f3fb5d2ca9f8bb395d61fac74a40',
      { variantOf: 'islands-trust-2006', versionLabel: 'Colour · 2019 open-house boards' }),
    specimen('islands-trust-2006', 'Islands Trust tree, shoreline and wordmark', 'trust', 63,
      'upper of two logos on the back cover', 'Green and turquoise paths form the tree, shore, sun and hills above the black name.', '73f9d1af246deb011562b3c1f851bf54dfe561a15b1443be1c072002eb5482cf'),
    specimen('islands-trust-outline-2006', 'Islands Trust landscape in outline', 'trust', 2,
      'lower left on the front cover', 'The black outline treatment prints directly on the russet panel. The SVG retains the original strokes.', 'f7f590c3f489591d95d2be749ab8e0164f8072cda3401702629add9b3c871892',
      { variantOf: 'islands-trust-2006', versionLabel: 'Black outline · front cover' })
  ],
  islands2050: [specimen('islands-2050-2019', 'Islands 2050 · The Future of the Trust Area', 'boards', 3,
    'far left of the footer', 'The tree and islands interrupt the blue field behind the name. The original outlines retain the project tagline.', '35566e4197f565df37a197c5b9204a4878c0c6dbd053c1f2f3593e068ed484d4')],
  fund: [
    specimen('conservancy-landscape-2019', 'Islands Trust Conservancy landscape and native plants', 'boards', 3,
      'beside the Land Conservation section', 'The 72 original paths include the white foreground plants, island silhouette, water and full Conservancy name.', 'd0d9aa259aeb016ff81807d12650390078741ba9fbf7e0f129d64366b9b879c8'),
    specimen('islands-trust-fund-2006', 'Blue Islands Trust Fund landscape and name', 'trust', 63,
      'lower of two logos on the back cover', 'The Fund uses the shared landscape in blue with its own name below.', '7ce89d74ae64162270a8b0755af0b42c3f7ba69416602b63b26c4780a091b3b4'),
    specimen('islands-fund-tagline-2006', 'Islands Trust Fund · Creating a legacy of special places', 'trust', 33,
      'Trust Fund Board column', 'The report stores the signature and tagline as two 399-pixel-wide images. Their original pixels are positioned at the printed spacing.', '485c2b6b56ab6c7ffbe304aab7c6e4d6dc52fcaab3baf3ee3d054988e6ccdf69', { format: 'png' })
  ],
  water: [
    {
      id: 'bcgwa-website', label: 'Ground Water Development in cyan and burgundy', publisher: 'British Columbia Ground Water Association',
      file: 'identity-archival-reports/bcgwa-website.svg', sourcePage: 'https://www.bcgwa.org/',
      sourceUrl: 'https://www.bcgwa.org/wp-content/themes/UWD/images/bcgwa-logo-2.svg', sourceLocator: 'Association website header, bcgwa-logo-2.svg',
      format: 'svg', isVector: true, containsRaster: false, reconstruction: false, role: 'current',
      observedDate: '2026-11-27', evidenceType: 'official-website-vector', sourceGround: 'light', sha256: '75bdeda77a388fd4d9bcfdc54035cf4832b0251ae3423259f8370a0fe0d913e3',
      notes: 'The website uses cyan water and borehole shapes beside burgundy ground and lettering. The historical Pumphandle emblem has white outlines and lettering on black.',
      fidelityNote: 'The unmodified publisher SVG contains 59 paths, 12 polygons and one circle.'
    },
    specimen('bcgwa-pumphandle-2005', 'Ground Water Development · circular association emblem', 'well', 2,
      'rightmost of the three publisher signatures', 'White lettering, borehole and waves come from the PDF paths. The supplied standalone SVG shows the same emblem.', 'cb8882c2e851dde4eab4f2bed843609adf8d1c51e025fcd6e48ce486a90a8664', { sourceGround: 'dark' })
  ],
  wildlife: [
    specimen('fwcp-columbia-2006', 'Columbia Basin Fish & Wildlife Compensation Program', 'columbia', 2,
      'left of the newsletter masthead', 'The ram, fish, mountains and outlined program name are isolated from the adjoining partnership paragraph.', '22a542d5a939f93d70e46c239dc5d5931f93e36e4bc80312733a32299119f8de'),
    specimen('fwcp-columbia-ten-years', 'Conserving & Enhancing Fish & Wildlife · 1995–2005', 'columbia', 2,
      'ten-year badge at upper right', 'The original PDF form combines outlines and raster shadows. Both survive in the SVG.', '11b44a237d1b978be046f57f54b6ade9b06a65e6b3c16ecedefaf5a288465382', {
        containsRaster: true,
        // The program's July 2006 backgrounder prints the same badge in the middle of its cover. The
        // file name dates it 24 July 2006; the PDF was made on 21 July 2006.
        alsoSeen: [{
          label: 'Backgrounder: An introduction to the Fish & Wildlife Compensation Program – Columbia Basin, cover (file backgrounder-2006-july-24.pdf)',
          source: 'https://web.archive.org/web/20100525010649/http://fwcp.ca:80/version2/info/media/backgrounder-2006-july-24.pdf#page=1',
          date: 'July 2006'
        }]
      }),
    specimen('fwcp-columbia-seal-2014', 'Circular fish, bear and mountain emblem', 'columbiaAnnual', 2,
      'centre of the front cover, above the canoes', 'The cover prints the circular inscription and wildlife outlines at reduced opacity over a photograph. The SVG retains the paths and their opacity.', '7a0b01d79330afddd6fe48cf2f9f91f5e090db8b56777307a02850f697b09770'),
    specimen('fwcp-peace-2015', 'FWCP initials and full name beside the wildlife emblem', 'peace', 2,
      'upper left on the front cover', 'The colour signature uses native green, blue and white paths. Page 15 repeats the signature in a small bitmap.', '7adf081f29c6dbc7627422cd1c17785242b3080fe3386edf02ae8bcc38a8a0ad')
  ],
  injury: [
    specimen('bcirpu-2024', 'BC Injury Research and Prevention Unit in orange and blue', 'injury', 55,
      'upper right on the back cover', 'The 37 coloured paths include the two-line descriptor. The unit also uses this signature in its website header.', '513ed06b3008bcc2735b3b9f58d0f42c74b24f1af064af85c6aa59b0a71f6f21'),
    specimen('bcirpu-anniversary-2024', 'BCIRPU 25th-anniversary silver seal', 'injury', 10,
      'anniversary symposium feature', 'A crop retains the metallic gradients, layered images and lettering documenting the 2023 symposium.', 'dbb05d0650f6ba8bbd8f870901e268d1bd36bd109393c0600664581c0adc9033', { format: 'png' })
  ],
  catt: [specimen('catt-2024', 'CATT · Concussion Awareness Training Tool', 'injury', 20,
    'bottom left of the resource panel', 'The acronym, full name, divider and head symbol retain their original vector geometry.', '0531dfcb2793fbac2659e990a649f34f8d65cc419faaa0c0a4cdd2389f5ec0a4')],
  psbs: [specimen('psbsbc-2024', 'Prevent Shaken Baby Syndrome · PSBSBC', 'injury', 20,
    'upper left of the resource panel', 'This image combines the overlapping colour separations at the resolution of the embedded wordmark.', 'de75d202b4cc86636fecbe29983aa252b43fbcd832b6b4798800d956940b5ccd', { format: 'png' })],
  active: [specimen('active-safe-central-2024', 'Active & Safe Central shield and wordmark', 'injury', 20,
    'middle left of the resource panel', 'The original 269 × 68 image includes the red and blue shield and two-line name.', 'a01d055d3f6be151ebcb2eaad8ec3ef338e60081116ca30411874578503cd99a', { format: 'png' })],
  cost: [specimen('cost-of-injury-2024', 'Cost of Injury · Presented by BCIRPU', 'injury', 20,
    'upper right of the resource panel', 'The original 179 × 66 image includes the blue ground and presenter credit.', '84d6724b1fd30a70cc8439e99444637329d56a235579f418da869c555d26cc51', { format: 'png' })],
  outside: [specimen('outside-play-2024', 'Outside Play green signature', 'injury', 20,
    'lower right of the resource panel', 'The original 120 × 55 image pairs the white child silhouette and lettering on green.', 'd35b8654419a1e6208564d8d5566b0f494a885745640284780f8ff2431dc3bb5', { format: 'png' })]
}
