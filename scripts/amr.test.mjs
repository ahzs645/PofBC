// The AMR importer against vendored BC Laws pages (research/legislation/amr/raw, oic-resumes).
//
// These pin the readings that matter most: the period sentence in both wordings, a row's statreg
// link and details, a renamed Act kept as one Act, the February 2025 consumer-protection move
// dated from OIC 43/2025, and that a listing period is never passed off as an effective date.

import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { test } from 'node:test'
import { fileURLToPath } from 'node:url'
import {
  dateGap, diffListings, indexResumes, keyActs, parseAmrPage, parsePeriod, parseResume, titleKey
} from './lib/amr.mjs'
import { assemble, loadListings, loadResumeIndex } from './build-government-amr.mjs'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const AMR = join(ROOT, 'research/legislation/amr')
const manifest = JSON.parse(readFileSync(join(AMR, 'manifest.json'), 'utf8'))
const resumes = JSON.parse(readFileSync(join(AMR, 'oic-resumes.json'), 'utf8'))

const page = (key, idPart) => {
  const doc = manifest.snapshots.find((s) => s.key === key).documents.find((d) => d.id.includes(idPart))
  return parseAmrPage(readFileSync(join(AMR, doc.file), 'utf8'))
}
const resumeEntries = (id) => {
  const doc = resumes.documents.find((d) => d.id === id)
  return parseResume(readFileSync(join(AMR, doc.file), 'utf8'), { id: doc.id, url: doc.url })
}

test('period sentence: "for the period" wording, 2015', () => {
  const { period } = page('2015-12', 'hlth')
  assert.equal(period.wording, 'period')
  assert.equal(period.periodFrom, '2015-12-16')
  assert.equal(period.periodTo, '2016-06-22')
  assert.deepEqual(period.baseOics, ['233/2013'])
  assert.deepEqual(period.amendingOics, ['368/2014', '472/2015', '493/2015', '587/2015', '772/2015', '773/2015'])
})

test('period sentence: the 2024-11-18 "as at" wording', () => {
  const { period, ministers } = page('2024-11-18', 'hlth')
  assert.equal(period.wording, 'as-at')
  assert.equal(period.periodFrom, '2024-11-18')
  assert.equal(period.periodTo, '2024-11-18')
  assert.deepEqual(period.baseOics, ['596/2024'])
  assert.deepEqual(period.amendingOics, [])
  assert.ok(period.parsed)
  // This snapshot carries no statreg links.
  assert.ok(ministers[0].rows.every((row) => row.statregId === null))
})

test('period sentence: two base orders, each with amendments', () => {
  const period = parsePeriod('This page contains information for the period April 1, 2022 to May 26, 2022. The information is from Order in Council 602/2020, as amended by Orders in Council 30/2021, 404/2021 and 2/2022, and by Order in Council 92/2022, as amended by Order in Council 199/2022.')
  assert.deepEqual(period.baseOics, ['602/2020', '92/2022'])
  assert.deepEqual(period.amendingOics, ['30/2021', '404/2021', '2/2022', '199/2022'])
  assert.equal(period.periodFrom, '2022-04-01')
})

test('rows: statreg link, details text and scope', () => {
  const health = page('2026-08-31', 'hlth')
  assert.equal(health.ministers.length, 1)
  assert.equal(health.ministers[0].ministerTitle, 'Minister of Health')
  const rows = health.ministers[0].rows
  const hospital = rows.find((row) => row.actTitle === 'Hospital')
  assert.equal(hospital.statregId, '96200_01')
  assert.equal(hospital.scope, 'partial')
  assert.match(hospital.detailsRaw, /^The Act except sections 2 \(3\), 42\.2 \(3\) \(c\)/)
  const hpoa = rows.find((row) => row.statregId === '22043')
  assert.equal(hpoa.actTitle, 'Health Professions and Occupations')
  assert.equal(hpoa.detailsRaw.split('\n').length, 3)
  const anatomy = rows.find((row) => row.actTitle === 'Anatomy')
  assert.equal(anatomy.detailsRaw, '')
  assert.equal(anatomy.scope, 'whole')
  // An unclosed <tr> (Forensic Psychiatry) does not swallow the next row.
  assert.ok(rows.some((row) => row.actTitle === 'Public Health'))
  assert.equal(page('2026-08-31', 'prem').ministers[0].ministerTitle, 'Premier')
})

test('rows: titles keyed loosely for matching', () => {
  assert.equal(titleKey('Citizens’ Services Act'), titleKey("Citizens' Services"))
})

// Neither snapshot carries statreg links (BC Laws added them in 2025-11-24), so Acts are keyed
// across every listing, with the hand-checked aliases, as the build does.
const aliases = JSON.parse(readFileSync(join(AMR, 'act-aliases.json'), 'utf8')).aliases
let keyed = null
const consumerGap = () => {
  if (!keyed) {
    keyed = loadListings().listings
    keyActs(keyed, aliases)
  }
  const before = keyed.find((l) => l.id === '2025-01-31')
  const after = keyed.find((l) => l.id === '2025-05-29')
  return { before, after, diff: diffListings(before, after) }
}

