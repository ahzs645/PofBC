// Where the salaries are lives in the address bar — the search typed, its year and sector filters, the
// person, employer, title or employer's position open, how an employer's records are set out, and the
// year on that page — so a link opens there, and a body's salary panel links into it. URLs use year
// labels, not positions in an index that can grow when older sources arrive. `employerYear` is the
// year on an employer's or a title's page.
const PARAMETERS = {
  q: 'q', person: 'person', employer: 'employer', role: 'role', title: 'title', show: 'show', browse: 'browse', layout: 'layout',
  year: 'salary-year', sector: 'salary-sector', employerYear: 'employer-year'
}

export const readSalaryPlace = (search = '') => {
  const params = new URLSearchParams(search)
  return Object.fromEntries(Object.entries(PARAMETERS).map(([key, param]) => [key,
    params.get(param) ?? (key === 'q' ? '' : key === 'year' || key === 'sector' ? 'all' : null)
  ]))
}

export const salaryPlaceUrl = (href, place) => {
  const url = new URL(href)
  for (const [key, param] of Object.entries(PARAMETERS)) {
    const value = place[key]
    if (value && value !== 'all' && (key !== 'employerYear' || place.employer || place.title)) url.searchParams.set(param, value)
    else url.searchParams.delete(param)
  }
  return url
}

/** Unknown or stale shared filters resolve to all years, rather than an empty or broken view. */
export const salaryYearIndex = (label, years) => {
  const at = years.indexOf(label)
  return at < 0 ? 'all' : String(at)
}

const searchText = (value) => String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
const wordsOf = (value) => searchText(value).trim().split(/\s+/).filter(Boolean)

/** Employer search accepts a name in either order, as well as words from a position. */
export const matchesRecordQuery = (row, query) => {
  const text = searchText(`${row[0] ?? ''} ${row[1] ?? ''}`)
  return wordsOf(query).every((word) => text.includes(word))
}

/** A position search also searches its employees; retain the full size for "n of m" labels. */
export const filterPositionGroups = (positions, query) => positions.map((position) => ({
  ...position,
  totalRows: position.rows.length,
  rows: wordsOf(query).every((word) => searchText(position.label ?? 'position not given').includes(word))
    ? position.rows
    : position.rows.filter((row) => matchesRecordQuery(row, query))
})).filter((position) => position.rows.length > 0)

/** A zero amount is a disclosed value. Null and undefined are missing, not zero. */
export const hasExpenseAmount = (value) => value !== null && value !== undefined && Number.isFinite(value)

/**
 * A period filter as [first, last] indexes, or null for every period. It is written as one label
 * ("2020/21") or a range ("2018/19..2023/24"); a label no longer in the catalog is dropped rather
 * than emptying the view, and a range given backwards is read forwards.
 */
export const salaryYearRange = (value, years) => {
  if (!value || value === 'all') return null
  const [from, to = from] = String(value).split('..').map((label) => years.indexOf(label))
  if (from < 0 || to < 0) return null
  return [Math.min(from, to), Math.max(from, to)]
}

/** The address form of a range: one label when it is one period. */
export const salaryYearValue = (range, years) => (range ? (range[0] === range[1] ? years[range[0]] : `${years[range[0]]}..${years[range[1]]}`) : 'all')
