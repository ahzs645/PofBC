// Dated events, read at the precision their sources give.
//
// Every event keeps the precision its source gave it. A year stays a year — "1957", never 1 January
// 1957 — so it is shown as a year, counted in its year, and never placed on a day it was not
// recorded on. Scheduled events (the 2026 election's milestones) are kept apart from past ones:
// before their day they are shown as scheduled, and nothing is inferred from them.

import { EVENTS, EVENT_SOURCES } from './eventsData.js'

export { EVENTS, EVENT_SOURCES }

/** What each type of event is called, and which kind of change it is. */
export const EVENT_TYPES = {
  function_milestone: { label: 'Origin of the function', kind: 'origin' },
  retrospective_origin_claim: { label: 'Origin, as the body traces it', kind: 'origin' },
  operational_origin: { label: 'Began operating', kind: 'origin' },
  organizational_milestone: { label: 'Organizational change', kind: 'structure' },
  established: { label: 'Established', kind: 'structure' },
  legal_establishment: { label: 'Established in law', kind: 'structure' },
  dissolved: { label: 'Dissolved', kind: 'structure' },
  merged: { label: 'Merged', kind: 'structure' },
  split: { label: 'Split', kind: 'structure' },
  legal_name_change: { label: 'Legal name changed', kind: 'name' },
  operating_name_change: { label: 'Operating name adopted', kind: 'name' },
  name_change: { label: 'Renamed', kind: 'name' },
  logo_change: { label: 'New logo', kind: 'identity' },
  identity_change: { label: 'New identity', kind: 'identity' },
  executive_appointment: { label: 'Chief executive appointed', kind: 'people' },
  commission_issued: { label: 'Commission issued', kind: 'people' },
  sworn_into_office: { label: 'Sworn into office', kind: 'people' },
  agreement_signed: { label: 'Agreement signed', kind: 'relationship' },
  functions_transferred: { label: 'Functions transferred', kind: 'relationship' },
  election_called: { label: 'Election called', kind: 'election' },
  nominations_close: { label: 'Nominations close', kind: 'election' },
  advance_voting: { label: 'Advance voting', kind: 'election' },
  final_voting_day: { label: 'Final Voting Day', kind: 'election' },
  final_count: { label: 'Final count', kind: 'election' },
  return_day: { label: 'Return Day', kind: 'election' },
  general_election_period: { label: 'General election', kind: 'election' },
  electoral_system_context: { label: 'Electoral history', kind: 'election' },
  symbol_adopted: { label: 'Symbol adopted', kind: 'symbol' },
  symbol_granted: { label: 'Symbol granted', kind: 'symbol' }
}

/**
 * The research uses a richer vocabulary than the table above — "enabling_statute_assented",
 * "name_first_observed", "executive_departure" — so a type the table does not name is sorted by what
 * its name says, and labelled in plain words.
 */
const KIND_BY_NAME = [
  [/origin|operational_start|service_launch|program_launch|function_added/, 'origin'],
  [/name|retitled/, 'name'],
  [/logo|identity/, 'identity'],
  [/executive|appoint|sworn|commission|attested/, 'people'],
  [/statute|legislation|legal_basis|legal_instrument|act_/, 'law'],
  [/transfer|placement|grouping|partner|agreement|acquisition|jurisdiction/, 'relationship'],
  [/establish|reorgani|amalgamation|merger|succession|governance|status|dissol|repeal|headquarters/, 'structure'],
  [/election|voting|nomination|writ|return_day|count/, 'election']
]

const plain = (type) => {
  const text = type.replace(/_/g, ' ')
  return text.charAt(0).toUpperCase() + text.slice(1)
}

export const typeOf = (event) => EVENT_TYPES[event.type] ??
  { label: plain(event.type), kind: KIND_BY_NAME.find(([pattern]) => pattern.test(event.type))?.[1] ?? 'other' }

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

const part = (value) => {
  const [year, month, day] = String(value).split('-').map(Number)
  return { year, month: month || null, day: day || null }
}

const one = (value) => {
  const { year, month, day } = part(value)
  if (day) return `${day} ${MONTHS[month - 1]} ${year}`
  if (month) return `${MONTHS[month - 1]} ${year}`
  return String(year)
}

/** A date as precisely as it is known, and no more precisely: "1957", "March 1911", "16–21 October 2026". */
export const formatEventDate = ({ start, end }) => {
  if (!end) return one(start)
  const a = part(start)
  const b = part(end)
  if (a.year === b.year && a.month && a.month === b.month && a.day && b.day) return `${a.day}–${b.day} ${MONTHS[a.month - 1]} ${a.year}`
  if (a.year === b.year && a.month && b.month && !a.day && !b.day) return `${MONTHS[a.month - 1]}–${MONTHS[b.month - 1]} ${a.year}`
  return `${one(start)} – ${one(end)}`
}

export const yearOfEvent = (event) => part(event.date.start).year

/** Whether a scheduled event is still ahead on `day`; a past event never is. */
export const isAhead = (event, day) => event.status !== 'source_reported_past' && String(event.date.start) > day

/** Events about any of these subjects, oldest first. */
export const eventsFor = (subjects) => {
  const wanted = new Set(subjects)
  return EVENTS.filter((event) => wanted.has(event.subject))
}

/** Events that fall in `year` — a range counts in every year it touches. */
export const eventsInYear = (year) => EVENTS.filter((event) => {
  const from = part(event.date.start).year
  const to = event.date.end ? part(event.date.end).year : from
  return from <= year && year <= to
})

/**
 * Names a body has been known by other than its own — a legal name kept while it operated under
 * another. Kept as uses of a name, not as new bodies: WorkSafeBC is the Workers' Compensation Board.
 */
export const NAME_USES = [
  {
    subject: 'workers-compensation-board',
    name: 'WorkSafeBC',
    use: 'operating',
    from: '2005',
    note: 'Operating name since 2005; the legal name remains Workers’ Compensation Board.',
    event: 'pkg:worksafebc-name-2005'
  }
]

/** The operating name a body used in `year`, if it used one other than its own. */
export const operatingNameIn = (subject, year) => NAME_USES
  .filter((use) => use.subject === subject && part(use.from).year <= year && (!use.to || part(use.to).year > year))
  .at(-1) ?? null

/**
 * An election's stages on `day`: each milestone, whether it has passed, and which is next. Nothing
 * past the milestones is inferred — no results before they are published, no cabinet change on
 * voting day.
 */
export const electionStages = (day, subject = 'legislative-assembly', year = 2026) => {
  const stages = EVENTS
    .filter((event) => event.subject === subject && typeOf(event).kind === 'election' && yearOfEvent(event) === year)
    .map((event) => ({ ...event, ahead: isAhead(event, day) || String(event.date.end ?? event.date.start) > day }))
  const next = stages.find((stage) => stage.ahead)
  return stages.map((stage) => ({ ...stage, next: stage === next }))
}
