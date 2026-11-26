import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { fileOf, imagesOf, resolveInitiativeSelection, searchInitiatives } from './initiativeModel.js'
import { INITIATIVES, loadInitiative } from './initiatives.js'
import { tourismRebrandingSection, tourismRebrandingSources } from './tourismRebranding.js'
import { tourismBriefPublication, tourismBriefSources, tourismProgramsSection } from './tourismBrief.js'
import { TOURISM_COLLECTION } from '../gallery/tourismData.js'
import { TOURISM_MANIFESTS } from '../../scripts/build-tourism-collection.mjs'

// Deliberately unrelated to tourism: no domain inventory, marketing labels,
// tourism section IDs, cover image, registration list, or related-page links.
const schoolDesign = {
  id: 'school-design',
  title: 'School Design',
  subtitle: 'Public buildings',
  summary: 'Plans and publications about classroom design.',
  searchTerms: ['écoles', 'classrooms'],
  hero: { title: 'Classrooms through time', description: 'Building plans and their published evidence.' },
  sources: [{ id: 'school-report', title: 'School plans annual report', url: 'https://example.org/school-report.pdf', date: '1960' }],
  sections: [
    { id: 'building-history', label: 'Building history', type: 'timeline', records: [
      { id: 'standard-plan', date: '1960', title: 'A new building pattern', sourceRefs: [{ sourceId: 'school-report', page: 4 }] }
    ] },
    { id: 'building-designs', label: 'Building designs', type: 'records', records: [
      { id: 'classroom-plan', title: 'A classroom plan', kind: 'plan', description: 'A plan awaiting an image.', sourceRefs: [{ sourceId: 'school-report', page: 8 }] }
    ] },
    { id: 'printed-catalogue', label: 'Printed catalogue', type: 'publications', records: [
      {
        id: 'plan-catalogue', title: 'School plan catalogue', kind: 'catalogue',
        description: 'A publication containing the plan.',
        sourceRefs: [{ sourceId: 'school-report', page: 20 }],
        image: {
          file: 'fixtures/school-plan.png', title: 'The published plan',
          alt: 'Classroom plan from the annual report', evidenceType: 'printed-source-crop',
          sourceId: 'school-report', sourcePage: 12, date: '1960', dateLabel: 'Publication year',
          caption: 'The plan as published on page 12.'
        }
      }
    ] },
    { id: 'references', label: 'References', type: 'sources' }
  ]
}

test('initiative search finds a second subject without relying on tourism tags or fields', () => {
  const initiatives = [...INITIATIVES, schoolDesign]
  assert.deepEqual(searchInitiatives('ecoles classrooms', initiatives).map((item) => item.id), ['school-design'])
  assert.deepEqual(searchInitiatives('classroom plans', initiatives).map((item) => item.id), ['school-design'])
  assert.equal(searchInitiatives('classrooms HelloBC', initiatives).length, 0, 'words must match the same initiative')
  assert.deepEqual(searchInitiatives('  ', initiatives), initiatives)
})

test('Pacific Gateway opens both 2012 specimens in Initiatives with their publication and original vectors', async () => {
  const [entry] = searchInitiatives('Canada Starts Here', INITIATIVES)
  assert.equal(entry.id, 'pacific-gateway')
  const detail = await loadInitiative(entry.id)
  const { section } = resolveInitiativeSelection(detail)
  assert.deepEqual(section.records.map(({ id }) => id), ['vector-canada-starts-here-2012', 'vector-canada-starts-here-bc-jobs-plan-2012'])
  for (const item of section.records) {
    assert.equal(resolveInitiativeSelection(detail, { record: item.id }).record, item)
    assert.equal(item.image.sourcePage, 24)
    assert.ok(detail.sources.some(({ id }) => id === item.image.sourceId))
    const artwork = await readFile(new URL('../../public/' + item.image.file, import.meta.url), 'utf8')
    assert.match(artwork, /<svg\b/)
  }
  assert.ok(detail.relatedLinks.some(({ to }) => to.logos === 'bc-mark' && to.mark === 'pacific-gateway'))
})

test('Rainforest to Rockies opens under Tourism with the published primary and partner logos', async () => {
  const [entry] = searchInitiatives('Wander Mark', INITIATIVES)
  assert.equal(entry.parentId, 'tourism')
  const detail = await loadInitiative(entry.id)
  const primary = resolveInitiativeSelection(detail, { record: 'primary-logo' }).record
  const partner = resolveInitiativeSelection(detail, { record: 'partner-lockup' }).record
  assert.deepEqual(imagesOf(primary).map((image) => image.sourcePage), [5, 19])
  assert.deepEqual(imagesOf(partner).map((image) => [image.sourcePage, image.darkBackground]), [[5, false], [20, false], [5, true], [20, true]])
  assert.equal(entry.cover.file, imagesOf(partner)[0].file)
  for (const image of [...imagesOf(primary), ...imagesOf(partner)]) {
    assert.ok(detail.sources.some(({ id }) => id === image.sourceId))
    const bytes = await readFile(new URL('../../public/' + image.file, import.meta.url))
    assert.equal(bytes.toString('hex', 0, 8), '89504e470d0a1a0a')
  }
  assert.ok(detail.relatedLinks.some(({ to }) => to.initiative === entry.parentId && to.record === 'our-brand-2021'))
})

