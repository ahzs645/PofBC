// The research package's acceptance cases (tmp/research/package/QA_CASES.md, 2026-09-25), as far as
// this implementation reaches. Each test names the case it checks.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { compareYears } from './compare.js'
import { EVENTS, electionStages, eventsInYear, formatEventDate, operatingNameIn, typeOf } from './events.js'
import { governmentIn, PRESENT_YEAR } from './snapshot.js'

const find = (year, id, options) => governmentIn(year, options).nodes.find((node) => node.id === id)

test('QA 1: 1911 shows the parks function’s origin, not a Parks Branch that did not yet exist', () => {
  const in1911 = eventsInYear(1911).filter((event) => event.subject === 'sub-bc-parks')
  assert.equal(in1911.length, 1)
  assert.equal(typeOf(in1911[0]).kind, 'origin')
  assert.ok(!find(1911, 'sub-bc-parks'), 'no BC Parks node is drawn in 1911')
  assert.equal(eventsInYear(1957).find((event) => event.subject === 'sub-bc-parks')?.type, 'organizational_milestone')
})

test('QA 2: the 1912 wildfire origin is an origin claim, not the date of today’s name or logo', () => {
  const origin = EVENTS.find((event) => event.subject === 'sub-bc-wildfire-service' && event.date.start === '1912' && event.type === 'retrospective_origin_claim')
  assert.equal(typeOf(origin).kind, 'origin')
  assert.ok(!find(1912, 'sub-bc-wildfire-service'), 'the present-day service is not drawn in 1912')
})

