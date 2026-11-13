#!/usr/bin/env node
// Fetches BC Laws' "Acts – Ministers' Responsibilities" (AMR) collection into the repository.
//
// This is the only script in the AMR pipeline that touches the network. It walks the Content API
// tree (it cannot build document ids from a pattern: see research/legislation/bclaws-amr-feasibility.md
// §2), keeps every "Public Acts – Listed by Minister" document of every historical snapshot and of
// the current listing, and stores each as the raw HTML BC Laws served, with a manifest recording
// where and when each came from and its sha256. scripts/build-government-amr.mjs reads only what
// this leaves on disk, so builds stay offline and deterministic.
//
// With --resumes it also fetches the weekly Order in Council "Resumes" (HTML digests giving each
// OIC's approval date, and its effective date where it has one) for the years the AMR period
// sentences name, which the build uses to date changes.
//
// Usage:
//   node scripts/fetch-bclaws-amr.mjs              # AMR listings (skips documents already on disk)
//   node scripts/fetch-bclaws-amr.mjs --resumes    # and OIC Resumes
//   node scripts/fetch-bclaws-amr.mjs --resumes-only             # only the Resumés (AMR already on disk)
//   node scripts/fetch-bclaws-amr.mjs --refresh    # re-fetch documents already on disk
//
// Requests are sequential with a delay between them. TLS verification is never disabled; behind a
// proxy, Node is asked to honour HTTPS_PROXY (NODE_USE_ENV_PROXY).
//
// Licence: the AMR and OIC collections are "Licensed by: King's Printer" under the King's Printer
// Licence – British Columbia v1.1 (https://www.bclaws.gov.bc.ca/standards/Licence.html).

import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

// Native fetch ignores HTTPS_PROXY unless NODE_USE_ENV_PROXY is set at start-up; re-run with it.
if ((process.env.HTTPS_PROXY || process.env.https_proxy) && !process.env.NODE_USE_ENV_PROXY) {
  const child = spawnSync(process.execPath, [...process.execArgv, ...process.argv.slice(1)], {
    stdio: 'inherit',
    env: { ...process.env, NODE_USE_ENV_PROXY: '1', NODE_NO_WARNINGS: '1' }
  })
  process.exit(child.status ?? 1)
}

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
export const AMR_DIR = join(ROOT, 'research/legislation/amr')
const RAW_DIR = join(AMR_DIR, 'raw')
const MANIFEST = join(AMR_DIR, 'manifest.json')
const RESUME_MANIFEST = join(AMR_DIR, 'oic-resumes.json')

const BASE = 'https://www.bclaws.gov.bc.ca'
const CONTENT = (index, id) => `${BASE}/civix/content/${index}/${id ? `${id}/` : ''}`
const DOCUMENT = (index, id) => `${BASE}/civix/document/id/${index}/${id}`
const AMR_ROOT = 'amr/amr'
const DELAY_MS = 400

const args = new Set(process.argv.slice(2))
const REFRESH = args.has('--refresh')
const RESUMES = args.has('--resumes') || args.has('--resumes-only')

const sleep = (ms) => new Promise((done) => setTimeout(done, ms))
const sha256 = (text) => createHash('sha256').update(text).digest('hex')
const today = () => new Date().toISOString().slice(0, 10)

let requests = 0
const get = async (url) => {
  if (requests++) await sleep(DELAY_MS)
  for (let attempt = 1; ; attempt++) {
    try {
      const response = await fetch(url, { headers: { 'user-agent': 'pofbc-amr-importer (static research build)' } })
      if (response.status === 404) return null
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.text()
    } catch (error) {
      if (attempt >= 3) throw new Error(`${url}: ${error.message}`)
      await sleep(DELAY_MS * 5 * attempt)
    }
  }
}

const decode = (text) => text
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, '&')

/** A Content API directory listing, as [{ type, title, id, loc }]. */
const listing = async (index, id) => {
  const xml = await get(CONTENT(index, id))
  if (xml === null) throw new Error(`no listing for ${index}/${id}`)
  const entries = []
  for (const match of xml.matchAll(/<(dir|document)>([\s\S]*?)<\/\1>/g)) {
    const field = (name) => {
      const found = match[2].match(new RegExp(`<${name}>([\\s\\S]*?)</${name}>`))
      return found ? decode(found[1]).trim() : null
    }
    entries.push({ type: match[1], title: field('CIVIX_DOCUMENT_TITLE'), id: field('CIVIX_DOCUMENT_ID'), loc: field('CIVIX_DOCUMENT_LOC') })
  }
  return entries
}

const MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

/** "2026 August 31" -> "2026-08-31"; "2018 June" -> "2018-06". */
export const snapshotKey = (title) => {
  const match = String(title).trim().match(/^(\d{4})\s+([A-Za-z]+)(?:\s+(\d{1,2}))?$/)
  if (!match) return null
  const month = MONTHS.indexOf(match[2].toLowerCase()) + 1
  if (!month) return null
  return [match[1], String(month).padStart(2, '0'), match[3]?.padStart(2, '0')].filter(Boolean).join('-')
}

