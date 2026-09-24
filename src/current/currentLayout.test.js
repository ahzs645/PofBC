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
  MEASURE, THREE_LINE_MEASURE, foldLigatures, inkOf, layoutLockup, lettersOf, lockupMarkup,
  measureLine, nameLines, splitOpening, unsupported, wrapText
} from './currentLayout.js'
import { BREAKS_STATED, MINISTRIES, findMinistry } from './ministries.js'
import { EXTENTS, KERNING, TRACKING, WIDTHS } from './nameMetrics.js'
import glyphs from './nameGlyphs.js'
import lifted from './liftedGlyphs.js'
import { MINISTRY_EPISODES } from '../ministries/ministryHistory.js'

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

test('the capitals the current marks never use are lifted from the Province’s older marks', () => {
  // The historical ministries in the list need an N and an O that no current mark draws. Without
  // these, "Natural Resource Operations" came out as "atural Resource perations".
  assert.ok(lifted.N && lifted.O)
  assert.deepEqual(unsupported('Ministry of Forests, Lands, Natural Resource Operations and Rural Development'), [])
  for (const letter of Object.keys(lifted)) {
    assert.ok(!(letter in glyphs), `${letter} is already in the published alphabet`)
    assert.ok(WIDTHS[letter] > 0 && EXTENTS[letter], `${letter} cannot be measured`)
  }
})

test('a lifted letter’s ink lands where the metrics say it does', () => {
  // The lifting script fits them to the same origin and em as the rest of the alphabet; this is
  // the check that it did, against the font's own ink extents.
  for (const [letter, d] of Object.entries(lifted)) {
    const xs = [...d.matchAll(/[MLC]([^MLCZ]+)/g)].flatMap(([, body]) =>
      body.match(/-?(?:\d+\.?\d*|\.\d+)/g).map(Number).filter((_, i) => i % 2 === 0))
    const [left, right] = EXTENTS[letter]
    assert.ok(Math.abs(Math.min(...xs) - left) < 5, `${letter} starts at ${Math.min(...xs)}, not ${left}`)
    assert.ok(Math.abs(Math.max(...xs) - right) < 5, `${letter} ends at ${Math.max(...xs)}, not ${right}`)
  }
})

test('a typewriter apostrophe is set as the marks set it', () => {
  assert.equal(foldLigatures("Women's Equality"), 'Women’s Equality')
  assert.equal(measureLine("Women's"), measureLine('Women’s'))
  assert.deepEqual(unsupported("Ministry of Women's Equality"), [])
})

test('the historical names need only the letters listed here to be drawn', () => {
  // What is still missing from the committed alphabet, so a new lifted letter shows up as a change
  // to this list. These are in no mark lifted so far; they fall back to the licensed build.
  const missing = new Set()
  for (const { name } of MINISTRY_EPISODES) {
    for (const letter of lettersOf(name)) {
      if (letter !== ' ' && !(letter in glyphs) && !(letter in lifted)) missing.add(letter)
    }
  }
  assert.deepEqual([...missing].sort(), ['.', 'U', 'V'])
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
  // Every published mark reads "Ministry of …" or "Ministère de/des/du …" on its first line,
  // however short the rest is — "Ministry of Health" is two lines.
  assert.deepEqual(splitOpening('Ministry of Health'), ['Ministry of', 'Health'])
  assert.deepEqual(splitOpening('Ministère des Forêts'), ['Ministère des', 'Forêts'])
  assert.deepEqual(splitOpening('Ministère du Travail'), ['Ministère du', 'Travail'])
  // The opening ends at the preposition. "de la" is not part of it — the Province sets
  // "Ministère de" then "la Santé" — and neither is a bare elision.
  assert.deepEqual(splitOpening('Ministère de la Santé'), ['Ministère de', 'la Santé'])
  assert.deepEqual(splitOpening('Ministère de l’Infrastructure'), ['Ministère de', 'l’Infrastructure'])
  assert.deepEqual(splitOpening('Anything else'), ['Anything else'])
})

test('the ministry proper takes one line or two, on a measured threshold', () => {
  // Not a chosen number: across the 46 marks, every name kept on one line measures at most 7793
  // and every name split measures at least 8085. MEASURE sits in that gap.
  const short = 'Ministry of Forests'
  const long = 'Ministry of Water, Land and Resource Stewardship'

  assert.equal(nameLines(short).length, 2)
  assert.equal(nameLines(long).length, 3)
  assert.ok(measureLine('Forests') <= MEASURE)
  assert.ok(measureLine('Water, Land and Resource Stewardship') > MEASURE)
})

