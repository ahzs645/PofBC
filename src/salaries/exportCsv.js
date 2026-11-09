// Records as CSV, for a spreadsheet. Cells that a spreadsheet would run as a formula are prefixed
// with an apostrophe; amounts stay numbers.

const cell = (value) => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : ''
  const text = String(value)
  return `"${(/^[=+\-@\t\r]/.test(text) ? `'${text}` : text).replaceAll('"', '""')}"`
}

export const csvText = (header, rows) => [header, ...rows].map((row) => row.map(cell).join(',')).join('\r\n') + '\r\n'

/** Employer rows ([name, position, pay, expenses, year index, source id, PDF page]) as CSV. */
export const employerCsv = (rows, { employer, years, sources }) => csvText(
  ['Employer', 'Period', 'Name as published', 'Position', 'Remuneration', 'Expenses', 'Disclosure category', 'Source', 'Source URL', 'PDF page'],
  rows.map((row) => {
    const source = sources?.[row[5]] ?? {}
    return [employer, years[row[4]], row[0], row[1], row[2], row[3], source.scope ?? '', source.title ?? row[5], source.url ?? '', row[6] ?? null]
  })
)

/** Save text as a file in the browser. */
export const saveText = (text, filename, type = 'text/csv;charset=utf-8') => {
  const url = URL.createObjectURL(new Blob(['﻿', text], { type }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

/**
 * Where an amount would fall in a list of payments: its rank (1 = highest) and the share of
 * records it is above. Ties rank together, at the highest place they share.
 */
export const rankOf = (amount, pay) => {
  if (!Number.isFinite(amount) || !pay.length) return null
  const above = pay.filter((value) => value > amount).length
  const below = pay.filter((value) => value < amount).length
  return { rank: above + 1, of: pay.length, share: below / pay.length }
}
