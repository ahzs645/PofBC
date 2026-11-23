import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { PARTIES, PARTY_COUNTS, PARTY_GROUPS, partyAsset, partyById, partyHistory, partyIdFor, partySources, searchParties } from './parties.js'
import { PREMIERS } from '../government/timelineData.js'
import { ELECTION_RESULTS_2026 } from '../government/atlasData.js'

const publicDir = resolve(fileURLToPath(new URL('.', import.meta.url)), '../../public')

test('the roster keeps every party, including those without artwork', () => {
  assert.equal(PARTY_COUNTS.parties, 27)
  assert.equal(PARTY_COUNTS.withArtwork, 12)
  assert.equal(PARTY_COUNTS.files, 65)
  assert.equal(searchParties({ scope: 'all' }).length, 27)
  assert.equal(searchParties({ scope: 'artwork' }).length + searchParties({ scope: 'gaps' }).length, 27)
  for (const party of PARTIES.filter((entry) => !entry.files)) assert.ok(party.gaps.length || party.summary, `${party.id} explains its gap`)
})

test('every logo file and preview is served', () => {
  for (const party of PARTIES) {
    for (const design of party.designs) {
      for (const asset of design.assets) {
        assert.ok(existsSync(resolve(publicDir, asset.file)), asset.file)
        assert.ok(existsSync(resolve(publicDir, asset.preview)), asset.preview)
        for (const file of asset.companions) assert.ok(existsSync(resolve(publicDir, file)), file)
      }
    }
  }
})

test('designs run oldest first and group their colourways', () => {
  for (const party of PARTIES) {
    const dates = party.designs.map((design) => design.sortDate ?? '9999')
    assert.deepEqual(dates, [...dates].sort(), party.id)
    for (const design of party.designs) assert.ok(design.assets.every((asset) => asset.design === design.id), design.id)
  }
  const ndp = partyById('bc-ndp')
  assert.equal(ndp.designs.at(-1).id, 'bc-ndp-sun-box-italic')
  assert.ok(ndp.designs.at(-1).assets.length >= 5, 'the italic sun-box keeps its specimen and four official files together')
})

test('lineages link parties that the sources connect', () => {
  const ccf = PARTY_GROUPS.find((group) => group.id === 'ccf-ndp')
  assert.deepEqual(ccf.parties, ['bc-ccf', 'bc-ndp'])
  for (const group of PARTY_GROUPS) for (const design of group.designs) assert.ok(partyAsset(design.representative), design.id)
})

test('a party’s history and sources are its own', () => {
  const united = partyById('bc-united')
  const history = partyHistory(united)
  assert.ok(history.some((event) => event.type === 'registered-name-change'))
  assert.ok(history.every((event) => event.parties.includes('bc-united')))
  for (const party of PARTIES) assert.ok(partySources(party).every((source) => /^https?:/.test(source.url)), party.id)
})

test('the government’s party names open a party page', () => {
  for (const premier of PREMIERS) assert.ok(partyById(partyIdFor(premier.party)), `premier party ${premier.party}`)
  for (const party of Object.keys(ELECTION_RESULTS_2026.parties)) assert.ok(partyById(partyIdFor(party)), `election party ${party}`)
})

test('search finds a party by an earlier name', () => {
  assert.ok(searchParties({ query: 'greens of british columbia' }).some((party) => party.id === 'bc-green'))
  assert.ok(searchParties({ query: 'democratic alliance', scope: 'all' }).length > 0)
})
