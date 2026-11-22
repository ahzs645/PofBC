import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { fileOf, imagesOf, resolveInitiativeSelection, searchInitiatives } from './initiativeModel.js'
import { INITIATIVES, loadInitiative } from './initiatives.js'
import { TOURISM_COLLECTION } from '../gallery/tourismData.js'

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
    ...TOURISM_COLLECTION.timeline, ...TOURISM_COLLECTION.publications].map((record) => record.id).sort()
  assert.deepEqual(actualIds, expectedIds, 'moving the explorer must not omit a sourced record')
  assert.deepEqual(detail.sources, TOURISM_COLLECTION.sources, 'the complete source library survives the move')
  assert.deepEqual(detail.sections.flatMap((section) => section.leads ?? []), TOURISM_COLLECTION.leads)
  const inventories = detail.sections.filter((section) => section.inventory).map((section) => section.inventory)
  assert.equal(inventories.length, 1)
  assert.deepEqual(inventories[0].entries, TOURISM_COLLECTION.domains, 'source spellings and duplicate rows are preserved')
  assert.equal(await loadInitiative('unknown-initiative'), null)
})

test('every acquired specimen remains reachable with its own source, date and exact file', async () => {
  const detail = await loadInitiative('tourism')
  const sourceIds = new Set(detail.sources.map((source) => source.id))
  const records = detail.sections.filter((section) => ['records', 'publications'].includes(section.type)).flatMap((section) => section.records)
  const specimens = records.flatMap(imagesOf)
  const byId = new Map(specimens.map((image) => [image.id, image]))
  const manifests = await Promise.all(['artwork-manifest.json', 'website-manifest.json'].map(async (filename) =>
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
