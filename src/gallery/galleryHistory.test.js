import { test } from 'node:test'
import assert from 'node:assert/strict'
import { collectionById, entriesOf, entriesOfNode, childCollectionsOf } from './collections.js'
import { galleryHistoryOf } from './galleryHistory.js'

test('an operating name change is one collection, an era for each name, with the earlier name’s link kept', () => {
  const [next] = galleryHistoryOf('bc-safety-authority').successors
  const line = collectionById('collected-technical-safety-bc')
  assert.equal(next.type, 'renamed')
  assert.equal(next.date, '2017-09-20')
  assert.equal(next.collection, line)
  // The old collection's link opens the line, and the rename is its eras rather than a link to itself.
  assert.equal(collectionById('collected-bc-safety-authority'), line)
  assert.deepEqual(line.eras.map(({ id }) => id), ['name-bc-safety-authority', 'name-technical-safety-bc'])
  assert.ok(!galleryHistoryOf(line.graphNode).predecessors.some((row) => row.collection === line))
})

test('regional health pages show statutory amalgamations and service transfers with their own relationship types', () => {
  const authorityIds = ['fraser-health', 'interior-health', 'northern-health', 'vancouver-coastal-health', 'island-health']
  const histories = authorityIds.map((id) => galleryHistoryOf(id).predecessors)
  assert.deepEqual(histories.map((rows) => rows.filter((row) => row.type === 'amalgamated').length), [3, 17, 13, 5, 6])
  assert.deepEqual(histories.map((rows) => rows.filter((row) => row.collection).length), [3, 6, 1, 4, 3])
  assert.equal(histories[1].find((row) => row.id === 'kootenay-boundary-community-health-services-society').type, 'services')
  assert.equal(histories[3].find((row) => row.id === 'coast-garibaldi-community-health-services-society').type, 'services')
})

test('a split links all destinations to one historical record without rewriting a later territory move as a merger', () => {
  const cariboo = 'cariboo-community-health-services-society'
  const { successors } = galleryHistoryOf(cariboo)
  assert.deepEqual(successors.map(({ id, type, date }) => [id, type, date]), [
    ['interior-health', 'services', '2001-12-12'],
    ['northern-health', 'services', '2001-12-12'],
    ['vancouver-coastal-health', 'territory', '2002-03-18']
  ])
  for (const { id, type, date } of successors) {
    const reverse = galleryHistoryOf(id).predecessors.find((row) => row.id === cariboo)
    assert.equal(reverse.collection, undefined)
    assert.equal(reverse.type, type)
    assert.equal(reverse.date, date)
  }
  assert.deepEqual(galleryHistoryOf('bella-coola-and-district-transitional-health-authority').successors
    .map(({ id, type }) => [id, type]), [['interior-health', 'amalgamated'], ['vancouver-coastal-health', 'territory']])
})

test('the liquor split keeps one Board collection and a path to both successors', () => {
  const boardId = 'liquor-control-board'
  const distributionId = 'liquor-distribution-branch'
  const licensingId = 'liquor-control-and-licensing-branch'
  const board = collectionById(`collected-${boardId}`)
  assert.deepEqual(galleryHistoryOf(boardId).successors.map(({ id }) => id), [distributionId, licensingId])
  for (const id of [distributionId, licensingId]) {
    assert.equal(galleryHistoryOf(id).predecessors[0].collection, board)
  }
  assert.ok(!childCollectionsOf(`collected-${distributionId}`).includes(board))
  assert.equal(entriesOfNode(board, boardId)[0].id, 'source-recovered-followup-liquor-control-board-letterhead-1941')
})

test('SIFERP links to FORREX across the rename and each collection owns its period’s marks', () => {
  const early = collectionById('collected-siferp')
  const later = collectionById('collected-forrex')
  const [next] = galleryHistoryOf('siferp').successors
  assert.equal(next.collection, later)
  assert.equal(next.date, '2002-07-29')
  assert.equal(galleryHistoryOf('forrex').predecessors[0].collection, early)
  assert.deepEqual(early.entries.map(({ id }) => id), ['forrex-siferp'])
  assert.deepEqual(later.eras.map(({ entries }) => entries.map(({ id }) => id)), [
    ['forrex-partnership'], ['forrex-forum']
  ])
})

test('the two Science Council names lead through the BCIC merger to Innovate BC', () => {
  const science = collectionById('collected-science-council-of-bc')
  const bcic = collectionById('collected-bc-innovation-council')
  const current = collectionById('collected-innovate-bc')
  assert.deepEqual(science.eras.map((era) => era.entries.map((entry) => entry.id)), [
    ['source-recovered-science-council-2003'], ['iscbc-2004']
  ])
  // BCIC continued as Innovate BC in 2018, so one collection holds both names, an era each.
  assert.equal(bcic, current)
  assert.deepEqual(current.eras.map(({ id }) => id), ['name-bc-innovation-council', 'name-innovate-bc'])
  // The merger that formed BCIC still reads from both sides, on the line's page.
  const forward = galleryHistoryOf(science.graphNode).successors.find((row) => row.collection === current)
  const backward = galleryHistoryOf(current.graphNode).predecessors.find((row) => row.collection === science)
  for (const row of [forward, backward]) assert.deepEqual([row.type, row.date], ['merger', '2004-10'])
  // The rename inside the line is its eras, not a link to itself.
  assert.ok(!galleryHistoryOf(current.graphNode).predecessors.some((row) => row.collection === current))
  const early = entriesOf(bcic).find((entry) => entry.id === 'bcic-orbit')
  assert.deepEqual(early.versions.map((version) => version.sourceDate).sort(), ['2006/07', '2007/08'])
  assert.ok(entriesOf(bcic).some((entry) => entry.id === 'source-recovered-bcic-2008-09'))
})

