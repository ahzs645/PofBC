// Small adapters connect one district catalogue to the existing gallery, organization directory
// and salary employers. The source observations and payroll files are left intact.
import { CURRENT_DISTRICTS, SCHOOL_DISTRICTS, SCHOOL_FAMILY, SCHOOL_ACT_SOURCE, SCHOOL_DISTRICTS_AS_OF, connectionsOf, districtSources, formatHistoryDate, establishmentLabel } from './districts.js'

export const SCHOOL_IDENTITY_BODIES = SCHOOL_DISTRICTS.map((district) => ({
  id: district.id, name: district.name, shortName: district.title, kind: district.kind,
  graphNode: district.current ? district.id : null,
  from: district.established?.date ? Number(district.established.date.slice(0, 4)) : null,
  to: district.ended?.date ? Number(district.ended.date.slice(0, 4)) : null, current: district.current,
  status: district.assets.length ? 'asset-collected' : 'source-found',
  notes: `School district history and original identity specimens. ${district.established?.date ? `${establishmentLabel(district)}: ${formatHistoryDate(district.established.date)}. ` : ''}Each logo has its own source; a district's establishment does not date its artwork.`,
  assets: district.assets
}))
export const SCHOOL_IDENTITY_SUBJECTS = SCHOOL_DISTRICTS.map((district) => {
  const connections = connectionsOf(district.id)
  return {
    id: district.id, label: district.title, name: district.name, kind: district.kind, family: SCHOOL_FAMILY.id,
    schoolDistrict: district.id, current: district.current, graphNode: district.current ? district.id : null,
    aliases: district.aliases, collectionIds: district.assets.length ? [`collected-${district.id}`] : [],
    salaryEmployers: district.employerSlug ? [district.employerSlug] : [], priority: 2, scope: 'institution',
    sources: districtSources(district),
    note: district.current ? 'A current B.C. public school district, connected to its documented history, original artwork and existing salary disclosures.' : 'A documented predecessor district. Its own identity and sources are retained separately from its successors.',
    nextAction: district.assets.length ? 'Extend earlier logo coverage and verify adoption dates from district records.' : 'Locate an original district logo or seal in official or archival material.',
    relations: [
      ...connections.successors.map((link) => ({ type: 'predecessor-of', subject: link.district.id })),
      ...connections.predecessors.map((link) => ({ type: 'successor-of', subject: link.district.id }))
    ]
  }
})
export const SCHOOL_RELATED_BODIES = CURRENT_DISTRICTS.map((district) => ({
  id: district.id, name: district.legalName ?? `School District No. ${district.number} (${district.name})`,
  shortName: district.title, kind: district.kind, aliases: district.aliases, officialUrl: district.officialUrl,
  schoolDistrict: district.id, checked: SCHOOL_DISTRICTS_AS_OF,
  description: district.number === 93 ? 'The francophone public school district serving British Columbia, governed through the Conseil scolaire francophone.' : 'A British Columbia public school district governed by a board of education under the School Act.',
  historyNote: district.established?.date ? `${establishmentLabel(district)}: ${formatHistoryDate(district.established.date)}. ${district.established.disputed ? 'Sources record competing dates. ' : ''}The connected district history explains the evidence and later changes.` : 'The current district is documented. Its original establishment date remains under review.',
  sources: [SCHOOL_ACT_SOURCE, ...districtSources(district)],
  salaryEmployers: [{ slug: district.employerSlug, label: district.title }], relationships: []
}))
