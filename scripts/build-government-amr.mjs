// Builds src/government/amrData.js and research/audit/amr-review.json from the vendored BC Laws
// "Acts – Ministers' Responsibilities" (AMR) snapshots.
//
// Reads only what scripts/fetch-bclaws-amr.mjs left in research/legislation/amr/ — it never
// touches the network — plus two hand-kept files beside it:
//
//   crosswalk.json   minister title + the dates it holds for -> PofBC ministry episode id
//   oic-dates.json   OIC -> approved/effective date checked by hand (optional; wins over Resumés)
//   act-aliases.json an Act title no statreg link ever carried -> its statreg id, with evidence
//
// What it writes keeps two kinds of date apart (see scripts/lib/amr.mjs):
//
//   AMR_LISTINGS     each snapshot and the period its pages state — a listing period, never an
//                    effective date;
//   AMR_CHANGES      Act-by-Act differences between consecutive snapshots, with an effectiveDate
//                    only where exactly one new OIC explains the gap and its date is established;
//   AMR_ASSIGNMENTS  each run of an Act under one minister, with effectiveFrom/effectiveTo taken
//                    from those changes (basis "oic-resume"/"oic-checked"), or bounded by the
//                    snapshots (basis "bounded"), or before coverage.
//
// Everything that needs a person goes to research/audit/amr-review.json.
//
//   npm run build:amr

import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { MINISTRY_EPISODES } from '../src/government/episodes.js'
import { AMR_ATTRIBUTION, AMR_COLLECTION, AMR_LICENCE } from '../src/government/amrLicence.js'
import {
  buildListing, crosswalkLookup, dateGap, diffListings, indexResumes, keyActs, listingDate, parseAmrPage, parseResume, possibleRetitles
} from './lib/amr.mjs'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const AMR_DIR = join(ROOT, 'research/legislation/amr')
const OUT = join(ROOT, 'src/government/amrData.js')
const REVIEW = join(ROOT, 'research/audit/amr-review.json')

const readJson = (path, fallback) => (existsSync(path) ? JSON.parse(readFileSync(path, 'utf8')) : fallback)

/** Loads and parses every vendored snapshot, oldest first, the current listing last. */
export const loadListings = (dir = AMR_DIR) => {
  const manifest = readJson(join(dir, 'manifest.json'), null)
  if (!manifest) throw new Error(`no AMR manifest in ${dir}; run npm run fetch:amr`)
  return {
    manifest,
    listings: manifest.snapshots
      .filter((snapshot) => snapshot.documents.length)
      .map((snapshot) => buildListing({
        id: snapshot.key,
        title: snapshot.title,
        kind: snapshot.kind,
        pages: snapshot.documents.map((doc) => ({
          docId: doc.id,
          url: doc.url,
          page: parseAmrPage(readFileSync(join(dir, doc.file), 'utf8'))
        }))
      }))
  }
}

export const loadResumeIndex = (dir = AMR_DIR) => {
  const manifest = readJson(join(dir, 'oic-resumes.json'), { documents: [] })
  const entries = manifest.documents.flatMap((doc) => parseResume(readFileSync(join(dir, doc.file), 'utf8'), { id: doc.id, url: doc.url }))
  return { manifest, index: indexResumes(entries) }
}

const pick = (object, keys) => Object.fromEntries(keys.filter((key) => object[key] !== undefined).map((key) => [key, object[key]]))

/**
 * The whole pipeline over parsed listings: Act keys, gaps and their dated or bounded changes,
 * assignments, and the episode crosswalk. Pure apart from its inputs, so tests can run it.
 */