test('the shared council timeline owns each linked design and resolves both sides of the ASI merger', async () => {
  const { ASI_ID } = await import('./advancedSystemsInstitute.js')
  const { COUNCIL_TIMELINE, COUNCIL_TIMELINE_OWNERS } = await import('./scienceCouncilHistory.js')
  const bcic = collectionById('collected-bc-innovation-council')
  const partners = galleryHistoryOf(bcic.graphNode).predecessors.filter((row) => row.type === 'merger')
  assert.deepEqual(partners.map((row) => row.id).sort(), [ASI_ID, 'science-council-of-bc'])
  for (const row of partners) {
    assert.equal(row.collection, collectionById(`collected-${row.id}`))
    assert.equal(galleryHistoryOf(row.id).successors.find((next) => next.collection === bcic).date, '2004-10')
  }
  for (const owner of COUNCIL_TIMELINE_OWNERS) {
    const collection = collectionById(`collected-${owner}`)
    const art = COUNCIL_TIMELINE.filter((row) => row.owner === owner).flatMap((row) => row.marks ?? [])
    assert.deepEqual(art.sort(), entriesOfNode(collection, owner).map((entry) => entry.id).sort(), owner)
  }
})

test('ITAC’s official vector leads the collection and reconstructions keep their source versions', () => {
  const commission = collectionById('collected-industry-training-and-apprenticeship-commission')
  const authority = collectionById('collected-industry-training-authority')
  const skilledTrades = collectionById('collected-skilledtradesbc')
  const spiral = commission.entries.find((entry) => entry.id === 'source-recovered-itac-letterhead-2003')
  assert.equal(spiral.asset.id, 'itac-spiral-black-reconstruction')
  assert.equal(spiral.versions[0], spiral.asset)
  assert.equal(spiral.identity.provenance, 'third_party_reconstruction')
  assert.deepEqual(spiral.versions.filter((asset) => !asset.reconstruction).map((asset) => asset.sourceDate).sort(),
    ['2003-06-10', '2004-04-08', 'June 2001'])
  assert.ok(spiral.versions.filter((asset) => !asset.reconstruction).every((asset) => !asset.isVector))
  const reconstructions = spiral.versions.filter((asset) => asset.reconstruction)
  assert.equal(reconstructions.length, 2)
  assert.ok(reconstructions.every((asset) => asset.isVector && asset.supplied && asset.variantOf === spiral.id))
  const report = commission.entries.filter((entry) => entry.id.startsWith('itac-annual-report-'))
  assert.equal(report.length, 3)
  const nameLeft = report.find((entry) => entry.id === 'itac-annual-report-name-left-2000-01')
  assert.equal(nameLeft.asset.id, 'itac-annual-report-name-left-reconstruction')
  assert.equal(nameLeft.versions[0], nameLeft.asset)
  assert.equal(nameLeft.identity.provenance, 'reconstructed')
  const publishedLayouts = report.map((entry) => (entry.versions ?? [entry.asset]).find((asset) => asset.id === entry.id))
  assert.ok(publishedLayouts.every((asset) => asset.sourceDate === '2000/01' && !asset.isVector))
  assert.deepEqual(publishedLayouts.map((asset) => asset.extraction.sourcePageNumber).sort((a, b) => a - b), [2, 4, 19])
  assert.ok(report.filter((entry) => entry !== nameLeft).every(({ asset }) => !asset.isVector))
  assert.equal(galleryHistoryOf(commission.graphNode).predecessors.find((row) => row.id === 'provincial-apprenticeship-board')?.date, '1997-11-28')
  const earlier = commission.entries.find((entry) => entry.id === 'itac-gold-emblem-2000')
  assert.equal(commission.cover, earlier.id)
  assert.equal(earlier.asset.isVector, true)
  assert.equal(earlier.asset.reconstruction, false)
  assert.equal(earlier.owner, commission.graphNode)
  // The authority continued as SkilledTradesBC in 2022: one collection, an era for each name.
  assert.equal(authority, skilledTrades)
  assert.deepEqual(skilledTrades.eras.map(({ id }) => id), ['name-industry-training-authority', 'name-skilledtradesbc'])
  for (const [before, after, type, date] of [
    [commission, authority, 'replaced', '2004-01-02']
  ]) {
    assert.ok(galleryHistoryOf(before.graphNode).successors.some((row) => row.collection === after && row.type === type && row.date === date))
    assert.ok(galleryHistoryOf(after.graphNode).predecessors.some((row) => row.collection === before && row.type === type && row.date === date))
  }
})
