// Exercise the real salary UI against the generated, published data without browser automation.
// npm ci installs the application normally. For isolated test-only tools:
// npm install --prefix /tmp/salary-ui-tools --ignore-scripts --no-package-lock jsdom@29.1.1 esbuild@0.27.0
// SALARY_UI_TEST_MODULES=/tmp/salary-ui-tools/node_modules node scripts/verify-salary-search-ui.mjs
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { existsSync, mkdtempSync, rmSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { tmpdir } from 'node:os'
import { createRequire } from 'node:module'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { gunzipSync } from 'node:zlib'
import { chooseNameSearchBucket, searchNameSearchDocuments } from '../src/salaries/nameSearch.js'
import { displayName, nameOnly, nameQueryTier, personKey, surnameShard, withoutCompiledRepeats } from '../src/salaries/people.js'
import { formatMoney } from '../src/salaries/money.js'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const appRequire = createRequire(join(ROOT, 'package.json'))
const toolRequire = createRequire(join(resolve(process.env.SALARY_UI_TEST_MODULES || join(ROOT, 'node_modules')), '_salary-ui-tools.cjs'))
const { build } = await import(pathToFileURL(toolRequire.resolve('esbuild')).href)
const { JSDOM } = await import(pathToFileURL(toolRequire.resolve('jsdom')).href)
const output = mkdtempSync(join(tmpdir(), 'pofbc-salary-ui-'))
process.on('exit', () => rmSync(output, { recursive: true, force: true }))
const bundle = join(output, 'actual-view.mjs')
await build({
  entryPoints: [join(ROOT, 'src/salaries/SalariesView.jsx')],
  outfile: bundle, bundle: true, platform: 'node', format: 'esm', jsx: 'automatic',
  loader: { '.css': 'empty' },
  define: { 'import.meta.env': JSON.stringify({ BASE_URL: '/', DEV: false }) },
  // Always use the app's locked React, even if a tool package has another React installation.
  plugins: [{ name: 'app-react', setup(builder) {
    builder.onResolve({ filter: /^(react|react-dom)(\/.*)?$/ }, args => ({ path: appRequire.resolve(args.path), external: true }))
  } }],
  logLevel: 'warning',
})

// This is a DOM integration test, not browser automation. Real React effects and real salary
// components use exact on-disk published JSON/gzip; only browser plumbing and transport are mocked.
const PUBLIC = join(ROOT, 'public')
const dom = new JSDOM('<!doctype html><html><body></body></html>', {
  url: 'https://salary.test/?view=salaries', pretendToBeVisual: true,
})
const win = dom.window
for (const name of ['window', 'document', 'navigator', 'HTMLElement', 'Element', 'Node', 'Event', 'MouseEvent', 'KeyboardEvent', 'MutationObserver', 'location', 'history']) {
  Object.defineProperty(globalThis, name, { configurable: true, value: name === 'window' ? win : win[name] })
}
globalThis.getComputedStyle = win.getComputedStyle.bind(win)
globalThis.addEventListener = win.addEventListener.bind(win)
globalThis.removeEventListener = win.removeEventListener.bind(win)
globalThis.requestAnimationFrame = callback => setTimeout(() => callback(performance.now()), 0)
globalThis.cancelAnimationFrame = clearTimeout
globalThis.scrollTo = () => {}
globalThis.matchMedia = query => ({ matches: query.includes('min-width'), media: query, addEventListener() {}, removeEventListener() {} })
globalThis.IS_REACT_ACT_ENVIRONMENT = true
win.HTMLElement.prototype.scrollIntoView = () => {}
const React = appRequire('react')
const { createRoot } = appRequire('react-dom/client')
const roots = new Set()
function render(node) {
  const container = document.createElement('div')
  document.body.append(container)
  const root = createRoot(container)
  roots.add({ root, container })
  React.act(() => root.render(node))
  return root
}
function cleanup() {
  for (const { root, container } of roots) { React.act(() => root.unmount()); container.remove() }
  roots.clear()
}
async function waitFor(assertion, { timeout = 12000 } = {}) {
  const deadline = performance.now() + timeout
  let lastError
  while (performance.now() < deadline) {
    try { return assertion() } catch (error) { lastError = error }
    await React.act(async () => { await new Promise(resolve => setTimeout(resolve, 20)) })
  }
  throw lastError ?? new Error('Timed out waiting for DOM state')
}
const fireEvent = {
  click(node) { assert.ok(node, 'Click target exists'); React.act(() => node.dispatchEvent(new win.MouseEvent('click', { bubbles: true }))) },
  change(node, { target }) {
    assert.ok(node, 'Input target exists')
    React.act(() => {
      Object.getOwnPropertyDescriptor(win.HTMLInputElement.prototype, 'value').set.call(node, target.value)
      node.dispatchEvent(new win.Event('input', { bubbles: true }))
      node.dispatchEvent(new win.Event('change', { bubbles: true }))
    })
  },
}
function within(container) {
  assert.ok(container, 'Query container exists')
  return { getByRole(role, { name }) {
    assert.equal(role, 'button', 'Harness only queries actual buttons')
    const matches = [...container.querySelectorAll('button')].filter(button => {
      const text = (button.getAttribute('aria-label') ?? button.textContent).replace(/\s+/g, ' ').trim()
      return name instanceof RegExp ? name.test(text) : text === name
    })
    assert.equal(matches.length, 1, `Expected one button named ${name}; found ${matches.length}`)
    return matches[0]
  } }
}

const errors = []
const originalError = console.error
console.error = (...args) => { errors.push(args.map(String).join(' ')); originalError(...args) }
const reports = []
let caseId = 0
let mounted = null
const index = JSON.parse(await readFile(join(PUBLIC, 'salaries/people/index.json'), 'utf8'))
const manifest = JSON.parse(await readFile(join(PUBLIC, 'salaries/search/index.json'), 'utf8'))
const readRows = async shard => JSON.parse(gunzipSync(await readFile(join(PUBLIC, `salaries/people/${shard}.json.gzip`))))
const targetKey = personKey('Fathi Baghbadorani, Milad')
const targetShard = surnameShard('Fathi Baghbadorani, Milad')
const targetRows = (await readRows(targetShard)).filter(row => personKey(row[0]) === targetKey)
assert.ok(targetRows.length, 'The reported regression example must exist in the published records')
const latest = rows => rows.reduce((best, row) => row[5] > best[5] || (row[5] === best[5] && row[2] > best[2]) ? row : best)
const targetLatest = latest(targetRows)
const targetName = displayName(targetLatest[0], index.sources?.[targetLatest[6]]?.nameDisclosure)
const targetYears = [...new Set(targetRows.map(row => row[5]))].sort((a, b) => a - b)
const targetYearLabels = targetYears.map(at => index.years[at])
const targetSpan = targetYearLabels.length > 1 ? `${targetYearLabels[0]}–${targetYearLabels.at(-1)}` : targetYearLabels[0]
const targetPeriodSummary = `${targetYears.length} ${targetYears.length === 1 ? 'period' : 'periods'} · ${targetSpan}`
const expectedDetailRows = withoutCompiledRepeats(targetRows, index.sources).length
const directoryCache = new Map()
async function countFor(query, filters = {}) {
  const bucket = chooseNameSearchBucket(query, manifest)
  if (!bucket) return 0
  if (!directoryCache.has(bucket)) directoryCache.set(bucket, JSON.parse(gunzipSync(await readFile(join(PUBLIC, `salaries/search/${manifest.buckets[bucket].file}`)))))
  return searchNameSearchDocuments(directoryCache.get(bucket), query, filters).length
}
const miladCount = await countFor('milad')
const milaCount = await countFor('mila')
const multiwordCount = await countFor('milad fathi')
const surnameGivenCount = await countFor('baghbadorani milad')
const commaQuery = 'Fathi Baghbadorani, Milad'
const commaCount = new Set((await readRows(targetShard)).filter(row => {
  const tier = nameQueryTier(row[0], commaQuery, index.sources?.[row[6]]?.nameDisclosure)
  return tier !== null && tier < 2
}).map(row => personKey(row[0]))).size
const pageRange = page => `${((page - 1) * 24 + 1).toLocaleString('en-CA')}–${Math.min(milaCount, page * 24).toLocaleString('en-CA')} of ${milaCount.toLocaleString('en-CA')}`
const targetSectors = new Set(targetRows.map(row => index.employers[row[4]][1]))
const excludedSector = index.employers.map(row => row[1]).find(sector => sector && !targetSectors.has(sector))
const excludedYear = index.years.findIndex((_, at) => !targetYears.includes(at))
const sectorIds = new Set(index.employers.flatMap((employer, at) => employer[1] === excludedSector ? [at] : []))
const excludedSectorCount = await countFor('milad', { employerIds: sectorIds })
const excludedYearCount = await countFor('milad', { yearIds: new Set([excludedYear]) })
const peopleSection = () => document.querySelector('section[aria-labelledby="salaries-people-results"]')
const commaSection = () => document.querySelector('section[aria-labelledby="salaries-results"]')
const cards = (section = peopleSection()) => [...(section?.querySelectorAll('button.salaries__card') ?? [])]
const target = (section = peopleSection()) => cards(section).find(node => node.querySelector('.salaries__name')?.textContent === targetName)
const requestPath = input => new URL(typeof input === 'string' ? input : input.url, 'https://salary.test').pathname

async function mount(query, { faults = new Map(), delays = new Map(), params = '' } = {}) {
  if (mounted) { cleanup(); mounted = null }
  history.replaceState({}, '', `/?view=salaries&q=${encodeURIComponent(query)}${params}`)
  const requests = []
  globalThis.fetch = async (input, options = {}) => {
    const path = requestPath(input)
    const request = { path, options, status: null }
    requests.push(request)
    const delay = delays.get(path) ?? 0
    if (delay) await new Promise(resolve => setTimeout(resolve, delay))
    const fault = faults.get(path)
    if (fault) { request.status = fault; return new Response('', { status: fault }) }
    try {
      const file = resolve(PUBLIC, `.${path}`)
      assert.ok(file.startsWith(`${PUBLIC}/`), 'Fetch escaped public directory')
      const bytes = await readFile(file)
      request.status = 200
      return new Response(bytes, { status: 200, headers: { 'Content-Type': path.endsWith('.gzip') ? 'application/gzip' : 'application/json' } })
    } catch (error) {
      if (error.code !== 'ENOENT') throw error
      request.status = 404
      return new Response('', { status: 404 })
    }
  }
  const { SalariesView } = await import(`${pathToFileURL(bundle).href}?case=${++caseId}`)
  mounted = render(React.createElement(SalariesView))
  return { requests, faults, delays }
}

async function ready(expected, section = peopleSection) {
  await waitFor(() => {
    const node = section()
    assert.ok(node, 'Expected people section to be present')
    assert.equal(node.querySelector('.salaries__meta')?.textContent, `${expected.toLocaleString('en-CA')} ${expected === 1 ? 'name' : 'names'}`)
    assert.equal(cards(node).length, Math.min(24, expected), 'All cards on the visible result page should be hydrated')
    assert.equal(node.querySelector('[role="alert"]'), null, 'No load-error alert should be shown')
    if (section === peopleSection) assert.equal(node.getAttribute('aria-busy'), 'false')
  })
  return section()
}

function search(value) {
  const input = document.querySelector('.salaries__global-search input[type="search"]')
  assert.ok(input, 'Global search remains mounted')
  fireEvent.change(input, { target: { value } })
}

async function test(label, fn) {
  const start = performance.now()
  try {
    await fn()
    reports.push({ label, result: 'PASS', milliseconds: Math.round(performance.now() - start) })
    console.log(`PASS ${label}`)
  } catch (error) {
    reports.push({ label, result: 'FAIL', milliseconds: Math.round(performance.now() - start), error: error.message })
    console.log(`FAIL ${label}: ${error.message}`)
  }
}

try {
  await test('Milad: complete current results, original-record summary, detail and Back', async () => {
    const { requests } = await mount('milad')
    await ready(miladCount)
    const button = target()
    assert.ok(button, 'Milad target appears from first-name-only query')
    assert.ok(button.textContent.includes(index.employers[targetLatest[4]][0]))
    assert.ok(button.textContent.includes(formatMoney(targetLatest[2])))
    assert.ok(button.textContent.includes(targetPeriodSummary))
    const originalUrl = location.href
    fireEvent.click(button)
    await waitFor(() => assert.equal(document.querySelector('#salaries-person')?.textContent, targetName))
    assert.equal(document.querySelectorAll('.salaries-record').length, expectedDetailRows)
    assert.ok(document.querySelector('.salaries__person').textContent.includes(targetSpan))
    assert.ok(new URL(location.href).searchParams.has('person'))
    fireEvent.click(within(document.querySelector('.salaries__person')).getByRole('button', { name: 'Back' }))
    await ready(miladCount)
    assert.equal(location.href, originalUrl)
    assert.ok(target())
    assert.ok(requests.every(r => r.options.headers?.Accept === 'application/json'), 'All JSON fetches request JSON, preventing dev-server SPA fallback')
  })

  await test('Search field accepts case/whitespace, any order, and precise comma syntax', async () => {
    search('  MILAD  ')
    await ready(miladCount)
    assert.ok(target())
    search('milad fathi')
    await ready(multiwordCount)
    assert.ok(target())
    search('baghbadorani milad')
    await ready(surnameGivenCount)
    assert.ok(target())
    search(commaQuery)
    await ready(commaCount, commaSection)
    assert.ok(target(commaSection()))
    assert.equal(peopleSection(), null, 'Comma query uses existing precise surname path')
  })

  await test('Pagination hydrates new cards; changing query resets to page one', async () => {
    assert.ok(milaCount > 48, 'Pagination fixture must have at least three pages')
    search('mila')
    let section = await ready(milaCount)
    const first = cards(section).map(node => node.querySelector('.salaries__name').textContent)
    assert.equal(section.querySelector('.salaries-pager__range').textContent, pageRange(1))
    fireEvent.click(within(section).getByRole('button', { name: 'Next page' }))
    await waitFor(() => {
      section = peopleSection()
      assert.equal(section.querySelector('.salaries-pager__range').textContent, pageRange(2))
      assert.equal(section.getAttribute('aria-busy'), 'false')
      assert.equal(cards(section).length, 24)
      assert.notDeepEqual(cards(section).map(node => node.querySelector('.salaries__name').textContent), first)
    })
    search('milad')
    await ready(miladCount)
    assert.ok(target())
    search('mila')
    section = await ready(milaCount)
    assert.equal(section.querySelector('.salaries-pager__range').textContent, pageRange(1))
    assert.deepEqual(cards(section).map(node => node.querySelector('.salaries__name').textContent), first)
  })

  await test('Sector and period controls narrow results and can restore the Milad target', async () => {
    search('milad')
    await ready(miladCount)
    const sectors = document.querySelector('.salaries__desktop-filters [aria-label="Sector"]')
    fireEvent.click([...sectors.querySelectorAll('button')].find(button => button.textContent.startsWith(`${excludedSector} `)))
    await ready(excludedSectorCount)
    await waitFor(() => {
      assert.equal(peopleSection()?.getAttribute('aria-busy'), 'false')
      assert.equal(target(), undefined)
      assert.equal(new URL(location.href).searchParams.get('salary-sector'), excludedSector)
    })
    fireEvent.click(within(sectors).getByRole('button', { name: 'All sectors' }))
    await ready(miladCount)
    assert.ok(target())
    fireEvent.click(document.querySelector('.salaries-range__trigger'))
    const periods = document.querySelector('.salaries-range__panel[role="dialog"]')
    fireEvent.click([...periods.querySelectorAll('button.salaries-range__chip')].find(button => button.querySelector('.salaries-range__year')?.textContent === index.years[excludedYear]))
    await ready(excludedYearCount)
    await waitFor(() => {
      assert.equal(peopleSection()?.getAttribute('aria-busy'), 'false')
      assert.equal(target(), undefined)
      assert.equal(new URL(location.href).searchParams.get('salary-year'), index.years[excludedYear])
    })
    fireEvent.click(within(periods).getByRole('button', { name: 'Every period' }))
    await ready(miladCount)
    assert.ok(target())
  })

  await test('Real absent optional link file returns 404 and still renders its person', async () => {
    // Select an actually absent optional file; adding reviewed links later must not break this test.
    let fixture
    for (const shard of Object.keys(index.shards).sort()) {
      if (existsSync(join(PUBLIC, `salaries/links/${shard}.json.gzip`))) continue
      const rows = await readRows(shard)
      const row = rows.find(row => /^[A-Za-z]{4,},/.test(nameOnly(row[0])))
      if (!row) continue
      const query = nameOnly(row[0]).split(',')[0]
      const total = await countFor(query)
      if (!total || total > 24) continue
      const latestRow = latest(rows.filter(each => personKey(each[0]) === personKey(row[0])))
      fixture = { shard, query, total, name: displayName(latestRow[0], index.sources?.[latestRow[6]]?.nameDisclosure) }
      break
    }
    assert.ok(fixture, 'Published data should contain a short search in a shard without optional links')
    const { requests } = await mount(fixture.query)
    await ready(fixture.total)
    assert.ok(cards().some(node => node.querySelector('.salaries__name')?.textContent === fixture.name))
    assert.ok(requests.some(r => r.path === `/salaries/links/${fixture.shard}.json.gzip` && r.status === 404))
  })

  for (const [kind, path, status] of [
    ['required record 404', `/salaries/people/${targetShard}.json.gzip`, 404],
    ['required record 500', `/salaries/people/${targetShard}.json.gzip`, 500],
    ['reviewed links 500', `/salaries/links/${targetShard}.json.gzip`, 500],
  ]) {
    await test(`${kind}: visible failure and real Retry recovers the complete page`, async () => {
      const faults = new Map([[path, status]])
      const { requests } = await mount('milad', { faults })
      await waitFor(() => assert.match(peopleSection()?.querySelector('[role="alert"]')?.textContent ?? '', /records for this page could not all be loaded/))
      assert.equal(cards().length, 0, 'Incomplete record pages must not silently show partial cards')
      faults.delete(path)
      fireEvent.click(within(peopleSection()).getByRole('button', { name: 'Retry these results' }))
      await ready(miladCount)
      assert.ok(target())
      assert.ok(requests.some(r => r.path === path && r.status === status))
      assert.ok(requests.some(r => r.path === path && r.status === 200 && r.options.cache === 'reload'))
    })
  }

  await test('Search manifest 500: specific error and Retry name search recovers', async () => {
    const path = '/salaries/search/index.json'
    const faults = new Map([[path, 500]])
    const { requests } = await mount('milad', { faults })
    await waitFor(() => assert.match(peopleSection()?.querySelector('[role="alert"]')?.textContent ?? '', /name search could not be loaded/))
    faults.delete(path)
    fireEvent.click(within(peopleSection()).getByRole('button', { name: 'Retry name search' }))
    await ready(miladCount)
    assert.ok(requests.some(r => r.path === path && r.status === 200 && r.options.cache === 'reload'))
  })

  console.log(JSON.stringify({ runtime: { react: React.version, jsdom: toolRequire('jsdom/package.json').version, esbuild: toolRequire('esbuild/package.json').version, lockedReact: appRequire('./package-lock.json').packages['node_modules/react'].version }, checks: reports, reactErrors: errors }, null, 2))
  assert.equal(errors.length, 0, 'React should emit no runtime errors/warnings during these interactions')
  assert.equal(reports.filter(report => report.result === 'FAIL').length, 0, 'All integration checks must pass')
} finally {
  cleanup()
  dom.window.close()
  rmSync(output, { recursive: true, force: true })
  console.error = originalError
}
