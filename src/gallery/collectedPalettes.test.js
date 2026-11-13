import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { COLLECTED_PALETTES, collectedPreviewFile, paletteFor, renderCollectedPalette } from './collectedPalettes.js'

const source = (file) => readFileSync(new URL(`../../public/identity-collected/${file}`, import.meta.url), 'utf8')
const groupOf = (id) => COLLECTED_PALETTES[id]
const hex = (value) => /^#[\da-f]{3}$/i.test(value) ? `#${[...value.slice(1)].map((digit) => digit + digit).join('')}`.toLowerCase() : value.toLowerCase()
const attributes = (tag) => Object.fromEntries([...tag.matchAll(/([\w:-]+)\s*=\s*(["'])(.*?)\2/g)].map(([, name, , value]) => [name, value]))
const shapeTags = (svg) => [...svg.matchAll(/<(path|polygon|polyline|rect|circle|ellipse|line)\b[^>]*>/g)].map((match) => ({ name: match[1], ...attributes(match[0]) }))
const geometry = (svg) => shapeTags(svg).map(({ fill, stroke, style, class: classes, ...shape }) => shape)
const paintValues = (svg) => [...new Set([...svg.matchAll(/(?:fill|stroke)\s*(?:=\s*["']|:\s*)(#[\da-f]{3,6})(?=["';\s}])/gi)].map(([, value]) => hex(value)))].sort()

// Resolve the simple original sources independently: each uses direct/group fills or class rules.
// Comparing the resulting painted shapes catches a lost implicit fill or a CSS-only reversal.
const paintedShapes = (svg) => {
  const classes = new Map()
  const css = [...svg.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/g)].map(([, content]) => content).join('\n')
  for (const [, selectors, body] of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    const fill = body.match(/(?:^|;)\s*fill\s*:\s*([^;]+)/)?.[1].trim()
    if (fill) for (const selector of selectors.trim().split(/\s*,\s*/)) classes.set(selector.replace(/^\./, ''), fill)
  }
  const stack = []
  const shapes = []
  for (const [tag, closing, name] of svg.matchAll(/<(\/?)([\w:-]+)\b[^>]*>/g)) {
    if (closing) { stack.pop(); continue }
    const attrs = attributes(tag)
    const fill = attrs.fill ?? (attrs.class ?? '').split(/\s+/).map((key) => classes.get(key)).find(Boolean) ?? stack.at(-1) ?? '#000000'
    if (/^(?:path|polygon|polyline|rect|circle|ellipse|line)$/.test(name)) {
      const { fill: ownFill, stroke, style, class: className, ...shape } = attrs
      shapes.push({ name, ...shape, fill: hex(fill) })
    }
    if (!tag.endsWith('/>')) stack.push(fill)
  }
  return shapes
}

test('reviewed groups retain public design IDs, source links and documented default choices', () => {
  const knowledge = groupOf('source-knowledge-network-knowledge-network-colour-eps')
  assert.equal(knowledge.masterId, 'source-knowledge-network-knowledge-network-svg')
  assert.deepEqual(knowledge.palettes.map(({ id }) => id), ['colour', 'white-lettering', 'black', 'white'])
  assert.equal(paletteFor(knowledge).id, 'colour')
  assert.equal(paletteFor(knowledge, { sourceId: knowledge.masterId }).id, 'white-lettering')
  assert.equal(paletteFor(knowledge, { sourceId: 'source-knowledge-network-knowledge-network-colour-png' }).id, 'colour')
  assert.equal(paletteFor(knowledge, { paletteId: 'black', sourceId: knowledge.masterId }).id, 'black')
  assert.equal(paletteFor(knowledge, { paletteId: 'unknown' }).id, 'colour')
  assert.equal(paletteFor(undefined), null)
  assert.equal(Object.keys(COLLECTED_PALETTES).length, 4)
  assert.equal(groupOf('vector-BCID_StrongerBC_RGB_pos'), undefined, 'endorsed geometries have not been folded into standalone wordmarks')
  assert.equal(groupOf('source-northern-health-northern-health-colour-svg'), undefined, 'the no-tagline drawing remains separate')
  for (const group of Object.values(COLLECTED_PALETTES)) {
    assert.equal(new Set(group.palettes.map(({ id }) => id)).size, group.palettes.length)
    const sources = group.palettes.flatMap(({ sourceIds }) => sourceIds)
    assert.equal(new Set(sources).size, sources.length, group.label)
    assert.ok(group.palettes.some(({ id }) => id === group.defaultId))
  }
})

test('all four Knowledge Network colourways keep the original 35 vector paths and exact RGB colours', () => {
  const svg = source('knowledge-network/knowledge-network.svg')
  assert.equal(createHash('sha256').update(svg).digest('hex'), '1c1e3071bd97c2dbed19367398d8f8bf16930e522ba4cc661b3f752bd8ebe7ee')
  const group = groupOf('source-knowledge-network-knowledge-network-colour-eps')
  const expected = {
    colour: ['#000000', '#00adee'],
    'white-lettering': ['#00adee', '#ffffff'],
    black: ['#000000'],
    white: ['#ffffff'],
  }
  for (const palette of group.palettes) {
    const rendered = renderCollectedPalette(svg, palette)
    assert.deepEqual(geometry(rendered), geometry(svg), palette.id)
    assert.equal(shapeTags(rendered).length, 35)
    assert.deepEqual(paintValues(rendered), expected[palette.id], palette.id)
    assert.doesNotMatch(rendered, /<(?:\w+:)?(?:image|rect)\b/, 'no bitmap or background is added')
    if (palette.id === 'white-lettering') assert.equal(rendered, svg, 'the original colourway remains byte-for-byte unchanged')
  }
})

test('Northern Health recolours exactly reproduce all 42 painted shapes of the supplied monochrome originals', () => {
  const master = source('northern-health/northern-health-colour-tagline.svg')
  const group = groupOf('source-northern-health-northern-health-colour-tagline-svg')
  assert.equal(shapeTags(master).length, 42)
  assert.equal(renderCollectedPalette(master, paletteFor(group)), master)
  for (const id of ['black', 'white']) {
    const counterpart = source(`northern-health/northern-health-${id}-tagline.svg`)
    const rendered = renderCollectedPalette(master, paletteFor(group, { paletteId: id }))
    assert.deepEqual(geometry(rendered), geometry(master))
    assert.deepEqual(paintedShapes(rendered), paintedShapes(counterpart), id)
    assert.equal(attributes(rendered.match(/<svg\b[^>]*>/)[0]).viewBox, attributes(counterpart.match(/<svg\b[^>]*>/)[0]).viewBox)
  }
})

test('StrongerBC reversals match their own originals, preserve gold and retain the transparent extent', () => {
  for (const [family, paletteId] of [['RGB', 'reversed'], ['Solid', 'white']]) {
    const group = groupOf(`vector-StrongerBC_${family}_pos`)
    const master = source(`stronger-bc/StrongerBC_${family}_pos.svg`)
    const counterpart = source(`stronger-bc/StrongerBC_${family}_rev.svg`)
    const rendered = renderCollectedPalette(master, paletteFor(group, { paletteId }))
    assert.equal(renderCollectedPalette(master, paletteFor(group)), master)
    assert.deepEqual(geometry(rendered), geometry(master))
    assert.deepEqual(paintedShapes(rendered), paintedShapes(counterpart), family)
    assert.equal(paintedShapes(rendered).filter(({ fill }) => fill === 'none').length, 1)
    assert.equal(shapeTags(rendered).length, 11)
    assert.deepEqual(paintValues(rendered), family === 'RGB' ? ['#e3a82b', '#ffffff'] : ['#ffffff'])
  }
  const rgb = source('stronger-bc/StrongerBC_RGB_pos.svg')
  const solid = source('stronger-bc/StrongerBC_Solid_pos.svg')
  assert.notEqual(attributes(rgb.match(/<svg\b[^>]*>/)[0]).viewBox, attributes(solid.match(/<svg\b[^>]*>/)[0]).viewBox)
})

test('recolouring is scoped to paint attributes and CSS declarations, never content or IDs', () => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg"><title>fill="#fff" and #fff</title><desc>stroke:#fff;</desc><!-- fill="#fff" -->
    <defs><style>/* fill:#fff; */ .paint { fill: #FFF; stroke: #123 !important; } .other { color:#fff; }</style></defs>
    <path id="fill:#fff" data-fill="#fff" d="M1 2h3v4z" fill='#FFFFFF' stroke="#fffaaa" style="fill:#fff;stroke:#123;stroke-width:2;content:'fill:#fff'"/>
    <path fill="url(#gradient)" stroke="none"/></svg>`
  const rendered = renderCollectedPalette(svg, { inks: { '#fff': '#000', '#112233': '#445566' } })
  assert.ok(rendered.includes('<title>fill="#fff" and #fff</title>'))
  assert.ok(rendered.includes('<desc>stroke:#fff;</desc>'))
  assert.ok(rendered.includes('<!-- fill="#fff" -->'))
  assert.ok(rendered.includes('/* fill:#fff; */'))
  assert.ok(rendered.includes('id="fill:#fff" data-fill="#fff"'))
  assert.ok(rendered.includes('fill: #000000; stroke: #445566 !important;'))
  assert.ok(rendered.includes('style="fill:#000000;stroke:#445566;stroke-width:2;content:\'fill:#fff\'"'))
  assert.ok(rendered.includes('fill=\'#000000\' stroke="#fffaaa"'))
  assert.ok(rendered.includes('fill="url(#gradient)" stroke="none"'))
  assert.deepEqual(geometry(rendered), geometry(svg))
})

test('masked drawings are refused because global styles and inherited paint also affect mask semantics', () => {
  for (const svg of [
    '<svg><mask><path fill="#fff"/></mask><path fill="#fff"/></svg>',
    '<svg fill="#fff"><mask><path/></mask><path/></svg>',
    '<svg><style>.paint{fill:#fff}</style><mask><path class="paint"/></mask><path class="paint"/></svg>',
  ]) assert.throws(() => renderCollectedPalette(svg, { inks: { '#fff': '#000' } }), /mask/)
})

test('explicit defaultFill supports implicit black shapes without adding a background or overriding an explicit fill', () => {
  const svg = '<svg viewBox="0 0 10 10"><path d="M0 0h10v10z"/></svg>'
  const rendered = renderCollectedPalette(svg, { inks: {}, defaultFill: '#fff' })
  assert.ok(rendered.startsWith('<svg viewBox="0 0 10 10" fill="#ffffff">'))
  assert.deepEqual(geometry(rendered), geometry(svg))
  assert.doesNotMatch(rendered, /<rect\b/)
  assert.equal(renderCollectedPalette('<svg fill="none"><path/></svg>', { inks: {}, defaultFill: '#fff' }), '<svg fill="none"><path/></svg>')
  assert.throws(() => renderCollectedPalette('<svg><mask><path/></mask></svg>', { inks: {}, defaultFill: '#fff' }), /mask/)
})

test('unsafe mappings, active content, external references and malformed SVG are refused', () => {
  const svg = '<svg><path fill="#fff"/></svg>'
  for (const inks of [{ '#fff': 'url(https://example.com)' }, { '#fff': 'red' }, { 'currentColor': '#fff' }, { '#fff': '#000', '#ffffff': '#111' }]) {
    assert.throws(() => renderCollectedPalette(svg, { inks }), TypeError)
  }
  for (const input of [
    '<svg><script>alert(1)</script></svg>', '<svg><image href="data:image/png;base64,AA"/></svg>',
    '<svg><foreignObject/></svg>', '<svg onload="run()"/>', '<svg><use href="https://example.com/a.svg#b"/></svg>',
    '<svg><path fill="url(https://example.com/a.svg#b)"/></svg>',
    '<svg><style>@import url(https://example.com/x.css);</style></svg>',
    '<!DOCTYPE svg [<!ENTITY x SYSTEM "https://example.com">]><svg/>',
    '<?xml-stylesheet href="https://example.com/x.css"?><svg/>',
    '<svg><path fill=#fff/></svg>', '<svg><path></svg>', '<svg/><svg/>', '<g/>',
  ]) assert.throws(() => renderCollectedPalette(input, { inks: { '#fff': '#000' } }), TypeError, input)
})

test('SVG artwork uses its vector file; non-browser formats retain their available preview', () => {
  assert.equal(collectedPreviewFile({ format: 'svg', file: 'logo.svg', preview: 'logo.png' }), 'logo.svg')
  assert.equal(collectedPreviewFile({ format: 'SVG', file: 'logo.svg' }), 'logo.svg')
  assert.equal(collectedPreviewFile({ format: 'eps', file: 'logo.eps', preview: 'logo.png' }), 'logo.png')
  assert.equal(collectedPreviewFile({ format: 'png', file: 'logo.png' }), 'logo.png')
  assert.equal(collectedPreviewFile(undefined), undefined)
})
