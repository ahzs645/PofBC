// One year of the Government of British Columbia, as nodes and edges to draw.
//
// Every year has its ministries (from the BC Archives diagram), who held each of them (from the
// Legislative Library's Executive Council records), its premier and Lieutenant Governor, the
// Legislature its last election returned and its Speaker, the officers of the Legislature and the
// chief justices then in office, and the Crown corporations and agencies that stood — the ones
// since wound up included. The present adds what only the present records: deputy ministers,
// ministers of state, chief executives and staffing.

import { CURRENT_BODIES, CURRENT_MINISTERS, CURRENT_AS_OF, CURRENT_SOURCES } from './currentData.js'
import { EVENT_SOURCES, eventsFor, operatingNameIn } from './events.js'
import { LIEUTENANT_GOVERNORS_OFFICIAL, PARLIAMENT_43, STAFFING } from './atlasData.js'
import { CURRENT_MINISTRIES, episodesIn, fold, forerunnerIn, MINISTRY_EPISODES, predecessorsOf, slugify, successorsOf } from './episodes.js'
import { ELECTIONS, LIEUTENANT_GOVERNORS, PENDING_ELECTION, PREMIERS } from './timelineData.js'
import { HISTORICAL_BODIES, HISTORY_SOURCES, MINISTERS, OFFICE_HOLDERS, SUB_AGENCIES } from './historyData.js'

/** The BC Archives diagram every ministry episode comes from. */
const ARCHIVES_DIAGRAM = {
  title: 'BC Archives — BC Government Ministry History Diagram (rev. 2024-12-16)',
  url: 'https://bcarchives.ca/wp-content/uploads/sites/2/2026/01/BC-Government-Ministry-History-Diagram.pdf'
}
const historySource = (index) => (index === null || index === undefined ? null : { url: HISTORY_SOURCES[index], title: null })
const TODAY_SOURCE = { title: CURRENT_SOURCES[0]?.title ?? 'Government of British Columbia', url: CURRENT_SOURCES[0]?.url ?? null }

export const FIRST_YEAR = 1871
export const PRESENT_YEAR = Number(CURRENT_AS_OF.slice(0, 4))

/** The day a year is read at: its last, or today for the present year. */
export const dayOf = (year) => (year >= PRESENT_YEAR ? CURRENT_AS_OF : `${year}-12-31`)

/** Whoever held an office on `day`, from a list of {from, to} terms. The later one wins a handover day. */
const holderOn = (terms, day) => {
  let found = null
  for (const term of terms) {
    if (term.from <= day && (term.to === null || term.to > day)) found = term
  }
  return found
}

/**
 * A date as precise as its source, as the first day it could mean. A year alone reads as 1 January
 * and a month as its first, so a handover recorded only by year falls before the year's end — which
 * is where the timeline reads — and the newcomer is the one shown.
 */
export const startOf = (value) => {
  if (!value) return null
  const text = String(value)
  if (text.length === 4) return `${text}-01-01`
  if (text.length === 7) return `${text}-01`
  return text
}

/**
 * Who held a post on `day`, from [name, from, to, …, acting] rows. A substantive holder is preferred
 * to an acting one, and a later appointment to an earlier.
 */
const termOn = (rows, day, actingAt) => {
  let found = null
  for (const row of rows) {
    const from = startOf(row[1])
    const to = startOf(row[2])
    if (!from || from > day || (to && to <= day)) continue
    if (!found || (found[actingAt] && !row[actingAt]) || (Boolean(found[actingAt]) === Boolean(row[actingAt]) && startOf(found[1]) <= from)) found = row
  }
  return found
}

/** An office's holder on `day`, as a head for the panel. */
export const officeHolderOn = (office, day, title) => {
  const record = OFFICE_HOLDERS[office]
  const row = record ? termOn(record.holders, day, 3) : null
  return row ? { title: title ?? record.title, person: row[0], since: row[1], acting: Boolean(row[3]), source: historySource(row[4]) } : null
}

