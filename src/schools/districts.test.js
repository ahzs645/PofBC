import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { CURRENT_DISTRICTS, HISTORICAL_DISTRICTS, SCHOOL_DISTRICTS, DISTRICT_CONNECTIONS, districtById, districtForEmployer, districtHistory, connectionsOf, searchDistricts, formatHistoryDate, formerDistrictId, establishmentLabel } from './districts.js'
import { SCHOOL_IDENTITY_BODIES, SCHOOL_IDENTITY_SUBJECTS, SCHOOL_RELATED_BODIES } from './integration.js'

const root = fileURLToPath(new URL('../../', import.meta.url))
const file = (path) => readFileSync(new URL(`../../${path}`, import.meta.url))

test('the official roster has all 60 current districts and 60 distinct existing salary employers', () => {
  const roster = JSON.parse(file('research/education/school-districts/roster.json'))
  const employerFiles = new Set(execFileSync('git', ['ls-tree', '-r', '--name-only', 'HEAD', 'public/salaries/employers'], { cwd: root, encoding: 'utf8' }).trim().split('\n'))
  assert.equal(CURRENT_DISTRICTS.length, 60)
  assert.equal(new Set(CURRENT_DISTRICTS.map((district) => district.number)).size, 60)
  assert.deepEqual(CURRENT_DISTRICTS.map((district) => district.number), roster.districts.map((district) => district.number))
  assert.equal(new Set(CURRENT_DISTRICTS.map((district) => district.employerSlug)).size, 60)
  assert.equal(districtById(99), null, 'the provincial aggregate is not a school district')
  for (const district of CURRENT_DISTRICTS) {
    assert.ok(employerFiles.has(`public/salaries/employers/${district.employerSlug}.json.gzip`), district.employerSlug)
    assert.equal(districtForEmployer(district.employerSlug).id, district.id)
  }
  assert.equal(districtById(93).kind, 'francophone-school-district')
})

test('amalgamation edges use the effective order date, and historical identities resolve independently', () => {
  const mergers = CURRENT_DISTRICTS.filter((district) => district.events.some((event) => event.type === 'amalgamation' && event.date === '1996-12-02'))
  assert.equal(mergers.length, 15)
  assert.equal(new Set(SCHOOL_DISTRICTS.map((district) => district.id)).size, SCHOOL_DISTRICTS.length)
  const keys = new Set()
  for (const edge of DISTRICT_CONNECTIONS) {
    assert.ok(districtById(edge.from), edge.from)
    assert.ok(districtById(edge.to), edge.to)
    assert.notEqual(edge.from, edge.to)
    assert.notEqual(edge.type, 'order-made')
    assert.notEqual(edge.date, '1996-07-25', 'approval did not transfer the districts')
    const key = `${edge.from}:${edge.to}:${edge.date}`
    assert.ok(!keys.has(key), key); keys.add(key)
    assert.ok(connectionsOf(edge.to).predecessors.some((link) => link.from === edge.from))
    assert.ok(connectionsOf(edge.from).successors.some((link) => link.to === edge.to))
  }
  assert.deepEqual(connectionsOf('school-district-67').predecessors.map((link) => link.district.number).sort((a, b) => a - b), [15, 77])
  assert.notEqual(districtById(58).id, formerDistrictId({ number: 58, name: 'McBride' }), 'a reused district number is not an identity join')
  for (const district of HISTORICAL_DISTRICTS) assert.equal(district.employerSlug, undefined, 'predecessors do not inherit current payroll')
})

