// Which differently written names at one employer are one person. Employers change how they write
// names ("Garant, D." one year, "Garant, Daniel" another), sources disagree, and extraction splits
// letters off ("Nevill, T homas"). Each spelling of a name at an employer is either joined to one
// fuller spelling there, with the evidence and the assumption behind it, or kept apart with the
// reason. Nothing here joins names across employers.
//
// A join is:
//   verified — the records establish it: an extraction split, a distinctive position held under both
//              spellings, or a reviewed decision (research/salaries/name-links/reviewed.json).
//   likely   — an assumption: the only fuller name at the employer that agrees, never in the same
//              period, and within LINK_RULES.maxGapYears of it. Between neighbouring years (a year
//              apart or less) pay may not jump more than LINK_RULES.maxPayRatio times; over longer
//              gaps a jump is a promotion as often as a different person, so it is not weighed.
//   Both spellings in one period keep them apart, unless every such period has the same payment
//   under both: one record disclosed twice, which verifies the join.
// Everything else — several fuller names fit, both spellings in one period, a long gap, a pay jump,
// a reviewed rejection — is kept apart, and listed with its reason.

import { nameOnly, nameParts, personKey, surnameShard } from './people.js'
import { titleKey } from './positions.js'

export const LINK_RULES = { maxGapYears: 6, maxPayRatio: 3, distinctiveTitle: 3 }

export { nameOnly }

const yearOf = (label) => Number(String(label).slice(0, 4))

/** How much a spelling says: a full first name outweighs any number of initials. */
const information = (given) => (given[0]?.length > 1 ? 1000 : 0) + given.join('').length * 10 + given.length

/** "T homas" read as the extraction split it: the first two given parts rejoined, else null. */
const rejoined = (given) => (given.length > 1 && given[0].length === 1 ? [given[0] + given[1], ...given.slice(2)] : null)

/**
 * Whether two names can be one person's: the same surname, and each given name the same, an initial
 * of the other, or — the first only — the start of the other of three letters or more ("Jeff",
 * "Jeffrey"). Middle names one spelling leaves out do not disagree.
 */
export const compatibleNames = (a, b) => {
  const x = nameParts(nameOnly(a))
  const y = nameParts(nameOnly(b))
  if (!x.surname || x.surname !== y.surname || !x.given.length || !y.given.length) return false
  return x.given.slice(0, Math.min(x.given.length, y.given.length)).every((left, at) => {
    const right = y.given[at]
    if (left === right) return true
    if (left[0] === right[0] && (left.length === 1 || right.length === 1)) return true
    const [short, long] = left.length < right.length ? [left, right] : [right, left]
    return at === 0 && short.length >= 3 && long.startsWith(short)
  })
}

const shown = (spelling) => spelling.reviewedSpelling ?? spelling.names[0]
const matchable = (spelling) => nameOnly(spelling.names[0])

/**
 * Every spelling-to-spelling decision for the rows given (the people index's row schema).
 * `years` are period labels; `employers` the index's [name, sector, body, slug] rows; `reviewed`
 * decisions by employer slug and both disclosed names: { employer, names: [a, b], decision:
 * 'verified' | 'reject', note }.
 * Returns { links: [{ employer, key, name, aliases: [{ key, name, status, reason }] }], decisions }.
 */