/** Every holder of an office up to `day`, newest first. */
export const officeHoldersTo = (office, day) => (OFFICE_HOLDERS[office]?.holders ?? [])
  .filter((row) => startOf(row[1]) && startOf(row[1]) <= day)
  .map((row) => ({ person: row[0], from: row[1], to: row[2], acting: Boolean(row[3]) }))
  .reverse()

/** Ministers of an episode, as the panel lists them. */
export const ministersOf = (episodeId) => (MINISTERS[episodeId] ?? [])
  .map(([person, from, to, title, party, acting]) => ({ person, from, to, title, party, acting: Boolean(acting) }))

/** The minister of an episode on `day`: whoever held it then, else — for a year it ended in — its last. */
const ministerOn = (episodeId, day) => {
  const rows = MINISTERS[episodeId] ?? []
  const row = termOn(rows, day, 5) ?? rows.filter((entry) => startOf(entry[1]) <= day).at(-1)
  return row ? { title: row[3], person: row[0], since: row[1], party: row[4], acting: Boolean(row[5]), source: historySource(row[6]) } : null
}

/** The sources an event gives, as {title, url}. */
const eventSources = (event) => event.sources.map((index) => EVENT_SOURCES[index]).filter(Boolean)

/**
 * Why a node is drawn as it is: one entry per claim, each with the source that supports it and,
 * for what only the present records, the day it was checked. A claim with no source is not listed
 * as though it had one.
 */
const claim = (text, source, extra = {}) => (source?.url ? { claim: text, source, ...extra } : null)

