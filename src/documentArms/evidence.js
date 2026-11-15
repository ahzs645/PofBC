// Evidence about particular specimens, separate from the renderer's provisional geometry.
// A document's approval/publication date is not automatically its engraving's creation date.
export const DOCUMENT_ARMS_RESEARCH_URL = 'https://github.com/ahzs645/PofBC/blob/main/research/identity/document-arms-2026-11-14/README.md'

const OIC_1121 = 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978'
const MINING_1954 = 'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf'

export const DOCUMENT_ARMS_SPECIMENS = {
  'mining-1954-title': {
    label: '1954 mining booklet · title page',
    status: 'Verified period specimen',
    date: 'Published 1954 · PDF page 2',
    description: 'Arms above the Queen’s Printer imprint. The title page and cover of this same booklet use visibly different engravings.',
    limitation: 'A dated printed example, not a reproduction master or a rule for other documents.',
    sourceUrl: `${MINING_1954}#page=2`,
    sourceLabel: 'Department of Mines · original PDF, page 2',
    alt: 'The narrower arms engraving on the 1954 Mining in British Columbia title page, above the Don McDiarmid printer imprint and year.',
    fullAlt: 'Complete title page of Mining in British Columbia, printed in 1954, with the arms and printer imprint near the bottom.',
    page: 2,
  },
  'mining-1954-cover': {
    label: '1954 mining booklet · cover',
    status: 'Verified period specimen',
    date: 'Published 1954 · PDF page 1',
    description: 'The wider arms engraving on the cover differs from the inner title page in its shield, sun and motto scroll.',
    limitation: 'This variation within one publication is evidence of more than one drawing, not a universal historical logo template.',
    sourceUrl: `${MINING_1954}#page=1`,
    sourceLabel: 'Department of Mines · original PDF, page 1',
    alt: 'The wider arms engraving on the cover of the 1954 Mining in British Columbia booklet, above its printer imprint.',
    fullAlt: 'Complete grey cover of Mining in British Columbia, dated 1954, with a border and arms above the printer imprint.',
    page: 1,
  },
  'official-1906': {
    label: '1906 design · provincial history illustration',
    status: 'Official historical illustration',
    date: '1906 design · illustration date not established',
    description: 'The Province’s history page identifies this as the arms after the 1906 modifications. Only the shield and motto were granted in 1906; the crest and supporters continued in use.',
    limitation: 'The supplied official image is 200 × 186 pixels. It does not establish a detailed printer’s master, historical typography or colour specifications.',
    sourceUrl: 'https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms',
    sourceLabel: 'Province of British Columbia · history of the arms',
    alt: 'The colour arms illustration labelled by the Province as the arms after the 1906 modifications.',
  },
  'oic-1121-heading': {
    label: 'OIC 1121/1978 · government heading',
    status: 'Verified period specimen',
    date: 'Approved 4 May 1978 · PDF page 1',
    description: 'The full BC Laws record verifies the supplied crop: arms above the government caption, order number 1121 and the approval date.',
    limitation: 'This verifies an example of use. The exact engraving and original lettering remain unidentified.',
    sourceUrl: `${OIC_1121}#page=1`,
    sourceLabel: 'BC Laws · original PDF, page 1',
    alt: 'Original OIC 1121 heading showing the arms, the two-line government caption and approval on 4 May 1978.',
    fullAlt: 'Complete first page of Order in Council 1121/1978, approved 4 May 1978, with the government heading and signatures.',
    page: 1,
  },
  'oic-832-heading': {
    label: 'OIC 832/1978 · government heading',
    status: 'Verified period specimen',
    date: 'Approved 6 April 1978 · PDF page 1',
    description: 'A second dated order carries the same kind of arms-over-government-caption arrangement.',
    limitation: 'This is a separate order from the supplied 1121 reference. It does not establish a single government-wide template.',
    sourceUrl: 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0832_1978#page=1',
    sourceLabel: 'BC Laws · original PDF, page 1',
    alt: 'Original OIC 832 heading with the arms, government caption and approval on 6 April 1978.',
    fullAlt: 'Complete first page of Order in Council 832/1978, approved 6 April 1978.',
    page: 1,
  },
  'oic-1121-grant': {
    label: 'OIC 1121/1978 · Crown-grant map',
    status: 'Verified period specimen',
    date: 'Attached to the order approved 4 May 1978 · PDF page 4',
    description: 'The supplied blackletter crop is identified on this map attachment: British Columbia, Crown Grant No. 8498, Kootenay District and Provincial Rental Housing Corporation.',
    limitation: 'The map sheet’s creation date and the grant’s issue date are not established. The 1978 date belongs to the order containing it.',
    sourceUrl: `${OIC_1121}#page=4`,
    sourceLabel: 'BC Laws · original PDF, page 4',
    alt: 'Blackletter British Columbia heading with the earlier arms, Crown Grant No. 8498 and the Kootenay District map caption.',
    fullAlt: 'Complete fourth page of OIC 1121/1978: a Kootenay District map attachment with the blackletter heading and Crown Grant No. 8498.',
    page: 4,
  },
  'supplied-split-serif': {
    label: 'Supplied split-serif heading',
    status: 'Supplied reference · source unresolved',
    date: 'Document date not established',
    description: 'BRITISH and COLUMBIA flank the arms, with the number 279 below. The supplied crop remains available unchanged.',
    limitation: 'The full document, date, engraving and exact typeface have not yet been identified.',
    alt: 'Supplied document crop with BRITISH and COLUMBIA in serif capitals beside the arms and number 279 below.',
  },
  'supplied-government': {
    label: 'Supplied government-heading crop',
    status: 'Supplied crop · original identified',
    date: 'OIC 1121/1978 · approved 4 May 1978',
    description: 'The original supplied image, now connected to page 1 of the full BC Laws record.',
    limitation: 'Kept unchanged for comparison with the independently retrieved PDF.',
    sourceUrl: `${OIC_1121}#page=1`,
    sourceLabel: 'BC Laws · matching original, page 1',
    alt: 'The original supplied government-heading crop for OIC 1121, showing approval on 4 May 1978.',
  },
  'supplied-blackletter': {
    label: 'Supplied Crown-grant crop',
    status: 'Supplied crop · original identified',
    date: 'Located in OIC 1121/1978 · PDF page 4',
    description: 'The original supplied image, now connected to the Crown-grant map attachment in the full order.',
    limitation: 'The map sheet’s creation date and the grant’s issue date remain unestablished.',
    sourceUrl: `${OIC_1121}#page=4`,
    sourceLabel: 'BC Laws · matching original, page 4',
    alt: 'The original supplied crop of British Columbia in blackletter around the arms, with Crown Grant No. 8498.',
  },
}

export const DOCUMENT_ARMS_REFERENCES = {
  emblem: ['mining-1954-title', 'mining-1954-cover', 'official-1906'],
  'split-serif': ['supplied-split-serif'],
  government: ['oic-1121-heading', 'oic-832-heading', 'supplied-government'],
  'split-blackletter': ['oic-1121-grant', 'supplied-blackletter'],
}

export function documentArmsReferences(layout) {
  return (DOCUMENT_ARMS_REFERENCES[layout] || DOCUMENT_ARMS_REFERENCES['split-serif'])
    .map((id) => ({ id, ...DOCUMENT_ARMS_SPECIMENS[id] }))
}
