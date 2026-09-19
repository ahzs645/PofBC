// Setting a ministry name the way the Province's own marks are set.
//
// The numbers these pin were measured off the published artwork, not chosen, so a change that
// moves them is a change that stops matching the Province's files. scripts/compare-current-lockups.mjs
// is the wider check — every official name against every published file — but it needs artwork
// that will not always be in the tree, so the ones worth defending permanently are here.

import assert from 'node:assert/strict'
import { test } from 'node:test'
import { CURRENT_MARK, NAME_LEADING } from '../assets/currentMark.js'
import {
  foldLigatures, inkOf, layoutLockup, lettersOf, lockupMarkup, measureLine, nameLines, splitOpening,
  unsupported, wrapText
} from './currentLayout.js'
import { MINISTRIES, findMinistry } from './ministries.js'
import { EXTENTS, KERNING, TRACKING, WIDTHS } from './nameMetrics.js'
import glyphs from './nameGlyphs.js'

test('the committed alphabet covers every letter the official wording uses', () => {
  // Against nameGlyphs.js specifically, not the merged alphabet: this is the guarantee that a
  // clone with no licensed font can still draw every official ministry mark.
  const missing = new Set()
  for (const ministry of MINISTRIES) {
    for (const language of ['en', 'fr']) {
      for (const letter of lettersOf(ministry[language].replace(/\n/g, ' '))) {
        if (letter !== ' ' && !(letter in glyphs)) missing.add(letter)
      }
    }
  }
  assert.deepEqual([...missing], [], 'letters with no drawn form')
})

test('every drawn letter can be measured', () => {
  // The other direction does not hold, and deliberately: the metrics cover the whole Latin range
  // so that wording can be measured and wrapped even where the letterform has to come from a
  // locally built alphabet.
  for (const letter of Object.keys(glyphs)) {
    assert.ok(WIDTHS[letter] > 0, `${letter} has no advance width`)
    assert.ok(EXTENTS[letter], `${letter} has no ink extent`)
  }
  assert.ok(Object.keys(WIDTHS).length > Object.keys(glyphs).length)
})

test('wording that cannot be drawn says which letters are missing', () => {
  // Silently dropping a letter would produce a plausible-looking lockup with a hole in the name.
  assert.deepEqual(unsupported('Ministry of Forests'), [])
  assert.deepEqual(unsupported('Ministry of \u0417\u0434\u043e\u0440'), ['\u0417', '\u0434', '\u043e', '\u0440'])
  assert.deepEqual(unsupported('aaa\u0417\u0417'), ['\u0417'], 'each missing letter is named once')
})

test('f-ligatures are folded, because the published marks are set with them', () => {
  // "Affairs" is four letterforms wide in the artwork, not six. Getting this wrong puts every
  // following letter in the wrong place.
  assert.equal(foldLigatures('Affairs'), 'Aﬀairs')
  assert.equal(lettersOf('Affairs').length, 6)
  assert.equal(foldLigatures('office'), 'oﬃce')
  assert.ok(WIDTHS['ﬀ'] < WIDTHS.f * 2, 'the ligature is tighter than two f’s')
})

test('measuring applies tracking between letters but not after the last', () => {
  // Tracking is space between letters, not a margin on the end.
  const one = measureLine('n')
  const two = measureLine('nn')

  assert.equal(one, WIDTHS.n)
  assert.equal(two, WIDTHS.n * 2 + TRACKING + (KERNING.nn ?? 0))
})

test('measuring applies the kerning the marks were set with', () => {
  // Ta is one of the strongest pairs in the face; without it the two letters sit visibly apart.
  assert.ok(KERNING.Ta < -50, `Ta kern is ${KERNING.Ta}`)
  assert.equal(measureLine('Ta'), WIDTHS.T + WIDTHS.a + TRACKING + KERNING.Ta)
})

test('ink is measured from the letterforms, not the advances', () => {
  // The two differ in both directions — a letter's ink can stop short of its advance or overhang
  // it — which is exactly why a lockup's bounding box cannot be built out of advances.
  assert.notEqual(inkOf('Ministry').right, measureLine('Ministry'))
  assert.ok(inkOf('n').right < WIDTHS.n, 'n stops short of its advance')
  assert.ok(inkOf('Ministry').top < 0 && inkOf('Ministry').bottom > 0, 'an ascender and a descender')
  assert.deepEqual(inkOf(''), { left: 0, right: 0, top: 0, bottom: 0 })
})

test('the opening goes on a line of its own, in both languages', () => {
  // Every published mark reads "Ministry of …" or "Ministère de/des/du/de la …" on its first line,
  // however short the rest is — "Ministry of Health" is two lines.
  assert.deepEqual(splitOpening('Ministry of Health'), ['Ministry of', 'Health'])
  assert.deepEqual(splitOpening('Ministère des Forêts'), ['Ministère des', 'Forêts'])
  assert.deepEqual(splitOpening('Ministère du Travail'), ['Ministère du', 'Travail'])
  assert.deepEqual(splitOpening('Ministère de la Santé'), ['Ministère de la', 'Santé'])
  // A bare elision stays with the word it elides, as the published French marks do.
  assert.deepEqual(splitOpening('Ministère de l’Infrastructure'), ['Ministère de', 'l’Infrastructure'])
  assert.deepEqual(splitOpening('Anything else'), ['Anything else'])
})