test('each dated claim has source and precision, and dates preserve their meaning', () => {
  const validDate = /^\d{4}(?:-\d{2}(?:-\d{2})?)?$/
  for (const district of SCHOOL_DISTRICTS) {
    assert.ok(Array.isArray(district.notes), district.id)
    for (const event of districtHistory(district)) {
      assert.match(event.sourceUrl, /^https:\/\//, `${district.id}: ${event.title}`)
      if (!event.date) continue
      if (event.precision === 'report-period') {
        assert.match(event.date, /^\d{4}-\d{4}$/)
        assert.match(event.type, /observed/)
        continue
      }
      assert.match(event.date, validDate, district.id)
      assert.ok(['year', 'month', 'day'].includes(event.precision), `${district.id}: ${event.date}`)
      assert.equal(event.date.length, { year: 4, month: 7, day: 10 }[event.precision])
    }
  }
  assert.equal(districtById(57).established.date, '1946-04-15', 'the district-reported date must not become a blanket April 12 date')
  assert.equal(districtById(50).established.date, '1946-04-01')
  assert.match(establishmentLabel(districtById(70)), /Institutional origin/)
  assert.equal(districtById(93).established.disputed, true)
  assert.equal(formatHistoryDate('1995'), '1995')
  assert.ok(!formatHistoryDate('1995').includes('January'))
  assert.ok(districtHistory(districtById(93)).some((event) => event.date === '1996-01-03'), 'retain the separate audited claim alongside the 1995 government account')
})

test('all 60 current districts have hashed source artwork, and bitmap SVGs are not called vectors', () => {
  const ids = new Set()
  for (const district of CURRENT_DISTRICTS) {
    assert.ok(district.assets.length, district.id)
    for (const asset of district.assets) {
      assert.ok(!ids.has(asset.id), asset.id); ids.add(asset.id)
      assert.match(asset.file, /^education\/school-districts\/logos\/[^/]+\.(svg|png|jpe?g|webp)$/)
      assert.match(asset.sourceUrl, /^https?:\/\//, 'retain the original source URL without inventing a secure endpoint')
      const bytes = file(`public/${asset.file}`)
      assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, asset.id)
      if (asset.originalSourceFile) assert.equal(createHash('sha256').update(file(`public/${asset.originalSourceFile}`)).digest('hex'), asset.originalSourceSha256, `${asset.id}: original source container`)
      if (asset.format === 'svg') {
        const svg = bytes.toString('utf8')
        assert.match(svg, /<svg\b/)
        assert.doesNotMatch(svg, /<script\b|<foreignObject\b|\bonload\s*=|javascript:/i, asset.id)
        if (/<image\b|data:image\/(?:png|jpeg|webp)/i.test(svg)) assert.equal(asset.isVector, false, asset.id)
      }
      assert.notEqual(asset.sourceDate, asset.observedDate, 'capture does not date adoption or historic use')
      if (asset.displayBackground) assert.equal(asset.darkBackground, true, 'white source art must retain a readable display ground in every view')
    }
  }
  assert.equal(districtById(70).assets[0].isVector, false)
})

test('the shared catalogue connects current governance and every identity without substituting successor artwork', () => {
  assert.equal(SCHOOL_RELATED_BODIES.length, 60)
  assert.equal(SCHOOL_IDENTITY_SUBJECTS.length, SCHOOL_DISTRICTS.length)
  for (const district of SCHOOL_DISTRICTS) {
    const subject = SCHOOL_IDENTITY_SUBJECTS.find((item) => item.id === district.id)
    const body = SCHOOL_IDENTITY_BODIES.find((item) => item.id === district.id)
    assert.deepEqual(body.assets, district.assets)
    assert.equal(subject.schoolDistrict, district.id)
    if (district.current) {
      assert.equal(subject.graphNode, district.id)
      assert.equal(SCHOOL_RELATED_BODIES.find((item) => item.id === district.id).salaryEmployers[0].slug, district.employerSlug)
    } else {
      assert.equal(subject.graphNode, null)
      assert.deepEqual(subject.salaryEmployers, [])
    }
  }
  assert.ok(searchDistricts({ query: 'Powell River' }).some((district) => district.number === 47))
  assert.ok(searchDistricts({ query: 'Penticton', scope: 'historical' }).some((district) => district.number === 15))
})
