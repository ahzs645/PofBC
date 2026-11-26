import { cleanPlacement } from './programPlacement.js'
import { programMarkVersion } from './programMarkVersions.js'
import layouts from './cleanbcSources.json' with { type: 'json' }

const publisher = 'Province of British Columbia'
const assetRoot = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/web-content-development-guides/corporate-identity-assets/'
const guide = assetRoot + 'visid-pdfs/guidelines_cleanbc-programmarks_april2024.pdf'
const kits = 'https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks#clean-bc-marks'
const forms = { endorsed: 'BC-endorsed marks', wordmark: 'Standalone wordmarks', special: 'Special lockups' }
const familyNote = 'The April 2024 guide pairs the base name, its tagline version and four named programs with the provincial signature and also shows each as a standalone wordmark. Two special lockups acknowledge provincial support or pair Better Buildings with Financeit.'
const notes = {
  endorsed: 'The provincial sun-and-mountains signature and a vertical rule precede the CleanBC lettering.',
  wordmark: 'The guide shows this wordmark at an independent scale when the provincial mark appears elsewhere in the same communication.',
  'supported-by': 'The horizontal provincial signature carries the words “Supported by the Province of British Columbia” beside the CleanBC tagline.',
  financeit: 'A second vertical rule separates the BC-endorsed Better Buildings signature from the Financeit logo.'
}

function versionsOf(layout) {
  const id = 'cleanbc-' + layout.id
  const label = layout.form === 'special' ? layout.name + ' lockup'
    : layout.name + (layout.form === 'endorsed' ? ' endorsed mark' : ' wordmark')
  const reverseId = layout.versions.some((v) => v.treatment === 'reverse') ? id + '-reverse' : null
  return layout.versions.map(({ treatment, member, printMember, method, page, locator, pdfBounds, sha256 }) => {
    const isDefault = treatment === 'positive'
    const examplePage = page ?? ({ endorsed: 2, wordmark: 3, special: 1 })[layout.form]
    const sourcePage = guide + '#page=' + examplePage
    const illustrated = isDefault || (treatment === 'reverse' && layout.form !== 'special')
    const monoExample = layout.id === 'tagline-wordmark' && ['white', 'black'].includes(treatment)
    return {
      ...programMarkVersion(isDefault ? id : id + '-' + treatment, id, treatment, reverseId),
      placement: cleanPlacement(layout, treatment, guide),
      ...(printMember ? { printMember } : {}),
      label, designLabel: label, format: 'svg', isVector: true, sha256,
      file: 'identity-collected/cleanbc/' + layout.id + '-' + treatment + '.svg',
      publisher, observedDate: '2026-11-25',
      notes: notes[layout.id] ?? notes[layout.form],
      ...(illustrated || monoExample ? { specimenDate: '2024-04' } : {}),
      ...(member ? {
        sourcePage: kits, sourceUrl: assetRoot + 'visid-files/' + layout.archive,
        sourceFile: member, sourceLocator: layout.archive,
        evidenceType: 'official-published-svg',
        fidelityNote: 'The original SVG was copied byte for byte from the provincial artwork kit. The lettering and symbols are vector paths.',
        ...(method ? {
          extraction: { method }, evidenceType: 'official-vector-master-conversion',
          fidelityNote: method === 'eps'
            ? 'The kit’s white EPS renders correctly. Ghostscript and pdftocairo converted its native paths to SVG. The separate SVG labelled solid white in the kit renders incorrectly.'
            : 'The kit’s SVG draws an opaque white rectangle over the entire white logo. This displayable source extraction removes that single rectangle and retains every logo path and fill.'
        } : {}),
        ...(illustrated || monoExample ? { alsoSeen: [{ label: 'April 2024 program marks guide', source: monoExample ? guide + '#page=4' : sourcePage }] } : {})
      } : {
        sourcePage, sourceLocator: 'PDF page ' + page + ', ' + locator,
        extraction: { pdfBounds }, evidenceType: 'native-pdf-vector-extraction',
        fidelityNote: 'PyMuPDF isolated the printed paths within the specimen bounds and exported them to SVG, preserving the outlines, fills and positions.'
      })
    }
  })
}

export const CLEANBC_BODY = {
  id: 'sub-cleanbc', graphNode: 'sub-cleanbc', name: 'CleanBC', kind: 'program', shelf: 'provincial-programs',
  from: 2018, current: true, status: 'asset-collected', cover: 'cleanbc-base-endorsed', notes: familyNote,
  assets: layouts.flatMap(versionsOf),
  artworkSections: Object.entries(forms).map(([form, label]) => ({
    id: 'cleanbc-' + form, label, marks: layouts.filter((l) => l.form === form).map((l) => 'cleanbc-' + l.id)
  }))
}

export const CLEANBC_SUBJECT = {
  id: 'sub-cleanbc', graphNode: 'sub-cleanbc', name: 'CleanBC', label: 'CleanBC', kind: 'service-brand',
  scope: 'core', family: 'provincial-programs', priority: 2, collectionIds: ['collected-sub-cleanbc'],
  aliases: ['Better Homes', 'Active Transportation', 'Better Buildings', 'Go Electric'], salaryEmployers: [],
  relations: [{ subject: 'stronger-bc', type: 'related-to', label: 'Economic-plan context in the provincial brand matrix' }],
  note: familyNote, nextAction: 'Locate the restricted tiny endorsed artwork and a publisher master for the Financeit lockup.',
  sources: [
    { title: 'CleanBC plan launch, December 5, 2018', url: 'https://news.gov.bc.ca/releases/2018PREM0088-002338' },
    { title: 'Guidelines for Use, CleanBC Program Marks, April 2024', url: guide },
    { title: 'Provincial artwork kits', url: kits }
  ]
}
