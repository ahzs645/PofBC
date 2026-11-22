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
  const recordSection = sections.find((section) => ['records', 'publications'].includes(section.type) &&
    section.records?.some((record) => record.id === place.record))
  const section = recordSection ?? sections.find((entry) => entry.id === place.section) ?? sections[0]
  const record = recordSection?.records.find((entry) => entry.id === place.record) ?? null
  return { section, record, missingRecord: Boolean(place.record && !record) }
}
