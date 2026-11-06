// Exact audited view-layer correction; frozen collection inputs remain byte-identical.
export function applyWestVancouverTitleRecovery(rows, corrections) {
  if (corrections.length !== 1752) throw new Error('West Vancouver correction count drift')
  const bySource = new Map()
  for (const c of corrections) {
    const list = bySource.get(c.sourceId) ?? []
    if (c.rowIndex !== list.length) throw new Error('West Vancouver correction ordinal drift')
    list.push(c)
    bySource.set(c.sourceId, list)
  }
  const seen = new Map()
  const result = rows.map(row => {
    if (!bySource.has(row.sourceId)) return row
    const at = seen.get(row.sourceId) ?? 0
    const c = bySource.get(row.sourceId)[at]
    if (!c || row.slug !== c.employerSlug || row.year !== c.year || row.name !== c.sourcePrefix || row.position !== null || row.pay !== c.remuneration || row.expenses !== c.expenses || row.page !== c.page) throw new Error(`West Vancouver exact-row correction mismatch: ${row.sourceId} row ${at}`)
    seen.set(row.sourceId, at + 1)
    return { ...row, name: c.name, position: c.position }
  })
  for (const [id, entries] of bySource) if (seen.get(id) !== entries.length) throw new Error(`West Vancouver missing correction rows: ${id}`)
  return result
}

// Restore only validated corrected packed rows for immutable historical receipt replay.
// Packed schema: name, position, pay, expenses, employerIndex, yearIndex, sourceId, page.
export function reverseWestVancouverTitleRecovery(packedRows, index, corrections) {
  const correctedKey = c => JSON.stringify([c.name,c.position,c.remuneration,c.expenses,c.employerSlug,c.year,c.sourceId,c.page])
  const map = new Map()
  for (const c of corrections) {
    const key = correctedKey(c)
    if (map.has(key)) throw new Error('Ambiguous West Vancouver reverse correction')
    map.set(key,c)
  }
  const sourceIds = new Set(corrections.map(c=>c.sourceId)), used = new Set()
  const result = packedRows.map(row => {
    if (!sourceIds.has(row[6])) return row
    const key=JSON.stringify([row[0],row[1],row[2],row[3],index.employers[row[4]][3],index.years[row[5]],row[6],row[7]])
    const c=map.get(key)
    if (!c || used.has(key)) throw new Error('Unrecognized or repeated West Vancouver corrected observation')
    used.add(key)
    const original=[...row];original[0]=c.sourcePrefix;original[1]=null
    return original
  })
  if(used.size!==corrections.length) throw new Error('Incomplete West Vancouver inverse correction')
  return result
}