/** The words that name what a ministry is for, as the build matched portfolios by. */
const STOP = new Set(['of', 'and', 'the', 'for', 'minister', 'ministry', 'department', 'dept', 'provincial', 'responsible', 'chief', 'commissioner'])
const ministryKey = (name) => String(name).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  // "Attorney-General's Department" is the Department of the Attorney-General.
  .replace(/[‘’ʼ']s\s+department\b/g, ' department')
  .replace(/[‘’ʼ']/g, '').replace(/&/g, ' and ').replace(/-/g, ' ')
  .replace(/[^a-z0-9 ]+/g, ' ').split(/\s+/).filter((word) => word && !STOP.has(word)).join(' ')

export const premierOn = (day) => holderOn(PREMIERS, day)
/**
 * The Lieutenant Governor — or an administrator acting between two — on `day`, from the Legislative
 * Library's list: in office from the swearing-in, not from the commission.
 */
export const lieutenantGovernorOn = (day) => holderOn(
  LIEUTENANT_GOVERNORS_OFFICIAL.map((holder) => ({ ...holder, from: startOf(holder.from), to: holder.to ? startOf(holder.to) : null })),
  day
) ?? holderOn(LIEUTENANT_GOVERNORS, day)

/** A body's staffing series: {fiscalYear, basis, value, printedAs, source, locator}, oldest first. */
export const staffingOf = (id) => (STAFFING[id] ?? [])
  .map(([fiscalYear, basis, value, printedAs, source, locator]) => ({ fiscalYear, basis, value, printedAs, source, locator }))

/** The last general election held on or before `day`. */
export const electionBefore = (day) => {
  let found = null
  for (const election of ELECTIONS) {
    if (String(election.date) <= day) found = election
  }
  return found
}

const PEOPLE_ID = 'people-of-british-columbia'

/**
 * Bodies that are partners of a ministry rather than part of it. The First Nations Health Authority
 * is governed by First Nations through the First Nations Health Council and Health Directors
 * Association, alongside a tripartite committee with the Province and Canada; its relationship to the
 * Ministry of Health is partnership, not direction.
 */
const PARTNERS = [
  { body: 'first-nations-health-authority', ministry: 'Ministry of Health', from: '2013' }
]

/**
 * The diagram for `year`.
 *
 * @returns {{
 *   year: number, day: string, present: boolean,
 *   premier: object|null, lieutenantGovernor: object|null, election: object|null, dissolved: boolean,
 *   nodes: object[], edges: {from: string, to: string, kind: string}[]
 * }}
 */
/**
 * @param {number} year
 * @param {{includeUndated?: boolean}} [options]  Also draw, before today, bodies whose start no source
 *   gives — marked uncertain, since an unknown founding date is not evidence that a body did not exist.
 */
export const governmentIn = (year, { includeUndated = false } = {}) => {
  const day = dayOf(year)
  const present = year >= PRESENT_YEAR
  const premier = premierOn(day)
  const lieutenantGovernor = lieutenantGovernorOn(day)
  const election = electionBefore(day)
  const dissolved = present && PENDING_ELECTION && PENDING_ELECTION.dissolved <= day && PENDING_ELECTION.date > day

  const nodes = []
  const edges = []
  const add = (node) => { nodes.push(node); return node }
  const link = (from, to, kind) => edges.push({ from, to, kind })

  add({
    id: PEOPLE_ID,
    kind: 'people',
    branch: null,
    ring: 'seal',
    name: 'People of British Columbia',
    description: 'Every adult citizen living in the province elects a Member of the Legislative Assembly for their electoral district.'
  })

  const assembly = add({
    id: 'legislative-assembly',
    kind: 'assembly',
    branch: 'legislative',
    ring: 'inner',
    name: 'Legislative Assembly of British Columbia',
    seats: election?.totalSeats ?? null,
    election,
    dissolved,
    head: officeHolderOn('speaker', day, 'Speaker'),
    clerk: officeHolderOn('clerk', day, 'Clerk of the Legislative Assembly'),
    events: eventsFor(['legislative-assembly']),
    // The members, where the research has them: the 43rd Parliament so far.
    parliament: election?.parliament === 43 ? PARLIAMENT_43 : null,
    staffing: staffingOf('legislative-assembly'),
    description: 'The elected house of the Legislature, which also includes the Lieutenant Governor. It makes provincial law, votes the government its money, and holds it to account; a government governs only while it has the Assembly’s confidence.',
    officialUrl: 'https://www.leg.bc.ca'
  })
  link(PEOPLE_ID, assembly.id, 'elects')

  const crown = add({
    id: 'lieutenant-governor',
    kind: 'crown',
    branch: 'executive',
    ring: 'inner',
    name: 'Lieutenant Governor of British Columbia',
    head: lieutenantGovernor
      ? {
          title: lieutenantGovernor.category === 'administrator' ? 'Administrator of the Government' : 'Lieutenant Governor',
          person: lieutenantGovernor.name,
          since: lieutenantGovernor.sworn ?? lieutenantGovernor.from,
          commissioned: lieutenantGovernor.commissioned ?? null,
          sequence: lieutenantGovernor.sequence ?? null
        }
      : null,
    events: eventsFor(['lieutenant-governor']),
    evidence: lieutenantGovernor?.source
      ? [claim(
          `${lieutenantGovernor.name}${lieutenantGovernor.sequence ? `, ${lieutenantGovernor.sequence}th in the Library’s numbering` : ''}${lieutenantGovernor.commissioned ? `; commissioned ${lieutenantGovernor.commissioned}` : ''}${lieutenantGovernor.sworn ? `, sworn in ${lieutenantGovernor.sworn}` : ''}`,
          { title: 'Legislative Library of BC — Lieutenant Governors of British Columbia, 1871–Present', url: lieutenantGovernor.source },
          lieutenantGovernor.evidence !== 'documented' ? { note: 'Unverified: from Wikipedia alone.' } : { note: lieutenantGovernor.locator }
        )].filter(Boolean)
      : [],
    description: 'The King’s representative in British Columbia. Gives royal assent to laws, summons and dissolves the Legislature, and appoints the Premier — by convention, whoever can hold the Assembly’s confidence.',
    officialUrl: 'https://ltgov.bc.ca'
  })

  const premierNode = add({
    id: 'premier',
    kind: 'premier',
    branch: 'executive',
    ring: 'inner',
    name: 'Premier of British Columbia',
    head: premier ? { title: 'Premier', person: premier.name, party: premier.party, since: premier.from } : null,
    description: 'Head of the government. Chooses the ministers of the Executive Council, who are appointed by the Lieutenant Governor on the Premier’s advice, and decides how the ministries are organised.'
  })
  link(crown.id, premierNode.id, 'appoints')
  link(assembly.id, premierNode.id, 'confidence')

  // The ministries of the year, and who held each. A ministry in office today takes its minister
  // from the present record, which also has its deputy and staffing.
  const standing = episodesIn(year)
  for (const episode of standing) {
    const today = present && CURRENT_MINISTRIES.some((name) => fold(name) === fold(episode.name))
    const current = today ? CURRENT_MINISTERS[slugify(episode.name)] : null
    add({
      id: episode.id,
      kind: 'ministry',
      branch: 'executive',
      ring: 'cabinet',
      name: episode.name,
      episode,
      head: current?.minister ?? ministerOn(episode.id, day),
      ministers: ministersOf(episode.id),
      deputy: current?.deputy ?? null,
      ministersOfState: current?.ministersOfState ?? [],
      employees: current?.employees ?? staffingOf(episode.id).find((row) => row.basis === 'actual' && Number(row.fiscalYear.slice(0, 4)) === year)?.value ?? null,
      staffing: staffingOf(episode.id),
      officialUrl: current?.officialUrl ?? null,
      description: current?.description ?? null,
      predecessors: predecessorsOf(episode.id),
      successors: successorsOf(episode.id),
      evidence: [
        claim(`${episode.name}, ${episode.from}–${episode.to ?? ''}`, ARCHIVES_DIAGRAM, episode.inferredEnd ? { note: 'End year inferred from what it became.' } : {}),
        current ? claim(`${current.minister.person}, ${current.minister.title}; ${current.deputy?.person ?? 'deputy not recorded'}, ${current.deputy?.title ?? 'Deputy Minister'}`, TODAY_SOURCE, { checked: CURRENT_AS_OF }) : null,
        !current && ministerOn(episode.id, day) ? claim(`${ministerOn(episode.id, day).person}, ${ministerOn(episode.id, day).title}`, ministerOn(episode.id, day).source) : null
      ].filter(Boolean)
    })
    link(premierNode.id, episode.id, 'appoints')
  }

  // Everything around the ministries: the present's bodies from their own record, back to the year
  // each began, and every body the research found standing in the year — Crown corporations and
  // agencies since wound up included.
  //
  // Which ministry answered for a body is known where a source states it for that period. Where it
  // is not, a body that still exists (or became one that does) is placed beside the forerunner of
  // the ministry that answers for it today, and carries `inferredGroup` so the view can say so.
  const todays = new Map(MINISTRY_EPISODES.filter((episode) => episode.to === null).map((episode) => [fold(episode.name), episode.id]))
  const standingByKey = new Map(standing.map((episode) => [ministryKey(episode.name), episode.id]))
  const research = new Map(HISTORICAL_BODIES.map((body) => [body.id, body]))
  const currentById = new Map(CURRENT_BODIES.map((body) => [body.id, body]))
  const stands = (established, ended) => {
    const from = startOf(established)
    const to = startOf(ended)
    return Boolean(from) && from <= day && (!to || to > day)
  }
  // A stated ministry is found among the year's by its name, or failing that by the one near name
  // that contains the other — "Energy, Mines" for "Energy, Mines and Petroleum Resources".
  const standingWords = standing.map((episode) => ({ id: episode.id, words: new Set(ministryKey(episode.name).split(' ')) }))
  const ministryNamed = (name) => {
    // Some bodies answered to the Premier directly, as President of the Executive Council.
    if (/\bpremier\b|president of the executive council/i.test(name)) return 'premier'
    const exact = standingByKey.get(ministryKey(name))
    if (exact) return exact
    const mine = new Set(ministryKey(name).split(' '))
    const near = standingWords.filter(({ words }) => [...words].every((word) => mine.has(word)) || [...mine].every((word) => words.has(word)))
    return near.length === 1 ? near[0].id : null
  }
  const statedPeriod = (record) => (record?.responsible ?? []).filter(([, from, to]) => stands(from ?? '1871', to)).at(-1) ?? null
  const statedGroup = (record) => {
    const period = statedPeriod(record)
    return period ? ministryNamed(period[0]) : null
  }
  // The present body a record is, or became.
  const presentOf = (record, seen = new Set()) => {
    if (!record || seen.has(record.id)) return null
    seen.add(record.id)
    if (currentById.has(record.id)) return currentById.get(record.id)
    return presentOf(research.get(record.became), seen)
  }
  const inferredGroup = (body) => {
    const todaysMinistry = body?.responsibleMinistry ? todays.get(fold(body.responsibleMinistry)) : body?.group
    if (!todaysMinistry) return null
    return present ? todaysMinistry : forerunnerIn(todaysMinistry, year)?.id ?? null
  }
  const lineage = (id) => ({
    cameFrom: HISTORICAL_BODIES.filter((body) => body.became === id).map(({ id: from, name, established, ended }) => ({ id: from, name, established, ended })),
    became: research.get(id)?.became ? (({ id: to, name, established, ended }) => ({ id: to, name, established, ended }))(research.get(research.get(id).became) ?? { id: research.get(id).became, name: currentById.get(research.get(id).became)?.name ?? research.get(id).became }) : null
  })
  const placed = new Set()
  const place = (body, record, { uncertain = false } = {}) => {
    const stated = statedGroup(record)
    const period = stated ? statedPeriod(record) : null
    // FNHA is governed by First Nations, not by a ministry: it is a partner, never a child.
    const partnerOnly = PARTNERS.some((partner) => partner.body === body.id)
    const group = partnerOnly ? null : stated ?? (present && currentById.has(body.id) ? inferredGroup(body) : inferredGroup(presentOf(record ?? body)))
    const family = lineage(body.id)
    const subjects = [body.id, ...family.cameFrom.map((entry) => entry.id), family.became?.id].filter(Boolean)
    const operating = operatingNameIn(body.id, year)
    const node = add({
      ...body,
      ...(operating ? { shortName: operating.name, operatingName: operating } : {}),
      group,
      inferredGroup: !present && Boolean(group) && !stated,
      // Known to have existed that year, with no ministry named for it in the sources.
      unattached: !group && body.ring === 'outer' && !partnerOnly,
      uncertain,
      present,
      events: eventsFor(subjects),
      relations: [...(record?.relations ?? []), ...family.cameFrom.flatMap((entry) => research.get(entry.id)?.relations ?? [])]
        .map(([relation, office, holder, from, to, source, locator]) => ({ relation, office, holder, from, to, source: historySource(source), locator })),
      staffing: staffingOf(body.id),
      ...family,
      evidence: [
        record?.source !== undefined && record?.source !== null
          ? claim(`${record.name}${record.established ? `, from ${record.established}` : ''}${record.ended ? ` to ${record.ended}` : ''}`, historySource(record.source))
          : null,
        period ? claim(`Answered to the ${period[0]}${period[1] ? ` from ${period[1]}` : ''}${period[2] ? ` to ${period[2]}` : ''}`, historySource(period[3])) : null,
        present && body.head?.person ? claim(`${body.head.person}, ${body.head.title}`, TODAY_SOURCE, { checked: CURRENT_AS_OF }) : null,
        !present && body.head?.source ? claim(`${body.head.person}, ${body.head.title}`, body.head.source) : null
      ].filter(Boolean)
    })
    placed.add(body.id)
    if (group) link(group, node.id, 'responsible')
    if (body.kind === 'officer') link(assembly.id, node.id, 'appoints')
    if (body.kind === 'central-agency') link(premierNode.id, node.id, 'responsible')
    return node
  }

  const OFFICES = new Set(Object.keys(OFFICE_HOLDERS))
  for (const body of CURRENT_BODIES) {
    const record = research.get(body.id)
    const established = record?.established ?? (body.established ? String(body.established) : null)
    // A body whose start no source gives is drawn before today only when asked, and marked uncertain.
    const undated = !established
    if (!present && !stands(established, null) && !(includeUndated && undated)) continue
    if (!present && undated) {
      place({ ...body, established: null, head: null, description: body.description ?? null }, record, { uncertain: true })
      continue
    }
    // Before today, a head is whoever held the office that year, where the office's holders are known.
    const head = present ? body.head : OFFICES.has(body.id) ? officeHolderOn(body.id, day) : null
    place({ ...body, established, head: head ?? null, description: body.description ?? record?.description ?? null }, record)
  }

  const KIND = { 'crown-corporation': 'crown-corporation', agency: 'agency', tribunal: 'tribunal', 'health-authority': 'health-authority' }
  for (const record of HISTORICAL_BODIES) {
    if (placed.has(record.id) || record.current || !record.name || !stands(record.established, record.ended)) continue
    place({
      id: record.id,
      kind: KIND[record.kind] ?? 'agency',
      branch: 'executive',
      ring: 'outer',
      name: record.name,
      shortName: record.shortName,
      established: record.established,
      ended: record.ended,
      head: null,
      description: record.description,
      historical: true
    }, record)
  }

  // The Merit Commissioner, an officer of the Legislature from 2001 until the office was folded
  // into the Public Service Agency on 30 June 2026.
  if (stands('2001', '2026-06-30')) {
    place({
      id: 'merit-commissioner',
      kind: 'officer',
      branch: 'legislative',
      ring: 'oversight',
      name: 'Merit Commissioner',
      established: '2001',
      ended: '2026-06-30',
      head: officeHolderOn('merit-commissioner', day, 'Merit Commissioner'),
      description: 'Monitored whether appointments in the BC Public Service were made on merit, reporting to the Legislative Assembly. Abolished by the Budget Measures Implementation Act, 2026; its reviews passed to the head of the BC Public Service Agency.',
      historical: true
    }, null)
  }

  // Sub-agencies, as dots beyond their parent: today's, and in earlier years those known to have
  // begun by then whose parent stood — a division of today's Ministry of Forests is placed beside
  // that ministry's forerunner, as the Crown corporations are.
  const drawn = new Map(nodes.map((node) => [node.id, node]))
  for (const entry of SUB_AGENCIES) {
    const undated = !entry.established
    if (!present && !(entry.established && stands(entry.established, null)) && !(includeUndated && undated)) continue
    const parentId = drawn.has(entry.parent) ? entry.parent
      : !present && MINISTRY_EPISODES.some((episode) => episode.id === entry.parent) ? forerunnerIn(entry.parent, year)?.id ?? null
        : null
    const parent = parentId ? drawn.get(parentId) : null
    if (!parent || !parent.branch) continue
    const node = add({
      ...entry,
      kind: 'sub',
      ring: 'sub',
      branch: parent.branch,
      parent: parent.id,
      parentName: parent.shortName ?? parent.name,
      inferredParent: parent.id !== entry.parent,
      uncertain: !present && undated,
      present,
      events: eventsFor([entry.id]),
      evidence: [claim(`${entry.name}, part of the ${parent.name}`, historySource(entry.source), present ? { checked: CURRENT_AS_OF } : {})].filter(Boolean)
    })
    link(parent.id, node.id, 'part')
  }

  // Partnerships: bodies that work with a ministry without answering to it.
  for (const partner of PARTNERS) {
    if (!stands(partner.from, null) || !drawn.has(partner.body)) continue
    const ministry = standing.find((episode) => fold(episode.name) === fold(partner.ministry))
    if (ministry) link(ministry.id, partner.body, 'partner')
  }

  return { year, day, present, premier, lieutenantGovernor, election, dissolved, nodes, edges }
}

export { PEOPLE_ID }