export const findNameLinks = (rows, { years, employers, reviewed = [] }) => {
  const employerAt = new Map(employers.map((entry, at) => [entry[3], at]))
  const explicitlyReviewed = new Set(reviewed.filter((entry) => entry.decision === 'verified').flatMap((entry) =>
    entry.names.map((name) => `${employerAt.get(entry.employer)}|${personKey(nameOnly(name))}`)))
  const spellings = new Map()
  for (const row of rows) {
    if (!row[0]) continue
    const key = personKey(nameOnly(row[0]))
    const id = `${row[4]}|${key}`
    if (!spellings.has(id)) {
      const { surname, given } = nameParts(nameOnly(row[0]))
      if (!surname || (!given.length && !explicitlyReviewed.has(id))) continue
      spellings.set(id, { id, employer: row[4], key, surname, given, raw: new Map(), nameCounts: new Map(), periods: new Map(), titles: new Set() })
    }
    const spelling = spellings.get(id)
    const raw = personKey(row[0])
    if (!spelling.raw.has(raw)) spelling.raw.set(raw, new Map())
    spelling.raw.get(raw).set(row[0], (spelling.raw.get(raw).get(row[0]) ?? 0) + 1)
    spelling.nameCounts.set(row[0], (spelling.nameCounts.get(row[0]) ?? 0) + 1)
    spelling.periods.set(row[5], Math.max(spelling.periods.get(row[5]) ?? 0, row[2]))
    if (row[1] && titleKey(row[1])) spelling.titles.add(titleKey(row[1]))
  }
  for (const spelling of spellings.values()) {
    // A name written without a position in it is shown before one with.
    spelling.names = [...spelling.nameCounts].sort((a, b) => Number(nameOnly(b[0]) === b[0]) - Number(nameOnly(a[0]) === a[0]) || b[1] - a[1]).map(([name]) => name)
    spelling.info = information(spelling.given)
    spelling.count = [...spelling.nameCounts.values()].reduce((sum, value) => sum + value, 0)
  }
  for (const entry of reviewed) {
    if (!entry.displaySpelling) continue
    const spelling = spellings.get(`${employerAt.get(entry.employer)}|${personKey(nameOnly(entry.displaySpelling))}`)
    if (!spelling?.nameCounts.has(entry.displaySpelling)) throw new Error('A reviewed display spelling must exist in the original observations')
    spelling.reviewedSpelling = entry.displaySpelling
  }

  // How many spellings at an employer held each title: a title few people hold says more.
  const holders = new Map()
  for (const spelling of spellings.values()) {
    for (const title of spelling.titles) holders.set(`${spelling.employer}|${title}`, (holders.get(`${spelling.employer}|${title}`) ?? 0) + 1)
  }
  const reviewOf = new Map()
  for (const entry of reviewed) {
    const [a, b] = entry.names.map((name) => personKey(nameOnly(name)))
    reviewOf.set(`${entry.employer}|${[a, b].sort().join('~')}`, entry)
  }

  const buckets = new Map()
  for (const spelling of spellings.values()) {
    const bucket = `${spelling.employer}|${spelling.surname}`
    if (!buckets.has(bucket)) buckets.set(bucket, [])
    buckets.get(bucket).push(spelling)
  }

  const decisions = []
  const placed = new Set()
  const parent = new Map()
  const find = (spelling) => {
    let at = spelling
    while (parent.get(at.id) && parent.get(at.id) !== at) at = parent.get(at.id)
    return at
  }
  const membersOf = new Map()
  const members = (root) => membersOf.get(root.id) ?? [root]
  const preferred = new Set(reviewed.filter((entry) => entry.decision === 'verified' && entry.preferredName)
    .map((entry) => `${employerAt.get(entry.employer)}|${personKey(nameOnly(entry.preferredName))}`))
  const fuller = (a, b) => (preferred.has(a.id) !== preferred.has(b.id)
    ? (preferred.has(b.id) ? b : a)
    : (b.info > a.info || (b.info === a.info && b.count > a.count) ? b : a))
  const bestOf = (root) => members(find(root)).reduce(fuller)
  const join = (spelling, other) => {
    const [from, to] = [find(spelling), find(other)]
    if (from === to) return
    parent.set(from.id, to)
    membersOf.set(to.id, [...members(to), ...members(from)])
    membersOf.delete(from.id)
  }

  // An explicit source review can correct a surname. Automatic candidates remain surname-bound.
  for (const review of reviewed) {
    if (review.decision !== 'verified') continue
    const at = employerAt.get(review.employer)
    const pair = review.names.map((name) => spellings.get(`${at}|${personKey(nameOnly(name))}`))
    if (pair.some((spelling) => !spelling) || pair[0] === pair[1]) continue
    if (review.preferredName && !pair.some((spelling) => spelling.key === personKey(nameOnly(review.preferredName)))) {
      throw new Error('A reviewed preferred name must be one of the disclosed spellings')
    }
    const other = review.preferredName ? pair.reduce(fuller) : pair.reduce((a, b) => (
      b.info > a.info || (b.info === a.info && b.id > a.id) ? b : a
    ))
    const spelling = pair.find((each) => each !== other)
    decisions.push({ employer: review.employer, name: shown(spelling), key: spelling.key,
      target: shown(other), targetKey: other.key, status: 'verified', reason: `Reviewed: ${review.note}`,
      ...(review.evidence?.length ? { evidence: review.evidence } : {}),
      pay: Math.max(...spelling.periods.values(), ...other.periods.values()) })
    join(spelling, other)
    placed.add(spelling.id)
    // A corrected source spelling may still have an existing fuller, likely variant.
    // Keep that separate confidence level; a reviewed typo must not erase its old link.
    if (!review.preferredName) placed.add(other.id)
  }

  for (const bucket of buckets.values()) {
    if (bucket.length < 2) continue
    const slug = employers[bucket[0].employer]?.[3]
    // A reviewed correction can move a split spelling out of its old family. Preserve its
    // deterministic rejoining edge as well, without treating other compatible names as verified.
    for (const spelling of bucket.filter((each) => placed.has(each.id))) {
      const split = rejoined(spelling.given)
      const other = split && bucket.find((each) => each !== spelling && each.given.join(' ') === split.join(' '))
      if (!other || placed.has(other.id) || find(other) === find(spelling)) continue
      const review = reviewOf.get(`${slug}|${[spelling.key, other.key].sort().join('~')}`)
      if (review?.decision === 'reject') continue
      const shared = [...spelling.periods.keys()].filter((at) => other.periods.has(at))
      if (shared.some((at) => spelling.periods.get(at) !== other.periods.get(at))) continue
      const target = bestOf(spelling)
      decisions.push({ employer: slug, name: shown(other), key: other.key, target: shown(target), targetKey: target.key,
        status: 'verified', reason: `Extraction split the given name: “${shown(spelling)}” is “${shown(other)}”; its reviewed source spelling is “${shown(target)}”`,
        pay: Math.max(...other.periods.values(), ...spelling.periods.values()) })
      join(other, spelling)
      placed.add(other.id)
    }
    for (const spelling of [...bucket].sort((a, b) => a.info - b.info).reverse()) {
      if (placed.has(spelling.id)) continue
      const split = rejoined(spelling.given)
      const fits = bucket.filter((other) => other !== spelling && other.info > spelling.info && compatibleNames(matchable(spelling), matchable(other)))
      const splitFit = split && bucket.find((other) => other !== spelling && other.given.join(' ') === split.join(' '))
      if (!fits.length && !splitFit) continue
      const roots = [...new Map((splitFit ? [splitFit] : fits).map((other) => [find(other).id, find(other)])).values()]
      const decide = (status, reason, root) => {
        const target = root ? bestOf(root) : null
        decisions.push({ employer: slug, name: shown(spelling), key: spelling.key, target: target && shown(target), targetKey: target?.key, status, reason, pay: Math.max(...spelling.periods.values(), ...(root ? members(root).flatMap((each) => [...each.periods.values()]) : [])) })
        if (root && status !== 'apart') join(spelling, root)
      }
      if (roots.length > 1) {
        decide('apart', `Agrees with ${roots.length} different names here: ${roots.map((root) => `“${shown(bestOf(root))}”`).join(', ')}`)
        continue
      }
      const [root] = roots
      const cluster = members(root)
      const review = cluster.map((each) => reviewOf.get(`${slug}|${[spelling.key, each.key].sort().join('~')}`)).find(Boolean)
      if (review?.decision === 'reject') { decide('apart', `Reviewed: ${review.note}`); continue }
      if (review?.decision === 'verified') { decide('verified', `Reviewed: ${review.note}`, root); continue }
      const conflicting = cluster.find((each) => each.surname === spelling.surname && !splitFit && !compatibleNames(matchable(spelling), matchable(each)))
      if (conflicting) { decide('apart', `Disagrees with “${shown(conflicting)}”, already joined to “${shown(bestOf(root))}”`); continue }
      const theirs = new Map(cluster.flatMap((each) => [...each.periods]))
      const shared = [...spelling.periods.keys()].filter((at) => theirs.has(at))
      const twice = shared.length > 0 && shared.every((at) => spelling.periods.get(at) === theirs.get(at))
      if (shared.length && !twice) { decide('apart', `Both spellings appear in ${years[shared[0]]}: two records in one period`); continue }
      if (twice) { decide('verified', `The same payment under both spellings in ${shared.map((at) => years[at]).join(', ')}: one record disclosed twice`, root); continue }
      if (splitFit) { decide('verified', `Extraction split the given name: “${shown(spelling)}” is “${shown(splitFit)}”`, root); continue }
      const title = [...spelling.titles].find((each) => cluster.some((other) => other.titles.has(each)) && holders.get(`${spelling.employer}|${each}`) <= LINK_RULES.distinctiveTitle)
      // The nearest periods of the two spellings, for the gap and the change in pay between them.
      let nearest = null
      for (const [mine, pay] of spelling.periods) {
        for (const [other, otherPay] of theirs) {
          const gap = Math.abs(yearOf(years[mine]) - yearOf(years[other]))
          if (!nearest || gap < nearest.gap) nearest = { gap, ratio: Math.max(pay, otherPay) / Math.max(1, Math.min(pay, otherPay)), mine, other }
        }
      }
      const span = (mine) => {
        const labels = [...mine.keys()].sort((a, b) => a - b).map((at) => years[at])
        return labels.length > 1 ? `${labels[0]}–${labels.at(-1)}` : labels[0]
      }
      if (title) {
        decide('verified', `Same position under both spellings: “${title}”, held by ${holders.get(`${spelling.employer}|${title}`) === 1 ? 'no one else' : 'few others'} here`, root)
        continue
      }
      if (nearest.gap > LINK_RULES.maxGapYears) { decide('apart', `${nearest.gap} years between “${shown(spelling)}” (${span(spelling.periods)}) and “${shown(bestOf(root))}” (${span(theirs)})`); continue }
      if (nearest.gap <= 1 && nearest.ratio > LINK_RULES.maxPayRatio) { decide('apart', `Pay changes ${nearest.ratio.toFixed(1)}× between ${years[nearest.mine]} and ${years[nearest.other]}`); continue }
      decide('likely', `Only fuller name here that agrees; “${shown(spelling)}” in ${span(spelling.periods)}, “${shown(bestOf(root))}” in ${span(theirs)}, never both in one period`, root)
    }
  }

  // Apply explicit, qualified inferences after the ordinary rules. They cannot supply new
  // evidence to an automatic rule or turn another spelling correction into a verified identity.
  const inferredMembers = new Set()
  for (const review of reviewed.filter((entry) => entry.decision === 'likely')) {
    const at = employerAt.get(review.employer)
    const pair = review.names.map((name) => spellings.get(`${at}|${personKey(nameOnly(name))}`))
    if (pair.some((spelling) => !spelling) || find(pair[0]) === find(pair[1])) continue
    const other = pair.reduce(fuller)
    const spelling = pair.find((each) => each !== other)
    decisions.push({ employer: review.employer, name: shown(spelling), key: spelling.key,
      target: shown(other), targetKey: other.key, status: 'likely', reason: `Assumption on review: ${review.note}`,
      evidence: review.evidence ?? [], pay: Math.max(...spelling.periods.values(), ...other.periods.values()) })
    join(spelling, other)
    inferredMembers.add(spelling.id)
    inferredMembers.add(other.id)
  }

  const verifiedEdges = new Map()
  for (const entry of decisions.filter((entry) => entry.status === 'verified')) {
    const a = `${employerAt.get(entry.employer)}|${entry.key}`
    const b = `${employerAt.get(entry.employer)}|${entry.targetKey}`
    if (!verifiedEdges.has(a)) verifiedEdges.set(a, new Set())
    if (!verifiedEdges.has(b)) verifiedEdges.set(b, new Set())
    verifiedEdges.get(a).add(b); verifiedEdges.get(b).add(a)
  }

  // Every disclosed spelling in a group, the fullest first; a group is published once it holds two.
  const clusters = new Map()
  for (const spelling of spellings.values()) {
    const root = find(spelling)
    if (!clusters.has(root.id)) clusters.set(root.id, members(root))
  }
  // An endpoint can also acquire a later likely bridge. Keep its stronger local decision,
  // including that decision's source evidence; equal-confidence decisions retain their order.
  const strongerDecision = (earlier, later) => {
    if (!earlier) return later
    if (!later) return earlier
    return earlier.status === 'verified' && later.status !== 'verified' ? earlier : later
  }
  const decisionOf = new Map()
  const joinedTo = new Map()
  for (const entry of decisions.filter((each) => each.status !== 'apart')) {
    const from = `${entry.employer}|${entry.key}`
    const to = `${entry.employer}|${entry.targetKey}`
    decisionOf.set(from, strongerDecision(decisionOf.get(from), entry))
    joinedTo.set(to, strongerDecision(joinedTo.get(to), entry))
  }
  const result = []
  const canonicalReviews = reviewed.filter((entry) => entry.decision === 'verified' && entry.canonicalName)
  for (const cluster of clusters.values()) {
    const employer = employers[cluster[0].employer]?.[3]
    const best = cluster.reduce(fuller)
    const hasInference = cluster.some((each) => inferredMembers.has(each.id))
    const verifiedFromBest = new Set([best.id])
    const todo = [best.id]
    if (hasInference) for (let at = 0; at < todo.length; at += 1) {
      for (const neighbor of verifiedEdges.get(todo[at]) ?? []) {
        if (!verifiedFromBest.has(neighbor)) { verifiedFromBest.add(neighbor); todo.push(neighbor) }
      }
    }
    const rawOf = (spelling) => [...spelling.raw].map(([key, names]) => ({ key,
      name: spelling.reviewedSpelling && names.has(spelling.reviewedSpelling) ? spelling.reviewedSpelling : [...names].sort((a, b) => b[1] - a[1])[0][0] }))
    const canonicalReview = canonicalReviews.find((entry) => entry.employer === employer
      && entry.names.every((name) => cluster.some((spelling) => spelling.key === personKey(nameOnly(name)))))
    const own = canonicalReview ? { key: personKey(canonicalReview.canonicalName), name: canonicalReview.canonicalName }
      : rawOf(best).find((each) => each.name === shown(best)) ?? rawOf(best)[0]
    const aliases = cluster.flatMap((spelling) => rawOf(spelling).filter((each) => each.key !== own.key).map((each) => {
      if (spelling === best) return canonicalReview
        ? { ...each, status: 'verified', reason: `Reviewed: ${canonicalReview.note}`, evidence: canonicalReview.evidence }
        : { ...each, status: 'verified', reason: 'The same name with a position written into it' }
      // A reviewed pair may name either spelling first: the decision is the join's, either way.
      const endpoint = `${employer}|${spelling.key}`
      const decision = strongerDecision(joinedTo.get(endpoint), decisionOf.get(endpoint))
      const inferredPath = hasInference && !verifiedFromBest.has(spelling.id)
      return { ...each, status: inferredPath ? 'likely' : decision.status,
        reason: inferredPath && decision.status === 'verified' ? `The connection to this history includes an unverified surname inference. Local source evidence: ${decision.reason}` : decision.reason,
        ...(decision.evidence?.length ? { evidence: decision.evidence } : {}) }
    }))
    if (aliases.length) result.push({ employer, key: own.key, name: own.name, aliases, ...(canonicalReview ? { reviewedName: true } : {}) })
  }
  return { links: result, decisions }
}

