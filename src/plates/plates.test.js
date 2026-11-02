// The licence plates come from the PlateForge submodule (vendor/plateforge), through its embed entry
// points (vendor/plateforge/docs/embed.md). Its TypeScript is compiled by Vite, not by Node's test
// runner, so these check the joins rather than render: that the submodule is checked out with the
// files the aliases point at, and that every font it imports is installed here at the version its
// font manifest recorded, since the export checks each face's bytes against that manifest.
// PlateForge's own tests (src/embed/embed.test.ts) cover the region data and the layout; the last
// test here checks this view's timeline arithmetic (timeline.js).

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'

const PLATEFORGE = new URL('../../vendor/plateforge/', import.meta.url)
const EMBED = new URL('src/embed/', PLATEFORGE)
const checkedOut = existsSync(new URL('bc.ts', EMBED))

test('the PlateForge submodule is checked out with its embed entry points', () => {
  assert.ok(checkedOut, 'vendor/plateforge is empty or too old: run `git submodule update --init --recursive`')
  assert.ok(existsSync(new URL('index.ts', EMBED)))
})

test('vite.config.js aliases plateforge and plateforge/bc to those entry points', () => {
  const config = readFileSync(new URL('../../vite.config.js', import.meta.url), 'utf8')
  assert.match(config, /vendor\/plateforge\/src\/embed\//)
  assert.match(config, /find: \/\^plateforge\\\/bc\$\/, replacement: plateforge\('bc\.ts'\)/)
  assert.match(config, /find: \/\^plateforge\$\/, replacement: plateforge\('index\.ts'\)/)
})

test('every font package the embed imports is installed at PlateForge’s pinned version', { skip: !checkedOut }, () => {
  const fonts = readFileSync(new URL('src/templates/font-assets-core.ts', PLATEFORGE), 'utf8')
  const packages = [...new Set([...fonts.matchAll(/from "(@fontsource\/[^/]+)\//g)].map((match) => match[1]))]
  assert.ok(packages.length > 0, 'font-assets-core.ts imports no @fontsource packages')
  const ours = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8')).dependencies
  const theirs = JSON.parse(readFileSync(new URL('package.json', PLATEFORGE), 'utf8')).dependencies
  for (const name of packages) {
    assert.ok(theirs[name], `PlateForge does not pin ${name}`)
    assert.equal(ours[name], theirs[name], `${name}: package.json has ${ours[name] ?? 'nothing'}, PlateForge pins ${theirs[name]}`)
  }
})

test('the embed never imports the CJK font subsets', { skip: !checkedOut }, () => {
  const fonts = readFileSync(new URL('src/templates/fonts.ts', PLATEFORGE), 'utf8')
  assert.doesNotMatch(fonts, /from '\.\/font-assets'/)
  assert.doesNotMatch(readFileSync(new URL('src/templates/font-assets-core.ts', PLATEFORGE), 'utf8'), /noto-sans-(sc|jp|kr)/)
})

test('the timeline packs a family into lanes that never overlap, and steps between changes', async () => {
  const { changeYears, inUse, lanesOf, spanOf } = await import('./timeline.js')
  const design = (id, from, to) => ({ id, period: [from, to] })
  const formats = [design('a', 1913, 1917), design('b', 1915, 1915), design('c', 1918, 1923), design('d', 1916, 1930), design('e', 1924, 1924)]
  assert.deepEqual(spanOf(formats), [1913, 1930])
  const lanes = lanesOf(formats)
  assert.deepEqual(lanes.map((lane) => lane.map((f) => f.id)), [['a', 'c', 'e'], ['b', 'd']])
  for (const lane of lanes) for (let i = 1; i < lane.length; i += 1) assert.ok(lane[i - 1].period[1] < lane[i].period[0])
  assert.ok(inUse(formats[0], 1913) && inUse(formats[0], 1917) && !inUse(formats[0], 1918))
  // A design's first year, and the year after its last, within the span.
  assert.deepEqual(changeYears(formats, [1913, 1930]), [1913, 1915, 1916, 1918, 1924, 1925])
})
