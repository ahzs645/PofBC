import specimens from './bearAwareSpecimens.json' with { type: 'json' }
import {
  bearAwareArchive, bearAwareFolder, bearAwareGalleryId, bearAwareMarkId, bearAwareReport,
  bearAwareWindowId, bearAwareWindowTitle
} from './bearAwareArtwork.js'

const sources = [
  {
    id: 'report', title: 'Revelstoke Bear Awareness Program, 1997 Final Report',
    shortTitle: '1997 Final Report', url: bearAwareReport, date: 'November 1997',
    description: 'Debby Robinson prepared the report for the Columbia Basin Fish & Wildlife Compensation Program and the B.C. Ministry of Environment, Lands and Parks.'
  },
  {
    id: 'catalogue', title: 'B.C. Ecological Reports Catalogue, report 40226',
    url: bearAwareArchive, description: 'The provincial catalogue lists the 1997 and 1998 final reports.'
  }
]

const topics = {
  'black-bear-range': 'Black bear range',
  'john-krebs': 'John Krebs',
  'grizzly-population': 'Grizzly bear population',
  'susan-hall': 'Susan Hall',
  'conservation-officer-budget': 'Conservation officer budget',
  'john-woods': 'John Woods',
  'future-bear-populations': 'Future bear populations',
  'bruce-mclellan': 'Bruce McLellan',
  'grizzly-reproduction': 'Grizzly reproduction',
  'cub-learning': 'How cubs learn'
}

const paperNames = { times: 'Times Review', unique: 'Unique' }
const printedPieces = {
  '01-we-are-bear-aware-window-sign': {
    id: bearAwareWindowId, kind: 'window-sign', title: bearAwareWindowTitle,
    description: 'Residents and businesses could earn this window sign by meeting their checklist criteria. The reconstruction redraws the lettering and paw and simplifies the sponsor marks.'
  },
  '02-business-checklist': { kind: 'checklist', title: 'Bear Aware Business Checklist' },
  '03-family-checklist': { kind: 'checklist', title: 'Bear Aware Family Checklist' }
}

const marks = {
  'be-bear-aware-paw-lockup': 'Be Bear Aware paw lockup',
  'bear-paw': 'Five-clawed paw',
  'walking-bear': 'Walking bear',
  'friends-mt-revelstoke-glacier': 'Friends of Mt. Revelstoke & Glacier crest',
  'columbia-basin-stacked': 'Columbia Basin Fish & Wildlife Compensation Program stacked signature',
  'columbia-basin-symbol': 'Columbia Basin Fish & Wildlife Compensation Program symbol',
  'columbia-basin-horizontal': 'Columbia Basin Fish & Wildlife Compensation Program horizontal signature',
  'columbia-basin-wordmark': 'Columbia Basin Fish & Wildlife Compensation Program wordmark',
  'bc-hydro-historic': 'BC Hydro signature on the window sign',
  'bc-environment-historic': 'BC Environment signature on the window sign'
}

const stemOf = (file) => file.split('/').at(-1).replace(/\.svg$/, '')

const specimensOf = (specimen, title) => {
  const evidence = { sourceId: 'report', sourcePage: specimen.page, alt: title }
  return [
    {
      ...evidence, file: bearAwareFolder + specimen.scan, width: specimen.scanWidth, height: specimen.scanHeight,
      label: 'Original scan', caption: 'Original campaign artwork as reproduced in the 1997 report.',
      evidenceType: 'printed-source-crop', downloadLabel: 'original scan'
    },
    {
      ...evidence, file: bearAwareFolder + specimen.file, width: specimen.width, height: specimen.height,
      label: 'SVG reconstruction', caption: 'Modern vector reconstruction from the report scan.',
      evidenceType: 'vector-reconstruction'
    }
  ]
}

const compositionRecord = (specimen) => {
  const stem = stemOf(specimen.file)
  const ad = stem.match(/^(times|unique)-(\d+)-(.+)$/)
  const large = stem.match(/^campaign-large-(times|unique)-(\d{4}-\d{2}-\d{2})$/)
  const paper = paperNames[(ad ?? large)?.[1]]
  const record = printedPieces[stem] ?? {
    kind: 'newspaper-ad',
    title: ad ? topics[ad[3]] + ' · ' + paper + ' ' + Number(ad[2]) : 'We’re so nice to bears it kills them · ' + paper
  }
  const date = large?.[2] ?? specimen.source.match(/\b\d{4}-\d{2}-\d{2}(?:\?| \(faint annotation\)| or 30 \(annotation\))?/)?.[0]
  const images = specimensOf(specimen, record.title)
  if (date) {
    for (const image of images) {
      if (date.length === 10) image.date = date
      image.dateLabel = date.length === 10 ? paper + ' publication date' : paper + ' · ' + date
    }
  }
  return {
    id: stem, description: specimen.notes, ...record, compareSpecimens: true, images
  }
}

const componentRecord = (specimen) => {
  const id = stemOf(specimen.file)
  const title = marks[id]
  return {
    id, title, kind: 'campaign-artwork', compareSpecimens: true,
    description: id === bearAwareMarkId
      ? 'The paw and stacked “Be Bear Aware” lettering appear together on the checklist. The supplied SVG redraws the claw shapes and lettering by hand.'
      : 'The report crop shows the mark in its printed setting. The supplied SVG redraws its details by hand.',
    artworkNote: 'Report scan and vector reconstruction',
    images: specimensOf(specimen, title)
  }
}

const campaign = specimens.compositions.map(compositionRecord)
const components = specimens.components.map(componentRecord)

export const bearAwareDetail = (entry) => ({
  id: entry.id, title: entry.title, sources,
  hero: { title: entry.title, eyebrow: entry.subtitle, description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  relatedLinks: [
    { label: 'Window sign in Signs', to: { view: 'signs', sign: bearAwareWindowId } },
    { label: 'Window sign in Posters', to: { view: 'posters', poster: bearAwareWindowId } },
    { label: 'Be Bear Aware paw lockup in Gallery', to: { view: 'gallery', logos: bearAwareGalleryId, mark: bearAwareMarkId } }
  ],
  sections: [
    { id: 'sign-and-checklists', label: 'Sign & checklists', type: 'records',
      title: 'The window sign and its checklists', records: campaign.slice(0, 3) },
    { id: 'times-review', label: 'Times Review', type: 'records',
      title: 'Times Review newspaper ads', records: [campaign.at(-1), ...campaign.slice(3, 13)] },
    { id: 'unique', label: 'Unique', type: 'records',
      title: 'Unique newspaper ads', records: [campaign.at(-2), ...campaign.slice(13, 25)] },
    { id: 'marks', label: 'Marks', type: 'records', layout: 'marks',
      title: 'Campaign and sponsor marks', records: components },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Report and archive', records: sources }
  ]
})
