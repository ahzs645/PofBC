// The four identities on guide page 16 plus the other public-facing programs documented by FireSmart BC.
const cover = (slug, alt, page) => ({
  file: `identity-collected/firesmart-bc/${slug}-positive.svg`, alt,
  caption: `FireSmart BC Brand Guidelines, version two, page ${page} (July 2025)`
})

export const fireSmartParent = {
  id: 'firesmart-bc', title: 'FireSmart BC', subtitle: 'BC FireSmart Committee',
  summary: 'FireSmart BC brings residents, First Nations, local governments and fire services together to reduce wildfire risk. Its work ranges from assessing individual homes to helping whole neighbourhoods prepare together.',
  cover: cover('signature', 'Yellow flame surrounding a house beside the British Columbia FireSmart name', 5),
  tags: ['Wildfire prevention', 'Community programs', 'Logos', 'Timeline'],
  searchTerms: ['BCFSC', 'Ember the FireSmart Fox', 'Community Resiliency Investment', 'Home Partners', 'FireSmart Canada', 'Community FireSmart and Resiliency Collaboratives'],
  relatedBodyIds: ['sub-bc-wildfire-service']
}

export const fireSmartChildren = [
  {
    key: 'wildfire-mitigation', title: 'FireSmart BC Wildfire Mitigation Program',
    summary: 'A trained specialist assesses a home with its resident and identifies changes specific to the property. The program grew out of FireSmart Canada’s Home Partners Program.',
    searchTerms: ['WMP', 'Home Partners Program', 'Wildfire Mitigation Specialist', 'home assessment'],
    cover: cover('wildfire-mitigation', 'Red flame above a roof and house beside the Wildfire Mitigation Program name', 17)
  },
  {
    key: 'local-collective', title: 'Local FireSmart Collective Program',
    summary: 'Residents and community organizations work with a local representative on a shared assessment and action plan. The collective succeeds the national neighbourhood recognition program in B.C.',
    searchTerms: ['LFCP', 'FCNRP', 'FireSmart Canada Neighbourhood Recognition Program', 'BCAA'],
    cover: cover('local-collective', 'Ring of blue houses beside the Local FireSmart Collective Program name', 19)
  },
  {
    key: 'plant-program', title: 'FireSmart Plant Program',
    summary: 'Participating nurseries and garden centres use plant tags and signs to help shoppers identify fire-resistant plants. A landscaping guide and staff training support the advice given in stores.',
    searchTerms: ['Plant Tagging Program', 'landscaping', 'Plant and Hardware Program'],
    cover: cover('plant-program', 'Green shield with nested flames beside the FireSmart Plant Program name', 20)
  },
  {
    key: 'training-summit', title: 'Wildfire Resiliency and Training Summit',
    summary: 'FireSmart BC’s annual gathering combines a conference on community wildfire resilience with practical training for firefighters. The two events first met under the summit name in Vancouver in 2023.',
    searchTerms: ['WRTS', 'FireSmart BC Conference', 'Wildland-Urban Interface Symposium', 'Lynn Orstad'],
    cover: cover('training-summit', 'Gold and orange house framing a tree inside a flame beside the summit name', 22)
  },
  {
    key: 'education',
    cover: { file: 'initiatives/firesmart-bc/education.webp', alt: 'Ember and a child learning together', caption: 'Artwork from the FireSmart BC Education Program website' },
    title: 'FireSmart BC Education Program',
    summary: 'Teachers use lessons aligned with the B.C. curriculum to explore wildfire with students from kindergarten through Grade 12. Schools can also enter the provincial classroom contest.',
    searchTerms: ['classroom contest', 'K–12', 'school curriculum', 'Ember']
  },
  {
    key: 'farm-and-ranch',
    cover: { file: 'initiatives/firesmart-bc/farm.webp', alt: 'Illustrated farm with three assessment zones around a red barn', caption: 'Cover of FireSmart BC’s sample Farm & Ranch Assessment' },
    title: 'FireSmart BC Farm and Ranch Program',
    summary: 'Farmers and ranchers can request an assessment of agricultural buildings and the land around them. The assessor identifies priorities specific to the operation.',
    searchTerms: ['Farm & Ranch', 'agricultural buildings', 'farm assessments']
  },
  {
    key: 'library',
    cover: { file: 'initiatives/firesmart-bc/library.webp', alt: 'Book covers and entries from the Wildfire Resiliency Readers’ Kit', caption: 'First page of the Library Program’s reading catalogue' },
    title: 'FireSmart BC Library Program',
    summary: 'Libraries introduce children to wildfire preparedness through stories, reading lists and activities with Ember. The program began in the Thompson-Nicola region in summer 2022.',
    searchTerms: ['Wildfire Resiliency Readers’ Kit', 'Read with Ember', 'library literacy']
  }
].map((program) => ({
  ...program, parentId: fireSmartParent.id, id: `firesmart-bc-${program.key}`, subtitle: 'FireSmart BC',
  tags: ['Wildfire prevention', 'FireSmart BC']
}))

export const FIRE_SMART_INITIATIVES = [fireSmartParent, ...fireSmartChildren]