const safeName = (id) => String(id).replace(/[^A-Za-z0-9_.-]/g, '_')

const readJson = (path, fallback) => (existsSync(path) ? JSON.parse(readFileSync(path, 'utf8')) : fallback)

/** The "Listed by Minister" documents of one AMR folder (a historical snapshot or the current one). */
const fetchSnapshot = async ({ key, title, folderId, kind }, previous) => {
  // Usually a child of the snapshot folder; one snapshot (2023 March 31) nests the three parts one
  // folder deeper, so folders without it are searched a level down.
  const findByMinister = async (id, depth) => {
    const children = await listing(AMR_ROOT, id)
    const found = children.find((entry) => entry.type === 'dir' && /listed by minister/i.test(entry.title))
    if (found || depth <= 0) return found ?? null
    for (const child of children.filter((entry) => entry.type === 'dir' && !/listed by act/i.test(entry.title))) {
      const deeper = await findByMinister(child.id, depth - 1)
      if (deeper) return deeper
    }
    return null
  }
  const byMinister = await findByMinister(folderId, 1)
  if (!byMinister) {
    console.warn(`  ${key}: no "Listed by Minister" folder`)
    return { key, title, folderId, kind, byMinisterFolderId: null, documents: [] }
  }
  const documents = []
  for (const entry of await listing(AMR_ROOT, byMinister.id)) {
    if (entry.type !== 'document') continue
    const file = join('raw', key, `${safeName(entry.id)}.htm`)
    const path = join(AMR_DIR, file)
    const url = DOCUMENT(AMR_ROOT, entry.id)
    const known = previous?.documents.find((doc) => doc.id === entry.id)
    if (!REFRESH && known && existsSync(path)) {
      documents.push(known)
      continue
    }
    const html = await get(url)
    if (html === null) {
      console.warn(`  ${key}: ${entry.id} returned 404`)
      continue
    }
    mkdirSync(dirname(path), { recursive: true })
    writeFileSync(path, html)
    documents.push({ id: entry.id, title: entry.title, loc: entry.loc, url, file, fetched: today(), bytes: Buffer.byteLength(html), sha256: sha256(html) })
  }
  console.log(`  ${key}: ${documents.length} documents`)
  return { key, title, folderId, kind, byMinisterFolderId: byMinister.id, documents }
}

const fetchAmr = async () => {
  const manifest = readJson(MANIFEST, { snapshots: [] })
  const previous = new Map(manifest.snapshots.map((snapshot) => [snapshot.key, snapshot]))

  const top = await listing(AMR_ROOT)
  const current = top.find((entry) => entry.type === 'dir' && !/historical/i.test(entry.title))
  const historical = top.find((entry) => entry.type === 'dir' && /historical/i.test(entry.title))
  if (!current || !historical) throw new Error('unexpected AMR root listing')

  const folders = (await listing(AMR_ROOT, historical.id))
    .filter((entry) => entry.type === 'dir')
    .map((entry) => ({ key: snapshotKey(entry.title), title: entry.title, folderId: entry.id, kind: 'historical' }))
  const unparsed = folders.filter((folder) => !folder.key)
  if (unparsed.length) throw new Error(`snapshot folder titles not understood: ${unparsed.map((f) => f.title).join(', ')}`)
  folders.push({ key: 'current', title: current.title, folderId: current.id, kind: 'current' })

  const snapshots = []
  for (const folder of folders) {
    // The current listing changes in place, so it is always fetched again.
    const prior = folder.kind === 'current' ? null : previous.get(folder.key)
    snapshots.push(await fetchSnapshot(folder, prior))
  }
  snapshots.sort((a, b) => (a.kind === b.kind ? a.key.localeCompare(b.key) : a.kind === 'current' ? 1 : -1))

  const out = {
    collection: 'BC Laws — Acts and Ministers’ Responsibilities (amr)',
    contentApi: CONTENT(AMR_ROOT),
    rootFolders: { current: current.id, historical: historical.id },
    licence: 'King’s Printer Licence – British Columbia v1.1 (https://www.bclaws.gov.bc.ca/standards/Licence.html)',
    lastFetched: today(),
    note: 'Raw HTML exactly as served by the BC Laws Document API. Written by scripts/fetch-bclaws-amr.mjs.',
    snapshots
  }
  writeFileSync(MANIFEST, `${JSON.stringify(out, null, 2)}\n`)
  const total = snapshots.reduce((sum, s) => sum + s.documents.reduce((n, d) => n + d.bytes, 0), 0)
  console.log(`AMR: ${snapshots.length} snapshots, ${snapshots.reduce((n, s) => n + s.documents.length, 0)} documents, ${(total / 1e6).toFixed(1)} MB`)
}

// --- OIC Resumes -------------------------------------------------------------------------------

/** The OIC numbers ("43/2025") named in the AMR period sentences on disk. */
const namedOics = (manifest) => {
  const oics = new Set()
  for (const snapshot of manifest.snapshots) {
    for (const doc of snapshot.documents) {
      const html = readFileSync(join(AMR_DIR, doc.file), 'utf8')
      const sentence = html.match(/<p class="body">([\s\S]*?)<\/p>/i)?.[1] ?? ''
      for (const match of sentence.matchAll(/\b(\d{1,4})\/(\d{4})\b/g)) oics.add(`${Number(match[1])}/${match[2]}`)
    }
  }
  return oics
}

