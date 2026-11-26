import { FORREX_RELATED_BODY as society, earlyFunding, forrexFunding, forrexSources as sources } from '../government/forrex.js'

const siferp = 'Southern Interior Forest Extension and Research Partnership'
const partnership = 'FORREX Forest Research Extension Partnership'
const forum = 'FORREX Forum for Research and Extension in Natural Resources'
const siferpNote = 'The Southern Interior Forest Extension and Research Partnership (SIFERP) was the first operating name of the Southern Interior Extension and Research Society, incorporated in 1998. Forest Renewal BC helped establish the charitable society and funded its work connecting forestry researchers with practitioners. As its work expanded across the province, the society adopted the operating name FORREX.'
const note = 'FORREX was an independent, board-governed society that delivered British Columbia’s Provincial Forest Extension Program. Provincial support included a Forestry Innovation Investment contract and extension funding through the Forest Investment Account.'

export const FORREX_SUBJECT = {
  id: society.id, name: society.name, label: society.shortName, graphNode: society.id, aliases: [partnership, forum, 'Forrex Forest Research Extension Society', 'S-0038583'],
  family: 'institutions', scope: 'institution', kind: 'charitable-institution', programDeliveryPartner: true,
  collectionIds: ['collected-forrex'], salaryEmployers: [], priority: 2, sources: society.sources, note,
  relations: [{ type: 'related-to', subject: 'university-of-british-columbia', label: 'Research and extension partner' }],
  nextAction: 'Locate a dated design credit or adoption record for the four-figure emblem.'
}

export const SIFERP_SUBJECT = {
  ...FORREX_SUBJECT, id: 'siferp', label: 'SIFERP', name: siferp,
  aliases: ['Southern Interior Extension and Research Society'], collectionIds: ['collected-siferp'],
  sources: [sources.establishment, sources.annual2002, sources.rename2002], note: siferpNote,
  relations: [], nextAction: 'Locate the first dated use of the four-figure SIFERP emblem.'
}

export const SIFERP_RENAME = {
  from: 'siferp', to: 'forrex', type: 'registered-name', date: '2002-07-29', source: sources.rename2002,
  note: 'Society S-0038583 changed its registered name to Forrex Forest Research Extension Society. It was already using FORREX in its June 2002 annual report.'
}

const vector = {
  format: 'svg', isVector: true, reconstruction: false, observedDate: '2026-11-25',
  evidenceType: 'native-pdf-vector-extraction'
}

export const SIFERP_COLLECTION = {
  id: 'siferp', name: siferp, shortName: 'SIFERP', graphNode: null, historyId: 'siferp',
  kind: society.kind, current: false, from: 1998, to: 2002, status: 'asset-collected',
  notes: siferpNote, fundingHistory: earlyFunding,
  eras: [
    { id: 'siferp-partnership', label: siferp, shortLabel: 'SIFERP', years: '1998–2002',
      note: 'The partnership used its four-figure emblem alongside its full name on the cover of Ground Work in 2001.',
      marks: ['forrex-siferp'], sources: [sources.establishment, sources.annual2002] }
  ],
  assets: [
    {
      ...vector, id: 'forrex-siferp', label: 'SIFERP emblem and partnership name', publisher: siferp,
      file: 'identity-collected/forrex/siferp.svg', sourceDate: '2001',
      sourcePage: 'https://sernbc.ca/uploads/library/additional_related/ecosystem_restoration/Ground_Work.pdf#page=1',
      sourceLocator: 'Ground Work, SIFERP Series 3, front cover, lower right above SER-BC',
      notes: 'Four figures surround an open square beside the full Southern Interior partnership name.',
      fidelityNote: 'The cover supplies 65 filled paths for the emblem and the three lines of lettering. Extracted with MuPDF in the original dark ink.',
      extraction: { page: 1, pdfBounds: [377, 632, 544, 693] },
      sha256: '2bdd9117f7488b55d242bc07514816ac916fe21dc58c6e04308e4495059c4273'
    }
  ]
}

export const FORREX_COLLECTION = {
  id: society.id, name: society.shortName, kind: society.kind, current: false, from: 2002, to: 2015,
  status: 'asset-collected', notes: note, cover: 'forrex-forum', fundingHistory: forrexFunding,
  eras: [
    { id: 'forrex-forest-partnership', label: 'Forest Research Extension Partnership', years: '2002–2007/08',
      note: 'The June 2002 annual report used the name FORREX. On 29 July 2002, society S-0038583 changed its registered name to Forrex Forest Research Extension Society. Its printed signature spelled out the partnership name above the wordmark.',
      marks: ['forrex-partnership'], sources: [sources.annual2002, sources.rename2002] },
    { id: 'forrex-natural-resources', label: 'Forum for Research and Extension in Natural Resources', years: '2007/08–2015',
      note: 'The board broadened the name in 2007/08 as mining and energy took a larger role. The society registered the new name on July 26, 2008 and dissolved on December 22, 2015.',
      marks: ['forrex-forum'], sources: [sources.annual2009, sources.rename2008, sources.dissolution] }
  ],
  assets: [
    {
      ...vector, id: 'forrex-partnership', label: 'FORREX with Forest Research Extension Partnership', publisher: partnership,
      file: 'identity-collected/forrex/forest-research-extension.svg', sourceDate: '2003',
      sourcePage: 'https://faculty.washington.edu/emer/eic/streamline_vol7_no1_art1.pdf#page=2',
      sourceLocator: 'Streamline Watershed Management Bulletin, vol. 7, no. 1, Winter 2003, p. 2, publisher panel',
      notes: 'An arc joins the emblem and the FORREX wordmark. The partnership name sits above the small capitals and the management tagline sits below.',
      fidelityNote: 'All 108 filled paths, including the small lettering, were isolated from the bulletin with MuPDF.',
      extraction: { page: 2, pdfBounds: [40, 654, 194, 714] },
      sha256: 'e308848afba4ab987da2aa77981c73048087db2ef416d32515ca0603201e2354'
    },
    {
      ...vector, id: 'forrex-forum', label: 'FORREX wordmark and management tagline', publisher: forum,
      file: 'identity-collected/forrex/forum.svg', sourceDate: '2009',
      sourcePage: 'https://fews.forestry.oregonstate.edu/publications/Silins_Streamline_2009.pdf#page=2',
      sourceLocator: 'Streamline Watershed Management Bulletin, vol. 12, no. 2, Spring 2009, p. 2, publisher panel',
      notes: 'The wordmark under the arc has open space above the small capitals. The four figures carry a small TM and the tagline runs below FORREX.',
      fidelityNote: 'MuPDF exported the single compound path containing the emblem, TM, arc, wordmark and tagline. The bulletin’s tinted panel lies outside that path.',
      extraction: { page: 2, pdfBounds: [40, 661, 193, 714] },
      alsoSeen: [{ label: 'Streamline, vol. 11, no. 2, Spring 2008, p. 2', source: 'https://dspace.library.uvic.ca/server/api/core/bitstreams/3e393cee-2309-4a94-90bb-c887b02743e4/content#page=3', date: '2008' }],
      sha256: '7b43653df9b7fd5ec1da69c9f86c2cd10076af328e1a103cff6a9db3e3bae5b5'
    }
  ]
}