test('bookmarks select custom record and publication sections and recover safely from stale IDs', () => {
  const initial = resolveInitiativeSelection(schoolDesign)
  assert.equal(initial.section.id, 'building-history')
  assert.equal(initial.record, null)

  const record = resolveInitiativeSelection(schoolDesign, { record: 'classroom-plan' })
  assert.equal(record.section.id, 'building-designs')
  assert.equal(record.record.title, 'A classroom plan')
  assert.equal(record.missingRecord, false)

  const publication = resolveInitiativeSelection(schoolDesign, { section: 'marks', record: 'plan-catalogue' })
  assert.equal(publication.section.id, 'printed-catalogue', 'the record resolves its actual custom section')
  assert.equal(publication.record.id, 'plan-catalogue')

  const stale = resolveInitiativeSelection(schoolDesign, { section: 'references', record: 'hellobc' })
  assert.equal(stale.section.id, 'references')
  assert.equal(stale.record, null, 'a tourism record must not leak into another initiative')
  assert.equal(stale.missingRecord, true)
  assert.equal(resolveInitiativeSelection(schoolDesign, { section: 'no-longer-present' }).section.id, 'building-history')
  assert.doesNotThrow(() => resolveInitiativeSelection({ id: 'empty-draft', sections: [] }, { record: 'removed' }))
})

test('deduplication retains specimen provenance when legacy filenames repeat a richer image', () => {
  const primary = {
    file: 'fixtures/plan.svg', sourceId: 'school-report', sourcePage: 12,
    date: '1960', dateLabel: 'Publication year', alt: 'Published plan'
  }
  const alternate = { file: 'fixtures/plan-reverse.svg', sourceId: 'school-report', sourcePage: 13, darkBackground: true }
  const item = { image: primary, images: ['fixtures/plan.svg'], specimens: [alternate], variants: ['fixtures/plan-reverse.svg'] }
  const before = JSON.stringify(item)
  const images = imagesOf(item)
  assert.deepEqual(images.map(fileOf), ['fixtures/plan.svg', 'fixtures/plan-reverse.svg'])
  assert.deepEqual(images[0], primary, 'a bare filename must not erase its source and publication date')
  assert.deepEqual(images[1], alternate, 'a bare filename must not erase a reverse specimen’s required backdrop')
  assert.equal(JSON.stringify(item), before, 'reading specimens must not mutate source data')
})

test('the tourism adapter preserves the complete sourced collection and research leads', async () => {
  const detail = await loadInitiative('tourism')
  const actualIds = detail.sections.filter((section) => ['records', 'publications', 'timeline'].includes(section.type))
    .flatMap((section) => section.records.map((record) => record.id)).sort()
  const expectedIds = [...TOURISM_COLLECTION.digitalRecords, ...TOURISM_COLLECTION.marks,
    ...TOURISM_COLLECTION.timeline, ...TOURISM_COLLECTION.publications, ...tourismRebrandingSection.records,
    ...tourismProgramsSection.records, tourismBriefPublication].map((record) => record.id).sort()
  assert.deepEqual(actualIds, expectedIds, 'moving the explorer must not omit a sourced record')
  assert.deepEqual(detail.sources, [...TOURISM_COLLECTION.sources, ...tourismRebrandingSources, ...tourismBriefSources], 'the complete source library survives the move')
  assert.deepEqual(detail.sections.flatMap((section) => section.leads ?? []), TOURISM_COLLECTION.leads)
  const inventories = detail.sections.filter((section) => section.inventory).map((section) => section.inventory)
  assert.equal(inventories.length, 1)
  assert.deepEqual(inventories[0].entries, TOURISM_COLLECTION.domains, 'source spellings and duplicate rows are preserved')
  assert.equal(await loadInitiative('unknown-initiative'), null)
})

test('Tourism Brief records open from bookmarks and connect the historical and current training providers', async () => {
  const detail = await loadInitiative('tourism')
  assert.deepEqual(searchInitiatives('go2HR', INITIATIVES).map(({ id }) => id), ['tourism'])
  const go2 = resolveInitiativeSelection(detail, { record: 'go2hr' })
  assert.equal(go2.section.id, 'programs')
  assert.match(go2.record.current, /independent society/)
  assert.ok(go2.record.links.some(({ url }) => url === 'https://www.go2hr.ca/'))
  assert.ok(go2.record.sourceRefs.some(({ page, url }) => page === 9 && url.endsWith('#page=9')))

  const worldhost = resolveInitiativeSelection(detail, { record: 'worldhost' })
  assert.equal(worldhost.section.id, 'websites')
  assert.match(worldhost.record.description, /2017/)
  assert.deepEqual(imagesOf(worldhost.record), imagesOf(TOURISM_COLLECTION.digitalRecords.find(({ id }) => id === 'worldhost')))

  for (const record of tourismProgramsSection.records) {
    assert.ok(record.current, `${record.id}: current status`)
    assert.ok(record.sourceRefs.some(({ sourceId, page }) => sourceId === 'tourism-brief-2009-05' && page >= 2 && page <= 12), record.id)
    for (const { url } of record.links ?? []) {
      const params = new URL(url, 'https://example.org/').searchParams
      if (params.get('initiative') === 'tourism' && params.has('record')) {
        assert.ok(resolveInitiativeSelection(detail, { record: params.get('record') }).record, url)
      }
    }
  }
})

