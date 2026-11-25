import { YOUTH_BODY, YOUTH_SOURCES } from '../gallery/bcYouth.js'

const refs = (...ids) => ids.map((sourceId) => ({ sourceId }))
const sources = Object.entries(YOUTH_SOURCES).map(([id, source]) => ({ id, ...source }))
const [right, left] = YOUTH_BODY.assets

const printSpecimen = (name, file, sourceId, date) => ({
  file: 'initiatives/bc-youth/' + file, sourceId, date, label: name, evidenceType: 'printed-source-crop',
  alt: 'BC Youth mark as printed in ' + name, caption: YOUTH_SOURCES[sourceId].title
})

const artwork = (asset, sourceId, dateLabel, darkBackground = false) => ({
  file: asset.file, label: asset.label, alt: asset.label, caption: asset.notes, darkBackground, dateLabel, sourceId,
  evidenceType: 'vector-reconstruction'
})

export const bcYouthDetail = (entry) => ({
  id: entry.id, title: entry.title,
  hero: { title: entry.title, eyebrow: 'Provincial youth programs', description: entry.summary, image: entry.cover, caption: entry.cover.caption },
  sources,
  relatedLinks: [
    { label: 'BC Youth identity register', to: { view: 'gallery', subject: 'bc-youth' } },
    { label: 'Challenge ’89 summer employment program', to: { view: 'initiatives', initiative: 'challenge-89' } },
    { label: 'Passport to Apprenticeship', to: { view: 'initiatives', initiative: 'passport-to-apprenticeship' } },
    { label: 'Environment Youth Corps', to: { view: 'initiatives', initiative: 'environment-youth-corps' } },
    { label: 'BC Youth Advisory Council', to: { view: 'gallery', subject: 'bc-youth-advisory-council' } },
    { label: 'Ministry of Labour (1985 atlas)', to: { view: 'government', node: 'ministry-of-labour-1976', year: 1985 } },
    { label: 'Hagen’s Ministry of Advanced Education and Job Training', to: { view: 'government', node: 'ministry-of-advanced-education-and-job-training-1986', year: 1988 } }
  ],
  sections: [
    { id: 'marks', label: 'Logos', type: 'records', layout: 'marks', title: 'Two printed arrangements', records: [
      { id: right.id, title: right.label, kind: 'program-identity', artworkNote: 'Reconstructed SVG and two newspaper printings', description: 'The figure forms the Y. BC sits above the other letters and the flag extends to the right. Two newspapers printed this arrangement in the Youth Grants Program advertisement in October 1989.',
        images: [
          { ...artwork(right, 'hashilthsa', 'Reconstructed from the two October 1989 printings'), shortLabel: 'Reconstructed SVG' },
          printSpecimen('Gulf Islands Driftwood', 'driftwood-specimen.png', 'driftwood', '1989-10-04'),
          printSpecimen('Ha-Shilth-Sa', 'ha-shilth-sa-specimen.png', 'hashilthsa', '1989-10-24')
        ], sourceRefs: refs('driftwood','hashilthsa') },
      { id: left.id, title: left.label, kind: 'program-identity', artworkNote: 'Wordmark and full ministerial signature', description: 'In the white version, the flag sits above BC beside the figure. The full imprint credits Stanley B. Hagen as Minister of Advanced Education and Job Training and Minister Responsible for Youth.',
        dateNote: left.dateNote, images: [{ ...artwork(left, 'reverse', 'Undated reverse imprint', true), shortLabel: 'Wordmark' },
          { ...artwork(left, 'reverse', 'Undated reverse imprint', true), file: left.downloads[0].file, label: 'With ministerial credit', alt: 'White BC Youth signature beside the Province and ministerial credit', caption: 'The full ministerial credit reconstructed alongside the wordmark.' }],
        sourceRefs: refs('reverse') }
    ] },
    { id: 'history', label: 'History', type: 'timeline', title: 'The Council, the ministries and the grants', records: [
      { id: 'youth-council-founded', date: '1985', title: 'British Columbia Youth Council created', description: 'In the 1987 ministry estimates, Hagen dated the Council’s creation to 1985 and described its role in bringing young people into policy discussions.', sourceRefs: refs('estimates') },
      { id: 'youth-council-labour', date: 'March 1986', title: 'Council appointed by the Minister of Labour', description: 'The Speech from the Throne reported the appointment and identified subsidized transit fares as one of the Council’s recommendations.', sourceRefs: refs('labour') },
      { id: 'youth-council-advanced-education', date: 'July 1987', title: 'Youth portfolio in Advanced Education and Job Training', description: 'Hagen reported on the Council in the ministry’s estimates.', sourceRefs: refs('estimates') },
      { id: 'youth-guide', date: 'Spring 1989', title: 'The Next Step updated', description: 'The Council published a guide to public services for young people. In May, Hagen described the updated edition and a council with 16 members drawn from eight regions.', sourceRefs: refs('debate') },
      { id: 'youth-grants-advertising', date: 'October 1989', title: 'Grant applications advertised', description: 'The Council invited applications to the Youth Grants Program. The notice carried the BC Youth mark and named Hagen as Minister Responsible for Youth. The ministry imprint also listed Advanced Education and Job Training and responsibility for Science and Technology.', sourceRefs: refs('driftwood','hashilthsa') }
    ] },
    { id: 'sources', label: 'Sources', type: 'sources', title: 'Newspapers and legislative records', records: sources }
  ]
})
