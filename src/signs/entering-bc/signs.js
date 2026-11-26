const manual = {
  label: 'B.C. Ministry of Transportation and Highways, Manual of Standard Traffic Signs & Pavement Markings, September 2000, p. 6.12',
  href: 'https://www2.gov.bc.ca/assets/gov/driving-and-transportation/transportation-infrastructure/engineering-standards-and-guidelines/traffic-engineering-and-safety/traffic-engineering/traffic-signs-and-pavement-markings/manual_signs_pavement_marking.pdf#page=162'
}

const box = (x, y, w, h) => ({ x, y, w, h })

const trademark = 'The manual credits Tourism B.C. with the registered landscape graphic and “Super, Natural British Columbia” trademark and records permission for their use in the manual.'
const landscape = (bounds) => ({
  id: 'landscape', label: 'The landscape mark', box: bounds,
  lede: 'A yellow sun rises behind two green mountains. Two blue waves run beneath them.',
  blocks: [trademark]
})

const plates = [
  {
    id: 'i-180', title: 'I-180 · Welcomes You!', size: '240 × 240', view: box(79.74, 81.65, 49.56, 49.70),
    lede: 'The manual places this square welcome sign among the first signs travellers would see on a conventional highway entering British Columbia.',
    details: [
      landscape(box(86, 87, 37, 15)),
      { id: 'greeting', label: 'Welcomes You!', box: box(81, 121, 47, 8),
        lede: 'White script crosses a black band at the foot of the sign. Above it, the landscape and the province’s name are stacked on white.' }
    ]
  },
  {
    id: 'i-180x', title: 'I-180X · Welcomes You!', size: '490 × 180', view: box(48.77, 166.97, 123.74, 46.10),
    lede: 'The manual assigns this wide welcome sign to multi-lane highways. The landscape sits beside the blue tourism wordmark, leaving the lower half for the greeting.',
    details: [
      landscape(box(54, 173, 46, 18)),
      { id: 'greeting', label: 'Welcomes You!', box: box(80, 197, 62, 10),
        lede: 'The English greeting is centred beneath the landscape and wordmark in pale blue italic lettering.' }
    ]
  },
  {
    id: 'i-180b', title: 'I-180B · Welcomes You! / Bienvenue!', size: '488 × 305', view: box(22.01, 260.21, 193.10, 72.50),
    lede: 'The bilingual panel was reserved for monument-style signs in national parks, where the greeting appeared in English and French to meet federal language policy.',
    details: [
      landscape(box(30, 270, 71, 28)),
      { id: 'greeting', label: 'Welcomes You! / Bienvenue!', box: box(33, 308, 173, 13),
        lede: 'A slash separates the two greetings on a single line. Both use the same size, colour and italic lettering.' }
    ]
  },
  {
    id: 'i-181', title: 'I-181 · Seat belts', size: '180 × 90', view: box(61.67, 395.75, 99.14, 49.70),
    lede: 'The manual places this seat-belt reminder after the welcome sign. A seated figure on the left introduces four lines of condensed lettering.',
    details: [{ id: 'symbol', label: 'Seat-belt symbol', box: box(69, 401, 23, 39),
      lede: 'A white diagonal cuts across the black seated figure to show the shoulder belt.' }]
  },
  {
    id: 'i-182', title: 'I-182 · Thinkmetric', size: '210 × 120', view: box(55.79, 503.99, 120.02, 68.66),
    lede: 'At crossings from the United States, this sign followed the seat-belt reminder to tell drivers that British Columbia used metric units for speeds and distances.',
    details: [{ id: 'examples', label: 'The two speed signs', box: box(64, 525, 104, 44),
      lede: 'The brown panel pairs a 90 km/h maximum with the former 55 mph maximum. The word “WAS” connects the two miniature signs.' }]
  }
]

export const ENTRY_CARDS = Object.fromEntries(plates.map(({ id, title, view }) => [id, {
  id, title, view, series: 'entering-bc', when: 'September 2000',
  page: { w: 12, h: Number((12 * view.h / view.w).toFixed(3)) }
}]))

export const ENTRY_SIGNS = Object.fromEntries(plates.map(({ id, title, view, lede, size, details }) => {
  const blocks = [{ facts: [['Sign size listed in the manual', size + ' cm']] }]
  if (id.startsWith('i-180')) blocks.push(trademark)
  blocks.push({ sources: [manual] })
  const parts = { overview: { label: 'Whole sign', box: view, pad: 0.06,
    panel: { eyebrow: 'Entering British Columbia · September 2000', heading: title, lede, blocks } } }
  for (const detail of details) {
    parts[detail.id] = {
      label: detail.label, layer: '#' + id + '-' + detail.id, box: detail.box, pad: 0.12,
      panel: { eyebrow: id.toUpperCase(), heading: detail.label, lede: detail.lede, blocks: detail.blocks ?? [] }
    }
  }
  const regions = details.map((detail) => detail.id)
  return [id, { id, parts, regions, order: ['overview', ...regions], spotlight: { keep: [id + '-panel'] } }]
}))
