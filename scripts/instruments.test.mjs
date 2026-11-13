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

test('policy events have a policy category and lead to their implementation, not to bodies they do not name', () => {
  const announced = EVENTS.filter((event) => event.type === 'policy_announced')
  assert.equal(announced.length, 2)
  for (const event of announced) {
    assert.equal(typeOf(event).kind, 'policy')
    assert.equal(event.relatedEvents.length, 1)
    assert.equal(event.related, undefined)
  }
  assert.equal(byId('policy-better-teamwork-better-care-1996').type, 'policy')
})
