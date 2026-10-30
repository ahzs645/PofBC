// Reading a disclosed position, so one title can be found across employers and years.
//
// Employers write the same title many ways: "Teacher", "TEACHERS", "Sr. Policy Analyst", "Senior
// Policy Analyst", "Mayor (Jan–Oct) · City Council". A title is the position before any department
// the compiled records add after a " · ", without a note in brackets, read as words, each in one
// spelling: capitals, stops and spacing set aside (positionKey), a handful of common abbreviations
// written out, and a plural read as its singular. Titles whose words agree are one title; the
// spellings, departments and notes are kept with it. Nothing else is assumed: "Teacher" and "Teacher
// Elementary" stay two titles, and the search offers the second as a related one rather than merging it.

import { positionKey } from './people.js'

// Only abbreviations that cannot be read another way in a job title.
const ABBREVIATIONS = {
  sr: ['senior'], snr: ['senior'], jr: ['junior'], asst: ['assistant'], assoc: ['associate'],
  mgr: ['manager'], mngr: ['manager'], dir: ['director'], coord: ['coordinator'], supv: ['supervisor'],
  supvr: ['supervisor'], exec: ['executive'], dept: ['department'], govt: ['government'],
  vp: ['vice', 'president'], rn: ['registered', 'nurse'], lpn: ['licensed', 'practical', 'nurse'], '&': ['and']
}

/** A word's singular, where its plural is the regular one: "analysts" → "analyst", "deputies" → "deputy". */
const singular = (word) => {
  if (word.length > 4 && word.endsWith('ies')) return `${word.slice(0, -3)}y`
  if (word.length > 3 && word.endsWith('s') && !/(ss|us|is)$/.test(word)) return word.slice(0, -1)
  return word
}

/** A position's words, each in one spelling. */
export const titleWords = (position) => positionKey(String(position ?? '').split(' · ')[0].replace(/\([^)]*\)/g, ' ')).split(/[\s/+]+/)
  .flatMap((word) => ABBREVIATIONS[word] ?? [word]).filter(Boolean).map(singular)

/** The key one title is grouped under, however its employer spelled it. */
export const titleKey = (position) => titleWords(position).join(' ')

/** The slice of the position index a title is filed under: its key's first two letters or digits. */
export const titleShard = (key) => String(key ?? '').replace(/[^a-z0-9]/g, '').slice(0, 2).padEnd(2, '_')

/**
 * A test of how closely a title's key answers what was typed, best first: 0 the same title, 1 a title
 * that begins with it ("teacher" → "teacher elementary", "teach" → "teaching staff"), 2 one with every
 * word typed beginning one of its words, in any order ("analyst policy" → "senior policy analyst").
 * null where it does not answer. A word typed is read as titles are, so "teachers" finds "teacher".
 */
export const titleMatcher = (query) => {
  const wanted = titleWords(query)
  const typed = wanted.join(' ')
  return (key) => {
    if (!wanted.length || !key) return null
    if (key === typed) return 0
    if (key.startsWith(typed)) return 1
    const words = key.split(' ')
    return wanted.every((part) => words.some((word) => word.startsWith(part))) ? 2 : null
  }
}

/**
 * A title as it is shown for every spelling it gathers: the commonest spelling, without the department
 * or bracketed note that the key sets aside ("Nurse 4 (C) · Ward 3" is shown as "Nurse 4").
 */
export const titleLabel = (spelling) => String(spelling ?? '').split(' · ')[0].replace(/\s*\([^)]*\)/g, ' ').replace(/\s+/g, ' ').trim() || String(spelling ?? '')

/** An average of pay, to the dollar: it is worked out here, not disclosed, so its cents would mislead. */
export const meanMoney = (values) => (values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : null)

const keyed = new WeakMap()

/**
 * The position index's titles, each with its key: { key, label, rows, employers, first, last }, in the
 * index's order (most records first). Worked out once an index.
 */
export const keyedTitles = (index) => {
  if (!keyed.has(index)) {
    keyed.set(index, index.titles.map(([spelling, rows, employers, first, last]) => ({ key: titleKey(spelling), label: titleLabel(spelling), rows, employers, first, last })))
  }
  return keyed.get(index)
}

/**
 * Titles near a title: those that add to it ("teacher" → "teacher elementary school"), then those it
 * adds to ("senior policy analyst" → "policy analyst"); within each, the most widely used first.
 */
export const relatedTitles = (titles, key) => {
  const adds = titleMatcher(key)
  const words = new Set(key.split(' '))
  const narrower = titles.filter((title) => title.key !== key && adds(title.key) !== null)
  const broader = titles.filter((title) => title.key !== key && title.key.split(' ').every((word) => words.has(word)))
  const order = (a, b) => b.employers - a.employers || b.rows - a.rows
  return { narrower: narrower.sort(order), broader: broader.sort(order) }
}