/** The OIC numbers a Resume lists ("ORDER IN COUNCIL 43"), for the Resume's own year. */
const oicsInResume = (html) => [...html.matchAll(/ORDER\s+IN\s+COUNCIL\s+(\d{1,4})\b/gi)].map((match) => Number(match[1]))

/**
 * Finds each wanted year's "Resumes" folder in the OIC collection (oic_cur for recent years,
 * arc_oic/<decade>/<year> before that), fetches its weekly Resumes one at a time, and keeps only
 * those that list an OIC named in an AMR period sentence. The ids of the others are recorded so a
 * re-run does not fetch them again.
 */
const fetchResumes = async () => {
  const manifest = readJson(MANIFEST, null)
  if (!manifest) throw new Error('fetch the AMR listings first')
  const wanted = namedOics(manifest)
  const years = [...new Set([...wanted].map((oic) => Number(oic.split('/')[1])))].sort()
  const prior = readJson(RESUME_MANIFEST, { documents: [], skipped: [] })
  const known = new Map(prior.documents.map((doc) => [doc.id, doc]))
  const skippedBefore = new Set(prior.skipped ?? [])
  const documents = []
  const skipped = []
  const folders = []

  const yearFolders = new Map()
  for (const entry of await listing('oic/oic_cur')) {
    if (entry.type === 'dir' && /^\d{4}$/.test(entry.title)) yearFolders.set(Number(entry.title), { index: 'oic/oic_cur', id: entry.id })
  }
  for (const decade of await listing('oic/arc_oic')) {
    const span = decade.title.match(/^(\d{4})\s*-\s*(\d{4})$/)
    if (decade.type !== 'dir' || !span) continue
    if (!years.some((year) => year >= Number(span[1]) && year <= Number(span[2]) && !yearFolders.has(year))) continue
    for (const entry of await listing('oic/arc_oic', decade.id)) {
      if (entry.type === 'dir' && /^\d{4}$/.test(entry.title) && !yearFolders.has(Number(entry.title))) {
        yearFolders.set(Number(entry.title), { index: 'oic/arc_oic', id: entry.id })
      }
    }
  }

  for (const year of years) {
    const folder = yearFolders.get(year)
    if (!folder) {
      folders.push({ year, resumesFolderId: null, note: 'no year folder found' })
      continue
    }
    const resumes = (await listing(folder.index, folder.id)).find((entry) => entry.type === 'dir' && /resume/i.test(entry.title))
    folders.push({ year, index: folder.index, yearFolderId: folder.id, resumesFolderId: resumes?.id ?? null })
    if (!resumes) continue
    const wantedHere = new Set([...wanted].filter((oic) => oic.endsWith(`/${year}`)).map((oic) => Number(oic.split('/')[0])))
    for (const entry of await listing(folder.index, resumes.id)) {
      if (entry.type !== 'document') continue
      const had = known.get(entry.id)
      if (!REFRESH && had && existsSync(join(AMR_DIR, had.file))) {
        documents.push(had)
        continue
      }
      if (!REFRESH && skippedBefore.has(entry.id)) {
        skipped.push(entry.id)
        continue
      }
      const url = DOCUMENT(folder.index, entry.id)
      const html = await get(url)
      if (html === null) continue
      const listed = oicsInResume(html)
      if (!listed.some((number) => wantedHere.has(number))) {
        skipped.push(entry.id)
        continue
      }
      const file = join('oic-resumes', String(year), `${safeName(entry.id)}.htm`)
      mkdirSync(dirname(join(AMR_DIR, file)), { recursive: true })
      writeFileSync(join(AMR_DIR, file), html)
      documents.push({ id: entry.id, year, title: entry.title, url, file, fetched: today(), bytes: Buffer.byteLength(html), sha256: sha256(html) })
    }
    console.log(`  ${year}: ${documents.filter((doc) => doc.year === year).length} Resumes kept`)
  }
  documents.sort((a, b) => a.id.localeCompare(b.id, 'en', { numeric: true }))
  writeFileSync(RESUME_MANIFEST, `${JSON.stringify({
    collection: 'BC Laws — Orders in Council, weekly Resumés',
    licence: 'King’s Printer Licence – British Columbia v1.1 (https://www.bclaws.gov.bc.ca/standards/Licence.html)',
    lastFetched: today(),
    note: 'Only Resumés listing an OIC named in an AMR period sentence are kept. Written by scripts/fetch-bclaws-amr.mjs --resumes.',
    years,
    folders,
    documents,
    skipped: skipped.sort()
  }, null, 2)}\n`)
  console.log(`Resumes: ${documents.length} kept, ${skipped.length} not needed`)
}

const main = async () => {
  mkdirSync(RAW_DIR, { recursive: true })
  if (!args.has('--resumes-only')) await fetchAmr()
  if (RESUMES) await fetchResumes()
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error)
    process.exit(1)
  })
}
