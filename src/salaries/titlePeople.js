// The people behind one title across employers, and the title's employers over every year.
//
// The position index (positions/<shard>.json.gzip) holds only figures: an employer's records under a
// title in a year, and what they paid. The names are in each employer's own file, so the title page
// reads those, for the employers that have the title, and keeps the records under it, as an
// employer's position page does (titleRecords). A name at two employers stays two rows: nothing here
// assumes that the same name at different employers is one person.

import { personKey } from './people.js'
import { titleKey, titleRecords } from './positions.js'

/** Read the people of up to this many employers without being asked; past it, a button offers them. */
export const AUTO_EMPLOYERS = 8

/** Whether the people of `employers` (a count) are read without being asked. */
export const loadsUnasked = (employers) => employers <= AUTO_EMPLOYERS

/** A title's cells in a sector and a year; `year` null for every year. */
export const scopedCells = (cells, sector = 'all', year = null) => cells.filter((cell) =>
  (sector === 'all' || cell.entry.sector === sector) && (year === null || cell.year === year))

/** The employers among `cells`, most records first: the order their files are asked for in. */
export const cellEmployers = (cells) => {
  const records = new Map()
  for (const cell of cells) records.set(cell.entry.slug, (records.get(cell.entry.slug) ?? 0) + cell.count)
  return [...records].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([slug]) => slug)
}

/**
 * Each employer's cells taken together over every year: its records, its range, its average (each
 * year's average weighted by its records), the years it has the title in and the latest of them.
 * A median does not combine across years, so there is none.
 */
export const employerTotals = (cells) => {
  const totals = new Map()
  for (const cell of cells) {
    const slug = cell.entry.slug
    if (!totals.has(slug)) totals.set(slug, { entry: cell.entry, name: cell.name, slug, count: 0, total: 0, low: Infinity, high: -Infinity, first: cell.year, latest: cell.year, years: new Set() })
    const total = totals.get(slug)
    total.count += cell.count
    total.total += cell.mean * cell.count
    total.low = Math.min(total.low, cell.low)
    total.high = Math.max(total.high, cell.high)
    total.first = Math.min(total.first, cell.year)
    total.latest = Math.max(total.latest, cell.year)
    total.years.add(cell.year)
  }
  return [...totals.values()].map(({ total, years, ...rest }) => ({ ...rest, year: rest.latest, periods: years.size, mean: Math.round(total / rest.count), median: null }))
}

/**
 * The people disclosed under a title at the employers whose files are given: one row a record, with
 * its employer. `files` are [{ entry, rows, nameKeys }] (rows in an employer file's layout, nameKeys
 * that employer's reviewed name joins, nameLinks.js, or null); `keep(row, entry)` drops a row from
 * the comparison (another currency), counted in `setAside`. `year` null keeps every year.
 */
export const titlePeople = (files, key, { sources = {}, year = null, keep = () => true } = {}) => {
  const people = []
  let setAside = 0
  for (const { entry, rows, nameKeys } of files) {
    const nameKey = (row) => {
      const name = personKey(row[0] ?? '')
      return nameKeys?.get(name) ?? name
    }
    const kept = []
    for (const row of rows ?? []) {
      if (year !== null && row[4] !== year) continue
      if (keep(row, entry)) kept.push(row)
      else if (row[1] && titleKey(row[1]) === key) setAside += 1
    }
    for (const row of titleRecords(kept, key, sources, { nameKey })) {
      people.push({
        row, name: row[0] || null, position: row[1], pay: row[2], expenses: row[3], year: row[4], sourceId: row[5], page: row[6],
        slug: entry.slug, employer: entry.names.at(-1), sector: entry.sector
      })
    }
  }
  return { people, setAside }
}

const folded = (value) => String(value ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

/** Whether every word typed is in a person's name, employer or position as disclosed. */
export const matchesPerson = (person, query) => {
  const text = folded(`${person.name ?? ''} ${person.employer} ${person.position ?? ''}`)
  return folded(query).split(/\s+/).filter(Boolean).every((word) => text.includes(word))
}

export const PEOPLE_ORDER = {
  pay: (a, b) => b.pay - a.pay || b.year - a.year,
  recent: (a, b) => b.year - a.year || b.pay - a.pay,
  name: (a, b) => folded(a.name ?? '￿').localeCompare(folded(b.name ?? '￿')) || b.year - a.year
}
