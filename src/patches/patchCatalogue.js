// Browsing helpers are independent of React and the renderer. A card keeps its own identity while
// filters can select one of its variants; template membership never merges designs or source records.

export const OTHER_TEMPLATES = 'other'

/** Only an explicit reconstruction note identifies a generated colourway. Missing evidence does not. */
export const isGeneratedColourway = (patch) => /generated recolou?r/i.test(patch.limitations ?? '')

export const sourcePhotoCount = (patch) => new Set((patch.sightings ?? [])
  .map(({ id }) => id.replace(/-O\d+$/, ''))).size

export function catalogueCards(sections, { isCard, variantsOf, cardLabel, templateFamilyOf }) {
  return sections.flatMap(({ sector, orgs }) => orgs.flatMap((org) => org.patches.filter(isCard).map((patch) => {
    const members = variantsOf(patch)?.members ?? [patch]
    return {
      patch,
      org,
      sector,
      label: cardLabel(patch),
      members,
      templates: new Map(members.map((member) => [member.id, templateFamilyOf(member)]))
    }
  })))
}

/** Every search word must describe the same variant, together with its card, owner and family. */
export function filterCatalogue(cards, { q = '', org = null, family = null } = {}) {
  const query = q.trim().toLowerCase()
  const words = query.split(/\s+/).filter(Boolean)
  const aliasesOf = (member) => [...(member.merged ?? []), ...(member.absorbs ?? []), ...(member.sightings ?? []).map(({ id }) => id)]
  // Some real IDs are prefixes of others (FO-green-gold-black / FO-green-gold-black-gold).
  // An exact ID or historical alias selects its own edition before general text matching.
  const exactIds = new Set(query ? cards.flatMap(({ members }) => members
    .filter((member) => [member.id, ...aliasesOf(member)].some((id) => id.toLowerCase() === query))
    .map(({ id }) => id)) : [])
  return cards.flatMap((card) => {
    if (org && card.org.id !== org) return []
    const matchingMembers = card.members.filter((member) => {
      if (exactIds.size && !exactIds.has(member.id)) return false
      const template = card.templates.get(member.id)
      if (family && (template?.id ?? OTHER_TEMPLATES) !== family) return false
      const aliases = aliasesOf(member)
      const text = `${card.label} ${member.label} ${member.variant ?? ''} ${member.id} ${aliases.join(' ')} ${member.medium} ${card.org.name} ${template?.label ?? ''}`.toLowerCase()
      return words.every((word) => text.includes(word))
    })
    if (!matchingMembers.length) return []
    const selected = matchingMembers.find((member) => member.id === card.patch.id) ?? matchingMembers[0]
    return [{ ...card, matchingMembers, selected, template: card.templates.get(selected.id) ?? null }]
  })
}

/** Unclassified cards remain visible. A card appears once, under its selected variant's family. */
export function groupCatalogueByTemplate(cards, families) {
  const buckets = new Map()
  for (const card of cards) {
    const id = card.template?.id ?? OTHER_TEMPLATES
    if (!buckets.has(id)) buckets.set(id, [])
    buckets.get(id).push(card)
  }
  return [...families, {
    id: OTHER_TEMPLATES,
    label: 'Other designs',
    description: 'These designs have no assigned template family yet.'
  }].flatMap((family) => buckets.has(family.id) ? [{ family, cards: buckets.get(family.id) }] : [])
}

export const variantCount = (cards) => cards.reduce((total, card) => total + (card.matchingMembers ?? card.members).length, 0)

export function readPatchPlace(search, { collection, orgIds, familyIds, findPatch }) {
  const params = new URLSearchParams(search)
  const patch = findPatch(params.get('patch') ?? '')
  return {
    org: orgIds.includes(params.get('org')) ? params.get('org') : null,
    patch: patch?.collection === collection ? patch.id : null,
    group: params.get('group') === 'template' ? 'template' : 'organization',
    family: familyIds.includes(params.get('family')) ? params.get('family') : null,
    q: params.get('q') ?? ''
  }
}

export const patchPlaceParams = (view, place) => ({
  view,
  org: place.org,
  patch: place.patch,
  group: place.group === 'template' ? 'template' : null,
  family: place.family,
  q: place.q || null
})

export function patchPlaceUrl(href, view, place) {
  const url = new URL(href)
  for (const [key, value] of Object.entries(patchPlaceParams(view, place))) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  return url
}
