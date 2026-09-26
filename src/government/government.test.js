import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  changesIn, CURRENT_MINISTRIES, episodesIn, fold, forerunnerIn, MINISTRY_EPISODES, predecessorsOf, standsIn, successorsOf
} from './episodes.js'
import { generatorPatchFor, identityFor, renderEraMark } from './eraMark.js'
import { layoutGovernment } from './layout.js'
import { dayOf, governmentIn, premierOn, PRESENT_YEAR } from './snapshot.js'
import { DEFAULTS } from '../site/lockupDefaults.js'
import { applyUpdate } from '../site/lockupReducer.js'
import { chosenName } from '../site/ministryLink.js'

const names = (episodes) => episodes.map((episode) => episode.name).sort()

test('the present has exactly the ministries in office today', () => {
  assert.deepEqual(names(episodesIn(PRESENT_YEAR)).map(fold), CURRENT_MINISTRIES.map(fold).sort())
})

test('only today’s ministries are left open-ended', () => {
  const open = MINISTRY_EPISODES.filter((episode) => episode.to === null)
  assert.deepEqual(names(open).map(fold), CURRENT_MINISTRIES.map(fold).sort())
})

test('a year is read at its end, so a reorganisation shows one government, not two', () => {
  const in2024 = names(episodesIn(2024))
  assert.ok(in2024.includes('Ministry of Housing and Municipal Affairs'))
  assert.ok(!in2024.includes('Ministry of Housing'))
  assert.ok(!in2024.includes('Ministry of Municipal Affairs'))
})

test('a ministry that began and ended in one year appears in it, unless its successor stands for it', () => {
  const brief = MINISTRY_EPISODES.find((episode) => episode.from === episode.to && !successorsOf(episode.id).some((next) => next.from === episode.from))
  assert.ok(standsIn(brief, brief.from))
  assert.ok(!standsIn(brief, brief.from + 1))
  const renamed = MINISTRY_EPISODES.find((episode) => episode.name === 'Ministry of Jobs, Economic Development and Competitiveness')
  assert.equal(renamed.from, renamed.to)
  assert.ok(!standsIn(renamed, renamed.from))
})

test('renames bind to the run of a name they belong to, not every run of it', () => {
  const forests2022 = MINISTRY_EPISODES.find((episode) => episode.name === 'Ministry of Forests' && episode.from === 2022)
  // Forests became Forests and Lands in 1986; the 2022 ministry has become nothing yet.
  assert.deepEqual(successorsOf(forests2022.id), [])
  const forests1976 = MINISTRY_EPISODES.find((episode) => episode.name === 'Ministry of Forests' && episode.from === 1976)
  assert.deepEqual(names(successorsOf(forests1976.id)), ['Ministry of Forests and Lands'])
})

test('the November 2024 restructure reads as its splits, merges and renames', () => {
  const byType = (type) => changesIn(2024).filter((change) => change.type === type)
  const split = byType('split')
  assert.deepEqual(split.map((change) => names(change.successors)).sort(), [
    ['Ministry of Energy and Climate Solutions', 'Ministry of Mining and Critical Minerals'],
    ['Ministry of Infrastructure', 'Ministry of Transportation and Transit']
  ])
  const merged = byType('merged')
  assert.deepEqual(names(merged[0].predecessors), ['Ministry of Housing', 'Ministry of Municipal Affairs'])
})

test('the 2025 rename is carried past the archive’s last revision', () => {
  const growth = MINISTRY_EPISODES.find((episode) => episode.name === 'Ministry of Jobs and Economic Growth')
  assert.deepEqual(names(predecessorsOf(growth.id)), ['Ministry of Jobs, Economic Development and Innovation'])
})

test('a body is placed beside the forerunner of today’s responsible ministry', () => {
  const finance2001 = MINISTRY_EPISODES.find((episode) => episode.name === 'Ministry of Finance' && episode.from === 2001)
  assert.equal(forerunnerIn(finance2001.id, 2010)?.id, finance2001.id)
  // Which ministry answered for the Liquor Distribution Branch in 1995 is not in the sources.
  const branch = governmentIn(1995).nodes.find((node) => node.id === 'liquor-distribution-branch')
  assert.ok(branch.inferredGroup)
  // Where a source does say, that is what is drawn, and it is not marked as inferred.
  const transit = governmentIn(2001).nodes.find((node) => node.id === 'bc-transit')
  assert.ok(!transit.inferredGroup)
  assert.match(transit.group, /^ministry-of-transportation/)
})

test('bodies appear only from the year they were established', () => {
  assert.ok(!governmentIn(1960).nodes.some((node) => node.id === 'bc-hydro'))
  assert.ok(governmentIn(PRESENT_YEAR).nodes.some((node) => node.id === 'bc-hydro'))
})

test('the premier is read on the year’s last day', () => {
  assert.equal(premierOn(dayOf(1986)).name, 'Bill Vander Zalm')
  assert.equal(premierOn(dayOf(1991)).name, 'Mike Harcourt')
  assert.equal(premierOn(dayOf(PRESENT_YEAR)).to, null)
})