/**
 * The published links as a lookup: `${employer index}|${disclosed name key}` → the group's
 * { key, name, status, reason } (status and reason null for the group's own spelling).
 */
export const linkLookup = (published, employers) => {
  const lookup = new Map()
  if (!published) return lookup
  const reviewedNames = new Set(published.reviewedNames ?? [])
  const indexOf = new Map(employers.map((entry, at) => [entry[3], at]))
  for (const [slug, key, name, aliases] of published.links) {
    const at = indexOf.get(slug)
    if (at === undefined) continue
    const reviewedName = reviewedNames.has(`${slug}|${key}`)
    lookup.set(`${at}|${key}`, { key, name, status: null, reason: null, ...(reviewedName ? { reviewedName } : {}) })
    for (const [aliasKey, aliasName, status, reason, evidence] of aliases) lookup.set(`${at}|${aliasKey}`, {
      key, name, aliasName, status, reason, ...(reviewedName ? { reviewedName } : {}), ...(evidence?.length ? { evidence } : {})
    })
  }
  return lookup
}

/** A reviewed surname correction can refer to a different people-index slice. */
export const personRecordShards = (published, key) => {
  const keys = new Set([key])
  for (const [, canonical, , aliases] of published?.links ?? []) {
    if (canonical !== key) continue
    keys.add(canonical)
    for (const [alias] of aliases) keys.add(alias)
  }
  return [...new Set([...keys].map((nameKey) => surnameShard(`${nameKey.split('|')[0]},`)))].sort()
}

/** One employer's joins from its published file: each spelling's name key → its group's key. */
export const employerNameKeys = (published, slug) => {
  const keys = new Map()
  for (const [employer, key, , aliases] of published?.links ?? []) {
    if (employer !== slug) continue
    keys.set(key, key)
    for (const [aliasKey] of aliases) keys.set(aliasKey, key)
  }
  return keys
}
