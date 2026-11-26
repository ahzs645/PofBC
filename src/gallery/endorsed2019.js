import { endorsedPlacement } from './programPlacement.js'
import specimens from './endorsed2019Sources.json' with { type: 'json' }
import { programMarkVersion } from './programMarkVersions.js'

export const endorsedGuide = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/web-content-development-guides/corporate-identity-assets/visid-pdfs/bcid_use_of_endorsedmarks_2019.pdf'
const names = {
  lockup: 'BCProgram endorsed mark',
  wordmark: 'BCProgram standalone wordmark',
  province: 'Provincial mark in the 2019 guide'
}
const notes = {
  lockup: 'The guide uses BCProgram as example lettering for an endorsed program.',
  wordmark: 'The separate wordmark can be placed at its own scale when the provincial mark appears elsewhere.',
  province: 'Page 2 illustrates the provincial mark in six treatments for light and dark backgrounds.'
}

export const ENDORSED_2019 = {
  id: 'endorsed-marks-2019', name: 'BC endorsed marks · 2019 guide', kind: 'guide', graphNode: null, publicationDate: 'June 2019', shelf: 'provincial-programs',
  status: 'asset-collected', cover: 'endorsed-2019-lockup',
  notes: 'Examples of the joined program signature, separate wordmark and accompanying provincial mark from the June 2019 guidelines.',
  assets: specimens.map(({ layout, treatment, page, pdfBounds, sha256 }) => {
    const design = 'endorsed-2019-' + layout
    const id = treatment === 'positive' ? design : design + '-' + treatment
    return {
      ...programMarkVersion(id, design, treatment, layout !== 'wordmark' && design + '-reverse'),
      placement: endorsedPlacement(layout, treatment, endorsedGuide),
      label: names[layout], designLabel: names[layout], notes: notes[layout],
      format: 'svg', isVector: true, publisher: 'Province of British Columbia', sha256,
      file: 'identity-collected/endorsed-marks-2019/' + layout + '-' + treatment + '.svg',
      sourcePage: endorsedGuide + '#page=' + page, sourceLocator: 'Page ' + page + ', ' + names[layout],
      observedDate: '2026-11-25', specimenDate: '2019-06',
      evidenceType: 'native-pdf-vector-extraction', extraction: { pdfBounds },
      fidelityNote: 'PyMuPDF isolated the specimen within the recorded PDF bounds and exported its native paths and outlined lettering without the demonstration background.'
    }
  })
}

export const ENDORSED_2019_SUBJECT = {
  id: ENDORSED_2019.id, label: ENDORSED_2019.name, name: ENDORSED_2019.name,
  kind: 'identity-guide', graphNode: null, family: 'provincial-programs', scope: 'core', priority: 3,
  aliases: ['BCProgram'], collectionIds: ['bc-mark'], salaryEmployers: [], relations: [],
  note: ENDORSED_2019.notes, nextAction: 'Compare any original production files with the illustrated examples.',
  sources: [{ title: 'BC ID Guidelines for Use of Endorsed Marks, June 2019', url: endorsedGuide }]
}
