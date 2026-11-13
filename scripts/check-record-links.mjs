// Validate typed links against the same organization/event IDs the application actually reads.
import { writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { CURRENT_BODIES } from '../src/government/currentData.js'
import { HISTORICAL_BODIES, LOCAL_BODIES, SUB_AGENCIES } from '../src/government/historyData.js'
import { MINISTRY_EPISODES } from '../src/government/episodes.js'
import { EVENTS, EVENT_SOURCES } from '../src/government/eventsData.js'

export const checkRecordLinks = () => {
  const entities = new Set([...CURRENT_BODIES, ...HISTORICAL_BODIES, ...LOCAL_BODIES, ...SUB_AGENCIES, ...MINISTRY_EPISODES].map((entry) => entry.id))
  for (const id of ['legislative-assembly', 'lieutenant-governor', 'executive-council', 'people-of-bc']) entities.add(id)
  const eventIds = new Set(EVENTS.map((event) => event.id))
  const issues = []
  const unresolvedEntities = []
  const eventsWithoutSource = []
  let relatedEntityLinks = 0, relatedEventLinks = 0, legalReferences = 0
  for (const event of EVENTS) {
    if (!entities.has(event.subject) && !['symbol:flag', 'symbol:arms'].includes(event.subject)) issues.push({ event: event.id, field: 'subject', value: event.subject })
    for (const id of event.related ?? []) {
      relatedEntityLinks++
      if (!entities.has(id)) issues.push({ event: event.id, field: 'related', value: id })
    }
    for (const id of event.relatedEvents ?? []) {
      relatedEventLinks++
      if (!eventIds.has(id)) issues.push({ event: event.id, field: 'relatedEvents', value: id })
    }
    for (const id of event.competingEvents ?? []) {
      relatedEventLinks++
      if (!eventIds.has(id)) issues.push({ event: event.id, field: 'competingEvents', value: id })
      else if (!(EVENTS.find((other) => other.id === id).competingEvents ?? []).includes(event.id)) issues.push({ event: event.id, field: 'competingEvents', value: id, reason: 'Competing claims must name each other' })
    }
    for (const reference of event.legalReferences ?? []) {
      legalReferences++
      if (!/^https:\/\//.test(reference.source_url) || !reference.locator) issues.push({ event: event.id, field: 'legalReferences', value: reference })
    }
    for (const reference of event.unresolvedRelated ?? []) {
      unresolvedEntities.push({ event: event.id, ...reference })
      if (!reference.label || !reference.reason) issues.push({ event: event.id, field: 'unresolvedRelated', value: reference })
    }
    if (!event.sources.length) eventsWithoutSource.push({ event: event.id, title: event.title, locator: event.locator, reviewed: event.reviewed })
    for (const index of [...event.sources, ...(event.evidence ?? []).flatMap((entry) => entry.sources)]) {
      if (!Number.isInteger(index) || !/^https?:\/\//.test(EVENT_SOURCES[index]?.url)) issues.push({ event: event.id, field: 'sources', value: index })
    }
  }
  return { schema: 'record-link-audit/1', events: EVENTS.length, entities: entities.size,
    relatedEntityLinks, relatedEventLinks, legalReferences, issues, unresolvedEntities, eventsWithoutSource }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const report = checkRecordLinks()
  const writeAt = process.argv.indexOf('--write')
  if (writeAt >= 0) writeFileSync(process.argv[writeAt + 1], JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify(report, null, 2))
  if (report.issues.length) process.exitCode = 1
}
