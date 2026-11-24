// Institutional identities, not salary-employer deduplication or inferred legal dates.
import registry from '../../research/identity/postsecondary-2026-11-24/source-register.json' with { type: 'json' }

import { isLogoSource, postsecondaryArtworkOf } from './postsecondaryArtwork.js'

export const POSTSECONDARY_FAMILY = {
  id: 'postsecondary-history',
  label: 'Public colleges and post-secondary history',
  description: 'Current public colleges, missing universities and institutes, historical names, mergers, splits and transferred operations. Source links do not establish artwork holdings.'
}

export const POSTSECONDARY_SUBJECTS = registry.records.map((record) => {
  const artworkReview = postsecondaryArtworkOf(record.id)
  const shared = artworkReview.shared
  const artworkSource = artworkReview.specimens.some(isLogoSource)
  const documented = artworkReview.specimens.some(({ format }) => format === 'description-only')
  const identityStatus = shared ? 'shared-identity' : artworkSource || documented ? undefined : record.identityStatus ?? 'distinct-unconfirmed'
  return {
    id: record.id, name: record.name, label: record.name, kind: record.kind,
    family: POSTSECONDARY_FAMILY.id, graphNode: null,
    aliases: record.aliases, salaryEmployers: record.salaryEmployers, collectionIds: [],
    priority: record.current ? 1 : 2, scope: 'institution', sources: record.sources,
    note: record.note, artworkReview,
    relations: [...record.relations, ...(shared ? [{ type: 'shares-identity-with', subject: shared.targetSubjectId }] : [])],
    ...(identityStatus ? { identityStatus } : {}),
    nextAction: shared
      ? 'This subject’s shared branding does not count as a separately held logo.'
      : artworkReview.specimens.length
        ? 'Review the sources below. Artwork is counted only after its provenance and reuse terms have been checked.'
        : 'Find a dated specimen from this institution; do not substitute a successor’s logo.'
  }
})
