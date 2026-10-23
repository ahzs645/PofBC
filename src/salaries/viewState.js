// Salary URLs use year labels, not positions in an index that can grow when older sources arrive.
const PARAMETERS = { q: 'q', person: 'person', employer: 'employer', year: 'salary-year', sector: 'salary-sector', employerYear: 'employer-year' }

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
    if (value && value !== 'all' && (key !== 'employerYear' || place.employer)) url.searchParams.set(param, value)
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