test('every acquired specimen remains reachable with its own source, date and exact file', async () => {
  const detail = await loadInitiative('tourism')
  const sourceIds = new Set(detail.sources.map((source) => source.id))
  const records = detail.sections.filter((section) => ['records', 'publications'].includes(section.type)).flatMap((section) => section.records)
  const specimens = records.flatMap(imagesOf).filter((image) => image.manifest?.includes('/tourism-asset-transfer-2013/'))
  const byId = new Map(specimens.map((image) => [image.id, image]))
  const manifests = await Promise.all(TOURISM_MANIFESTS.map(async (filename) =>
    JSON.parse(await readFile(new URL(`../../research/identity/tourism-asset-transfer-2013/${filename}`, import.meta.url), 'utf8'))))
  const acquired = manifests.flatMap((manifest) => manifest.assets)
  assert.deepEqual(new Set(byId.keys()), new Set(acquired.map((asset) => asset.id)), 'all acquired specimens are browsable, without substitute images')

  for (const asset of acquired) {
    const image = byId.get(asset.id)
    assert.equal(fileOf(image), asset.path.replace(/^public\//, ''), asset.id)
    assert.equal(image.sourceId, asset.sourceId, `${asset.id}: source identity`)
    assert.ok(sourceIds.has(image.sourceId), `${asset.id}: a visible source-library entry`)
    assert.equal(image.sha256, asset.sha256, `${asset.id}: source checksum`)
    assert.equal(image.width, asset.width, `${asset.id}: original width`)
    assert.equal(image.height, asset.height, `${asset.id}: original height`)
    assert.equal(Boolean(image.darkBackground), asset.displayBackground === 'dark', `${asset.id}: reverse artwork backdrop`)
    if (asset.sourcePage) assert.equal(image.sourcePage, asset.sourcePage, `${asset.id}: its own PDF page`)
    if (asset.sourcePdfPage) assert.equal(image.sourcePdfPage, asset.sourcePdfPage, `${asset.id}: PDF cross-reference`)
    if (asset.sourceImageUrl) assert.equal(image.sourceImageUrl, asset.sourceImageUrl, `${asset.id}: publisher’s original image`)
    if (asset.date) assert.equal(image.date, asset.date, `${asset.id}: specimen date must not become the initiative date`)
    const bytes = await readFile(new URL(`../../${asset.path}`, import.meta.url))
    assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, `${asset.id}: referenced bytes are present and unchanged`)
  }
  for (const record of records) {
    for (const reference of record.sourceRefs ?? []) assert.ok(sourceIds.has(reference.sourceId), `${record.id}: unresolved source ${reference.sourceId}`)
  }
})

test('the shared detail renderer supports a second initiative without tourism sections or an address inventory', async () => {
  const [{ createServer }, { default: reactPlugin }, { default: React }, { renderToStaticMarkup }] = await Promise.all([
    import('vite'), import('@vitejs/plugin-react'), import('react'), import('react-dom/server')
  ])
  const server = await createServer({
    configFile: false,
    root: fileURLToPath(new URL('../../', import.meta.url)),
    plugins: [reactPlugin()],
    server: { middlewareMode: true, hmr: false, watch: null },
    appType: 'custom', logLevel: 'silent'
  })
  try {
    const { InitiativeDetail } = await server.ssrLoadModule('/src/initiatives/InitiativeDetail.jsx')
    const render = (place) => renderToStaticMarkup(React.createElement(InitiativeDetail, { initiative: schoolDesign, place, onChange: () => {} }))
    const history = render({ section: 'building-history' })
    assert.match(history, /Classrooms through time/)
    assert.match(history, /A new building pattern/)
    assert.doesNotMatch(history, /HelloBC|Tourism BC|The 2013 address inventory/)
    assert.match(render({ section: 'building-designs' }), /A classroom plan/)

    const publication = render({ record: 'plan-catalogue' })
    assert.match(publication, /School plan catalogue/)
    assert.match(publication, /Selected specimen provenance/)
    assert.match(publication, /school-report\.pdf#page=12/, 'the selected specimen cites its page, independently of record-level page 20')
    assert.match(publication, /Publication year/)

    const references = render({ section: 'references' })
    assert.match(references, /School plans annual report/)
    assert.doesNotMatch(references, /Download inventory|Search the address inventory|matching entries/)
  } finally {
    await server.close()
  }
})
