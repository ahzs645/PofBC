import { buyBCDesigns, buyBCSpecimens, buyBCStandards } from '../gallery/buyBC.js'

const sources = [
  { id: 'standards', title: 'Buy BC Graphic Standards', publisher: 'Province of British Columbia', url: buyBCStandards,
    description: 'The supplied nine-page guide matches the copy published by Buy BC. Its internal title refers to 2019 and its PDF creation date is April 12, 2023. The guide gives no adoption date for the artwork.' },
  { id: 'month', title: '“Eat well, live well” is theme for Buy BC Month', date: 'September 2000', url: 'https://archive.news.gov.bc.ca/releases/archive/pre2001/2000/4013.asp' },
  { id: 'handover', title: 'Ag Council brings new expertise in Buy BC handover', date: 'September 21, 2002', url: 'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2002AGF0019-000822.htm' },
  { id: 'dining', title: 'Make your reservation to Buy BC: Eat Drink Local', date: 'October 11, 2017', url: 'https://news.gov.bc.ca/releases/2017AGRI0055-001719' },
  { id: 'relaunch', title: 'Province relaunches Buy BC to connect people to made-in-B.C. products', date: 'June 23, 2018', url: 'https://news.gov.bc.ca/releases/2018AGRI0048-001274' },
  { id: 'strategy', title: 'Buy BC 3-Year Strategic Plan', date: '2024–2027', url: 'https://buybc.gov.bc.ca/app/uploads/sites/386/2025/01/BuyBC_3YearStrategicPlan2024_2027.pdf' }
]

const timeline = [
  { id: 'launch', date: '1993', title: 'Buy BC begins', description: 'The Province established a year-round program to help shoppers recognize B.C. food and beverages, from seafood caught on the coast to fruit grown in the Interior.', sourceRefs: [{ sourceId: 'month' }] },
  { id: 'buy-bc-month', date: 'September 2000', title: 'Buy BC Month reaches grocery aisles', description: 'The sixth annual campaign paired Team BC athletes with local food. Grocery stores received posters and displays, and the Province announced a website and television commercial.', sourceRefs: [{ sourceId: 'month' }] },
  { id: 'withdrawal', date: 'July 2001', title: 'The Province withdraws', description: 'The government withdrew from the program. Industry groups and the Province then sought a way to keep it running without provincial funding.', sourceRefs: [{ sourceId: 'handover' }] },
  { id: 'council', date: 'September 21, 2002', title: 'BC Agriculture Council takes on management', description: 'An agreement gave the Council an exclusive five-year licence to display the Buy BC graphics. Both parties could agree to a second five-year term.', sourceRefs: [{ sourceId: 'handover' }] },
  { id: 'eat-drink-local', date: 'October 11, 2017', title: 'Eat Drink Local announces the logo’s return', description: 'At a Kelowna kickoff, the Ministry of Agriculture and the restaurant industry invited chefs and producers to join a dining campaign built around B.C. ingredients.', sourceRefs: [{ sourceId: 'dining' }] },
  { id: 'partnership', date: 'June 23, 2018', title: 'Buy BC relaunches at Moss Street Market', description: 'At the Victoria market, the Province announced three years of marketing funding through the Investment Agriculture Foundation of British Columbia. Producers could also license the logo for their products without applying for funding.', sourceRefs: [{ sourceId: 'relaunch' }] },
  { id: 'graphic-standards', date: 'April 2023', title: 'The graphic standards document the logo family', description: 'The supplied PDF was created in April 2023. It shows vertical and horizontal lettering arrangements, four print colourways and an emblem for small screens.', sourceRefs: [{ sourceId: 'standards', page: 3 }, { sourceId: 'standards', page: 4 }, { sourceId: 'standards', page: 8 }] },
  { id: 'strategy', date: '2024–2027', title: 'A three-year plan for grocery stores', description: 'The program set goals to get more Buy BC products into stores, make them easier to spot on shelves and encourage shoppers to choose them.', sourceRefs: [{ sourceId: 'strategy', page: 2 }] }
]

const marks = buyBCDesigns.map(({ title, layout, description, page, usagePage }) => {
  const id = `buy-bc-${layout}-colour`
  const images = buyBCSpecimens.assets.filter((asset) => asset.id === id || asset.variantOf === id).map((asset) => ({
    file: asset.file, label: asset.versionLabel, alt: `Buy BC ${title.toLowerCase()} in ${asset.versionLabel.toLowerCase()}`,
    caption: asset.sourceLocator, darkBackground: asset.darkBackground,
    sourceId: 'standards', sourcePage: page, evidenceType: asset.evidenceType, date: asset.sourceDate, dateLabel: 'PDF creation date'
  }))
  return { id, title, kind: 'program-identity', description, images, artworkStatus: 'native-vector-held',
    sourceRefs: [page, ...(usagePage ? [usagePage] : [])].map((number) => ({ sourceId: 'standards', page: number })) }
})

export const buyBCDetail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'The Buy BC mark',
      description: 'The graphic standards specify full colour for general use, blue for single-colour printing, black for black-and-white printing and white for dark backgrounds.', records: marks },
    { id: 'timeline', label: 'Timeline', type: 'timeline', title: 'Buy BC program history', records: timeline },
    { id: 'sources', label: 'Sources', type: 'sources', records: sources }
  ],
  relatedLinks: [
    { label: 'Buy BC in the government history', to: { view: 'government', node: 'sub-buy-bc' } },
    { label: 'Buy BC in the logo gallery', to: { view: 'gallery', logos: 'specimens-buy-bc' } },
    { label: 'BC Agriculture Council', to: { view: 'gallery', subject: 'bc-agriculture-council' } },
    { label: 'Investment Agriculture Foundation of British Columbia', to: { view: 'gallery', subject: 'investment-agriculture-foundation' } }
  ]
})
