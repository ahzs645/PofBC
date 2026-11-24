const program = 'bc-youth'
const council = 'bc-youth-advisory-council'
const files = 'identity-collected/bc-youth'

export const YOUTH_SOURCES = {
  labour: { title: 'Speech from the Throne, March 11, 1986', url: 'https://lims.leg.bc.ca/hdms/file/Debates/33rd4th/33p_04s_860311p.htm' },
  estimates: { title: 'Advanced Education and Job Training estimates, July 14, 1987', url: 'https://lims.leg.bc.ca/hdms/file/Debates/34th1st/34p_01s_870714p.htm' },
  debate: { title: 'Stanley Hagen on youth programs and The Next Step, May 12, 1989', url: 'https://lims.leg.bc.ca/hdms/file/Debates/34th3rd/34p_03s_890512a.htm' },
  driftwood: { title: 'Gulf Islands Driftwood, October 4, 1989, p. A3', url: 'https://saltspringarchives.com/driftwood/1989/v30n40Oct4-1989A.pdf#page=3' },
  hashilthsa: { title: 'Ha-Shilth-Sa, October 24, 1989, p. 14', url: 'https://data2.archives.ca/e/e449/e011207352.pdf#page=8' },
  reverse: { title: 'Supplied reverse BC Youth advertisement detail', citation: 'White mark on a black field beside the Province of British Columbia credit to Stanley B. Hagen, Minister of Advanced Education and Job Training and Minister Responsible for Youth. The supplied crop carries no publication date.' }
}

const common = { graphNode: null, salaryEmployers: [], scope: 'core', priority: 2, family: 'historical-research' }
export const YOUTH_SUBJECTS = [
  {
    ...common, id: program, name: 'BC Youth', label: 'BC Youth', kind: 'service-brand', aliases: ['B.C. Youth'], collectionIds: ['collected-bc-youth'],
    relations: [{ subject: council, type: 'related-to', label: 'Council named in the grants advertisement' }],
    sources: [YOUTH_SOURCES.driftwood, YOUTH_SOURCES.hashilthsa, YOUTH_SOURCES.reverse],
    note: 'The Province used this identity to advertise youth programs. A 1989 notice names the Youth Advisory Council as the provider of Youth Grants Program funding.',
    nextAction: 'Locate an original colour printing or a dated full page for the reverse signature.'
  },
  {
    ...common, id: council, name: 'British Columbia Youth Advisory Council', label: 'BC Youth Advisory Council', kind: 'advisory-council',
    aliases: ['British Columbia Youth Council', 'B.C. Youth Council'], collectionIds: [], relations: [],
    sources: [YOUTH_SOURCES.labour, YOUTH_SOURCES.estimates, YOUTH_SOURCES.debate, YOUTH_SOURCES.driftwood],
    identityStatus: 'distinct-unconfirmed',
    note: 'Created in 1985, the Council advised the minister responsible for youth and helped fund community projects. In 1989 its 16 members represented eight regions. The dated grant notice carries the provincial BC Youth identity.',
    nextAction: 'Find the Council’s own letterhead and the order or report recording when its mandate ended.'
  }
]

const shared = {
  publisher: 'Province of British Columbia', observedDate: '2026-11-24', format: 'svg', isVector: true,
  reconstruction: true, fidelity: 'source compared', evidenceType: 'vector-reconstruction'
}
export const YOUTH_BODY = {
  id: program, name: 'BC Youth', kind: 'service-brand', graphNode: null, current: false, status: 'asset-collected',
  notes: YOUTH_SUBJECTS[0].note,
  assets: [
    {
      ...shared, id: 'bc-youth-right-flag', label: 'BC Youth with flag at right', file: files + '/right-flag.svg',
      sourcePage: YOUTH_SOURCES.driftwood.url, sourceLocator: YOUTH_SOURCES.driftwood.title,
      alsoSeen: [{ label: YOUTH_SOURCES.hashilthsa.title, source: YOUTH_SOURCES.hashilthsa.url }],
      sourceDate: '1989-10-04', dateNote: 'Also printed on October 24 in Ha-Shilth-Sa.',
      notes: 'Black ink, BC above the Youth lettering and the flag at the right.',
      fidelityNote: 'The figure and letterforms were constructed as editable paths. The provincial waving flag reuses the project’s artwork.'
    },
    {
      ...shared, id: 'bc-youth-left-flag', label: 'BC Youth with flag above BC', file: files + '/left-flag.svg',
      sourceFile: YOUTH_SOURCES.reverse.title, darkBackground: true,
      dateNote: 'The supplied image names Minister Hagen. Its publication and date remain unidentified.',
      notes: 'The small flag and stacked BC sit to the left of the white Youth wordmark.',
      fidelityNote: 'Reconstructed from the reverse imprint. The lettering, flag and ministerial credit are available on transparent backgrounds.',
      downloads: [{ label: 'Download full ministerial signature', file: files + '/left-flag-minister.svg' }]
    }
  ]
}
