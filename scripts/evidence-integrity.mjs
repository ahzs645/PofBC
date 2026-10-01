import { createHash } from 'node:crypto'
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname } from 'node:path'

export const stable = (value) => JSON.stringify(value, (_, item) => item && typeof item === 'object' && !Array.isArray(item) ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item)
export const digest = (value) => createHash('sha256').update(stable(value)).digest('hex').slice(0, 16)

/** All input assertions, including rejected assertions, remain available for inspection. */
export const ledger = () => {
  const rows = []
  return {
    rows,
    record(origin, disposition, input, detail = {}) { rows.push({ origin, disposition, input, ...detail }) },
    write(path) {
      mkdirSync(dirname(path), { recursive: true })
      const counts = rows.reduce((result, row) => { result[row.disposition] = (result[row.disposition] ?? 0) + 1; return result }, {})
      writeFileSync(path, JSON.stringify({ schema: 'import-accounting/1', counts, rows }, null, 2) + '\n')
    }
  }
}

export function eventCollector(accounting) {
  const events = []
  const groups = new Map()
  const add = (event, origin, input = event) => {
    if (!event.id || !event.subject || !event.date?.start) {
      accounting.record(origin, 'unresolved_unmapped', input, { reason: 'Missing event id, subject or date' })
      return
    }
    // Differing interpretation text remains a conflict; only locators/review metadata may differ in corroboration.
    const assertion = { subject: event.subject, type: event.type, date: event.date, status: event.status, title: event.title ?? null, notes: event.notes ?? null }
    const fingerprint = stable(assertion)
    const group = groups.get(event.id) ?? []
    const same = group.find((item) => item.fingerprint === fingerprint)
    const evidence = { sources: event.sources, locator: event.locator, reviewed: event.reviewed ?? null, title: event.title, notes: event.notes, origin }
    if (same) {
      same.event.sources = [...new Set([...same.event.sources, ...event.sources])].sort((a, b) => a - b)
      same.event.evidence.push(evidence)
      accounting.record(origin, 'corroborating_duplicate', input, { output_id: same.event.id })
      return
    }
    const output = { ...event, evidence: [evidence], origins: [origin] }
    if (group.length) {
      for (const item of group) {
        item.event.conflictGroup = event.id
        item.event.status = 'conflicting'
        const oldId = item.event.id
        item.event.id = `${event.id}:variant:${digest(item.assertion)}`
        for (const row of accounting.rows) if (row.output_id === oldId) { row.output_id = item.event.id; row.conflict_group = event.id }
        item.account.disposition = 'conflicting'
        item.account.output_id = item.event.id
      }
      output.conflictGroup = event.id
      output.status = 'conflicting'
      output.id = `${event.id}:variant:${digest(assertion)}`
    }
    accounting.record(origin, group.length ? 'conflicting' : 'accepted', input, { output_id: output.id })
    group.push({ event: output, fingerprint, assertion, account: accounting.rows.at(-1) })
    groups.set(event.id, group)
    events.push(output)
  }
  // A claim under another ID that dates the same happening joins that event as further evidence,
  // with its own wording kept, rather than drawing the happening twice.
  const attach = (target, event, origin, input = event, reason) => {
    target.sources = [...new Set([...target.sources, ...event.sources])].sort((a, b) => a - b)
    target.evidence.push({ sources: event.sources, locator: event.locator, reviewed: event.reviewed ?? null, title: event.title, notes: event.notes, origin })
    target.origins.push(origin)
    accounting.record(origin, 'corroborating_duplicate', input, { output_id: target.id, reason })
  }
  return { events, add, attach }
}

/** Calendar bounds used for matching only; never written back as source precision. */
export function dateBound(value, end = false) {
  if (!value) return null
  const text = String(value)
  if (text.length === 4) return `${text}-${end ? '12-31' : '01-01'}`
  if (text.length === 7) {
    const [year, month] = text.split('-').map(Number)
    if (month < 1 || month > 12) throw new Error(`Invalid month: ${text}`)
    const days = month === 2 ? (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 29 : 28) : [4, 6, 9, 11].includes(month) ? 30 : 31
    return `${text}-${end ? String(days) : '01'}`
  }
  return text
}
