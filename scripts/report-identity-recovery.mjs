#!/usr/bin/env node
// Compare the fixed acquisition baseline with actual owner-resolved gallery coverage.
// These reports describe held evidence; they never claim a complete identity history.
import assert from 'node:assert/strict'
import fs from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { IDENTITY_COVERAGE, COVERAGE_FAMILIES, coverageSummary } from '../src/gallery/identityCoverage.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const directory = resolve(root, 'research/identity/missing-recovery-2026-11-20')
const read = (file) => JSON.parse(fs.readFileSync(resolve(directory, file), 'utf8'))
const write = (file, value) => fs.writeFileSync(resolve(directory, file), typeof value === 'string' ? value : JSON.stringify(value, null, 2) + '\n')
const before = read('coverage-before.json')
const manifest = read('assets-manifest.json')
const outcomes = fs.existsSync(resolve(directory, 'research-outcomes.json')) ? read('research-outcomes.json') : { subjects: [] }
const notes = new Map(outcomes.subjects.map((subject) => [subject.id, subject]))
const old = new Map(before.subjects.map((subject) => [subject.id, subject]))
const current = new Map(IDENTITY_COVERAGE.map((subject) => [subject.id, subject]))
assert.deepEqual([...current.keys()].sort(), [...old.keys()].sort(), 'Acquisition must preserve the declared subject scope')
for (const subject of before.subjects.filter((subject) => subject.hasArtwork)) {
  assert.equal(current.get(subject.id).hasArtwork, true, `Previously held artwork lost: ${subject.id}`)
}
for (const body of manifest.bodies) {
  assert.equal(old.get(body.id)?.hasArtwork, false, `Recovery does not fill a baseline gap: ${body.id}`)
  assert.equal(current.get(body.id)?.hasArtwork, true, `Recovered owner is not held: ${body.id}`)
}
const acquired = IDENTITY_COVERAGE.filter((subject) => subject.hasArtwork && !old.get(subject.id).hasArtwork)
assert.equal(acquired.length, manifest.bodies.length, 'Every newly held subject must have its own acquisition record')
const assets = manifest.bodies.flatMap((body) => body.assets)
const families = COVERAGE_FAMILIES.map((family) => {
  const initial = before.subjects.filter((subject) => subject.family === family.id)
  const now = IDENTITY_COVERAGE.filter((subject) => subject.family === family.id)
  const heldBefore = initial.filter((subject) => subject.hasArtwork).length
  const heldAfter = now.filter((subject) => subject.hasArtwork).length
  return { id: family.id, label: family.label, subjects: now.length, heldBefore, heldAfter, recovered: heldAfter - heldBefore, missing: now.length - heldAfter }
})
const formats = Object.fromEntries([...new Set(assets.map((asset) => asset.format))].sort().map((format) => [format, assets.filter((asset) => asset.format === format).length]))
const summary = {
  baselineCommit: before.baseCommit, observedDate: manifest.observedDate, observationTimezone: manifest.observationTimezone,
  ...(manifest.followUpObservedDate ? { followUpObservedDate: manifest.followUpObservedDate } : {}),
  before: { ...before.summary, missing: before.summary.subjects - before.summary.held },
  after: { ...coverageSummary(), missing: IDENTITY_COVERAGE.filter((subject) => !subject.hasArtwork).length },
  recoveredSubjects: acquired.length, artworkFiles: assets.length,
  vectorFiles: assets.filter((asset) => asset.isVector).length, rasterFiles: assets.filter((asset) => !asset.isVector).length,
  formats, retainedSourceRecords: manifest.sources.length, reproducibleExtractions: manifest.extractions.length, families
}
write('coverage-summary.json', summary)
write('coverage-after.json', { baselineCommit: before.baseCommit, summary: summary.after, subjects: IDENTITY_COVERAGE.map((subject) => ({
  id: subject.id, label: subject.label, family: subject.family, state: subject.state, hasArtwork: subject.hasArtwork,
  evidence: subject.evidence, entryIds: subject.entries.map((entry) => entry.id), nextAction: subject.nextAction
})) })
const remaining = IDENTITY_COVERAGE.filter((subject) => !subject.hasArtwork).map((subject) => ({
  id: subject.id, label: subject.label, family: subject.family, state: subject.state, nextAction: subject.nextAction,
  sources: subject.sources, ...(notes.get(subject.id) ?? {}),
  ...(subject.family === 'atlas-health' ? { researchScope: 'Historical council/board remains in the declared register. The focused archival checks described in research-outcomes.json are not an exhaustive search for every council.' } : {})
}))
write('remaining-gaps.json', { observedDate: manifest.followUpObservedDate ?? manifest.observedDate, missingSubjects: remaining.length, subjects: remaining })
const md = (value) => String(value ?? '').replace(/\|/g, '\\|').replace(/\n/g, ' ')
write('remaining-gaps.md', `# Remaining identity gaps\n\n${remaining.length} registered subjects still have no accepted artwork after this acquisition. These include shared or unconfirmed identities, not just missing download files. A parent or successor logo does not fill a subject's gap.\n\nThe [research outcomes](research-outcomes.json) identify which sources were actually inspected. The historical health group remains an archival research queue; no exhaustive search of every council is claimed.\n\n| Subject | Family | Evidence state | Remaining work / inspected outcome |\n|---|---|---|---|\n${remaining.map((subject) => `| ${md(subject.label)} | ${md(subject.family)} | ${md(subject.state)} | ${md(subject.reason ?? subject.outcome ?? subject.nextAction)} |`).join('\n')}\n`)
write('acquired-identities.md', `# Acquired identities\n\n${acquired.length} previously missing subjects now hold ${assets.length} artwork files (${summary.vectorFiles} native vectors and ${summary.rasterFiles} raster specimens). More than one file can belong to the same subject. A held specimen does not establish all eras, all colourways, an adoption date, or permission to use the mark.\n\nFull hashes, source locators, date qualifications, dimensions and extraction recipes are in [assets-manifest.json](assets-manifest.json).\n\n| Subject | Artwork | Format | Primary source |\n|---|---|---|---|\n${manifest.bodies.flatMap((body) => body.assets.map((asset) => `| ${md(body.shortName)} | [${md(asset.label)}](../../../public/${asset.file}) | ${asset.format.toUpperCase()}${asset.isVector ? ' · native vector' : ' · raster'} | [Source](${asset.sourceUrl}) |`)).join('\n')}\n`)
console.log(`Recovery report: ${summary.before.held} → ${summary.after.held} held; ${summary.recoveredSubjects} gaps filled, ${summary.after.missing} remain; ${summary.artworkFiles} artwork files.`)
