// Research links are not gallery assets. Never fetch, hotlink or count any of these as artwork held.
import registry from '../../research/identity/postsecondary-2026-11-24/source-register.json' with { type: 'json' }
import pdfReview from '../../research/identity/postsecondary-2026-11-24/artwork-review-candidates.json' with { type: 'json' }
import newEvidence from '../../research/identity/postsecondary-2026-11-24/artwork-coverage-evidence.json' with { type: 'json' }

export const POSTSECONDARY_ARTWORK_SCOPE = {
  'institutional': 'Institutional identity',
  'campus': 'Campus signature',
  'historical': 'Historical identity',
  'cover-art': 'Publication cover, institutional status unconfirmed',
  'artifact': 'Physical specimen, institutional status unconfirmed',
  'heraldry': 'Heraldry, not the graphic logo',
  'military-insignia': 'Military insignia, not the successor university logo',
  'program': 'Program mark, not the institutional logo',
  'athletics': 'Athletics, not the institutional logo',
  'campaign': 'Campaign or anniversary, not the primary logo',
  'retrospective': 'Retrospective source, not a first-use date'
}

export const POSTSECONDARY_ARTWORK_FORMAT = {
  'native-vector': 'Native vector source',
  'heraldic-register': 'Official heraldic record',
  'raster-source': 'Raster source',
  'format-unverified': 'Published specimen, format unverified',
  'raster-lead': 'Raster acquisition lead',
  'description-only': 'Design described, no artwork shown',
  'reconstruction-reference': 'Reference for a reconstruction, not original artwork'
}

const sourceLink = (url, page) => `${url.split('#')[0]}#page=${page}`
const verifiedPdf = pdfReview.candidates.map((candidate) => {
  const source = pdfReview.documents[candidate.document]
  const vector = candidate.extraction.type === 'native-vector-region'
  const locator = [`PDF p. ${candidate.pdfPage}`, candidate.printedPage ? `printed p. ${candidate.printedPage}` : null, !vector ? `object ${candidate.extraction.objectNumber}` : null].filter(Boolean).join(' · ')
  return {
    id: candidate.id, subjectId: candidate.subjectId, label: candidate.label,
    format: vector ? 'native-vector' : 'raster-source', scope: candidate.id.includes('campaign') ? 'cover-art' : candidate.id.startsWith('selkirk-guide') ? 'institutional' : 'historical',
    url: sourceLink(source.url, candidate.pdfPage), locator, publisher: source.publisher,
    publicationDate: source.publicationDate, note: candidate.note, rightsNote: source.rightsNote,
    evidence: 'source-only'
  }
})
const directLeads = registry.records.flatMap((subject) => subject.artworkCandidates.map((candidate) => ({
  id: candidate.id, subjectId: subject.id, label: candidate.label,
  format: 'raster-lead',
  scope: /anniversary/i.test(candidate.label + ' ' + candidate.note) ? 'campaign' : /retrospective/i.test(candidate.note) ? 'retrospective' : 'institutional',
  url: candidate.sourceUrl,
  publisher: candidate.publisher, publicationDate: candidate.publicationDate,
  note: candidate.note, evidence: 'source-only'
})))
const specimens = [...newEvidence.specimens, ...verifiedPdf, ...directLeads]
const bySubject = new Map()
for (const item of specimens) {
  if (!bySubject.has(item.subjectId)) bySubject.set(item.subjectId, [])
  bySubject.get(item.subjectId).push(item)
}
const shared = new Map(newEvidence.sharedIdentities.map((item) => [item.subjectId, item]))
const identityHistories = new Map(newEvidence.identityHistories.map(({ subjectId, events }) => [subjectId, events]))

// Cover art and heraldry can be useful specimens without proving a distinct graphic logo.
export const isLogoSource = ({ format, scope }) => ['native-vector', 'raster-source', 'format-unverified', 'raster-lead'].includes(format)
  && ['institutional', 'historical', 'campus', 'retrospective'].includes(scope)

export function postsecondaryArtworkOf(id) {
  return { specimens: bySubject.get(id) ?? [], shared: shared.get(id) ?? null, history: identityHistories.get(id) ?? [] }
}

// The three evidence counts partition subjects; holdings are a separate count. Variants,
// repeated publications, covers, shields and parent identities cannot inflate the vector count.
export const summarizePostsecondaryArtwork = (subjects) => {
  const counts = { total: subjects.length, held: 0, vector: 0, observedNonvector: 0, unverified: 0, shared: 0 }
  for (const subject of subjects) {
    if (subject.hasArtwork) counts.held++
    const { specimens = [], shared } = subject.artworkReview ?? {}
    if (shared) {
      counts.shared++
      counts.unverified++
    } else if (subject.evidence?.vector || specimens.some((item) => item.format === 'native-vector' && isLogoSource(item))) {
      counts.vector++
    } else if (subject.evidence?.raster || specimens.some((item) => item.format === 'raster-source' && isLogoSource(item))) {
      counts.observedNonvector++
    } else {
      counts.unverified++
    }
  }
  return counts
}
