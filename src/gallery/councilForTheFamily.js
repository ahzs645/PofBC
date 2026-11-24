const id = 'bc-council-for-the-family'
const name = 'British Columbia Council for the Family'
const directory = `identity-collected/${id}`
const history = 'https://www.bccf.ca/media/uploads/attached_files/bccf_caseforsupport_final.pdf'

export const FAMILY_COUNCIL_SUBJECT = {
  id, name, label: name, kind: 'nonprofit-society', family: 'institutions', scope: 'institution',
  aliases: ['BC Council for Families', 'BC Council for the Family'], collectionIds: [`collected-${id}`],
  graphNode: null, priority: 3, salaryEmployers: [], relations: [],
  sources: [
    { title: 'BC Council for Families, Our History', url: history },
    { title: 'BC Council for Families, legal name and society status', url: 'https://www.bccf.ca/bccf/terms-conditions/' },
    { title: 'Historical council signatures', citation: 'Supplied letterhead with a Parliament Buildings address and two handbook cover details, one greyscale and one green. The three crops are undated.' }
  ],
  note: 'The society, founded in 1977 and now known as the BC Council for Families, used the longer name printed on these specimens.',
  nextAction: 'Find dated copies of the two handbooks or a printer’s proof of the original signature.'
}

const emblemDownload = { label: 'Download green handbook emblem', file: `${directory}/emblem-green.svg` }

const shared = {
  publisher: name, observedDate: '2026-11-24', format: 'svg', isVector: true,
  reconstruction: true, supplied: false, fidelity: 'source compared', evidenceType: 'vector-reconstruction',
  dateNote: 'The supplied crop is undated.'
}

export const FAMILY_COUNCIL_BODY = {
  id, name, kind: 'nonprofit-society', graphNode: null, from: 1977, current: true,
  status: 'asset-collected', notes: FAMILY_COUNCIL_SUBJECT.note,
  assets: [
    {
      ...shared, id: 'bccf-letterhead', label: 'Council letterhead with Parliament Buildings address',
      file: `${directory}/letterhead.svg`, sourceFile: 'Supplied letterhead detail',
      notes: 'The taller looped emblem sits above a rule, with the council name below and a right-aligned Victoria mailing address.',
      fidelityNote: 'The silhouette and display capitals were drawn by hand. The address uses fitted Nimbus Sans outlines. The grey approximates the printed screen.'
    },
    {
      ...shared, id: 'bccf-handbook-green', label: 'Handbook cover with green emblem',
      downloads: [emblemDownload], designLabel: 'Council handbook cover signature', versionLabel: 'Green emblem',
      file: `${directory}/handbook-green.svg`, sourceFile: 'Supplied green “Parents of…” handbook cover detail',
      notes: 'The green two-loop emblem meets the top of the black cover band. The full council name is set in white.',
      fidelityNote: 'The green is an estimate from the supplied image. The editable band is cropped to the signature. Its full width depends on the cover.'
    },
    {
      ...shared, id: 'bccf-handbook-grey', label: 'Handbook cover with grey emblem',
      downloads: [emblemDownload], variantOf: 'bccf-handbook-green', versionLabel: 'Grey emblem',
      file: `${directory}/handbook-grey.svg`, sourceFile: 'Supplied greyscale “Blended Fa…” handbook cover detail',
      notes: 'The greyscale cover gives the white council name more space at the top and left of the black band.',
      fidelityNote: 'The reconstruction follows the placement in the supplied crop. A flat grey approximates the printed screen.'
    }
  ]
}