export const assemble = ({ listings, resumeIndex = new Map(), manual = {}, crosswalk = [], aliases = [], episodes = MINISTRY_EPISODES }) => {
  const review = []
  const keyProblems = keyActs(listings, aliases)
  for (const listing of listings) review.push(...listing.problems)

  // Act-key problems, one item per Act rather than one per row and snapshot.
  const keyed = new Map()
  for (const problem of keyProblems) {
    const id = `${problem.kind}|${problem.act}|${problem.citation ?? ''}`
    if (!keyed.has(id)) keyed.set(id, { ...pick(problem, ['kind', 'act', 'candidates']), citation: problem.citation ?? null, ministerTitles: new Set(), listings: [] })
    keyed.get(id).ministerTitles.add(problem.ministerTitle)
    if (!keyed.get(id).listings.includes(problem.listing)) keyed.get(id).listings.push(problem.listing)
  }
  for (const item of keyed.values()) review.push({ ...item, ministerTitles: [...item.ministerTitles] })

  const episodeIds = new Set(episodes.map((episode) => episode.id))
  for (const entry of crosswalk) {
    if (entry.episodeId && !episodeIds.has(entry.episodeId)) throw new Error(`crosswalk: unknown episode ${entry.episodeId} for ${entry.amrTitle}`)
  }
  const titleSeen = new Map()
  const episodeAt = (title, listing) => {
    const date = listingDate(listing)
    const found = crosswalkLookup(crosswalk, title, date)
    const id = `${title}|${found.status}`
    if (found.status !== 'mapped') {
      if (!titleSeen.has(id)) titleSeen.set(id, { title, status: found.status, entry: found.entry ?? null, listings: [] })
      titleSeen.get(id).listings.push(listing.id)
    }
    return found.status === 'mapped' ? found.entry.episodeId : null
  }

  // Gaps between consecutive listings.
  const gaps = []
  const changes = []
  for (let i = 1; i < listings.length; i++) {
    const before = listings[i - 1]
    const after = listings[i]
    const diff = diffListings(before, after)
    const gap = dateGap(before, after, diff, { resumeIndex, manual })
    const responsibility = gap.changes.filter((change) => change.type !== 'retitled')
    gaps.push({
      between: [before.id, after.id],
      candidateOics: gap.candidateOics,
      status: gap.status,
      ...(gap.oicDate ? { date: gap.oicDate.date, dateKind: gap.oicDate.dateKind, approvedDate: gap.oicDate.approved, source: gap.oicDate.source } : {}),
      ...(gap.undatedReason ? { undatedReason: gap.undatedReason } : {}),
      changeCount: responsibility.length,
      retitleCount: gap.changes.length - responsibility.length
    })
    for (const pair of possibleRetitles(gap.changes)) {
      review.push({ kind: 'possible-retitle', between: [before.id, after.id], ...pair, note: 'One Act left this minister and one arrived with the same details, and no statreg id ties them. If it is a renaming, add an alias to act-aliases.json.' })
    }
    for (const change of gap.changes) {
      changes.push({
        ...change,
        fromEpisodeId: change.from ? episodeAt(change.from, before) : null,
        toEpisodeId: change.to ? episodeAt(change.to, after) : null
      })
      const last = changes.at(-1)
      // A minister's title changing while the ministry stays the same (a "Minister Responsible
      // for …" added, say) moves every one of its Acts on paper only.
      if (last.type === 'moved' && last.fromEpisodeId && last.fromEpisodeId === last.toEpisodeId) last.sameEpisode = true
    }
    if (responsibility.length && gap.status !== 'dated') {
      review.push({
        kind: { 'multi-oic': 'multi-oic-gap', 'no-new-oic': 'no-new-oic-gap', 'oic-undated': 'oic-undated' }[gap.status],
        between: [before.id, after.id],
        candidateOics: gap.candidateOics,
        changeCount: responsibility.length,
        ...(gap.undatedReason ? { reason: gap.undatedReason } : {}),
        note: gap.status === 'multi-oic'
          ? 'More than one new OIC: read the OIC Schedules and match Appendix items to Acts to date these changes.'
          : gap.status === 'no-new-oic'
            ? 'The listing changed but names no new OIC.'
            : gap.undatedReason === 'effective-date-covers-part'
              ? 'One new OIC, but its Resumé gives an effective date for only part of it; read the order to see which Acts take which date, then record them in oic-dates.json.'
              : 'One new OIC, but its date could not be established from a Resumé; add it to oic-dates.json once checked.'
      })
    }
    if (before.baseOics.join() !== after.baseOics.join()) {
      review.push({ kind: 'base-oic-change', between: [before.id, after.id], from: before.baseOics, to: after.baseOics, changeCount: responsibility.length })
    }
  }
  for (const change of changes) {
    if (change.type === 'retitled') {
      review.push({ kind: 'retitled', statregId: change.statregId, between: change.betweenListings, fromTitle: change.fromTitle, toTitle: change.toTitle, note: 'Same statreg id under a new short title: treated as a retitle, not a reassignment. Confirm.' })
    }
  }
  const scopeChanges = changes.filter((change) => change.type === 'scope-changed')
  for (const change of scopeChanges) {
    review.push({ kind: 'scope-changed', act: change.act, statregId: change.statregId, ministerTitle: change.from, between: change.betweenListings, ...(change.punctuationOnly ? { punctuationOnly: true } : {}), detailsBefore: change.detailsBefore, detailsAfter: change.detailsAfter })
  }
  for (const listing of listings) {
    if (listing.periodWording === 'as-at') review.push({ kind: 'period-wording-variant', listing: listing.id, text: listing.periodText, note: '"as at" wording: the period is a single day, and rows carry full citations and no statreg links.' })
    if (listing.kind === 'current') review.push({ kind: 'current-listing-provisional', listing: listing.id, periodTo: listing.periodTo, note: 'The current listing changes in place and is ahead of the newest historical snapshot; it is included as a provisional last listing.' })
  }

  // Assignments: runs of an Act under one minister across consecutive listings.
  const changeFor = (gapIndex, actKey, test) => changes.find((change) => change.betweenListings[0] === listings[gapIndex - 1].id
    && change.betweenListings[1] === listings[gapIndex].id && change.actKey === actKey && test(change))
  const presence = new Map()
  listings.forEach((listing, index) => {
    for (const row of listing.rows) {
      const key = `${row.actKey}|${row.ministerTitle}`
      if (!presence.has(key)) presence.set(key, new Map())
      presence.get(key).set(index, row)
    }
  })
  const bound = (gapIndex, change) => {
    if (!change) return { date: null, basis: 'bounded', between: [listings[gapIndex - 1].id, listings[gapIndex].id], oic: null }
    if (change.effectiveDate) return { date: change.effectiveDate, basis: change.basis, dateKind: change.dateKind, oic: change.oic, source: change.source }
    return { date: null, basis: 'bounded', between: change.betweenListings, candidateOics: change.candidateOics, oic: null }
  }
  const assignments = []
  for (const [key, seen] of presence) {
    const indexes = [...seen.keys()].sort((a, b) => a - b)
    let start = indexes[0]
    for (let k = 0; k < indexes.length; k++) {
      const index = indexes[k]
      const next = indexes[k + 1]
      if (next === index + 1) continue
      const first = seen.get(start)
      const last = seen.get(index)
      const ministerTitle = last.ministerTitle
      const runEpisodes = []
      for (let i = start; i <= index; i++) {
        const episodeId = episodeAt(ministerTitle, listings[i])
        const prior = runEpisodes.at(-1)
        if (prior && prior.episodeId === episodeId) prior.lastListing = listings[i].id
        else runEpisodes.push({ episodeId, firstListing: listings[i].id, lastListing: listings[i].id })
      }
      assignments.push({
        actKey: last.actKey,
        act: { statregId: last.statregId ?? null, title: last.actTitle, ...(last.citation ? { citation: last.citation } : {}), ...(first.actTitle !== last.actTitle ? { firstTitle: first.actTitle } : {}), ...(last.annotation ? { annotation: last.annotation } : {}) },
        statregSource: last.statregSource,
        ministerTitle,
        episodeId: runEpisodes.length === 1 ? runEpisodes[0].episodeId : null,
        episodes: runEpisodes,
        scope: last.scope,
        detailsRaw: last.detailsRaw,
        ...(first.detailsRaw !== last.detailsRaw ? { detailsFirst: first.detailsRaw } : {}),
        seenIn: { first: listings[start].id, last: listings[index].id, count: index - start + 1 },
        effectiveFrom: start === 0
          ? { date: null, basis: 'before-coverage' }
          : bound(start, changeFor(start, last.actKey, (change) => change.to === ministerTitle && (change.type === 'moved' || change.type === 'added'))),
        effectiveTo: index === listings.length - 1
          ? null
          : bound(index + 1, changeFor(index + 1, last.actKey, (change) => change.from === ministerTitle && (change.type === 'moved' || change.type === 'removed')))
      })
      start = next
    }
  }
  assignments.sort((a, b) => a.act.title.localeCompare(b.act.title) || a.seenIn.first.localeCompare(b.seenIn.first) || a.ministerTitle.localeCompare(b.ministerTitle))

  for (const seen of titleSeen.values()) {
    review.push({
      kind: seen.status === 'ambiguous' ? 'ambiguous-title' : 'unmapped-title',
      value: seen.title,
      listings: [...new Set(seen.listings)],
      ...(seen.entry?.reason ? { reason: seen.entry.reason } : {}),
      note: seen.status === 'missing' ? 'Not in crosswalk.json.' : seen.status === 'ambiguous' ? 'More than one crosswalk entry covers these listings.' : 'In crosswalk.json without an episode.'
    })
  }

  return { listings, gaps, changes, assignments, review }
}