test('explicit line breaks are obeyed exactly and never re-wrapped', () => {
  // Several of the Province's own lines run wider than any sensible measure. Re-wrapping them
  // would overrule the artwork — and would overrule anyone editing a name, too.
  const text = 'Ministère du\nDéveloppement de l’enfance\net de la famille'
  assert.deepEqual(nameLines(text), text.split('\n'))
  assert.ok(measureLine('Développement de l’enfance') > 8500, 'and that line is a long one')
})

test('wording with no breaks of its own gets wrapped', () => {
  const lines = nameLines('Ministry of Social Development and Poverty Reduction')
  assert.equal(lines[0], 'Ministry of')
  assert.ok(lines.length > 2)
  assert.equal(lines.join(' '), 'Ministry of Social Development and Poverty Reduction')
})

test('wrapping is greedy and never splits a word', () => {
  const lines = wrapText('one two three four', measureLine('one two'))
  assert.equal(lines[0], 'one two')
  assert.equal(lines.join(' '), 'one two three four')
})

test('empty wording produces no lines rather than an empty one', () => {
  assert.deepEqual(nameLines(''), [])
  assert.deepEqual(nameLines('   \n  '), [])
})

test('the last line sits on the wordmark’s baseline, and extra lines grow upward', () => {
  // This is the alignment rule the published marks use, and it holds to a hundredth of a point
  // across all 46 of them.
  const two = layoutLockup({ text: 'Ministry of\nForests' })
  const three = layoutLockup({ text: 'Ministry of\nAgriculture\nand Food' })

  assert.equal(two.lines.at(-1).baseline, CURRENT_MARK.en.baseline)
  assert.equal(three.lines.at(-1).baseline, CURRENT_MARK.en.baseline)
  assert.ok(Math.abs((two.lines[1].baseline - two.lines[0].baseline) - NAME_LEADING) < 1e-9)
  assert.ok(three.box.height > two.box.height, 'a third line makes the lockup taller')
  assert.equal(three.box.width > 0, true)
})

test('every line starts at the same place, to the right of the rule', () => {
  const { mark, lines } = layoutLockup({ text: 'Ministry of\nAgriculture\nand Food' })

  for (const line of lines) assert.equal(line.x, mark.nameX)
  assert.ok(mark.nameX > mark.divider.x + mark.divider.width, 'the name clears the rule')
  assert.ok(mark.divider.x > mark.width, 'the rule clears the mark')
})

test('the lockup is at least as tall and wide as the mark itself', () => {
  const { box } = layoutLockup({ text: 'Ministry of\nX' })
  assert.ok(box.width >= CURRENT_MARK.en.width)
  assert.ok(box.height >= CURRENT_MARK.en.height)
})

test('each language uses its own wordmark and measurements', () => {
  const english = layoutLockup({ text: 'Ministry of\nForests', language: 'en' })
  const french = layoutLockup({ text: 'Ministère des\nForêts', language: 'fr' })

  assert.notEqual(english.mark.nameX, french.mark.nameX)
  assert.notEqual(english.mark.divider.x, french.mark.divider.x)
  // An unknown language falls back rather than drawing nothing.
  assert.equal(layoutLockup({ text: 'x', language: 'de' }).mark.nameX, english.mark.nameX)
})

test('markup carries a role on every shape, as the published files do', () => {
  const { markup } = lockupMarkup({
    text: 'Ministry of\nForests',
    fills: { sun: '#e3a82b', mountains: '#234075', knockout: '#fff', wordmark: '#234075', divider: '#e3a82b', name: '#234075' }
  })
  const roles = new Set([...markup.matchAll(/data-role="(\w+)"/g)].map((m) => m[1]))

  assert.deepEqual([...roles].sort(), ['divider', 'knockout', 'mountains', 'name', 'sun', 'wordmark'])
})

test('a role with no colour is dropped, not painted', () => {
  const { markup } = lockupMarkup({
    text: 'Ministry of\nForests',
    fills: { sun: '#000', mountains: '#000', knockout: null, wordmark: '#000', divider: null, name: '#000' }
  })

  assert.ok(!markup.includes('data-role="knockout"'))
  assert.ok(!markup.includes('data-role="divider"'))
  assert.ok(markup.includes('data-role="name"'))
})

test('the official wording is what the catalogue holds, breaks and all', () => {
  const forests = findMinistry('for')
  assert.equal(forests.en, 'Ministry of\nForests')
  assert.equal(forests.fr, 'Ministère des\nForêts')
  assert.equal(findMinistry('nope'), undefined)

  for (const ministry of MINISTRIES) {
    assert.ok(ministry.en.startsWith('Ministry'), `${ministry.code}: ${ministry.en}`)
    assert.ok(ministry.fr.startsWith('Ministère'), `${ministry.code}: ${ministry.fr}`)
  }
})

test('every official name lays out without a missing letterform', () => {
  for (const ministry of MINISTRIES) {
    for (const language of ['en', 'fr']) {
      const { markup, lines } = lockupMarkup({
        text: ministry[language],
        language,
        fills: { sun: '#000', mountains: '#000', knockout: null, wordmark: '#000', divider: '#000', name: '#000' }
      })
      const drawn = (markup.match(/data-role="name"/g) || []).length
      const expected = lines.reduce((n, line) => n + lettersOf(line).filter((c) => c !== ' ').length, 0)
      assert.equal(drawn, expected, `${ministry.code} ${language}`)
    }
  }
})
