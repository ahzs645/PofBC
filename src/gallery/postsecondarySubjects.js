// Institutional identities, not salary-employer deduplication or inferred legal dates.
import registry from '../../research/identity/postsecondary-2026-11-24/source-register.json' with { type: 'json' }

export const POSTSECONDARY_FAMILY = {
  id: 'postsecondary-history',
  label: 'Public colleges and post-secondary history',
  description: 'Current public colleges, missing universities and institutes, historical names, mergers, splits and transferred operations. Source links do not establish artwork holdings.'
}

export const POSTSECONDARY_SUBJECTS = registry.records.map(record => ({
  id: record.id, name: record.name, label: record.name, kind: record.kind,
  family: POSTSECONDARY_FAMILY.id, graphNode: null,
  aliases: record.aliases, salaryEmployers: record.salaryEmployers, collectionIds: [],
  priority: record.current ? 1 : 2, scope: 'institution', sources: record.sources,
  note: record.note, relations: record.relations,
  ...(record.identityStatus ? { identityStatus: record.identityStatus } : {}),
  nextAction: record.artworkCandidates.length
    ? 'Archive and visually verify published specimens; seek source-native vectors and dated earlier examples.'
    : 'Find dated artwork from the named institution; distinguish separate marks, legal names and later reproductions.'
}))
