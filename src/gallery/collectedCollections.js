// Downloaded artwork and supplied originals retain their own format and source.
// A date on a report is a sighting, never an inferred logo adoption date.
import { COLLECTED_BODIES, COLLECTED_SPECIMENS } from './collectedData.js'
import { COLLECTED_DISPLAY } from './collectedDisplay.js'

/**
 * The file a body's card shows: one with a display copy that keeps its own colours on the light
 * page, else any with a display copy, else the first file. A display copy is drawn for the page
 * in both themes, where a raster file still sits on a plate of its own.
 */
const coverOf = (all) => {
  const assets = all.filter((asset) => !asset.variantOf)
  return (assets.find((asset) => COLLECTED_DISPLAY[asset.id] && !COLLECTED_DISPLAY[asset.id].light.recoloured) ??
    assets.find((asset) => COLLECTED_DISPLAY[asset.id]) ?? assets[0])?.id
}

export const assetUrl = (path, base = import.meta.env?.BASE_URL ?? '/') =>
  `${base.replace(/\/?$/, '/')}${path.replace(/^\//, '')}`

/**
 * When a design's files were seen: one or two sightings as given, more as the years they span. A
 * retrieval date is not a sighting of the logo.
 */
const yearOf = (date) => Number(String(date).match(/\d{4}/)?.[0])

/** A date as a card can show it: a short one as given; a sentence about one, as the year it names. */
const shortDate = (date) => {
  if (!date || String(date).length <= 24) return date
  return yearOf(date) ? `about ${yearOf(date)}` : null
}

/** The years a date covers: a fiscal year such as 1982/83 covers both. */
const yearsOf = (date) => {
  const fiscal = String(date).match(/(\d{4})\/(\d{2})\b/)
  return fiscal ? [Number(fiscal[1]), Number(fiscal[1].slice(0, 2) + fiscal[2])] : [yearOf(date)]
}

const seenDates = (versions) => {
  const all = [...new Set(versions.flatMap((each) => [each.sourceDate, ...(each.alsoSeen ?? []).map((seen) => seen.date)]).map(shortDate).filter(Boolean))]
  // A bare year another date already covers says nothing more (1982/83 and 1983).
  const dates = all.filter((date) => !/^\d{4}$/.test(date) || !all.some((other) => other !== date && yearsOf(other).includes(Number(date))))
    .sort((a, b) => yearOf(a) - yearOf(b))
  if (dates.length < 3 || !dates.every(yearOf)) return dates.join(' and ')
  const [first, last] = [yearOf(dates[0]), yearOf(dates.at(-1))]
  return first === last ? String(first) : `${first}–${last}`
}

