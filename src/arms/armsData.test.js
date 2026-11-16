import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import {
  ACQUISITION_DIR, CATALOGUE_DIR, GROUPS, HOLDERS, PROVINCE, PROVINCE_SPECIMENS, holderById, holdersInGroup, provinceSections
} from './armsData.js'
import acquisition from './artwork.json' with { type: 'json' }

const root = fileURLToPath(new URL('../../', import.meta.url))
const imagesDir = fileURLToPath(new URL('./images/', import.meta.url))
const artworkDir = fileURLToPath(new URL('./artwork/', import.meta.url))

test('the Province comes first, with its three designs', () => {
  assert.equal(HOLDERS[0], PROVINCE)
  assert.deepEqual(PROVINCE.stages.map(({ year }) => year), ['1895', '1906', '1987'])
  for (const stage of PROVINCE.stages) assert.ok(stage.sources.length > 0, `${stage.year} has a source`)
})

test('every catalogue specimen is shown once, in catalogue order, with its image on disk', () => {
  const numbers = PROVINCE_SPECIMENS.map(({ number }) => number)
  assert.deepEqual(numbers, [...numbers].sort((a, b) => a - b))
  assert.equal(new Set(numbers).size, numbers.length)
  const shown = provinceSections().flatMap(({ specimens }) => specimens)
  assert.equal(shown.length, PROVINCE_SPECIMENS.length)
  for (const item of PROVINCE_SPECIMENS) {
    assert.ok(existsSync(`${root}${CATALOGUE_DIR}/reference/${item.image}`), `${item.id}: ${item.image}`)
    assert.ok(item.sources.every(({ url }) => /^https:\/\//.test(url)), `${item.id} sources are links`)
  }
})

test('sections keep the catalogue order and carry no numbering', () => {
  const titles = provinceSections().map(({ title }) => title)
  assert.equal(new Set(titles).size, titles.length, 'each section appears once')
  for (const title of titles) assert.doesNotMatch(title, /^\d/)
})

test('every holder has a known group, a unique id and a primary source', () => {
  const groups = new Set(GROUPS.map(({ id }) => id))
  const ids = new Set()
  for (const holder of HOLDERS) {
    assert.ok(groups.has(holder.group), `${holder.id}: group ${holder.group}`)
    assert.ok(!ids.has(holder.id), `${holder.id} is unique`)
    ids.add(holder.id)
    assert.equal(holderById(holder.id), holder)
    const links = [holder.register?.url, ...(holder.sources ?? []).map(({ url }) => url)].filter(Boolean)
    assert.ok(holder.register?.url || holder.sources?.length, `${holder.id} has a register entry or its own source`)
    assert.ok(links.length > 0, `${holder.id} cites a source`)
    for (const url of links) assert.match(url, /^https:\/\//, `${holder.id}: ${url}`)
  }
})

test('holder images exist and carry a credit', () => {
  for (const holder of HOLDERS) {
    if (holder.image?.file) assert.ok(existsSync(`${imagesDir}${holder.image.file}`), `${holder.id}: ${holder.image.file}`)
    if (holder.image?.artwork) assert.ok(existsSync(`${artworkDir}${holder.image.artwork}.webp`), `${holder.id}: ${holder.image.artwork}`)
    if (holder.image?.kind !== 'vector' && holder.image) assert.ok(holder.image.credit, `${holder.id} credits its image`)
  }
})

test('every acquired artwork record is on exactly one page, with its display copy and original', () => {
  const shown = HOLDERS.flatMap(({ artwork }) => artwork ?? []).filter(({ file }) => !file)
  assert.equal(shown.length, Object.keys(acquisition.artwork).length)
  assert.equal(new Set(shown.map(({ id }) => id)).size, shown.length)
  for (const item of shown) {
    assert.ok(existsSync(`${artworkDir}${item.id}.webp`), `${item.id} display copy`)
    assert.ok(existsSync(`${root}${ACQUISITION_DIR}/assets/${item.original}`), `${item.id}: ${item.original}`)
    for (const file of item.alternates) assert.ok(existsSync(`${root}${ACQUISITION_DIR}/assets/${file}`), `${item.id}: ${file}`)
    assert.ok(item.author, `${item.id} credits its artist or source`)
    assert.match(item.page, /^https:\/\//, `${item.id} links its source`)
  }
})

test('every holder but Kinnaird leads with a picture', () => {
  const without = HOLDERS.filter(({ image }) => !image).map(({ id }) => id)
  assert.deepEqual(without, ['town-of-kinnaird'])
})

test('every municipal register entry has a page, and renamed places keep one', () => {
  const municipal = holdersInGroup('municipal')
  assert.equal(municipal.length, 63)
  const urls = municipal.flatMap((holder) => [holder.register.url, ...holder.related.map(({ url }) => url)])
  assert.equal(new Set(urls).size, urls.length)
  assert.equal(urls.length, 73)
  const burnaby = holderById('city-of-burnaby')
  assert.match(burnaby.register.url, /project\/488$/, 'the city’s confirmation leads')
  assert.equal(burnaby.year, '1991', 'dated from the district’s grant')
  assert.ok(burnaby.related.some(({ url }) => url.endsWith('/1502')))
})

test('an unknown holder is no holder', () => {
  assert.equal(holderById('nowhere'), null)
  assert.equal(holderById(null), null)
})

test('register holders have ids, years and link only to real salary employers and gallery subjects', async () => {
  const { identitySubjectById } = await import('../gallery/identityCoverage.js')
  const others = HOLDERS.filter(({ group, register }) => group !== 'province' && register)
  assert.ok(others.length >= 30, `${others.length} holders`)
  for (const holder of others) {
    assert.match(holder.id ?? '', /^[a-z0-9-]+$/, `${holder.name} has an id`)
    assert.match(holder.year, /^\d{4}$/, `${holder.id} year`)
    assert.match(holder.register.url, /^https:\/\/www\.gg\.ca\/en\/heraldry\/public-register\/project\/\d+$/, holder.id)
    for (const { to } of holder.links) {
      if (to.view === 'salaries') assert.ok(existsSync(`${root}public/salaries/employers/${to.employer}.json.gzip`), `${holder.id}: salaries ${to.employer}`)
      if (to.view === 'gallery') assert.ok(identitySubjectById(to.subject), `${holder.id}: subject ${to.subject}`)
    }
  }
})

test('the earliest record wins: UBC is dated 1915, the Lieutenant Governor 1982', () => {
  assert.equal(holderById('university-of-british-columbia').year, '1915')
  assert.equal(holderById('lieutenant-governor').year, '1982')
})

test('the Province carries its register record, blazon and symbolism', () => {
  assert.match(PROVINCE.register.url, /project\/1406$/)
  assert.match(PROVINCE.blazon.arms, /three bars wavy Azure/)
  assert.ok(PROVINCE.symbolism.supporters)
})

test('Douglas College, outside the register, is dated from its unveiling and cites the College', () => {
  const douglas = holderById('douglas-college')
  assert.equal(douglas.group, 'post-secondary')
  assert.equal(douglas.register, null)
  assert.equal(douglas.year, '2020')
  assert.match(douglas.sources[0].url, /douglascollege\.ca/)
})

test('municipal mottoes are split from the register’s gloss', () => {
  assert.deepEqual(holderById('city-of-kamloops').motto, { text: 'SALUS ET OPES', translation: 'Health and wealth', note: null })
  const kinnaird = holderById('town-of-kinnaird').motto
  assert.equal(kinnaird.text, 'LUMENES HAEC ERRANTIAE NUNQUAM')
  assert.match(kinnaird.note, /^The motto appears in the Lyon Register/)
  for (const holder of HOLDERS) assert.doesNotMatch(holder.motto?.text ?? '', /This Latin phrase/, holder.id)
})