test('every edge joins two bodies on the diagram', () => {
  for (const year of [1871, 1920, 1986, 2001, PRESENT_YEAR]) {
    const government = governmentIn(year)
    const ids = new Set(government.nodes.map((node) => node.id))
    for (const edge of government.edges) assert.ok(ids.has(edge.from) && ids.has(edge.to), `${year}: ${edge.from} → ${edge.to}`)
    const { positions } = layoutGovernment(government.nodes.filter((node) => node.branch))
    for (const node of government.nodes) if (node.branch) assert.ok(positions[node.id], `${year}: ${node.id} placed`)
  }
})

test('a year’s mark takes that year’s identity', () => {
  assert.equal(identityFor(1950), null)
  assert.equal(identityFor(1986).era, 'flag')
  assert.equal(identityFor(2003).era, 'crest')
  assert.equal(identityFor(PRESENT_YEAR).era, 'current')
  for (const era of ['historical', 'flag', 'crest', 'current']) {
    assert.match(renderEraMark({ era, name: 'Ministry of Forests and Lands' }), /^<svg /)
  }
})

test('the generator shows the ministry handed over, whatever it held before', () => {
  // From a state that had a different ministry, and a hand-edited current-era wording.
  const before = applyUpdate(DEFAULTS, { currentName: 'Something typed' })
  const health = applyUpdate(before, generatorPatchFor({ era: 'current', name: 'Ministry of Health' }))
  assert.equal(health.era, 'current')
  assert.equal(health.currentMinistry, 'HLTH')
  assert.equal(health.currentName, 'Ministry of Health')
  assert.equal(chosenName(health), 'Ministry of Health')

  const lands = applyUpdate(health, generatorPatchFor({ era: 'flag', name: 'Ministry of Forests and Lands' }))
  assert.equal(lands.era, 'flag')
  assert.equal(chosenName(lands), 'Ministry of Forests and Lands')
  assert.equal(lands.currentName, 'Ministry of Forests and Lands')
})

test('no year draws the same ministry twice, and every year has one', () => {
  for (let year = 1871; year <= PRESENT_YEAR; year += 1) {
    const standing = episodesIn(year).map((episode) => fold(episode.name))
    assert.ok(standing.length > 0, `${year} is empty`)
    assert.equal(new Set(standing).size, standing.length, `${year} repeats a ministry`)
  }
  // A ministry renamed within its first year gives way to its successor.
  assert.ok(!names(episodesIn(2022)).includes('Ministry of Land, Water and Resource Stewardship'))
})

test('a pair of names joined more than once is joined each time', () => {
  const health2011 = MINISTRY_EPISODES.find((episode) => episode.id === 'ministry-of-health-2011')
  assert.deepEqual(names(predecessorsOf(health2011.id)), ['Ministry of Health Services'])
  assert.equal(forerunnerIn(health2011.id, 2005)?.name, 'Ministry of Health')
})

test('Public Safety is folded into Justice from 2012 to 2017', () => {
  assert.ok(!names(episodesIn(2014)).includes('Ministry of Public Safety and Solicitor General'))
  assert.equal(changesIn(2012).find((change) => change.type === 'merged')?.successors[0].name, 'Ministry of Justice')
  assert.equal(changesIn(2017).find((change) => change.type === 'split')?.predecessors[0].name, 'Ministry of Justice')
})

test('a past ministry has the minister who held it that year', () => {
  const lands = governmentIn(1986).nodes.find((node) => node.id === 'ministry-of-forests-and-lands-1986')
  assert.equal(lands.head.person, 'Jack Kempf')
  assert.deepEqual(lands.ministers.map((minister) => minister.person), ['Jack Kempf', 'John Savage', 'Dave Parker'])
})

test('nearly every ministry of every year has its minister', () => {
  let ministries = 0
  let led = 0
  for (let year = 1872; year < PRESENT_YEAR; year += 1) {
    for (const node of governmentIn(year).nodes) {
      if (node.kind !== 'ministry') continue
      ministries += 1
      if (node.head?.person) led += 1
    }
  }
  assert.ok(led / ministries > 0.95, `${led}/${ministries}`)
})

test('the Speaker, officers and chief justices are those of the year shown', () => {
  assert.equal(governmentIn(1950).nodes.find((node) => node.id === 'legislative-assembly').head.person, 'Nancy Hodges')
  assert.equal(governmentIn(2012).nodes.find((node) => node.id === 'chief-electoral-officer').head.person, 'Keith Archer')
})

test('a body wound up long ago stands in its own years only', () => {
  assert.ok(governmentIn(1985).nodes.some((node) => node.id === 'bc-ferry-corporation'))
  assert.ok(!governmentIn(2005).nodes.some((node) => node.id === 'bc-ferry-corporation'))
  assert.ok(governmentIn(2020).nodes.some((node) => node.id === 'merit-commissioner'))
  assert.ok(!governmentIn(PRESENT_YEAR).nodes.some((node) => node.id === 'merit-commissioner'))
})

test('marks are drawn for the interface: no ground of their own, and the reverse colourway on dark', () => {
  const light = renderEraMark({ era: 'current', name: 'Ministry of Health', theme: 'light' })
  const dark = renderEraMark({ era: 'current', name: 'Ministry of Health', theme: 'dark' })
  assert.doesNotMatch(light, /<rect[^>]*fill="#ffffff"/i)
  assert.notEqual(light, dark)
  assert.match(renderEraMark({ era: 'crest', name: 'Ministry of Forests', theme: 'dark' }), /#ede9e2/i)
})