test('diff: a renamed Act with the same statreg id is a retitle, not a reassignment', () => {
  const { diff } = consumerGap()
  const retitle = diff.find((change) => change.type === 'retitled' && /Short-Term Holding/.test(change.toTitle))
  assert.ok(retitle, 'retitle found')
  assert.equal(retitle.statregId, '24014')
  assert.match(retitle.fromTitle, /^Budget Measures Implementation/)
  assert.ok(!diff.some((change) => change.statregId === retitle.statregId && change.type !== 'retitled'), 'not also moved, added or removed')
})

test('diff: statreg-keyed — a retitle is not a move, a move is not a retitle', () => {
  const rows = (pairs) => pairs.map(([ministerTitle, actTitle, statregId]) => ({ ministerTitle, actTitle, statregId, detailsRaw: '', scope: 'whole' }))
  const before = { id: 'a', rows: rows([['Minister of Finance', 'Old Name', '1'], ['Minister of Health', 'Stays Put', '2']]) }
  const after = { id: 'b', rows: rows([['Minister of Finance', 'New Name', '1'], ['Minister of Labour', 'Stays Put', '2']]) }
  keyActs([before, after])
  const diff = diffListings(before, after)
  assert.deepEqual(diff.map((change) => [change.type, change.statregId]).sort(), [['moved', '2'], ['retitled', '1']])
  // Without the links, the same rename reads as one Act removed and another added.
  const unlinked = (listing) => ({ ...listing, rows: listing.rows.map((row) => ({ ...row, statregId: null, actKey: undefined })) })
  const b2 = unlinked(before)
  const a2 = unlinked(after)
  keyActs([b2, a2])
  assert.deepEqual(diffListings(b2, a2).map((change) => change.type).sort(), ['added', 'moved', 'removed'])
})

test('rows: a multi-part link and a repeal note do not split an Act', () => {
  const html = '<title>Minister of Finance - Statute Administration</title><table><tr><th COLSPAN="2">MINISTER OF FINANCE</th></tr>'
    + '<tr><td><a href="/civix/document/id/complete/statreg/96141_00_multi">Financial Institutions</a></td><td>&nbsp;</td></tr>'
    + '<tr><td><a href="/civix/document/id/complete/statreg/96313_01">Mortgage Brokers [Repealed by the Mortgage Services Act, S.B.C. 2022, c. 27, s. 86.]</a></td><td>&nbsp;</td></tr></table>'
  const [minister] = parseAmrPage(html).ministers
  assert.equal(minister.rows[0].statregId, '96141_00')
  assert.equal(minister.rows[1].actTitle, 'Mortgage Brokers')
  assert.match(minister.rows[1].annotation, /^Repealed by/)
})

test('diff: consumer-protection Acts move from Public Safety to the Attorney General', () => {
  const { diff } = consumerGap()
  const moved = diff.filter((change) => change.type === 'moved'
    && change.from === 'Minister of Public Safety and Solicitor General' && change.to === 'Attorney General and Deputy Premier')
  const acts = moved.map((change) => change.act)
  assert.ok(acts.includes('Business Practices and Consumer Protection'))
  assert.ok(acts.includes('Motor Dealer'))
  assert.ok(moved.length >= 5)
})

