// The initiative renderer reads content rather than assuming tourism-specific sections.
export const fileOf = (image) => typeof image === 'string' ? image : image?.file

export const imagesOf = (item) => {
  const images = new Map()
  for (const image of [item.image, ...(item.images ?? []), ...(item.specimens ?? []), ...(item.variants ?? [])]) {
    const file = fileOf(image)
    if (!file) continue
    const previous = images.get(file)
    // A legacy filename must not erase the date and source attached to a richer specimen.
    if (previous && typeof image === 'string') continue
    images.set(file, previous && typeof previous === 'object' ? { ...previous, ...image } : image)
  }
  return [...images.values()]
}

const fold = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()

export const searchInitiatives = (query, initiatives) => {
  const words = fold(query).split(/[^\p{L}\p{N}]+/u).filter(Boolean)
  return initiatives.filter((initiative) => {
    const text = fold([initiative.title, initiative.subtitle, initiative.summary,
      ...(initiative.tags ?? []), ...(initiative.searchTerms ?? [])].join(' '))
    return words.every((word) => text.includes(word))
  })
}

/** A record-only link finds its section; an unknown section falls back to the first one. */
export const resolveInitiativeSelection = (initiative, place = {}) => {
  const sections = initiative.sections ?? []
  const matchesRecord = (record) => record.id === place.record ||
    Boolean(place.record && record.images?.some((image) => image.formerRecordId === place.record))
  const recordSection = sections.find((section) => ['records', 'publications'].includes(section.type) &&
    section.records?.some(matchesRecord))
  const section = recordSection ?? sections.find((entry) => entry.id === place.section) ?? sections[0]
  const record = recordSection?.records.find(matchesRecord) ?? null
  return { section, record, missingRecord: Boolean(place.record && !record) }
}

// Programs and their parts. An entry with a `parentId` is part of that program: it keeps its own
// page and address, and is listed on the index and on its program's page beneath the program.
const byId = (initiatives) => new Map(initiatives.map((initiative) => [initiative.id, initiative]))

/** An initiative's direct parts, in catalogue order. */
export const partsOf = (id, initiatives) => initiatives.filter((initiative) => initiative.parentId === id)

/** The programs above an initiative, outermost first; a broken or circular chain stops where it fails. */
export const ancestorsOf = (id, initiatives) => {
  const index = byId(initiatives)
  const chain = []
  const seen = new Set([id])
  let parent = index.get(index.get(id)?.parentId)
  while (parent && !seen.has(parent.id)) {
    chain.unshift(parent)
    seen.add(parent.id)
    parent = index.get(parent.parentId)
  }
  return chain
}

/** The index: each top-level program with the parts that match. A matching part brings its program. */
export const indexGroups = (matches, initiatives) => {
  const matched = new Set(matches.map((initiative) => initiative.id))
  const index = byId(initiatives)
  const rootOf = (initiative) => ancestorsOf(initiative.id, initiatives)[0] ?? initiative
  const roots = initiatives.filter((initiative) => !index.has(initiative.parentId))
  return roots.map((program) => {
    const descendants = initiatives.filter((initiative) => initiative !== program && rootOf(initiative) === program)
    const parts = matched.has(program.id) ? descendants : descendants.filter((part) => matched.has(part.id))
    return { program, parts, matched: matched.has(program.id) }
  }).filter((group) => group.matched || group.parts.length)
}

const CONTENT_LAST = { timeline: 1, sources: 2 }
const plural = (count, [one, many]) => count === 1 ? one : many

/**
 * One page template for every initiative: its material first, then its timeline, then its sources,
 * under the same tab names, with a row of facts under the title. Section IDs never change, so a
 * shared address still opens the same tab.
 */
export const templateInitiative = (detail, entry = {}, parts = []) => {
  const sections = (detail.sections ?? [])
    .map((section, order) => ({ section, order }))
    .sort((a, b) => (CONTENT_LAST[a.section.type] ?? 0) - (CONTENT_LAST[b.section.type] ?? 0) || a.order - b.order)
    .map(({ section }) => section.type === 'timeline' ? { ...section, label: 'Timeline' }
      : section.type === 'sources' && !section.inventory ? { ...section, label: 'Sources' } : section)
  const count = (types) => sections.filter((section) => types.includes(section.type))
    .reduce((total, section) => total + (section.records?.length ?? 0), 0)
  const derived = [
    { value: count(['records', 'publications']), label: ['record', 'records'] },
    { value: count(['timeline']), label: ['dated event', 'dated events'] },
    { value: detail.sources?.length ?? 0, label: ['source', 'sources'] }
  ].filter((fact) => fact.value > 0).map((fact) => ({ value: fact.value, label: plural(fact.value, fact.label) }))
  const stats = detail.stats?.length ? [...detail.stats] : derived
  if (parts.length) stats.push({ value: parts.length, label: plural(parts.length, entry.parts?.noun ?? ['part', 'parts']) })
  return { ...detail, sections, stats }
}
