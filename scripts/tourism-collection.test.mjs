import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { buildTourismCollection, renderTourismModule, validateTourismData } from './build-tourism-collection.mjs'

const folder = new URL('../research/identity/tourism-asset-transfer-2013/', import.meta.url)
const read = (name) => JSON.parse(readFileSync(new URL(name, folder), 'utf8'))
const fixture = () => ({
  catalogue: read('catalogue.json'),
  register: read('source-register.json'),
  domains: read('domains.json'),
})

test('the committed tourism module is reproducible from sources and verified image bytes', () => {
  const data = buildTourismCollection()
  assert.equal(readFileSync(new URL('../src/gallery/tourismData.js', import.meta.url), 'utf8'), renderTourismModule(data))
  assert.deepEqual(data.digitalRecords.slice(0, 6).map((item) => item.id), [
    'hellobc', 'worldhost', 'near-me-bc', 'bc-escapes', 'bc-magazine', 'share-your-bc',
  ])
  assert.equal(data.stats.listedAddresses, 193)
  assert.equal(data.stats.distinctAddresses, 191)
})

test('the source’s email addresses, subdomains, spelling and repeated entries stay visible', () => {
  const { catalogue, register, domains } = fixture()
  assert.equal(validateTourismData(catalogue, register, domains), true)
  const records = domains.records
  assert.equal(records.filter((row) => row.kind === 'email').length, 7)
  assert.equal(records.filter((row) => row.kind === 'subdomain').length, 8)
  assert.equal(records.filter((row) => row.duplicateOf).length, 2)
  for (const value of ['britishcolombia.ca', 'commmunitytourismfoundations.com', 'canadawestmarketplace.ca']) {
    assert.ok(records.some((row) => row.value === value), `source spelling retained: ${value}`)
  }
  const email = records.find((row) => row.kind === 'email')
  email.kind = 'domain'
  assert.throws(() => validateTourismData(catalogue, register, domains), /email classified as website/)
})

test('a listed address cannot quietly become a current or operating website', () => {
  const { catalogue, register, domains } = fixture()
  domains.records[0].url = `https://${domains.records[0].value}/`
  assert.throws(() => validateTourismData(catalogue, register, domains), /inventory claims a live address/)
})

test('Tourism BC’s 2010 dissolution cannot be collapsed into the 2013 transfer', () => {
  const { catalogue, register, domains } = fixture()
  catalogue.timeline.find((event) => event.id === 'tourism-bc-dissolved').date = '2013-04-01'
  assert.throws(() => validateTourismData(catalogue, register, domains), /dissolution must remain separate/)
})

test('editorial items require resolvable sources', () => {
  const { catalogue, register, domains } = fixture()
  catalogue.digitalRecords[0].sourceRefs[0].sourceId = 'unverified-source'
  assert.throws(() => validateTourismData(catalogue, register, domains), /unknown source/)
})

test('publication specimens retain their date meaning and capture provenance', () => {
  const data = buildTourismCollection()
  const hello = data.digitalRecords.find((record) => record.id === 'hellobc')
  const worldhost = data.digitalRecords.find((record) => record.id === 'worldhost')
  assert.deepEqual(hello.images.map((image) => image.id), ['hellobc-listing-2022', 'supernaturalbc-launch-2025'])
  assert.equal(hello.images[0].sourcePage, 13)
  assert.match(hello.images[0].dateLabel, /[Pp]ublication/)
  assert.equal(worldhost.image.evidenceType, 'official-published-website-screenshot')
  assert.equal(worldhost.image.sourcePage, 47)
  assert.match(worldhost.image.caption, /capture date is not stated/)
  assert.equal(data.marks.filter((mark) => mark.kind === 'word-mark').every((mark) => !mark.image), true)
})
