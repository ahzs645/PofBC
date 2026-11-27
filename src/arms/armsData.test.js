import assert from 'node:assert/strict'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import {
  ACQUISITION_DIR, CATALOGUE_DIR, GROUPS, HOLDERS, PROVINCE, PROVINCE_SPECIMENS, PROVINCE_STORY, holderById, holdersInGroup, provinceSections,
  provinceStoryEntries
} from './armsData.js'
import acquisition from './artwork.json' with { type: 'json' }
import armsCatalogue from '../../research/identity/arms-variants-2026-11-14/catalogue.json' with { type: 'json' }
import acquisitionCatalogue from '../../research/identity/arms-acquisition-2026-11-16/catalogue.json' with { type: 'json' }
import acquisitionHolders from '../../research/identity/arms-acquisition-2026-11-16/holders.json' with { type: 'json' }

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

test('the two flag-derived shields are credited vector supplements, not new lead arms', () => {
  for (const [holderId, original, author] of [
    ['city-of-dawson-creek', 'cha-1370-arms-1', 'Cookieman1.1.1'],
    ['city-of-kimberley', 'cha-925-arms-1', 'Jack Ryan Morris']
  ]) {
    const holder = holderById(holderId)
    assert.equal(holder.image.artwork, original)
    const entries = holder.artwork.filter(({ kind, file }) => kind === 'shield' && file)
    assert.equal(entries.length, 1)
    const [entry] = entries
    assert.ok(entry.vector)
    assert.ok(entry.author.includes(author))
    assert.match(entry.page, /^https:\/\/commons\.wikimedia\.org\/wiki\/File:Flag_of_/)
    assert.equal(entry.licenceUrl, 'https://creativecommons.org/licenses/by-sa/4.0/')
    assert.ok(existsSync(`${imagesDir}${entry.file}`))
  }
})

// The Province's account: one entry per design, object or treatment, oldest first.

const storyFiles = () => provinceStoryEntries().flatMap(({ files }) => files)

test('the Province’s page shows every catalogue specimen and every acquired file exactly once', () => {
  const files = storyFiles()
  const ids = files.map(({ from, id }) => `${from}:${id}`)
  assert.equal(new Set(ids).size, ids.length, 'no file appears twice')
  assert.deepEqual(
    files.filter(({ from }) => from === 'catalogue').map(({ id }) => id).sort(),
    PROVINCE_SPECIMENS.map(({ id }) => id).sort(),
    'every catalogue specimen'
  )
  assert.deepEqual(
    files.filter(({ from }) => from === 'artwork').map(({ id }) => id).sort(),
    PROVINCE.artwork.map(({ id }) => id).sort(),
    'every acquired rendering of the Province'
  )
  const entries = provinceStoryEntries().map(({ id }) => id)
  assert.equal(new Set(entries).size, entries.length, 'no entry appears twice')
})

test('no design or treatment appears twice: each copy sits within the entry it names', () => {
  const entryOf = new Map(provinceStoryEntries().flatMap((entry) => entry.files.map((file) => [`${file.from}:${file.id}`, entry.id])))
  const copies = [
    ...armsCatalogue.entries.filter(({ sameAs }) => sameAs).map(({ id, sameAs }) => [`catalogue:${id}`, sameAs]),
    ...Object.entries(acquisition.artwork).filter(([, item]) => item.sameAs).map(([id, item]) => [`artwork:${id}`, item.sameAs])
  ]
  assert.deepEqual(copies.map(([key]) => key).sort(), [
    'artwork:cha-1406-arms-1',
    'artwork:province-official-monochrome-sample',
    'artwork:province-official-reverse-sample',
    'artwork:province-older-arms-window-makaristos',
    'catalogue:full-current-government-web',
    'catalogue:full-current-legislature-web'
  ])
  for (const [key, target] of copies) {
    assert.ok(armsCatalogue.entries.some(({ id }) => id === target), `${key} names a catalogue entry`)
    assert.equal(entryOf.get(key), target, `${key} is shown within ${target}`)
  }
  // The pairs the merge was for: the guide's treatments are held once, as source vectors.
  const entry = (id) => provinceStoryEntries().find((item) => item.id === id)
  assert.equal(entry('guide-monochrome').lead.id, 'province-official-monochrome-sample')
  assert.equal(entry('guide-reverse').lead.id, 'province-official-reverse-sample')
  assert.ok(entry('guide-monochrome').lead.vector)
  assert.equal(entry('full-1987-period-report').files.length, 3)
  assert.equal(entry('full-1990-cha-registration').files.length, 2)
})

