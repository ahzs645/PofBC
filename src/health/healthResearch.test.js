import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { HEALTH_RESEARCH } from './healthResearch.generated.js'
import { HEALTH_CATALOGUE } from './healthAreas.generated.js'
import { buildHealthResearch, researchMarkdown } from '../../scripts/health-map-research.mjs'

const read = (path) => JSON.parse(readFileSync(new URL(`../../${path}`, import.meta.url), 'utf8'))
const comparison = read('public/health-geography/boundary-comparison.json')
const input = read('research/health-geography/evidence-plan.json')

test('the app and downloadable review derive from the same evidence inputs', () => {
  const built = buildHealthResearch(HEALTH_CATALOGUE, comparison, input)
  assert.deepEqual(HEALTH_RESEARCH, built)
  assert.deepEqual(read('public/health-geography/research-plan.json'), built)
  const report = researchMarkdown(built)
  for (const path of ['research/health-geography/records-to-obtain.md', 'public/health-geography/records-to-obtain.md']) {
    assert.equal(readFileSync(new URL(`../../${path}`, import.meta.url), 'utf8'), report)
  }
})

test('every source label has a stated assumption and scoped next steps without promoting identity or geometry', () => {
  assert.equal(HEALTH_RESEARCH.assessments.length, 52)
  assert.equal(HEALTH_RESEARCH.coverage.institutionalMatches, 51)
  assert.equal(HEALTH_RESEARCH.coverage.verifiedHistoricalBoundaries, 0)
  assert.equal(HEALTH_RESEARCH.coverage.scopeReviewNeeded, 7)
  for (const area of HEALTH_RESEARCH.assessments) {
    assert.ok(area.assumption.length > 20)
    assert.equal(area.boundaryIdentityVerified, false)
    assert.equal(area.historicalOverlapMeasured, false)
    const tasks = HEALTH_RESEARCH.workItems.filter((item) => area.workItemIds.includes(item.id))
    assert.ok(tasks.some((item) => item.kind === 'analysis'))
    assert.ok(tasks.some((item) => item.kind === 'records'))
    assert.ok(tasks.every((item) => item.areaIds.includes('*') || item.areaIds.includes(area.areaId)))
  }
  assert.equal(HEALTH_RESEARCH.assessments.find((area) => area.areaId === 'nisgaa-source-area').identityConfirmed, false)
})

test('acquisition targets retain routes, dates, closure criteria and unsent request drafts', () => {
  const records = HEALTH_RESEARCH.workItems.filter((item) => item.kind === 'records')
  assert.equal(records.length, 7)
  for (const item of records) {
    assert.equal(item.status, 'not-requested')
    assert.equal(item.custodyConfirmed, false)
    for (const key of ['requestText', 'dateRange', 'recordsNeeded', 'route', 'completionEvidence']) assert.ok(item[key].trim().length > 0, `${item.id}: ${key}`)
  }
  assert.match(records.find((item) => item.id === 'nisgaa-identity').route, /do not presume Nisga’a institutions/)
  assert.match(records.find((item) => item.id === 'completed-transfers').route, /102906/)
})

test('the compiler rejects unknown sources and area scopes', () => {
  const badSource = structuredClone(input)
  badSource.workItems[0].sourceIds.push('missing-source')
  assert.throws(() => buildHealthResearch(HEALTH_CATALOGUE, comparison, badSource), /Unknown research source/)
  const badArea = structuredClone(input)
  badArea.workItems[0].areaIds.push('missing-area')
  assert.throws(() => buildHealthResearch(HEALTH_CATALOGUE, comparison, badArea), /Unknown work area/)
})