// The generated module is kept small: a field that is null, or that repeats another, is left out.
// effectiveDate is always written, null included, since its absence would read as unknown.
const dropEmpty = (object) => Object.fromEntries(Object.entries(object).filter(([key, value]) => value !== null && value !== undefined || key === 'effectiveDate'))

export const compactChange = (change) => {
  const sameDetails = change.detailsBefore !== undefined && change.detailsBefore === change.detailsAfter
  return dropEmpty({
    ...pick(change, ['type', 'act', 'statregId', 'fromTitle', 'toTitle', 'from', 'to', 'fromEpisodeId', 'toEpisodeId', 'sameEpisode', 'punctuationOnly']),
    actKey: change.statregId ? null : change.actKey,
    ...(sameDetails ? { details: change.detailsBefore } : pick(change, ['detailsBefore', 'detailsAfter'])),
    ...pick(change, ['actStillListed', 'actPreviouslyListed', 'betweenListings', 'candidateOics', 'effectiveDate', 'dateKind', 'approvedDate', 'basis', 'oic', 'source'])
  })
}

export const compactAssignment = (assignment) => dropEmpty({
  ...assignment,
  actKey: assignment.act.statregId ? null : assignment.actKey,
  episodeId: assignment.episodeId,
  // One episode throughout is said by episodeId alone; episodes lists them only where they differ.
  episodes: assignment.episodes.length > 1 ? assignment.episodes : null,
  effectiveFrom: dropEmpty(assignment.effectiveFrom),
  effectiveTo: assignment.effectiveTo ? dropEmpty(assignment.effectiveTo) : null
})

