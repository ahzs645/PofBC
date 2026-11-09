// A discovery index for every word in a disclosed name. Search normalization never changes
// person keys or makes identity decisions: the existing employer-scoped links do that work.
import { nameOnly, personKey, surnameShard } from './people.js'

const collator = new Intl.Collator('en')
const alphabetically = (a, b) => collator.compare(a, b) || (a < b ? -1 : a > b ? 1 : 0)
const numerically = (a, b) => a - b

/**
 * Search words, independent of surname/given-name order. Apostrophes are optional in a word
 * (O’Neill / oneill); hyphens and other punctuation separate words (Anne-Marie / anne marie).
 * Keep query whitespace harmless. Call nameOnly first when the input is a disclosed name that
 * may have a position appended to it; document spellings already contain names alone.
 */
export const nameSearchTokens = (text) => [...new Set(String(text ?? '')
  .normalize('NFD').replace(/\p{M}/gu, '').toLowerCase()
  .replace(/['\u0060\u00b4\u02bb\u02bc\u2018\u2019\uff07]/g, '')
  .replace(/[^a-z0-9]+/g, ' ').trim().split(/\s+/).filter(Boolean))]

const queryWords = (query) => Array.isArray(query)
  ? [...new Set(query.flatMap(nameSearchTokens))]
  : nameSearchTokens(query)

// Generated documents are immutable and reused by the JSON loader. Cache only their normalized
// spellings, never a query or its filters. A WeakMap does not retain a bucket after it is released.
const preparedDocuments = new WeakMap()
const documentWords = (document) => {
  let prepared = preparedDocuments.get(document)
  if (!prepared) {
    prepared = document[4].map(nameSearchTokens)
    preparedDocuments.set(document, prepared)
  }
  return prepared
}

const matchWords = (words, wanted) => {
  let tier = 0
  for (const token of wanted) {
    if (words.includes(token)) continue
    if (!words.some((word) => word.startsWith(token))) return null
    tier = 1
  }
  return tier
}

/** 0: every typed word is complete; 1: at least one is a word prefix; null: no match. */
export const matchNameSearch = (name, queryTokens) => {
  const wanted = queryWords(queryTokens)
  return wanted.length ? matchWords(nameSearchTokens(nameOnly(name)), wanted) : null
}

/**
 * All words must occur in one spelling, so any one of their two-character buckets contains
 * every possible result. Pick the smallest download. A missing required bucket proves there
 * are no matches; a lone initial has no bucket and needs another word to narrow the search.
 * The manifest's buckets are { prefix: { file, documents, bytes } }.
 */
export const chooseNameSearchBucket = (query, manifest) => {
  const prefixes = [...new Set(queryWords(query).filter((word) => word.length >= 2).map((word) => word.slice(0, 2)))]
  if (!prefixes.length) return null
  const entries = prefixes.map((prefix) => ({ prefix, bucket: manifest?.buckets?.[prefix] }))
  if (entries.some(({ bucket }) => !bucket || bucket.documents === 0)) return null
  const hasBytes = entries.every(({ bucket }) => Number.isFinite(bucket.bytes) && bucket.bytes >= 0)
  const documents = (bucket) => Number.isFinite(bucket.documents) ? bucket.documents : Infinity
  entries.sort((a, b) => (hasBytes ? a.bucket.bytes - b.bucket.bytes : 0)
    || documents(a.bucket) - documents(b.bucket) || alphabetically(a.prefix, b.prefix))
  return entries[0].prefix
}

/**
 * Compact documents: [key, name, employerAt, years, spellings, recordShards]. One document per
 * existing name key at one employer keeps both alias matching and reporting-period coverage
 * scoped to that employer. `links` is the existing nameLinks.js linkLookup Map. A raw name key
 * remains unchanged even when nameOnly removes an appended position from its searchable text.
 * Rows use the published people-index schema; index supplies its employer and period tables.
 */
export const createNameSearchDocuments = (rows, index, links = new Map()) => {
  const groups = new Map()
  for (const row of rows) {
    const spelling = nameOnly(row[0])
    if (!spelling) continue
    const employerAt = row[4]
    const yearAt = row[5]
    if (!Number.isInteger(employerAt) || !index?.employers?.[employerAt]) throw new Error('Name search row refers to an unknown employer')
    if (!Number.isInteger(yearAt) || index?.years?.[yearAt] === undefined) throw new Error('Name search row refers to an unknown reporting period')
    const disclosedKey = personKey(row[0])
    const link = links.get(`${employerAt}|${disclosedKey}`)
    const key = link?.key ?? disclosedKey
    const name = nameOnly(link?.name) || spelling
    const linkedName = Boolean(link?.name)
    const id = `${employerAt}|${key}`
    if (!groups.has(id)) groups.set(id, { key, name, linkedName, employerAt, years: new Set(), spellings: new Set(), recordShards: new Set() })
    const group = groups.get(id)
    // Prefer the existing link's canonical spelling, then choose deterministically among case
    // or punctuation variants of the same key, irrespective of the input rows' order.
    if ((linkedName && !group.linkedName) || (linkedName === group.linkedName && alphabetically(name, group.name) < 0)) {
      group.name = name
      group.linkedName = linkedName
    }
    group.years.add(yearAt)
    group.spellings.add(spelling)
    group.spellings.add(name)
    group.recordShards.add(surnameShard(row[0]))
  }
  return [...groups.values()].sort((a, b) => alphabetically(a.key, b.key) || a.employerAt - b.employerAt)
    .map((group) => [group.key, group.name, group.employerAt,
      [...group.years].sort(numerically), [...group.spellings].sort(alphabetically), [...group.recordShards].sort(alphabetically)])
}

/**
 * Match and filter before combining documents by their existing group key. Each spelling must
 * satisfy the entire query on its own; tokens from different aliases are never combined.
 * employerIds/yearIds are Sets of indexes, or null for all. Summary arrays contain only the
 * documents and periods that passed the filters, ready for pagination and original-row loading.
 */
export const searchNameSearchDocuments = (documents, query, { employerIds = null, yearIds = null } = {}) => {
  const wanted = queryWords(query)
  if (!wanted.length) return []
  const groups = new Map()
  for (const document of documents) {
    const [key, name, employerAt, periods, spellings, recordShards] = document
    if (employerIds && !employerIds.has(employerAt)) continue
    const years = yearIds ? periods.filter((year) => yearIds.has(year)) : periods
    if (!years.length) continue
    // Query words are already normalized. Repeating that work for every spelling in a common
    // two-letter bucket adds noticeable typing latency; a complete-word match cannot improve.
    // Among complete matches, a spelling whose whole surname was typed comes first: "smith" lists
    // the Smiths before Armstrong-Smith, and before a Smith who is only a given name.
    let tier = null
    let surname = 1
    const prepared = documentWords(document)
    for (let at = 0; at < prepared.length; at += 1) {
      const matched = matchWords(prepared[at], wanted)
      if (matched === null) continue
      const whole = nameSearchTokens(personKey(spellings[at]).split('|')[0]).every((word) => wanted.includes(word)) ? 0 : 1
      if (tier === null || matched < tier || (matched === tier && whole < surname)) { tier = matched; surname = whole }
      if (tier === 0 && surname === 0) break
    }
    if (tier === null) continue
    const group = groups.get(key)
    // Most results have one employer document. Copy its already-unique arrays directly instead
    // of allocating four Sets and converting them back to arrays for every result on each keypress.
    if (!group) {
      groups.set(key, { key, name, tier, surname, employerIds: [employerAt], years: [...years], spellings: [...spellings], recordShards: [...recordShards] })
      continue
    }
    if (tier < group.tier || (tier === group.tier && surname < group.surname)) { group.tier = tier; group.surname = surname }
    if (alphabetically(name, group.name) < 0) group.name = name
    if (!group.employerIds.includes(employerAt)) group.employerIds.push(employerAt)
    for (const year of years) if (!group.years.includes(year)) group.years.push(year)
    for (const spelling of spellings) if (!group.spellings.includes(spelling)) group.spellings.push(spelling)
    for (const shard of recordShards) if (!group.recordShards.includes(shard)) group.recordShards.push(shard)
  }
  return [...groups.values()].sort((a, b) => a.tier - b.tier || a.surname - b.surname || alphabetically(a.key, b.key))
    .map((group) => ({ ...group,
      employerIds: group.employerIds.sort(numerically), years: group.years.sort(numerically),
      spellings: group.spellings.sort(alphabetically), recordShards: group.recordShards.sort(alphabetically) }))
}
