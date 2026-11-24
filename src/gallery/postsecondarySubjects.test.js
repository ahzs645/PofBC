import { test } from 'node:test'
import assert from 'node:assert/strict'
import registry from '../../research/identity/postsecondary-2026-11-24/source-register.json' with { type: 'json' }
import { POSTSECONDARY_SUBJECTS } from './postsecondarySubjects.js'

test('all eleven public colleges have source leads without assuming held artwork', () => {
  const colleges = registry.records.filter(r => r.current && r.kind === 'public-college')
  assert.equal(colleges.length, 11)
  assert.ok(colleges.every(r => r.artworkCandidates.length))
  assert.equal(new Set(registry.records.map(r => r.id)).size, registry.records.length)
  const candidates = registry.records.flatMap(r => r.artworkCandidates)
  assert.equal(new Set(candidates.map(a => a.id)).size, candidates.length)
  assert.ok(candidates.every(a => a.sourceUrl.startsWith('https://') && a.sourcePage.startsWith('https://')))
  assert.ok(POSTSECONDARY_SUBJECTS.every(s => s.graphNode === null && s.collectionIds.length === 0))
})

test('splits, amalgamations and operations transfers are not one-to-one renames', () => {
  const byId = new Map(POSTSECONDARY_SUBJECTS.map(s => [s.id, s]))
  const targets = (id, type) => byId.get(id).relations.filter(r => r.type === type).map(r => r.subject)
  assert.deepEqual(targets('okanagan-university-college', 'split-into'), ['okanagan-college', 'ubc-okanagan-campus'])
  assert.deepEqual(targets('kwantlen-college', 'split-from'), ['douglas-college'])
  assert.deepEqual(targets('langara-college', 'split-from'), ['vancouver-community-college'])
  assert.deepEqual(targets('bc-vocational-school-prince-george', 'amalgamated-into'), ['college-of-new-caledonia'])
  assert.deepEqual(targets('bc-open-university', 'transferred-operations-to'), ['thompson-rivers-university'])
  assert.deepEqual(targets('royal-roads-military-college', 'site-succeeded-by'), ['royal-roads-university'])
  assert.equal(targets('royal-roads-military-college', 'renamed-to').length, 0)
})