test('a merge is recorded in the research records, the same way in each, with its evidence', () => {
  const linked = (assets) => Object.fromEntries(assets.filter(({ sameAs }) => sameAs).map(({ id, sameAs, sameAsEvidence }) => {
    assert.ok(sameAsEvidence?.length > 40, `${id} says why it is a copy`)
    return [id, sameAs]
  }))
  const fromCatalogue = linked(acquisitionCatalogue.assets)
  const fromHolders = linked(acquisitionHolders.flatMap(({ artwork }) => artwork ?? []))
  const fromIndex = Object.fromEntries(Object.entries(acquisition.artwork).filter(([, item]) => item.sameAs).map(([id, item]) => [id, item.sameAs]))
  assert.deepEqual(fromHolders, fromCatalogue)
  assert.deepEqual(fromIndex, fromCatalogue)
  for (const entry of armsCatalogue.entries.filter(({ sameAs }) => sameAs)) assert.ok(entry.sameAsEvidence?.length > 40, entry.id)
})

test('every merged entry keeps all its files, credits and sources', () => {
  for (const entry of provinceStoryEntries()) {
    const urls = new Set(entry.sources.map(({ url }) => url))
    for (const file of entry.files) {
      if (file.from === 'catalogue') {
        assert.ok(existsSync(`${root}${CATALOGUE_DIR}/reference/${file.image}`), `${entry.id}: ${file.image}`)
        for (const source of file.sources) assert.ok(urls.has(source.url), `${entry.id} keeps ${file.id}’s source ${source.url}`)
      } else {
        assert.ok(existsSync(`${root}${ACQUISITION_DIR}/assets/${file.original}`), `${entry.id}: ${file.original}`)
        for (const path of file.alternates) assert.ok(existsSync(`${root}${ACQUISITION_DIR}/assets/${path}`), `${entry.id}: ${path}`)
        assert.ok(file.author, `${file.id} keeps its credit`)
        assert.match(file.page, /^https:\/\//, `${file.id} keeps its source page`)
      }
    }
    if (entry.files.length > 1) assert.equal(entry.lead, entry.files[0], `${entry.id} shows its lead first`)
    // A source vector leads wherever one is held.
    if (entry.files.some(({ vector }) => vector)) assert.ok(entry.lead.vector, `${entry.id} leads with its vector`)
  }
})

test('the account runs oldest first, with the modern renderings set apart at the end', () => {
  const dated = PROVINCE_STORY.filter(({ renderings }) => !renderings)
  const years = dated.map(({ from }) => from)
  assert.ok(years.every((year) => Number.isInteger(year)), 'every period has a starting year')
  assert.deepEqual(years, [...years].sort((a, b) => a - b))
  assert.equal(new Set(years).size, years.length)
  assert.deepEqual(PROVINCE_STORY.map(({ id }) => id), ['precursors', 'beanlands', 'grant-1906', 'augmentation-1987', 'current', 'seal', 'renderings'])
  assert.ok(PROVINCE_STORY.at(-1).renderings)
  for (const section of PROVINCE_STORY) {
    const urls = section.sources.map(({ url }) => url)
    assert.equal(new Set(urls).size, urls.length, `${section.id} cites each source once`)
  }
  // The design stages introduce their periods instead of standing apart.
  assert.deepEqual(PROVINCE_STORY.filter(({ stage }) => stage).map(({ stage }) => stage.year), ['1895', '1906', '1987'])
  // Third-party and supplied drawings are kept out of the dated sections.
  const renderings = PROVINCE_STORY.at(-1).groups.flatMap(({ entries }) => entries).map(({ id }) => id)
  for (const id of ['province-1895-fenn-o-manic', 'province-current-leonid2', 'province-shield-fry1989', 'province-shield-zorlot', 'reconstruction-colour-ornate', 'reconstruction-monochrome-engraved', 'reconstruction-monochrome-line']) {
    assert.ok(renderings.includes(id), `${id} is a modern rendering`)
  }
  for (const entry of dated.flatMap(({ groups }) => groups.flatMap(({ entries }) => entries))) {
    assert.ok(!renderings.includes(entry.id), `${entry.id} is not also among the renderings`)
    assert.ok(entry.number || entry.lead.page?.includes('gg.ca'), `${entry.id} is a catalogued specimen or a register record`)
  }
})

test('the SAMPLE marks stay and the withheld rights note is not shown', () => {
  for (const id of ['province-official-monochrome-sample', 'province-official-reverse-sample']) {
    const item = acquisition.artwork[id]
    assert.equal(item.licence, null, `${id} shows no licence line`)
    assert.match(item.rights, /No open reproduction licence/, `${id} keeps its rights in the record`)
    assert.match(item.title, /SAMPLE retained/)
  }
})