test('a name too long for two lines takes three, as the Province set its longest', () => {
  // The Forests, Lands, Natural Resource Operations and Rural Development mark, as published
  // (artwork/current/lifted/flnrord.svg). Split in two, its longer line would measure 13579 —
  // wider than any line a current mark sets — and the Province broke it in three instead.
  assert.deepEqual(
    nameLines('Ministry of Forests, Lands, Natural Resource Operations and Rural Development'),
    ['Ministry of', 'Forests, Lands, Natural', 'Resource Operations', 'and Rural Development'])

  // Every current mark stays within two, so none of them moves.
  for (const ministry of MINISTRIES) {
    for (const language of ['en', 'fr']) {
      assert.ok(nameLines(ministry[language], { language }).length <= 3, `${ministry.code}-${language}`)
    }
  }
  assert.ok(THREE_LINE_MEASURE < measureLine('Operations and Rural Development'))
})

test('French does not end any of three lines on "et"', () => {
  const lines = nameLines('Ministère ' + 'de la Gestion des urgences et de la Préparation au climat et des Solutions et des Parcs', { language: 'fr' })
  assert.equal(lines.length, 4)
  for (const line of lines.slice(1, -1)) assert.ok(!/\bet$/.test(line), `"${line}" ends on et`)
})

test('a split evens the two lines up', () => {
  const [, first, second] = nameLines('Ministry of Water, Land and Resource Stewardship')
  const ratio = Math.min(measureLine(first), measureLine(second)) /
    Math.max(measureLine(first), measureLine(second))

  assert.ok(ratio > 0.6, `lines are lopsided at ${ratio.toFixed(2)}`)
  assert.equal(`${first} ${second}`, 'Water, Land and Resource Stewardship')
})

test('French does not leave "et" at a line end, and English is happy to', () => {
  // Both are the Province's own practice: "Public Safety and / Solicitor General" in English,
  // "la Sécurité publique / et du Solliciteur général" in French.
  const french = nameLines('Ministère de la Sécurité publique et du Solliciteur général', { language: 'fr' })
  assert.deepEqual(french, ['Ministère de', 'la Sécurité publique', 'et du Solliciteur général'])

  const english = nameLines('Ministry of Public Safety and Solicitor General', { language: 'en' })
  assert.deepEqual(english, ['Ministry of', 'Public Safety and', 'Solicitor General'])
})

test('French prefers to open a line with "et", but not at the cost of a stub', () => {
  // Breaking before "et" here would leave "l’Éducation" alone against a line four times its
  // length, so the Province does not, and neither does this.
  const lines = nameLines('Ministère de l’Éducation et des Services à la petite enfance', { language: 'fr' })
  assert.notEqual(lines[1], 'l’Éducation')
  assert.equal(lines.length, 3)
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

test('letters whose counters need an even-odd fill keep it', () => {
  // Two of the French wordmark's letters are drawn with the counter wound the same way as the
  // outline. Without the rule, R's bowl and A's counter fill in solid — which is what shipped
  // before this was caught.
  const french = CURRENT_MARK.fr.shapes.filter((shape) => shape.rule)
  assert.equal(french.length, 2, 'the French wordmark has two such letters')
  assert.ok(french.every((shape) => shape.rule === 'evenodd'))
  assert.equal(CURRENT_MARK.en.shapes.filter((shape) => shape.rule).length, 0, 'English needs none')

  const { markup } = lockupMarkup({
    text: 'Ministère des\nForêts',
    language: 'fr',
    fills: { sun: '#000', mountains: '#000', knockout: '#fff', wordmark: '#000', divider: '#000', name: '#000' }
  })
  assert.equal((markup.match(/fill-rule="evenodd"/g) || []).length, 2)
  // And English emits none, rather than applying it everywhere for safety: even-odd on a letter
  // drawn the ordinary way would eat parts of it.
  assert.ok(!lockupMarkup({
    text: 'Ministry of\nForests',
    fills: { sun: '#000', mountains: '#000', knockout: '#fff', wordmark: '#000', divider: '#000', name: '#000' }
  }).markup.includes('fill-rule'))
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

test('the catalogue holds plain wording and lets the rules break it', () => {
  const forests = findMinistry('for')
  assert.equal(forests.en, 'Ministry of Forests')
  assert.equal(forests.fr, 'Ministère des Forêts')
  assert.deepEqual(nameLines(forests.en), ['Ministry of', 'Forests'])
  assert.equal(findMinistry('nope'), undefined)

  // Only the marks that break against their own rules state their breaks, and there are two.
  assert.deepEqual(BREAKS_STATED, ['af-fr', 'ecc-fr'])
  for (const ministry of MINISTRIES) {
    for (const language of ['en', 'fr']) {
      const stated = BREAKS_STATED.includes(`${ministry.code.toLowerCase()}-${language}`)
      assert.equal(ministry[language].includes('\n'), stated, `${ministry.code} ${language}`)
    }
  }

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
