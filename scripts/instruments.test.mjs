import { test } from 'node:test'
import assert from 'node:assert/strict'
import { INSTRUMENTS } from '../src/government/instrumentsData.js'
import { instrumentsOfBody } from '../src/government/instruments.js'
import { typeOf, EVENTS } from '../src/government/events.js'

const byId = (id) => INSTRUMENTS.find((entry) => entry.id === id)

test('the Teachers Act gathers its three bodies with their sections, as today\'s basis, not their founding', () => {
  const act = byId('act-teachers-act')
  const basis = act.relations.filter((relation) => relation.relation === 'current_legal_basis')
  assert.deepEqual(basis.map((relation) => [relation.body, relation.provisions[0]]).sort(),
    [['sub-bc-teachers-council', 's. 9'], ['sub-commissioner-for-teacher-regulation', 's. 2'], ['sub-disciplinary-and-professional-conduct-board', 's. 26']])
  for (const relation of basis) assert.equal(relation.from, null)
  // The dated establishment comes from the 2012 commencement, through the regulation that brought it in.
  const founded = act.relations.find((relation) => relation.relation === 'established_by' && relation.body === 'sub-bc-teachers-council')
  assert.equal(founded.from, '2012-01-09')
  assert.match(founded.evidence[0].note, /B\.C\. Reg\. 239\/2011/)
})

test('BC Hydro: established by the 1962 Act at assent, its 1962 commencement a milestone, the 1964 Act and 1965 order later', () => {
  const act = byId('act-british-columbia-hydro-and-power-authority-act')
  assert.deepEqual(act.relations.map((relation) => [relation.body, relation.relation, relation.from]), [['bc-hydro', 'established_by', '1962-03-29']])
  assert.deepEqual(act.milestones.map((milestone) => milestone.date.start), ['1962-03-29', '1962-03-30'])
  const { groups } = instrumentsOfBody('bc-hydro')
  assert.deepEqual(groups.map((group) => group.kind), ['established_by', 'reorganized_by'])
  assert.ok(groups[1].rows.some((row) => row.instrument.id === 'oic-1965-2386'))
})

test('a ministry is not ended or established by orders about the bodies filed under it', () => {
  for (const entry of INSTRUMENTS) {
    for (const relation of entry.relations) {
      if (/^(ministry|department)-/.test(relation.body)) assert.ok(['reorganized_by', 'announced', 'administers'].includes(relation.relation), `${entry.id} → ${relation.body}`)
    }
  }
})

test('every relationship names a body and rests on a source or citation; ids are unique', () => {
  assert.equal(new Set(INSTRUMENTS.map((entry) => entry.id)).size, INSTRUMENTS.length)
  for (const entry of INSTRUMENTS) for (const relation of entry.relations) assert.ok(relation.body && (relation.source?.url || relation.citation), entry.id)
})

test('health and trades policy announcements link to the events that carried them out', () => {
  const implementations = [
    ['atlas:health-lineage-new-directions', 'atlas:health-lineage-act-1993'],
    ['atlas:health-lineage-better-teamwork', 'atlas:health-lineage-devolution-1997'],
    ['atlas:itac-announced-1997', 'atlas:itac-established-1997'],
    ['atlas:itac-wind-up-announced-2002', 'atlas:itac-interim-administration-2002']
  ]
  for (const [announcement, implementation] of implementations) {
    const event = EVENTS.find(({ id }) => id === announcement)
    assert.equal(event?.type, 'policy_announced', announcement)
    assert.equal(typeOf(event).kind, 'policy', announcement)
    assert.deepEqual(event.relatedEvents, [implementation], announcement)
    assert.equal(event.related, undefined, announcement)
    assert.ok(EVENTS.some(({ id }) => id === implementation), implementation)
  }
  assert.equal(byId('policy-better-teamwork-better-care-1996').type, 'policy')
})

test('the 1977 Apprenticeship and Training Development Act established the board on commencement', () => {
  const act = byId('act-apprenticeship-and-training-development-act')
  assert.deepEqual(act?.citations, ['SBC 1977, c. 65'])
  const founding = act.relations.find(({ body }) => body === 'provincial-apprenticeship-board')
  assert.equal(founding?.relation, 'established_by')
  assert.deepEqual(founding.provisions, ['s. 10(1)'])
  assert.equal(founding.from, '1978')
  assert.equal(founding.precision, 'year')
})

test('the development corporations retain their different commencement histories and the transfer of assets', () => {
  const development = byId('act-development-corporation-of-british-columbia-act')
  assert.deepEqual(development.relations.map(({ relation, from }) => [relation, from]), [['established_by', '1973-03-31']])
  assert.deepEqual(development.milestones.map(({ date }) => date.start), ['1973-04-18'])

  const transfer = byId('act-british-columbia-enterprise-corporation-financial-restructuring-act')
  assert.deepEqual(transfer.relations.map(({ body, relation, from }) => [body, relation, from]),
    [['bc-development-corporation', 'reorganized_by', '1987-03-31']])
  assert.equal(byId('bc-reg-1987-289').milestones[0].event, 'atlas:bcdc-transfer-to-bcec-1987')

  const trade = byId('act-trade-development-corporation-act')
  assert.deepEqual(trade.relations.map(({ body, from }) => [body, from]), [['bc-trade-development-corporation', '1989-06-01']])
  assert.equal(byId('bc-reg-1989-148').milestones[0].event, 'atlas:bctrade-act-assented-1989')
})

test('every citation is read or decided: the review list stays empty unless a new citation arrives', async () => {
  const { readFileSync } = await import('node:fs')
  const review = JSON.parse(readFileSync('research/audit/instruments-review.json', 'utf8'))
  assert.equal(review.count, 0, review.rows.map((row) => `${row.origin}: ${row.reason}`).join('\n'))
})

test('B.C. Reg. 293/2001: the five authorities formed by it and the 44 Schedule A authorities ended by it', () => {
  const reg = byId('bc-reg-2001-293')
  const formed = reg.relations.filter((relation) => relation.relation === 'established_by').map((relation) => relation.body).sort()
  assert.deepEqual(formed, ['fraser-health', 'interior-health', 'island-health', 'northern-health', 'vancouver-coastal-health'])
  const ended = reg.relations.filter((relation) => relation.relation === 'ended_by')
  assert.equal(ended.length, 44)
  for (const relation of ended) assert.equal(relation.from, '2001-12-12')
  const northern = ended.filter((relation) => /Northern Health Authority/.test(relation.note))
  assert.equal(northern.length, 13)
})

test('BC Laws responsibilities join an Act page by short title and a ministry by episode, never by listing period', async () => {
  const amr = await import('../src/government/amr.js')
  const teachers = amr.assignmentsOfActTitle('Teachers Act')
  assert.equal(teachers.ambiguous, false)
  assert.ok(teachers.assignments.length >= 2)
  for (const run of teachers.assignments) {
    // A start is an order's date, two listings it fell between, or "already listed in December 2015".
    assert.ok(['oic-resume', 'oic-checked', 'bounded', 'before-coverage'].includes(run.effectiveFrom.basis))
    if (run.effectiveFrom.basis !== 'oic-resume' && run.effectiveFrom.basis !== 'oic-checked') assert.equal(amr.isDated(run.effectiveFrom), false)
  }
  const acts = amr.actsOfEpisode('ministry-of-attorney-general-2017')
  assert.ok(acts.length > 100)
  assert.equal(new Set(acts.map((act) => act.key)).size, acts.length)
  assert.equal(amr.actKey('Teachers Act'), amr.actKey('Teachers'))
})
