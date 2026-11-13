import { dateBound, digest } from '../evidence-integrity.mjs'

const bounds = (date) => ({
  start: dateBound(date.start),
  end: dateBound(date.end ?? date.start, !date.end || date.inclusive),
  inclusive: !date.end || Boolean(date.inclusive)
})

const contains = (outerDate, innerDate) => {
  const outer = bounds(outerDate), inner = bounds(innerDate)
  return outer.start <= inner.start && (outer.end > inner.end ||
    (outer.end === inner.end && (outer.inclusive || !inner.inclusive)))
}

/**
 * Apply an explicit, reviewed choice between assertions about one event. Similar dates alone
 * never merge events. The selected assertion must be contained in each corroborating date's
 * bounds, and subject/type must agree; every original assertion remains in the import ledger.
 */
export const collectEventAssertions = (assertions, decisions, collector) => {
  const byOrigin = new Map()
  for (const assertion of assertions) {
    if (!byOrigin.has(assertion.origin)) byOrigin.set(assertion.origin, [])
    byOrigin.get(assertion.origin).push(assertion)
  }
  const unique = (origin) => byOrigin.get(origin)?.length === 1 ? byOrigin.get(origin)[0] : null
  const choices = new Map()
  const claimed = new Map()
  for (const decision of decisions.filter((entry) => String(entry.subject).startsWith('events/'))) {
    if (typeof decision.id !== 'string' || !decision.id.trim()) throw new Error('Missing event decision ID')
    if (choices.has(decision.id)) throw new Error(`Duplicate event decision ID: ${decision.id}`)
    if (decision.field !== 'preferred_assertion') throw new Error(`Unsupported event decision: ${decision.id}`)
    const id = decision.subject.slice('events/'.length)
    const preferred = unique(decision.value?.origin)
    const origins = [decision.value?.origin, ...(decision.value?.corroboratingOrigins ?? [])]
    if (!preferred || preferred.event.id !== id || !decision.reason || !decision.decided) {
      throw new Error(`Incomplete event decision: ${decision.id}`)
    }
    if (new Set(origins).size !== origins.length || origins.length < 2) throw new Error(`Invalid event decision origins: ${decision.id}`)
    const corroborating = origins.slice(1).map((origin) => {
      const assertion = unique(origin)
      const event = assertion?.event
      const selected = preferred.event
      if (!event || event.id !== id || event.subject !== selected.subject || event.type !== selected.type ||
          event.status !== selected.status || !contains(event.date, selected.date)) {
        throw new Error(`Incompatible corroborating assertion for ${decision.id}: ${origin}`)
      }
      return assertion
    })
    for (const origin of origins) {
      if (claimed.has(origin)) throw new Error(`Event assertion has multiple decisions: ${origin}`)
      if (decision.value.inputDigests?.[origin] !== digest(unique(origin).input)) {
        throw new Error(`Reviewed event assertion changed or was not pinned: ${origin}`)
      }
      claimed.set(origin, decision.id)
    }
    choices.set(decision.id, { preferred, corroborating, decision })
  }

  const applied = new Set()
  for (const assertion of assertions) {
    const choiceId = claimed.get(assertion.origin)
    if (!choiceId) {
      collector.add(assertion.event, assertion.origin, assertion.input)
      continue
    }
    if (applied.has(choiceId)) continue
    const { preferred, corroborating, decision } = choices.get(choiceId)
    collector.add(preferred.event, preferred.origin, preferred.input)
    const target = collector.events.find((event) => event.id === preferred.event.id)
    if (!target) throw new Error(`Event decision did not produce a unique canonical event: ${decision.id}`)
    target.decisions = [{ id: decision.id, reason: decision.reason, decided: decision.decided }]
    for (const item of corroborating) collector.attach(target, item.event, item.origin, item.input, `Reviewed precision refinement: ${decision.id}. ${decision.reason}`)
    applied.add(choiceId)
  }
}
