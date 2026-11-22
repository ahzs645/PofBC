// Rebuild the district catalogue from reviewed research. No network access is needed.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { currentDistrictId, formerDistrictId } from '../src/schools/districtIds.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const area = resolve(root, 'research/education/school-districts')
const read = (file) => JSON.parse(readFileSync(resolve(area, file), 'utf8'))
const roster = read('roster.json')
const history = read('history.json')
const logos = read('logos.json')
const employers = read('employers.json')
const histories = new Map(history.records.map((row) => [row.number, row]))
const artwork = new Map(logos.records.map((row) => [row.number, row]))
if (roster.districts.length !== 60 || new Set(roster.districts.map((row) => row.number)).size !== 60) throw new Error('The reviewed current directory must contain 60 unique districts')
const districts = roster.districts.map((row) => {
  const record = histories.get(row.number) ?? {}
  const art = artwork.get(row.number) ?? {}
  return {
    ...row,
    id: currentDistrictId(row.number),
    current: true,
    employerSlug: employers[row.number],
    legalName: record.legalName ?? null,
    aliases: record.aliases ?? [],
    established: record.established ?? null,
    events: [...(record.events ?? []), ...(art.events ?? [])],
    notes: record.notes ?? [],
    sources: record.sources ?? [],
    assets: (art.assets ?? []).map((asset) => ({ ...asset, darkBackground: Boolean(asset.darkBackground || asset.displayBackground) })),
    logoStatus: art.status ?? 'not-reviewed',
    logoNotes: art.notes ?? '',
    logoSources: art.sources ?? []
  }
})
for (const row of districts) {
  if (!row.employerSlug) throw new Error(`SD${row.number} has no existing employer link`)
  if (row.established?.date && !row.established.sourceUrl) throw new Error(`SD${row.number} has an unsourced establishment date`)
  for (const event of row.events) if (!event.sourceUrl) throw new Error(`SD${row.number} has an unsourced history event`)
  for (const asset of row.assets) if (!asset.file || !asset.sourceUrl || !asset.sha256) throw new Error(`SD${row.number} has an incomplete asset record`)
}
const list = (value) => value ? Array.isArray(value) ? value : [value] : []
const historical = new Map((history.historical ?? []).map((row) => [formerDistrictId(row), {
  ...row, id: formerDistrictId(row), current: false, aliases: list(row.aliases),
  assets: row.assets ?? [], events: row.events ?? [], sources: row.sources ?? [], notes: list(row.notes)
}]))
const connections = new Map()
// Approval and publication are distinct events. Only the effective succession event makes an edge.
const successionTypes = new Set(['amalgamation', 'merger', 'succession', 'absorption', 'reorganization'])
const pending = [...districts, ...historical.values()]
const visited = new Set()
for (const row of pending) {
  if (visited.has(row.id)) continue
  visited.add(row.id)
  for (const event of row.events.filter((item) => successionTypes.has(item.type))) {
    for (const predecessor of event.predecessors ?? []) {
      const id = formerDistrictId(predecessor)
      const source = { title: event.sourceTitle ?? event.title, url: event.sourceUrl, locator: event.locator }
      const ended = typeof predecessor.ended === 'string' ? {
        date: predecessor.ended, precision: event.precision,
        meaning: `District abolished by ${event.sourceTitle ?? 'the cited succession instrument'}.`,
        sourceUrl: event.sourceUrl, sourceTitle: source.title, locator: event.locator
      } : predecessor.ended ?? null
      if (!historical.has(id)) {
        historical.set(id, {
        ...predecessor, id, current: false, established: predecessor.established ?? null,
        ended, aliases: list(predecessor.aliases), events: predecessor.events ?? [], assets: [],
        notes: list(predecessor.notes), sources: [...list(predecessor.sources), source]
        })
        pending.push(historical.get(id))
      }
      else {
        const previous = historical.get(id)
        previous.ended ??= ended
        if (!previous.sources.some((item) => item.url === source.url && item.locator === source.locator)) previous.sources.push(source)
      }
      const edge = { from: id, to: row.id, date: event.date, precision: event.precision, type: event.type,
        title: event.title, detail: event.detail, sourceUrl: event.sourceUrl, sourceTitle: event.sourceTitle, locator: event.locator }
      connections.set(`${id}:${row.id}:${event.date ?? ''}`, edge)
    }
  }
}
const data = { asOf: roster.asOf, directorySource: roster.sourceUrl,
  methodology: history.methodology ?? [], districts,
  historical: [...historical.values()].sort((a, b) => a.number - b.number || a.name.localeCompare(b.name)),
  connections: [...connections.values()] }
const json = JSON.stringify(data, null, 2) + '\n'
const outputs = [
  ['src/schools/districtData.js', '// Generated by scripts/build-school-districts.mjs from reviewed, source-qualified research.\nexport const SCHOOL_DISTRICT_DATA = ' + json],
  ['public/education/school-districts/catalogue.json', json]
]
for (const [path, content] of outputs) {
  const file = resolve(root, path)
  if (process.argv.includes('--check')) {
    if (readFileSync(file, 'utf8') !== content) throw new Error(`${path} is stale; run npm run build:school-districts`)
  } else {
    mkdirSync(dirname(file), { recursive: true })
    writeFileSync(file, content)
  }
}
console.log(`School districts: ${districts.length} current, ${data.historical.length} explicit historical records; ${districts.filter((row) => row.established?.date).length} establishment dates, ${districts.reduce((n, row) => n + row.assets.length, 0)} logo files.`)
