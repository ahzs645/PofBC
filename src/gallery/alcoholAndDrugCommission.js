const id = 'alcohol-and-drug-commission'
const name = 'Alcohol and Drug Commission of British Columbia'
const note = 'The 1973 Alcohol and Drug Commission Act made the Commission an agent of the provincial Crown. The Lieutenant Governor in Council appointed its members and designated its chair and vice-chair. The Act was repealed in 1983.'

export const ALCOHOL_AND_DRUG_COMMISSION_SUBJECT = {
  id, name, label: name, kind: 'agency', family: 'specialist-health', scope: 'core',
  aliases: ['Alcohol and Drug Commission', 'ADCBC'], collectionIds: [`collected-${id}`],
  graphNode: null, priority: 3, salaryEmployers: [], relations: [], note,
  sources: [
    { title: 'Alcohol and Drug Commission Act, SBC 1973, c. 3, sections 2–4', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/408463782' },
    { title: 'Alcohol and Drug Commission Act Repeal Act, SBC 1983, c. 12', url: 'https://www.bclaws.gov.bc.ca/civix/document/id/hstats/hstats/577115892' },
    { title: 'Commission reports and fact sheets, 1973–1977, Wellcome Collection', url: 'https://wellcomecollection.org/works/py73rfj2' },
    { title: 'Education Department booklet imprint', citation: 'Two supplied scans of the same undated booklet page bearing the Commission name, its interlocking initials and the address 307 West Broadway, Vancouver, B. C.' }
  ],
  nextAction: 'Identify the booklet title and publication date from a complete copy.'
}

export const ALCOHOL_AND_DRUG_COMMISSION_BODY = {
  id, name, kind: 'agency', graphNode: null, from: 1973, to: 1983, current: false,
  status: 'asset-collected', notes: note,
  assets: [{
    id: 'adc-bc-booklet-monogram', label: 'Education Department booklet monogram',
    file: `identity-collected/${id}/monogram.svg`, sourceFile: 'Two supplied views of the Education Department booklet imprint',
    publisher: name, observedDate: '2026-11-24', format: 'svg', isVector: true,
    reconstruction: true, supplied: false, fidelity: 'source compared', evidenceType: 'vector-reconstruction',
    notes: 'The tall A, D and C surround a smaller B and C. Each letter is an individually editable shape.',
    dateNote: 'The title and date of this booklet are unknown.',
    fidelityNote: 'The reconstructed ink overlaps 97.0% and 97.4% of the combined ink area in the larger and smaller supplied scans, respectively. Both show the same booklet page.'
  }]
}