test('dating: the 2025-01-31 → 2025-05-29 move takes OIC 43/2025’s effective date', () => {
  const { before, after, diff } = consumerGap()
  const entries = resumes.documents.filter((d) => d.year === 2025).flatMap((d) => resumeEntries(d.id))
  const oic43 = entries.find((entry) => entry.oic === '43/2025')
  assert.equal(oic43.approved, '2025-01-30')
  assert.equal(oic43.effective, '2025-02-01')
  const gap = dateGap(before, after, diff, { resumeIndex: indexResumes(entries), manual: {} })
  assert.deepEqual(gap.candidateOics, ['43/2025'])
  assert.equal(gap.status, 'dated')
  const bpcpa = gap.changes.find((change) => change.act === 'Business Practices and Consumer Protection' && change.type === 'moved')
  assert.equal(bpcpa.effectiveDate, '2025-02-01')
  assert.equal(bpcpa.dateKind, 'effective')
  assert.equal(bpcpa.approvedDate, '2025-01-30')
  assert.equal(bpcpa.oic, '43/2025')
  assert.equal(bpcpa.basis, 'oic-resume')
  assert.match(bpcpa.source, /bclaws\.gov\.bc\.ca\/civix\/document\/id\/oic\//)
  assert.deepEqual(bpcpa.betweenListings, ['2025-01-31', '2025-05-29'])
  // Neither listing period is the effective date.
  assert.notEqual(bpcpa.effectiveDate, after.periodFrom)
  assert.equal(after.periodFrom, '2024-11-18')
  // A retitle is never dated.
  assert.ok(gap.changes.filter((change) => change.type === 'retitled').every((change) => change.effectiveDate === null))
})

test('dating: without OIC dates nothing is dated, whatever the listing periods say', () => {
  const { listings } = loadListings()
  const result = assemble({ listings, resumeIndex: new Map(), manual: {}, crosswalk: [] })
  assert.ok(result.changes.length > 0)
  assert.ok(result.changes.every((change) => change.effectiveDate === null))
  for (const assignment of result.assignments) {
    assert.equal(assignment.effectiveFrom.date, null)
    assert.equal(assignment.effectiveTo?.date ?? null, null)
  }
})

test('dating: every date in the full build comes from one OIC, never from a listing', () => {
  const { listings } = loadListings()
  const { index } = loadResumeIndex()
  const result = assemble({ listings, resumeIndex: index, manual: {}, crosswalk: [] })
  const dated = result.changes.filter((change) => change.effectiveDate)
  assert.ok(dated.length > 0)
  for (const change of dated) {
    assert.ok(['oic-resume', 'oic-checked'].includes(change.basis))
    assert.equal(change.candidateOics.length, 1)
    assert.equal(change.oic, change.candidateOics[0])
    assert.ok(change.source)
    assert.ok(['effective', 'approved'].includes(change.dateKind))
  }
  for (const assignment of result.assignments) {
    for (const boundary of [assignment.effectiveFrom, assignment.effectiveTo]) {
      if (boundary?.date) assert.ok(['oic-resume', 'oic-checked'].includes(boundary.basis) && boundary.oic)
    }
  }
})

test('dating: an effective date that covers only part of an order does not date the gap', () => {
  const entries = indexResumes([{ oic: '1/2030', approved: '2030-01-10', effective: '2030-02-01', effectiveCandidates: ['2030-02-01'], summary: '(a) OIC 9/2029 is amended as set out in Schedule 1, and (b) effective February 1, 2030, as set out in Schedule 2.' }])
  const before = { id: 'a', periodTo: '2030-01-05', oics: [] }
  const after = { id: 'b', periodTo: '2030-03-01', oics: ['1/2030'] }
  const gap = dateGap(before, after, [{ type: 'moved', act: 'X', actKey: 'statreg:1', from: 'A', to: 'B' }], { resumeIndex: entries, manual: {} })
  assert.equal(gap.status, 'oic-undated')
  assert.equal(gap.undatedReason, 'effective-date-covers-part')
  assert.equal(gap.changes[0].effectiveDate, null)
})

test('crosswalk: date-aware, and the repeated Public Safety title maps to the 2017 episode only', async () => {
  const { crosswalkLookup } = await import('./lib/amr.mjs')
  const { MINISTRY_EPISODES } = await import('../src/government/episodes.js')
  const crosswalk = JSON.parse(readFileSync(join(AMR, 'crosswalk.json'), 'utf8')).entries
  const ids = new Set(MINISTRY_EPISODES.map((episode) => episode.id))
  for (const entry of crosswalk) if (entry.episodeId) assert.ok(ids.has(entry.episodeId), entry.episodeId)
  const pssg = 'Minister of Public Safety and Solicitor General'
  assert.equal(crosswalkLookup(crosswalk, pssg, '2018-07-12').entry.episodeId, 'ministry-of-public-safety-and-solicitor-general-2017')
  assert.equal(crosswalkLookup(crosswalk, pssg, '2016-06-23').status, 'unmapped')
  assert.equal(crosswalkLookup(crosswalk, 'Premier', '2025-05-29').status, 'unmapped')
  assert.equal(crosswalkLookup(crosswalk, 'Minister of Education', '2022-05-26').status, 'missing')
})

test('generated data: effective dates only from OICs, and the helpers find what they should', async () => {
  const { AMR_CHANGES, AMR_LISTINGS, AMR_SOURCE } = await import('../src/government/amrData.js')
  const { assignmentsOfEpisode, ministersOfAct } = await import('../src/government/amr.js')
  const { AMR_ATTRIBUTION } = await import('../src/government/amrLicence.js')
  assert.equal(AMR_SOURCE.attribution, AMR_ATTRIBUTION)
  assert.match(AMR_ATTRIBUTION, /THESE MATERIALS ARE NOT AN OFFICIAL VERSION\.$/)
  for (const change of AMR_CHANGES) {
    if (change.effectiveDate === null) continue
    assert.ok(['oic-resume', 'oic-checked'].includes(change.basis), JSON.stringify(change))
    assert.ok(change.oic && change.source)
  }
  // Listings carry periods, never effective dates.
  for (const listing of AMR_LISTINGS) assert.ok(!('effectiveDate' in listing) && !('effectiveFrom' in listing))
  const bpcpa = AMR_CHANGES.find((change) => change.act === 'Business Practices and Consumer Protection' && change.type === 'moved' && change.oic === '43/2025')
  assert.equal(bpcpa.effectiveDate, '2025-02-01')
  assert.equal(bpcpa.toEpisodeId, 'ministry-of-attorney-general-2017')
  assert.equal(bpcpa.fromEpisodeId, 'ministry-of-public-safety-and-solicitor-general-2017')
  const health = assignmentsOfEpisode('ministry-of-health-2011')
  assert.ok(health.some((assignment) => assignment.act.statregId === '96200_01'))
  const hospital = ministersOfAct('96200_01')
  assert.ok(hospital.length >= 1 && hospital.every((assignment) => assignment.act.statregId === '96200_01'))
})
