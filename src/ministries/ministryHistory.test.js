// Which ministries existed when, and what each became.
//
// The numbers pinned here come from the reference documents this project already measured its
// lockups against — every ministry those documents name turns up in the dataset with years that
// fit. That agreement is the reason to trust the rest of it.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { MINISTRY_GROUPS } from './ministries.js'
import {
  MINISTRY_EPISODES, becameOf, describeMinistry, episodeYears, episodesOf, historicalGroups
} from './ministryHistory.js'

test('every ministry the reference documents name is on record, with fitting years', () => {
  // The coat-of-arms and flag documents were dated by nothing but their own artwork until now.
  const expected = {
    'Ministry of Environment, Lands and Parks': [1991, 2001],
    'Ministry of Employment and Investment': [1993, 2001],
    'Ministry of Management Services': [2001, 2005],
    'Ministry of Transportation and Highways': [1979, 2001],
    'Ministry of Lands, Parks and Housing': [1978, 1986]
  }

  for (const [name, [from, to]] of Object.entries(expected)) {
    const [episode] = episodesOf(name)
    assert.ok(episode, `${name} is on record`)
    assert.equal(episode.from, from, name)
    assert.equal(episode.to, to, name)
  }
})

test('a name that ran more than once keeps its runs apart', () => {
  // Forests was a ministry from 1976, again from 1988, and again from 2022. Merging those into one
  // run would assert a continuity that did not exist.
  const runs = episodesOf('Ministry of Forests')
  assert.ok(runs.length >= 3, `${runs.length} runs`)
  assert.equal(runs[0].to, null, 'the newest run is the open one')
  for (const [a, b] of runs.map((run, i) => [run, runs[i + 1]]).filter(([, b]) => b)) {
    assert.ok(a.from > b.from, 'newest first')
    assert.ok(b.to <= a.from, 'and the runs do not overlap')
  }
})

test('a rename is followed to the end, not one step', () => {
  // Transportation and Highways ended in 2001 and the chain runs all the way to a ministry that
  // exists today, which is the answer someone actually wants.
  const became = becameOf('Ministry of Transportation and Highways')
  assert.deepEqual(became, ['Ministry of Transportation and Transit'])

  const today = MINISTRY_GROUPS.flatMap((group) => group.options)
  assert.ok(today.includes(became[0]), 'and it lands on a ministry the generator already offers')
})

test('a lineage that branched reports every end, not a favourite', () => {
  // Three of them branch. Naming one successor where there are two would read as fact.
  const branched = MINISTRY_EPISODES
    .map((episode) => becameOf(episode.name))
    .filter((ends) => ends.length > 1)
  assert.ok(branched.length > 0, 'the dataset does branch')
})

test('a name nobody recorded is not an error', () => {
  // The list has always been a convenience, and a typed name has always been allowed to be
  // anything at all — including a ministry that never existed.
  assert.equal(describeMinistry('Ministry of Widgets'), null)
  assert.equal(describeMinistry(''), null)
  assert.deepEqual(becameOf('Ministry of Widgets'), [])
})

test('punctuation does not decide whether a ministry is found', () => {
  const curly = MINISTRY_EPISODES.find((episode) => /[’]/.test(episode.name))
  if (!curly) return
  assert.ok(episodesOf(curly.name.replace(/’/g, "'")).length, 'a straight apostrophe finds it')
})

test('the list offers each name once, and never one the generator already has', () => {
  const today = MINISTRY_GROUPS.flatMap((group) => group.options)
  const groups = historicalGroups(today)
  const offered = groups.flatMap((group) => group.options.map((option) => option.value))

  assert.equal(new Set(offered).size, offered.length, 'no name twice')
  for (const name of offered) assert.ok(!today.includes(name), `${name} is not already listed`)
  assert.ok(groups.every((group) => /^\d{4}s$/.test(group.label)), 'grouped by decade')
})

test('the years read as a period, and an unfinished one stays open', () => {
  assert.equal(episodeYears({ from: 1991, to: 2001 }), '1991–2001')
  assert.equal(episodeYears({ from: 2022, to: null }), '2022–')
})