/** A note's first sentence, for a card: the rest is on the mark's own page. */
const firstSentence = (text = '') => {
  const end = String(text).search(/[.!?](?=\s+[A-Z“"(])/)
  return end < 0 ? text : String(text).slice(0, end + 1)
}

/** A body's files as one entry per design, each with its other colourways as versions, oldest first. */
const designsOf = (assets) => assets.filter((asset) => !asset.variantOf).map((asset) => {
  const versions = [asset, ...assets.filter((each) => each.variantOf === asset.id)]
  return { asset, versions }
}).map((design, order) => ({ ...design, order, year: Math.min(...design.versions.flatMap((each) => [each.sourceDate, ...(each.alsoSeen ?? []).map((seen) => seen.date)]).map(yearOf).filter(Boolean)) }))
  // Undated designs keep their place after the dated ones.
  .sort((a, b) => (Number.isFinite(a.year) ? a.year : 9999) - (Number.isFinite(b.year) ? b.year : 9999) || a.order - b.order)

/**
 * A collected file as a gallery entry; `timeline` places a program's specimen on its timeline, and
 * `owner` is the body it was collected for, kept when its collection holds a body's successors too.
 */
const collectedEntry = (asset, timeline, owner, versions = [asset]) => ({
  id: asset.id,
  kind: 'collected',
  ...(timeline ? { timeline } : {}),
  ...(owner ? { owner } : {}),
  label: versions.length > 1 ? asset.publisher : asset.label,
  // A card says what the mark is in a sentence; its full account, versions and sources are on its page.
  note: firstSentence(asset.notes),
  years: seenDates(versions) ? `Seen ${seenDates(versions)}` : 'Logo dates unestablished',
  asset,
  ...(versions.length > 1 ? { versions } : {}),
  identity: {
    provenance: asset.reconstruction ? 'third_party_reconstruction' : asset.supplied ? 'original_supplied' : asset.isVector ? 'published_vector' : 'published_raster',
    fidelity: 'source compared',
    fidelityNote: asset.fidelityNote,
    applicability: {
      kind: seenDates(versions) ? 'dated_specimen' : 'unknown',
      years: seenDates(versions) || 'undated',
      note: asset.sourceDate
        ? 'This is the date of the cited specimen, not a verified first use or adoption date. ' + (asset.dateNote || '')
        : `Collected on ${asset.observedDate}. A retrieval date does not establish when the design was adopted.`,
    },
    rights: {
      status: 'unresolved',
      note: 'The mark belongs to its respective owner. No permission to reproduce it here has been sought or documented.',
    },
  },
})

const BODIES = new Map(COLLECTED_BODIES.map((body) => [body.id, body]))
const kindOf = (body) => body.kind === 'health-authority' ? 'health organization' : 'Crown corporation'

/** A body's collected files as gallery entries. */
export const collectedEntriesOf = (bodyId) => designsOf(BODIES.get(bodyId)?.assets ?? [])
  .map(({ asset, versions }) => collectedEntry(asset, undefined, bodyId, versions))

/** Published specimens folded into a researched collection rather than a one-off timeline. */
export const specimenEntriesOf = (program, timeline) => designsOf(COLLECTED_SPECIMENS.find((each) => each.program === program)?.assets ?? [])
  .map(({ asset, versions }) => collectedEntry(asset, timeline, undefined, versions))

const collectionOf = (body) => ({
  id: `collected-${body.id}`,
  shelf: 'bodies',
  graphNode: body.id,
  fileCollection: true,
  label: body.shortName || body.name,
  body: `${body.current ? 'Current' : 'Former'} ${kindOf(body)}`,
  years: `${body.from ?? '?'}–${body.current ? 'present' : body.to ?? '?'}`,
  // The body's own account where it has one; that its years are not its logos' is said on each card
  // (“Seen …”) and under About.
  intro: body.notes || 'Collected artwork, with its source recorded for each file.',
  cover: coverOf(body.assets),
  entries: collectedEntriesOf(body.id),
})

/**
 * Bodies that carried on as another under a new name, each with the body it became, as the
 * government history records them (historyData.js: the body's `became`, with no other body holding
 * logos here becoming the same one). Each line is shown as one collection — the last body's, under
 * which the earlier ones are an era each — rather than as a collection per name. BC Ferries' and
 * BC Transit's earlier names are eras of their researched histories instead (collections.js).
 *
 * Only one-to-one lines are folded. An amalgamation (several bodies becoming one, as the 2001 health
 * regions did) or a split (one body's work passing to several) is not a line of names: putting a
 * predecessor's logos on one successor's timeline would claim a single lineage the history does
 * not record, and would hide that the others shared it. Those bodies keep a collection each, and
 * their links stay in the government diagram. collectedCollections.test.js checks every fold.
 */
export const CONTINUATIONS = [
  ['pacific-great-eastern-railway', 'bc-railway-company'],
  ['bc-enterprise-corporation', 'bc-pavilion-corporation'],
  ['bc-assets-and-land-corporation', 'land-and-water-bc'],
  ['oil-and-gas-commission', 'bc-energy-regulator'],
  ['partnerships-bc', 'infrastructure-bc']
]

const nameOf = (body) => body.shortName && body.shortName !== body.name ? `${body.name} (${body.shortName})` : body.name

/** A body's years under its own name, as an era of the line it belongs to. */
const nameEra = (body, from, to, next) => {
  const years = `${from ?? '?'}–${to ?? 'present'}`
  const sources = [...new Map(body.assets
    .filter((asset) => /^https:\/\//.test(asset.sourcePage || asset.sourceUrl || ''))
    .map((asset) => [asset.sourcePage || asset.sourceUrl, { title: asset.publisher, url: asset.sourcePage || asset.sourceUrl }])).values()]
  return {
    id: `name-${body.id}`,
    status: 'held',
    years,
    label: nameOf(body),
    note: next
      ? `The body under this name, until it became ${next.name} in ${to}. Its files are below, each with its own source and date.`
      : `The body under its present name. Its files are below, each with its own source and date.`,
    applicability: {
      kind: 'unknown',
      years,
      note: 'These are the body’s years under this name, not the dates of its logos: each file gives when it was seen.'
    },
    sources,
    entries: collectedEntriesOf(body.id)
  }
}

/** One collection for a line of names: the last body's, with an era for each name, oldest first. */
const lineCollection = (line) => {
  const bodies = line.map((id) => BODIES.get(id))
  const last = bodies.at(-1)
  const eras = bodies.map((body, at) => nameEra(body, at ? bodies[at - 1].to : body.from, at < bodies.length - 1 ? body.to : last.current ? null : last.to, bodies[at + 1]))
  const earlier = bodies.slice(0, -1)
  return {
    ...collectionOf(last),
    graphNodes: [last.id, ...earlier.map((body) => body.id)],
    aliases: earlier.map((body) => `collected-${body.id}`),
    body: `${last.current ? 'Current' : 'Former'} ${kindOf(last)} · formerly ${earlier.map((body) => body.name).join(', then ')}`,
    years: `${bodies[0].from ?? '?'}–${last.current ? 'present' : last.to ?? '?'}`,
    intro: `One body under ${['', 'one', 'two', 'three', 'four'][bodies.length] ?? bodies.length} names: ${bodies.map((body) => body.name).join(', then ')}. ` +
      'Each name is an era below, with the artwork collected under it and its source recorded for each file. ' +
      'The years are the body’s, not its logos’.',
    cover: coverOf(bodies.flatMap((body) => body.assets).reverse()) ?? last.assets[0]?.id,
    entries: undefined,
    eras
  }
}

/** Each body's line of names, oldest first, built from the links above. */
const LINES = (() => {
  const nextOf = new Map(CONTINUATIONS)
  const starts = CONTINUATIONS.map(([from]) => from).filter((id) => !CONTINUATIONS.some(([, to]) => to === id))
  return starts.map((start) => {
    const line = [start]
    while (nextOf.has(line.at(-1))) line.push(nextOf.get(line.at(-1)))
    return line
  })
})()
const HELD_LINES = LINES.filter((line) => line.every((id) => BODIES.get(id)?.assets.length))
const IN_A_LINE = new Set(HELD_LINES.flat())

export const COLLECTED_COLLECTIONS = [
  ...COLLECTED_BODIES.filter((body) => body.assets.length && !IN_A_LINE.has(body.id)).map(collectionOf),
  ...HELD_LINES.map(lineCollection)
].sort((a, b) => COLLECTED_BODIES.findIndex((body) => body.id === a.graphNode) - COLLECTED_BODIES.findIndex((body) => body.id === b.graphNode))

/** The bodies a collection holds the logos of: its own, and those of any names it went by before. */
export const nodesOf = (collection) => collection.graphNodes ?? (collection.graphNode ? [collection.graphNode] : [])

// The one-off programs' published specimens (WorkBC, WelcomeBC, StrongerBC, Canada Starts Here, Where
// ideas work). They are not bodies of the inventory: each program's collection is not shelved, and
// its files are reached from the eras of its timeline (timelines.js), which they keep in view.
export const SPECIMEN_COLLECTIONS = COLLECTED_SPECIMENS.map(({ program, assets }) => ({
  id: `specimens-${program}`,
  shelf: 'specimens',
  fileCollection: true,
  label: assets[0]?.publisher ?? program,
  intro: 'Published vector specimens, each with its source recorded. A capture or document date is a sighting, not an adoption date.',
  entries: designsOf(assets).map(({ asset, versions }) => collectedEntry(asset, program, undefined, versions))
}))

export const COLLECTION_RESEARCH = new Map(COLLECTED_BODIES.map((body) => [body.id, body]))

export const researchLabel = (record) => {
  if (record?.status === 'source-found') return 'Source located · artwork wanted'
  if (record?.status === 'unresolved') return 'Wanted · searched'
  return 'Wanted'
}
