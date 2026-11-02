// Join the spellings of one person's name at one employer, from the published people index, and
// write what was joined and what was kept apart. Run after build:salaries: npm run build:name-links.
//   public/salaries/links/<surname slice>.json.gzip  the joins the site applies, sliced as the people index
//   public/salaries/links/top.json.gzip              the joins touching the highest-paid records
//   research/salaries/name-links/decisions.csv        every decision, highest pay first, with its reason
//   research/salaries/name-links/summary.json         counts by decision and by reason
// Reviewed decisions (research/salaries/name-links/reviewed.json) override the rules either way.
import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { gunzipSync, gzipSync } from 'node:zlib'
import { findNameLinks, LINK_RULES } from '../src/salaries/nameLinks.js'
import { personKey, surnameShard } from '../src/salaries/people.js'
import { validateReviewedNameConnections } from './lib/reviewed-name-connections.mjs'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const people = join(root, 'public/salaries/people')
const research = join(root, 'research/salaries/name-links')
const gzip = (path) => JSON.parse(gunzipSync(readFileSync(path)).toString('utf8'))
const index = JSON.parse(readFileSync(join(people, 'index.json'), 'utf8'))
const reviewed = JSON.parse(readFileSync(join(research, 'reviewed.json'), 'utf8')).decisions

const rows = Object.keys(index.shards).flatMap((shard) => gzip(join(people, `${shard}.json.gzip`)))
const sourceReviewed = JSON.parse(readFileSync(join(research, 'source-reviewed.json'), 'utf8'))
reviewed.push(...validateReviewedNameConnections(sourceReviewed, rows, index))
const continuedReview = JSON.parse(readFileSync(join(research, 'continuation-reviewed.json'), 'utf8'))
reviewed.push(...validateReviewedNameConnections(continuedReview, rows, index))
const { links, decisions } = findNameLinks(rows, { years: index.years, employers: index.employers, reviewed })

const note = 'Spellings of one name at one employer joined as one person. verified: the records establish it (an extraction split, a distinctive position under both spellings, or a reviewed decision). likely: the only fuller name at the employer that agrees, never in the same period, close in time and pay. Never across employers. Each row: [employer slug, name key, disclosed name, [[alias key, disclosed alias, status, reason]]].'
// One file a surname slice, as the people index is sliced, and one of the links the highest-paid
// browse needs, so neither the browse nor a name's page loads every link.
const out = join(root, 'public/salaries/links')
rmSync(out, { recursive: true, force: true })
mkdirSync(out, { recursive: true })
const packed = (list) => gzipSync(JSON.stringify({
  note, rules: LINK_RULES,
  links: list.map((link) => [link.employer, link.key, link.name, link.aliases.map((alias) => [alias.key, alias.name, alias.status, alias.reason, ...(alias.evidence?.length ? [alias.evidence] : [])])])
}), { level: 9, mtime: 0 })
const byShard = new Map()
for (const link of links) {
  // Include the group in alias slices too, so an old misspelled URL still finds its reviewed name.
  for (const shard of new Set([link.name, ...link.aliases.map((alias) => alias.name)].map(surnameShard))) {
    if (!byShard.has(shard)) byShard.set(shard, [])
    byShard.get(shard).push(link)
  }
}
for (const [shard, list] of byShard) writeFileSync(join(out, `${shard}.json.gzip`), packed(list))
const slugOf = (at) => index.employers[at][3]
const topKeys = new Set(gzip(join(people, 'top.json.gzip')).rows.filter((row) => row[0]).map((row) => `${slugOf(row[4])}|${personKey(row[0])}`))
writeFileSync(join(out, 'top.json.gzip'), packed(links.filter((link) => [link.key, ...link.aliases.map((alias) => alias.key)].some((key) => topKeys.has(`${link.employer}|${key}`)))))

const csv = (value) => (/[",\n]/.test(String(value ?? '')) ? `"${String(value).replace(/"/g, '""')}"` : String(value ?? ''))
const sorted = [...decisions].sort((a, b) => b.pay - a.pay || a.employer.localeCompare(b.employer) || a.key.localeCompare(b.key))
writeFileSync(join(research, 'decisions.csv'), [
  'decision,employer,name,joined_to,highest_pay,reason',
  ...sorted.map((each) => [each.status, each.employer, each.name, each.target ?? '', each.pay, each.reason].map(csv).join(','))
].join('\n') + '\n')

const reasonKind = (each) => each.reason.replace(/“[^”]*”/g, '…').replace(/\d{4}(\/\d{2})?/g, '#').replace(/[\d.]+×/, 'N×').replace(/^\d+ years/, 'N years').replace(/: .*$/, '')
const count = (list, by) => Object.fromEntries([...list.reduce((map, each) => map.set(by(each), (map.get(by(each)) ?? 0) + 1), new Map())].sort((a, b) => b[1] - a[1]))
writeFileSync(join(research, 'summary.json'), JSON.stringify({
  rules: LINK_RULES,
  groups: links.length,
  decisions: count(decisions, (each) => each.status),
  reasons: { verified: count(decisions.filter((each) => each.status === 'verified'), reasonKind), likely: decisions.filter((each) => each.status === 'likely').length, apart: count(decisions.filter((each) => each.status === 'apart'), reasonKind) }
}, null, 2) + '\n')
console.log(`name links  ${links.length} groups · ${Object.entries(count(decisions, (each) => each.status)).map(([key, value]) => `${value} ${key}`).join(' · ')}`)