test('QA 3: WorkSafeBC is an operating name beside the legal name, not a second body', () => {
  assert.equal(operatingNameIn('workers-compensation-board', 2004), null)
  assert.equal(operatingNameIn('workers-compensation-board', 2005).name, 'WorkSafeBC')
  const board = find(2010, 'workers-compensation-board')
  assert.equal(board.shortName, 'WorkSafeBC')
  assert.match(board.name, /Workers' Compensation Board/)
  assert.equal(governmentIn(2010).nodes.filter((node) => /worksafe/i.test(node.id)).length, 0)
})

test('QA 4: year-only events stay year-precise', () => {
  const logo = EVENTS.find((event) => event.id === 'pkg:wcb-logo-1968')
  assert.equal(logo.date.precision, 'year')
  assert.equal(formatEventDate(logo.date), '1968')
  for (const event of EVENTS.filter((entry) => entry.date.precision === 'year')) assert.match(event.date.start, /^\d{4}$/)
})

test('QA 5: a commission is not a swearing-in', () => {
  const commission = EVENTS.find((event) => event.type === 'commission_issued')
  const sworn = EVENTS.find((event) => event.type === 'sworn_into_office')
  assert.equal(commission.date.start, '2024-12-19')
  assert.equal(sworn.date.start, '2025-01-30')
  assert.notEqual(find(2024, 'lieutenant-governor').head.person, 'Wendy Lisogar-Cocchia')
})

test('QA 7 and 8: the 2026 election is scheduled, with no results and no new cabinet on voting day', () => {
  const stages = electionStages('2026-09-25')
  assert.ok(stages.length >= 5)
  assert.ok(stages.filter((stage) => stage.date.start > '2026-09-25').every((stage) => stage.ahead))
  const assembly = find(PRESENT_YEAR, 'legislative-assembly')
  assert.equal(assembly.election.date, '2024-10-19', 'the Assembly still reads the last election held')
  assert.equal(governmentIn(PRESENT_YEAR).premier.name, 'David Eby')
})

test('QA 9: FNHA is a partner of the Ministry of Health, not its child, and its transfers stay separate', () => {
  const government = governmentIn(PRESENT_YEAR)
  const fnha = government.nodes.find((node) => node.id === 'first-nations-health-authority')
  assert.equal(fnha.group, null)
  assert.ok(government.edges.some((edge) => edge.to === fnha.id && edge.kind === 'partner'))
  assert.ok(!government.edges.some((edge) => edge.to === fnha.id && edge.kind === 'responsible'))
  const transfers = EVENTS.filter((event) => event.subject === fnha.id && event.type === 'functions_transferred')
  assert.deepEqual(transfers.map((event) => event.date.start), ['2013-07-02', '2013-10-01'])
})

test('QA 10: a body whose ministry is unknown stays visible, with no guessed edge', () => {
  const government = governmentIn(1985)
  const rail = government.nodes.find((node) => node.id === 'bc-railway-company')
  assert.ok(rail, 'BC Rail is drawn in 1985')
  if (!rail.group) {
    assert.ok(rail.unattached)
    assert.ok(!government.edges.some((edge) => edge.to === rail.id && edge.kind === 'responsible'))
  }
})

test('QA 11: a present-day chief executive is not shown as fact in an earlier year', () => {
  assert.equal(find(2015, 'bc-hydro').head, null)
  assert.ok(find(PRESENT_YEAR, 'bc-hydro').head?.person)
})

test('QA 19: an unknown start is not rendered as "did not exist" when undated bodies are asked for', () => {
  const plain = governmentIn(1990)
  const withUndated = governmentIn(1990, { includeUndated: true })
  const extra = withUndated.nodes.filter((node) => node.uncertain)
  assert.ok(extra.length > 0)
  assert.ok(extra.every((node) => !plain.nodes.some((other) => other.id === node.id)))
})

test('every claim of evidence names a source', () => {
  for (const year of [1950, 1986, 2010, PRESENT_YEAR]) {
    for (const node of governmentIn(year).nodes) {
      for (const entry of node.evidence ?? []) assert.ok(entry.source?.url, `${year} ${node.id}: ${entry.claim}`)
    }
  }
})

test('the comparison accounts for every ministry on both sides', () => {
  const result = compareYears(1986, 2001)
  const { continuing, transformed, created, ended, before, after } = result.ministries
  assert.equal(continuing + transformed.length + ended.length, before)
  assert.ok(continuing + created.length <= after)
  assert.ok(result.offices.some((office) => office.label === 'Premier'))
})

// ── The sub-agency review (tmp/research/history/sub-agencies-researched.json, 2026-09-26) ────────

import { SUB_AGENCIES } from './historyData.js'

const sub = (id) => SUB_AGENCIES.find((entry) => entry.id === id)

test('a body in two collection files keeps the date only the second file had', () => {
  for (const id of ['sub-bc-farm-industry-review-board', 'sub-civil-resolution-tribunal', 'sub-employment-standards-tribunal']) {
    assert.ok(sub(id).established, id)
    assert.equal(SUB_AGENCIES.filter((entry) => entry.id === id).length, 1, `${id} is kept once`)
  }
})

test('no date is ever an object turned into text', () => {
  for (const entry of SUB_AGENCIES) {
    for (const value of [entry.established, entry.ended]) {
      if (value !== null && value !== undefined) assert.match(value, /^\d{4}(-\d{2}(-\d{2})?)?$/, entry.id)
    }
  }
})

test('GPEB stands until IGCO replaces it on 13 April 2026, and not after', () => {
  // Its start is unknown, so before today it is drawn only when undated bodies are asked for.
  assert.ok(find(2025, 'sub-gaming-policy-and-enforcement-branch', { includeUndated: true }))
  assert.ok(!find(PRESENT_YEAR, 'sub-gaming-policy-and-enforcement-branch'))
  const igco = find(PRESENT_YEAR, 'sub-independent-gambling-control-office')
  assert.ok(igco)
  assert.ok(igco.cameFrom.some((body) => body.id === 'sub-gaming-policy-and-enforcement-branch'))
})

test('CRT: its 2012 assent is an event, its 2016 commencement the start', () => {
  assert.equal(sub('sub-civil-resolution-tribunal').established, '2016-07-13')
  assert.ok(!find(2014, 'sub-civil-resolution-tribunal'))
  const assent = EVENTS.find((event) => event.subject === 'sub-civil-resolution-tribunal' && event.date.start === '2012-05-31')
  assert.equal(assent?.type, 'legislation_assented')
})

test('IIO: legal establishment (July 2011) and opening are kept apart, at month precision', () => {
  const iio = sub('sub-independent-investigations-office')
  assert.equal(iio.established, '2011-07')
  assert.equal(iio.establishedClaim.precision, 'month')
  assert.ok(EVENTS.some((event) => event.subject === iio.id && event.date.start !== '2011-07'))
})

test('BC Renal is not drawn under PHSA before the sourced 2002 relationship', () => {
  const in2001 = find(2001, 'sub-bc-renal')
  assert.ok(in2001, 'it stood from 1997')
  assert.notEqual(in2001.parent, 'provincial-health-services-authority')
  assert.ok(in2001.unplacedSub)
  const in2003 = find(2003, 'sub-bc-renal')
  assert.equal(in2003.parent, 'provincial-health-services-authority')
  assert.ok(!in2003.inferredParent)
})

test('an observation is not a period: BCTS is placed by it in 2003 only', () => {
  assert.ok(!find(2003, 'sub-bc-timber-sales').inferredParent)
  assert.ok(find(2010, 'sub-bc-timber-sales').inferredParent)
  // And an observed name is used only in the year it was seen.
  assert.equal(find(1973, 'sub-hospital-appeal-board').name, 'Medical Appeal Board')
  assert.equal(find(1990, 'sub-hospital-appeal-board').name, 'Hospital Appeal Board')
})

test('the bodies WCAT replaced are drawn in their years, apart, and lead to it', () => {
  const board = find(1980, 'sub-workers-compensation-review-board')
  assert.equal(board.name, 'Boards of Review')
  assert.ok(board.unplacedSub && !board.parent)
  assert.equal(find(1995, 'sub-workers-compensation-review-board').became.id, 'sub-workers-compensation-appeal-tribunal')
  assert.ok(!find(2004, 'sub-workers-compensation-review-board'))
})

test('a start the review could not settle is marked, not presented as resolved', () => {
  // (BC Timber Sales was, until a recorded decision settled it — tested below.)
  const powertech = find(2000, 'sub-powertech-labs')
  assert.ok(powertech?.reconcile)
})

test('a recorded decision settles BCTS on 20 June 2003, and keeps the dates it set aside as events', () => {
  const bcts = find(2010, 'sub-bc-timber-sales')
  assert.equal(bcts.established, '2003-06-20')
  assert.ok(!bcts.reconcile)
  assert.match(bcts.evidence[0].note, /Decided 2026-09-26/)
  const dates = EVENTS.filter((event) => event.subject === 'sub-bc-timber-sales').map((event) => event.date.start)
  assert.ok(dates.includes('2003-04-01') && dates.includes('2003-05-29'))
})
