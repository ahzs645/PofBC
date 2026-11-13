// Parsing, diffing and dating for BC Laws' "Acts – Ministers' Responsibilities" (AMR) listings.
//
// Pure functions only: scripts/build-government-amr.mjs does the reading and writing, and
// scripts/amr.test.mjs exercises these against vendored raw pages.
//
// Two kinds of date are kept apart throughout, because confusing them is the mistake this module
// exists to avoid (research/legislation/bclaws-amr-feasibility.md §4):
//
//   * a listing's period ("November 18, 2024 to May 29, 2025") says what span a snapshot page
//     covers. Since 2017 it runs from the base reorganization OIC to the day the snapshot was
//     taken, so it is never the date any one Act changed hands;
//   * a change's effective date comes only from an Order in Council: when exactly one OIC is new
//     between two snapshots and that OIC's date is established (from its weekly Resumé, or from a
//     hand-checked entry). Everything else stays undated, bounded by the two snapshots.

const MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

const NAMED = { nbsp: ' ', amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", copy: '©', rsquo: '’', lsquo: '‘', ndash: '–', mdash: '—', eacute: 'é' }

export const decodeEntities = (text) => String(text)
  .replace(/&#x([0-9a-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
  .replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(Number(dec)))
  .replace(/&([a-z]+);/gi, (match, name) => NAMED[name.toLowerCase()] ?? match)

/** Visible text of an HTML fragment: line breaks kept, tags dropped, spaces collapsed. */
export const htmlText = (fragment) => decodeEntities(String(fragment)
  .replace(/<br\s*\/?>/gi, '\n')
  .replace(/<[^>]*>/g, ''))
  .replace(/[ \t ]+/g, ' ')
  .replace(/ *\n */g, '\n')
  .replace(/\n{2,}/g, '\n')
  .trim()

/** "November 18, 2024" -> "2024-11-18"; null if it is not such a date. */
export const isoDate = (text) => {
  const match = String(text).replace(/ /g, ' ').match(/([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})/)
  if (!match) return null
  const month = MONTHS.indexOf(match[1].toLowerCase()) + 1
  if (!month) return null
  return `${match[3]}-${String(month).padStart(2, '0')}-${match[2].padStart(2, '0')}`
}

const DATE = '([A-Z][a-z]+\\s+\\d{1,2},\\s+\\d{4})'
const OIC_LIST = '(\\d{1,4}\\/\\d{4}(?:(?:,\\s*|,?\\s+and\\s+)\\d{1,4}\\/\\d{4})*)'
const oicsIn = (list) => [...String(list).matchAll(/(\d{1,4})\/(\d{4})/g)].map((match) => `${Number(match[1])}/${match[2]}`)

/** Sorts OIC numbers by year, then number. */
export const compareOics = (a, b) => {
  const [na, ya] = a.split('/').map(Number)
  const [nb, yb] = b.split('/').map(Number)
  return ya - yb || na - nb
}

/**
 * The period sentence at the head of each page. Two wordings are known:
 *
 *   "This page contains information for the period December 16, 2015 to June 22, 2016. The
 *    information is from Order in Council 233/2013, as amended by Orders in Council 368/2014, …"
 *   "This page lists, as at November 18, 2024, ministerial responsibility for Acts assigned by
 *    Constitution Act Order in Council 596/2024."
 *
 * and a page may name more than one base order ("… from Order in Council 602/2020, as amended by
 * …, and by Order in Council 92/2022, as amended by …"). An OIC is a base order unless it follows
 * "amended by".
 */
export const parsePeriod = (rawText) => {
  const text = String(rawText ?? '').replace(/\s+/g, ' ').trim()
  const result = { wording: null, periodFrom: null, periodTo: null, baseOics: [], amendingOics: [], text }
  const range = text.match(new RegExp(`for the period ${DATE} to ${DATE}`))
  const asAt = text.match(new RegExp(`as at ${DATE}`))
  if (range) {
    result.wording = 'period'
    result.periodFrom = isoDate(range[1])
    result.periodTo = isoDate(range[2])
  } else if (asAt) {
    result.wording = 'as-at'
    result.periodFrom = isoDate(asAt[1])
    result.periodTo = result.periodFrom
  }
  const pattern = new RegExp(`(amended\\s+by\\s+)?Orders?\\s+in\\s+Council\\s+${OIC_LIST}`, 'gi')
  for (const match of text.matchAll(pattern)) {
    const list = oicsIn(match[2])
    if (match[1]) result.amendingOics.push(...list)
    else result.baseOics.push(...list)
  }
  result.baseOics = [...new Set(result.baseOics)]
  result.amendingOics = [...new Set(result.amendingOics)].filter((oic) => !result.baseOics.includes(oic))
  result.parsed = Boolean(result.wording && result.baseOics.length)
  return result
}

/** "Gaming Control, S.B.C. 2002, c. 14" -> { title: "Gaming Control", citation: "S.B.C. 2002, c. 14" }. */
export const splitCitation = (text) => {
  const match = String(text).match(/^(.*?),\s*((?:R\.?S\.?B\.?C\.?|S\.?B\.?C\.?)\s*\d{4},?\s*c(?:hapter|\.)\s*[\w.]+(?:\s*\(.*\))?)\s*\.?$/)
  return match ? { title: match[1].trim(), citation: match[2].trim() } : { title: String(text).trim(), citation: null }
}

/** A loose key for matching Act titles: case, quotes, dashes and a trailing "Act" ignored. */
export const titleKey = (title) => String(title)
  .normalize('NFKD')
  .replace(/[̀-ͯ]/g, '')
  .replace(/[‘’ʼ`]/g, "'")
  .replace(/[–—]/g, '-')
  .toLowerCase()
  .replace(/\s+act$/, '')
  .replace(/[^a-z0-9]+/g, ' ')
  .trim()

/**
 * The statreg id an Act is keyed by. BC Laws links a multi-part Act sometimes to its document
 * ("03053_00") and sometimes to its multi-part index ("03053_00_multi"); both are the one Act.
 */
export const statregKey = (id) => (id ? String(id).replace(/_multi$/i, '') : null)

/** "Firearm [Repealed by the … Act, … effective October 1, 2026 …]" -> title and the bracketed note. */
export const splitAnnotation = (text) => {
  const match = String(text).match(/^(.*?)\s*\[([^\]]*)\]\s*$/)
  return match && match[1] ? { title: match[1].trim(), annotation: match[2].trim() } : { title: String(text).trim(), annotation: null }
}

const scopeOf = (details) => (!details || /^the act\.?$/i.test(details) ? 'whole' : 'partial')

/**
 * One "Listed by Minister" page: its title, its period sentence and its rows, grouped by the
 * minister heading each falls under. The markup is loose (unclosed <tr>, <br> without a slash,
 * upper- and lower-case tags), so this reads it with patterns rather than an XML parser.
 */
export const parseAmrPage = (html) => {
  const source = String(html)
  const docTitle = htmlText(source.match(/<title>([\s\S]*?)<\/title>/i)?.[1] ?? '').replace(/\s*-\s*Statute Administration\s*$/i, '').trim()
  const bodies = [...source.matchAll(/<p[^>]*class="body"[^>]*>([\s\S]*?)<\/p>/gi)].map((match) => htmlText(match[1]))
  const periodText = bodies.find((text) => /Order[s]? in Council|for the period|as at/i.test(text)) ?? null
  const period = parsePeriod(periodText)

  // Mixed-case minister names, from the page title and the navigation links, to label the
  // upper-case table headings.
  const names = new Map()
  const remember = (name) => {
    const clean = htmlText(name).replace(/\s+/g, ' ').trim()
    if (clean) names.set(clean.toUpperCase(), clean)
  }
  if (docTitle) remember(docTitle)
  for (const match of source.matchAll(/<a[^>]*href="[^"]*\/amr\/amr\/[^"]*"[^>]*>([\s\S]*?)<\/a>/gi)) remember(match[1])
  for (const match of source.matchAll(/<strong>([\s\S]*?)<\/strong>/gi)) remember(match[1])

  const ministers = []
  const headingPattern = /<th[^>]*colspan="?2"?[^>]*>([\s\S]*?)<\/th>/gi
  const headings = [...source.matchAll(headingPattern)]
  headings.forEach((match, index) => {
    const heading = htmlText(match[1]).replace(/\s+/g, ' ')
    const start = match.index + match[0].length
    const end = index + 1 < headings.length ? headings[index + 1].index : source.length
    const block = source.slice(start, end).split(/<\/table>/i)[0]
    const rows = []
    for (const chunk of block.split(/<tr\b/i).slice(1)) {
      const cells = chunk.split(/<td\b/i).slice(1).map((cell) => cell.replace(/^[^>]*>/, '').replace(/<\/td>[\s\S]*$/i, ''))
      if (cells.length < 2) continue
      const link = cells[0].match(/href="[^"]*\/statreg\/([^"#?/]+)/i)
      const { title: titled, annotation } = splitAnnotation(htmlText(cells[0]).replace(/\s+/g, ' '))
      const { title, citation } = splitCitation(titled)
      if (!title) continue
      const detailsRaw = htmlText(cells[1])
      rows.push({
        actTitle: title,
        citation,
        ...(annotation ? { annotation } : {}),
        statregId: link ? statregKey(link[1]) : null,
        ...(link && statregKey(link[1]) !== link[1] ? { statregLink: link[1] } : {}),
        detailsRaw,
        scope: scopeOf(detailsRaw)
      })
    }
    // A heading can be cut short ("ENVIRONMENT AND CLIMATE CHANGE STRATEGY<br />AND MINISTER
    // RESPONSIBLE FOR TRANSLINK", 2022); a page with a single table is named by its own title.
    const known = names.get(heading.toUpperCase()) ?? (headings.length === 1 && docTitle ? docTitle : null)
    ministers.push({ heading, ministerTitle: known ?? heading, titleFromHeading: !known, rows })
  })
  return { docTitle, periodText, period, ministers }
}

// --- Snapshots ---------------------------------------------------------------------------------

/**
 * Combines the pages of one snapshot into a listing: one period (the pages are expected to agree;
 * disagreement is reported) and every row with its minister.
 */
export const buildListing = ({ id, title, kind, pages }) => {
  const rows = []
  const periods = new Map()
  const problems = []
  for (const { docId, url, page } of pages) {
    const key = JSON.stringify([page.period.periodFrom, page.period.periodTo, page.period.baseOics, page.period.amendingOics])
    if (!periods.has(key)) periods.set(key, { ...page.period, docIds: [] })
    periods.get(key).docIds.push(docId)
    if (!page.period.parsed) problems.push({ kind: 'period-unparsed', listing: id, docId, text: page.periodText })
    for (const minister of page.ministers) {
      if (minister.titleFromHeading) problems.push({ kind: 'minister-title-from-heading', listing: id, docId, heading: minister.heading })
      for (const row of minister.rows) rows.push({ ...row, ministerTitle: minister.ministerTitle, docId, url })
    }
  }
  // The period most pages share stands for the listing; any other is reported.
  const ranked = [...periods.values()].sort((a, b) => b.docIds.length - a.docIds.length)
  const period = ranked[0] ?? parsePeriod('')
  if (ranked.length > 1) {
    problems.push({ kind: 'period-disagrees', listing: id, variants: ranked.map((p) => ({ text: p.text, docIds: p.docIds })) })
  }
  const allOics = [...new Set(ranked.flatMap((p) => [...p.baseOics, ...p.amendingOics]))].sort(compareOics)
  return {
    id,
    title,
    kind,
    docIds: pages.map((p) => p.docId),
    periodFrom: period.periodFrom,
    periodTo: period.periodTo,
    periodWording: period.wording,
    baseOics: period.baseOics,
    amendingOics: period.amendingOics,
    oics: allOics,
    periodText: period.text,
    rows,
    problems
  }
}

/** "S.B.C. 2002, c. 14" -> "sbc2002c14", to compare citations however they are punctuated. */
export const citationKey = (citation) => (citation ? String(citation).toLowerCase().replace(/chapter/g, 'c').replace(/[^a-z0-9]/g, '') : null)

/**
 * Gives every row an Act key. A row with a statreg link is keyed by it, so a renamed Act stays
 * the same Act. BC Laws only began linking rows in the 2025-11-24 snapshot; an earlier row takes
 * the statreg id that the linked rows give its title — with its citation, where the page gives one
 * (two Gaming Control Acts stood together in 2022–2025) — provided they give exactly one. A title
 * no linked row ever carried (a repealed Act, or one renamed before the links began) can be tied
 * to its statreg id by a hand-checked alias; otherwise it keeps a title key and is reported.
 */
export const keyActs = (listings, aliases = []) => {
  const byTitle = new Map()
  const note = (key, id) => {
    if (!byTitle.has(key)) byTitle.set(key, new Set())
    byTitle.get(key).add(id)
  }
  for (const listing of listings) {
    for (const row of listing.rows) {
      if (!row.statregId) continue
      note(titleKey(row.actTitle), row.statregId)
      if (row.citation) note(`${titleKey(row.actTitle)}|${citationKey(row.citation)}`, row.statregId)
    }
  }
  const aliasFor = (row) => aliases.find((alias) => titleKey(alias.title) === titleKey(row.actTitle)
    && (!alias.citation || citationKey(alias.citation) === citationKey(row.citation)))
  const problems = []
  for (const listing of listings) {
    for (const row of listing.rows) {
      if (row.statregId) {
        row.actKey = `statreg:${row.statregId}`
        row.statregSource = 'link'
        continue
      }
      const alias = aliasFor(row)
      if (alias) {
        row.statregId = alias.statregId
        row.actKey = `statreg:${alias.statregId}`
        row.statregSource = 'alias'
        continue
      }
      const ids = (row.citation && byTitle.get(`${titleKey(row.actTitle)}|${citationKey(row.citation)}`)) || byTitle.get(titleKey(row.actTitle))
      if (ids && ids.size === 1) {
        const [id] = ids
        row.actKey = `statreg:${id}`
        row.statregId = id
        row.statregSource = 'title-match'
      } else {
        row.actKey = `title:${titleKey(row.actTitle)}${row.citation ? `|${citationKey(row.citation)}` : ''}`
        row.statregSource = null
        problems.push({
          kind: ids ? 'statreg-ambiguous' : 'statreg-missing',
          listing: listing.id,
          act: row.actTitle,
          citation: row.citation,
          ministerTitle: row.ministerTitle,
          ...(ids ? { candidates: [...ids] } : {})
        })
      }
    }
  }
  return problems
}

/**
 * Pairs in one gap that may be one Act under a new title: an Act that left a minister and another
 * that arrived with the same minister, the same details text and no statreg id to tell them
 * apart. Reported, never merged.
 */
export const possibleRetitles = (changes) => {
  const removed = changes.filter((change) => change.type === 'removed' && !change.actStillListed)
  const added = changes.filter((change) => change.type === 'added' && !change.actPreviouslyListed)
  const pairs = []
  for (const gone of removed) {
    for (const come of added) {
      if (gone.from !== come.to || (gone.detailsBefore ?? '') !== (come.detailsAfter ?? '')) continue
      if (gone.actKey.startsWith('statreg:') && come.actKey.startsWith('statreg:')) continue
      pairs.push({ ministerTitle: gone.from, fromAct: gone.act, fromKey: gone.actKey, toAct: come.act, toKey: come.actKey })
    }
  }
  // Only one-to-one pairings mean anything; a minister who lost two whole Acts and gained two
  // says nothing about which became which.
  const count = (key, value) => pairs.filter((pair) => pair[key] === value).length
  return pairs.filter((pair) => count('fromKey', pair.fromKey) === 1 && count('toKey', pair.toKey) === 1)
}

// --- OIC dates ---------------------------------------------------------------------------------

/**
 * The OICs a weekly Resumé lists, each with its approval date (the "Approved and Ordered" heading
 * it falls under), the effective date its summary states (if it states exactly one), and its
 * summary text.
 */
export const parseResume = (html, { id = null, url = null } = {}) => {
  const source = String(html)
  // Read in document order. The OIC part has no heading of its own in older Resumés ("Resume of
  // Orders in Council", 2018) and a "Schedule" heading inside it in others (2020), so the
  // Proclamations and Ministerial Orders parts are what switch reading off.
  const tokens = [...source.matchAll(/<h([23])[^>]*>([\s\S]*?)<\/h\1>|<p[^>]*class="order"[^>]*>([\s\S]*?)<\/p>|<p[^>]*class="(?:instruction|statutory|para-[a-z]+)"[^>]*>([\s\S]*?)<\/p>/gi)]
  const entries = []
  let approved = null
  let current = null
  let reading = true
  for (const token of tokens) {
    if (token[2] !== undefined) {
      const text = htmlText(token[2]).replace(/\s+/g, ' ')
      if (/^(Ministerial Orders|Proclamations)$/i.test(text)) {
        reading = false
        approved = null
        current = null
      } else if (/approved and ordered/i.test(text)) {
        reading = true
        approved = isoDate(text)
        current = null
      } else if (/orders in council/i.test(text)) {
        reading = true
        current = null
      }
    } else if (token[3] !== undefined) {
      const number = htmlText(token[3]).match(/^ORDER\s+IN\s+COUNCIL\s+(\d{1,4})\b/i)
      if (!reading || !number) {
        current = null
        continue
      }
      current = { number: Number(number[1]), approved, texts: [], authority: null, pdf: token[3].match(/href="([^"]+)"/i)?.[1] ?? null }
      entries.push(current)
    } else if (current) {
      const text = htmlText(token[4]).replace(/\s+/g, ' ')
      const authority = text.match(/^Statutory Authority:\s*(.*)$/i)
      if (authority) current.authority = authority[1]
      else if (!/^Ministry Responsible:/i.test(text)) current.texts.push(text)
    }
  }
  return entries.map((entry) => {
    const summary = entry.texts.join(' ')
    const effective = [...new Set([...summary.matchAll(new RegExp(`\\b[Ee]ffective\\s+${DATE}`, 'g'))].map((m) => isoDate(m[1])))]
    const year = entry.approved?.slice(0, 4) ?? null
    return {
      oic: year ? `${entry.number}/${year}` : null,
      number: entry.number,
      approved: entry.approved,
      effective: effective.length === 1 ? effective[0] : null,
      effectiveCandidates: effective,
      authority: entry.authority,
      summary,
      resumeId: id,
      resumeUrl: url,
      pdf: entry.pdf ? new URL(entry.pdf, 'https://www.bclaws.gov.bc.ca').href : null
    }
  })
}

/**
 * The date an OIC can date a change with: its stated effective date if it has one, otherwise its
 * approval date (when an order states no effective date it takes effect when made). A hand-checked
 * entry wins over the Resumé.
 */
export const oicDate = (oic, { resumeIndex, manual }) => {
  const checked = manual?.[oic]
  if (checked && (checked.effective || checked.approved)) {
    return {
      oic,
      date: checked.effective ?? checked.approved,
      dateKind: checked.effective ? 'effective' : 'approved',
      approved: checked.approved ?? null,
      basis: 'oic-checked',
      source: checked.source ?? null,
      note: checked.note ?? null
    }
  }
  const entries = resumeIndex?.get(oic) ?? []
  if (entries.length === 0) return { undated: 'not-in-resumes' }
  if (entries.length > 1) return { undated: 'resumes-disagree' }
  const [entry] = entries
  if (!entry.approved) return { undated: 'no-approval-date' }
  if (entry.effectiveCandidates.length > 1) return { undated: 'several-effective-dates' }
  // "(a) … as set out in Schedule 1, and (b) effective April 1, 2026, … Schedule 2": one part
  // takes effect when made and another later, and which Acts are in which part is in the order
  // itself, not the Resumé. Only an effective date that opens the summary covers the whole order.
  if (entry.effective && !/^Effective\b/i.test(entry.summary)) return { undated: 'effective-date-covers-part' }
  return {
    oic,
    date: entry.effective ?? entry.approved,
    dateKind: entry.effective ? 'effective' : 'approved',
    approved: entry.approved,
    basis: 'oic-resume',
    source: entry.resumeUrl,
    pdf: entry.pdf
  }
}

export const indexResumes = (entries) => {
  const index = new Map()
  for (const entry of entries) {
    if (!entry.oic) continue
    if (!index.has(entry.oic)) index.set(entry.oic, [])
    const list = index.get(entry.oic)
    // The same OIC can be repeated in a corrected Resumé; identical dates count once.
    if (!list.some((other) => other.approved === entry.approved && other.effective === entry.effective)) list.push(entry)
  }
  return index
}

// --- Diffs -------------------------------------------------------------------------------------

const groupByAct = (rows) => {
  const acts = new Map()
  for (const row of rows) {
    if (!acts.has(row.actKey)) acts.set(row.actKey, new Map())
    const ministers = acts.get(row.actKey)
    // A minister listed twice for one Act (rare) keeps both detail texts.
    const prior = ministers.get(row.ministerTitle)
    ministers.set(row.ministerTitle, prior ? { ...prior, detailsRaw: `${prior.detailsRaw}\n${row.detailsRaw}`.trim(), scope: 'partial' } : row)
  }
  return acts
}

/**
 * The changes between two consecutive listings, Act by Act (Acts keyed by statreg id):
 *
 *   moved          one minister gave way to another
 *   added/removed  a minister gained or lost the Act otherwise (shared Acts, new or repealed Acts)
 *   scope-changed  the same minister, different details text
 *   retitled       the same statreg id under a different short title
 */
export const diffListings = (before, after) => {
  const a = groupByAct(before.rows)
  const b = groupByAct(after.rows)
  const changes = []
  const actInfo = (key, row) => ({ actKey: key, statregId: row.statregId ?? null, act: row.actTitle })
  for (const key of new Set([...a.keys(), ...b.keys()])) {
    const was = a.get(key) ?? new Map()
    const now = b.get(key) ?? new Map()
    const any = [...now.values()][0] ?? [...was.values()][0]
    const info = actInfo(key, any)
    const lost = [...was.keys()].filter((title) => !now.has(title))
    const gained = [...now.keys()].filter((title) => !was.has(title))
    if (was.size && now.size) {
      const oldTitle = [...was.values()][0].actTitle
      const newTitle = [...now.values()][0].actTitle
      if (titleKey(oldTitle) !== titleKey(newTitle)) changes.push({ type: 'retitled', ...info, fromTitle: oldTitle, toTitle: newTitle })
    }
    if (lost.length === 1 && gained.length === 1) {
      const from = was.get(lost[0])
      const to = now.get(gained[0])
      changes.push({
        type: 'moved', ...info, from: lost[0], to: gained[0],
        detailsBefore: from.detailsRaw, detailsAfter: to.detailsRaw, scopeBefore: from.scope, scopeAfter: to.scope
      })
    } else {
      for (const title of lost) {
        const row = was.get(title)
        changes.push({ type: 'removed', ...info, from: title, to: null, detailsBefore: row.detailsRaw, scopeBefore: row.scope, actStillListed: now.size > 0 })
      }
      for (const title of gained) {
        const row = now.get(title)
        changes.push({ type: 'added', ...info, from: null, to: title, detailsAfter: row.detailsRaw, scopeAfter: row.scope, actPreviouslyListed: was.size > 0 })
      }
    }
    for (const title of was.keys()) {
      if (!now.has(title)) continue
      const old = was.get(title)
      const neu = now.get(title)
      if (old.detailsRaw.replace(/\s+/g, ' ') !== neu.detailsRaw.replace(/\s+/g, ' ')) {
        // Punctuation and line breaks alone ("Part 3" -> "Part 3.") are flagged, not dropped.
        const words = (text) => text.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
        const punctuationOnly = words(old.detailsRaw) === words(neu.detailsRaw)
        changes.push({ type: 'scope-changed', ...info, from: title, to: title, detailsBefore: old.detailsRaw, detailsAfter: neu.detailsRaw, scopeBefore: old.scope, scopeAfter: neu.scope, ...(punctuationOnly ? { punctuationOnly } : {}) })
      }
    }
  }
  const order = { moved: 0, added: 1, removed: 2, 'scope-changed': 3, retitled: 4 }
  return changes.sort((x, y) => order[x.type] - order[y.type] || x.act.localeCompare(y.act) || String(x.from ?? x.to).localeCompare(String(y.from ?? y.to)))
}

/** OICs named by `after` and not by `before`. */
export const newOics = (before, after) => after.oics.filter((oic) => !before.oics.includes(oic)).sort(compareOics)

/**
 * Dates the changes of one gap. Only a gap with exactly one new OIC, whose date is established,
 * dates its changes; a retitle is not a change of responsibility and is never dated.
 */
export const dateGap = (before, after, changes, dating) => {
  const candidates = newOics(before, after)
  const found = candidates.length === 1 ? oicDate(candidates[0], dating) : null
  let dated = found && !found.undated ? found : null
  let undatedReason = found?.undated ?? null
  // A date outside the gap means the reading is wrong somewhere: the order was already in force
  // when the earlier snapshot was taken, or not yet when the later one was.
  if (dated && ((before.periodTo && dated.date <= before.periodTo) || (after.periodTo && dated.date > after.periodTo))) {
    undatedReason = 'date-outside-gap'
    dated = null
  }
  const status = candidates.length === 0 ? 'no-new-oic' : candidates.length > 1 ? 'multi-oic' : dated ? 'dated' : 'oic-undated'
  return {
    status,
    undatedReason,
    oicDate: dated,
    candidateOics: candidates,
    changes: changes.map((change) => {
      const base = { ...change, betweenListings: [before.id, after.id], candidateOics: candidates }
      if (change.type === 'retitled' || !dated) {
        return { ...base, effectiveDate: null, dateKind: null, basis: change.type === 'retitled' ? 'not-applicable' : 'bounded', oic: null, source: null }
      }
      return {
        ...base,
        effectiveDate: dated.date,
        dateKind: dated.dateKind,
        approvedDate: dated.approved,
        basis: dated.basis,
        oic: dated.oic,
        source: dated.source
      }
    })
  }
}

// --- Crosswalk ---------------------------------------------------------------------------------

/** The date a listing stands for when matching it against the crosswalk: its snapshot day. */
export const listingDate = (listing) => {
  if (/^\d{4}-\d{2}-\d{2}$/.test(listing.id)) return listing.id
  // A folder titled by month only ("2017 July") is read as the first day its page states in that
  // month, so a cabinet sworn in mid-month is matched to the right side.
  if (/^\d{4}-\d{2}$/.test(listing.id)) {
    return [listing.periodFrom, listing.periodTo].find((date) => date?.startsWith(listing.id)) ?? `${listing.id}-15`
  }
  return listing.periodTo
}

/**
 * The PofBC ministry episode a minister title stood for on a date. Entries give a title and the
 * dates (inclusive) they hold for; a title with two entries covering the date is ambiguous.
 */
export const crosswalkLookup = (crosswalk, ministerTitle, date) => {
  const hits = crosswalk.filter((entry) => entry.amrTitle === ministerTitle
    && (!entry.validFrom || entry.validFrom <= date)
    && (!entry.validTo || entry.validTo >= date))
  if (hits.length === 1) return { status: hits[0].episodeId ? 'mapped' : 'unmapped', entry: hits[0] }
  if (hits.length > 1) return { status: 'ambiguous', entries: hits }
  return { status: 'missing' }
}