const KIND_ORDER = [
  'period-unparsed', 'period-disagrees', 'minister-title-from-heading', 'unmapped-title', 'ambiguous-title',
  'multi-oic-gap', 'oic-undated', 'no-new-oic-gap', 'base-oic-change', 'statreg-missing', 'statreg-ambiguous', 'possible-retitle',
  'retitled', 'scope-changed', 'period-wording-variant', 'current-listing-provisional'
]

const main = () => {
  const { manifest, listings } = loadListings()
  const { manifest: resumes, index: resumeIndex } = loadResumeIndex()
  const manual = readJson(join(AMR_DIR, 'oic-dates.json'), { oics: {} }).oics ?? {}
  const crosswalk = readJson(join(AMR_DIR, 'crosswalk.json'), { entries: [] }).entries
  const aliases = readJson(join(AMR_DIR, 'act-aliases.json'), { aliases: [] }).aliases
  const result = assemble({ listings, resumeIndex, manual, crosswalk, aliases })

  const source = {
    collection: AMR_COLLECTION.title,
    url: AMR_COLLECTION.url,
    fetched: manifest.lastFetched,
    resumesFetched: resumes.lastFetched ?? null,
    licence: AMR_LICENCE.name,
    licenceUrl: AMR_LICENCE.url,
    attribution: AMR_ATTRIBUTION,
    note: 'Derived from the vendored raw pages in research/legislation/amr/raw (see manifest.json for each page’s URL, fetch date and sha256). Listing periods are the periods the pages state, not effective dates. A change or assignment carries a date only when exactly one new Order in Council explains the gap between two snapshots and that order’s date is established from its BC Laws Resumé (or a hand-checked entry); dateKind says whether it is the order’s stated effective date or its approval date. Otherwise the date is null and the two bounding snapshots are given.'
  }
  const listingsOut = result.listings.map((listing) => ({
    id: listing.id,
    title: listing.title,
    kind: listing.kind,
    docIds: listing.docIds,
    periodFrom: listing.periodFrom,
    periodTo: listing.periodTo,
    periodWording: listing.periodWording,
    baseOics: listing.baseOics,
    amendingOics: listing.amendingOics,
    periodText: listing.periodText,
    rowCount: listing.rows.length,
    ministerTitles: [...new Set(listing.rows.map((row) => row.ministerTitle))]
  }))
  const changesOut = result.changes.map(compactChange)
  const assignmentsOut = result.assignments.map(compactAssignment)

  const counts = {
    listings: listingsOut.length,
    rows: listingsOut.reduce((n, l) => n + l.rowCount, 0),
    acts: new Set(result.assignments.map((a) => a.actKey)).size,
    assignments: result.assignments.length,
    changes: changesOut.filter((c) => c.type !== 'retitled').length,
    changesDated: changesOut.filter((c) => c.effectiveDate).length,
    retitles: changesOut.filter((c) => c.type === 'retitled').length
  }

  const json = (value) => JSON.stringify(value)
  const out = `// Generated by scripts/build-government-amr.mjs — do not edit.
//
// Which minister administered which Act, from BC Laws' "Acts – Ministers' Responsibilities"
// snapshots (December 2015 on), keyed by the Act's statreg id so a renamed Act is not read as
// reassigned. AMR_LISTINGS are the snapshots and the periods their pages state; those periods
// are never effective dates. AMR_CHANGES and AMR_ASSIGNMENTS carry an effective date only where
// one Order in Council dates it (basis "oic-resume" or "oic-checked"); otherwise the date is null
// and the bounding snapshots are given (basis "bounded").
//
// ${AMR_ATTRIBUTION}

export const AMR_SOURCE = ${json(source)}

export const AMR_COUNTS = ${json(counts)}

export const AMR_LISTINGS = ${json(listingsOut)}

export const AMR_GAPS = ${json(result.gaps)}

export const AMR_CHANGES = ${json(changesOut)}

export const AMR_ASSIGNMENTS = ${json(assignmentsOut)}
`
  writeFileSync(OUT, out)

  const items = result.review.sort((a, b) => KIND_ORDER.indexOf(a.kind) - KIND_ORDER.indexOf(b.kind))
  const byKind = Object.fromEntries(KIND_ORDER.map((kind) => [kind, items.filter((item) => item.kind === kind).length]).filter(([, n]) => n))
  const unknownKinds = [...new Set(items.map((item) => item.kind))].filter((kind) => !KIND_ORDER.includes(kind))
  if (unknownKinds.length) throw new Error(`review kinds without an order: ${unknownKinds.join(', ')}`)
  writeFileSync(REVIEW, `${JSON.stringify({
    schema: 'amr-review/1',
    generatedBy: 'scripts/build-government-amr.mjs',
    fetched: manifest.lastFetched,
    counts: byKind,
    items
  }, null, 2)}\n`)

  console.log(`AMR: ${counts.listings} listings, ${counts.rows} rows, ${counts.acts} acts, ${counts.assignments} assignments`)
  console.log(`     ${counts.changes} changes (${counts.changesDated} dated), ${counts.retitles} retitles`)
  console.log(`     review: ${Object.entries(byKind).map(([k, n]) => `${k} ${n}`).join(', ')}`)
  console.log(`     wrote ${OUT.replace(`${ROOT}/`, '')} (${(Buffer.byteLength(out) / 1024).toFixed(0)} KB) and ${REVIEW.replace(`${ROOT}/`, '')}`)
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main()
