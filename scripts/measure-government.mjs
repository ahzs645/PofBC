// How far the atlas's history reaches: the measures at the top of research/WANTED.md, counted
// across every year the diagram draws (1871 to today).
//
//   node scripts/measure-government.mjs
//
// A body-year is one body drawn in one year. Its ministry is stated when a source names it for that
// period, inferred when the diagram places it beside today's ministry, and none when it is drawn in
// the lane for bodies with no ministry (sub-agencies drawn there, partnerships and the courts, which
// have none by design, are not counted).

import { FIRST_YEAR, PRESENT_YEAR, governmentIn } from '../src/government/snapshot.js'
import { HISTORICAL_BODIES, HISTORY_SOURCES, SUB_AGENCIES } from '../src/government/historyData.js'

const NOT_BODIES = new Set(['people', 'assembly', 'crown', 'premier', 'ministry', 'officer', 'court'])
const count = { stated: 0, inferred: 0, none: 0, subYears: 0, subInferred: 0, ministryYears: 0, headless: 0 }
for (let year = FIRST_YEAR; year <= PRESENT_YEAR; year++) {
  for (const node of governmentIn(year).nodes) {
    if (node.kind === 'ministry') {
      count.ministryYears++
      if (!node.head?.person) count.headless++
    }
    if (node.kind === 'sub' && year < PRESENT_YEAR) {
      count.subYears++
      if (node.inferredParent) count.subInferred++
    }
    if (node.ring !== 'outer' || node.unplacedSub || node.partnerOnly || NOT_BODIES.has(node.kind)) continue
    if (node.inferredGroup) count.inferred++
    else if (node.group) count.stated++
    else if (node.unattached) count.none++
  }
}

const started = SUB_AGENCIES.filter((sub) => sub.established).length
const seen = SUB_AGENCIES.filter((sub) => !sub.established && sub.firstObservedClaim).length
const rows = [
  ['Ministry-years with no minister matched (annual snapshots, not day by day)', `${count.headless} of ${count.ministryYears}`],
  ['Body-years with a stated responsible ministry', count.stated],
  ['Body-years placed beside a ministry by inference', count.inferred],
  ['Body-years with no ministry', count.none],
  ['Sub-agencies with a start / a dated sighting / neither', `${started} / ${seen} / ${SUB_AGENCIES.length - started - seen} of ${SUB_AGENCIES.length}`],
  ['Past sub-agency-years whose parent is inferred from today\'s', `${count.subInferred} of ${count.subYears}`],
  ['Bodies whose main source is Wikipedia', HISTORICAL_BODIES.filter((body) => /wikipedia\.org/.test(HISTORY_SOURCES[body.source] ?? '')).length],
  ['Bodies whose start is a year only', HISTORICAL_BODIES.filter((body) => /^\d{4}$/.test(body.established ?? '')).length],
  ['Historical bodies with no start at all (listed in lineage only)', HISTORICAL_BODIES.filter((body) => !body.established && !body.firstSeen).length]
]
for (const [label, value] of rows) console.log(`| ${label} | ${value} |`)
