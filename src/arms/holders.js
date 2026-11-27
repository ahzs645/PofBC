// The register's other holders: the Crown's offices, universities and colleges, public bodies and
// local governments in British Columbia, from the Canadian Heraldic Authority's public register.
//
// The records are read from research/identity/arms-register-2026-11-16/register.json, as collected
// (every project page of the register, kept where the recipient is a civil institution in B.C.).
// The artwork is the 16 November 2026 acquisition (research/identity/arms-acquisition-2026-11-16),
// indexed by scripts/build-arms-artwork.py into ./artwork.json with a display copy of each file in
// ./artwork/. That index also says which register entries belong to one holder (a district that
// became a city keeps one page) and which picture leads its page. This file adds only what neither
// can: a short name and id, and the holder's pages elsewhere on this site.

import register from '../../research/identity/arms-register-2026-11-16/register.json' with { type: 'json' }
import acquisition from './artwork.json' with { type: 'json' }
import { MUNICIPAL_PROFILE_BY_REGISTER } from '../salaries/municipalProfiles.js'

export const REGISTER_DIR = 'research/identity/arms-register-2026-11-16'
export const ACQUISITION_DIR = acquisition.source

// Per holder, keyed by the register's name. `salaries` is an employer slug, `subject` a gallery
// identity subject; both are checked against the site's data by the tests.
const EXTRAS = {
  'Lieutenant Governor of British Columbia': {
    id: 'lieutenant-governor',
    image: { file: 'lieutenant-governor-flag.svg', alt: 'Flag of office', credit: 'Denelson83, Wikimedia Commons · public domain', page: 'https://commons.wikimedia.org/wiki/File:Flag_of_the_Lieutenant-Governor_of_British_Columbia.svg' }
  },
  'The University of British Columbia': {
    id: 'university-of-british-columbia',
    name: 'University of British Columbia',
    salaries: 'university-of-bc',
    subject: 'university-of-british-columbia',
    artwork: [{ id: 'commons-ubc-shield', file: 'ubc-shield.svg', title: 'Shield of the University of British Columbia', kind: 'shield', date: '1915 arms', author: 'Unknown, from an idea of UBC’s first president Frank F. Wesbrook · Wikimedia Commons', licence: 'Public domain', page: 'https://commons.wikimedia.org/wiki/File:British_columbia_univ_coat_arms.svg' }]
  },
  'Faculty of Law, University of British Columbia': { id: 'ubc-faculty-of-law', name: 'UBC Faculty of Law' },
  'Green College, University of British Columbia': { id: 'ubc-green-college', name: 'Green College, UBC' },
  'University of Victoria': {
    id: 'university-of-victoria',
    salaries: 'university-of-victoria',
    subject: 'university-of-victoria',
    artwork: [{ id: 'commons-uvic-shield', file: 'uvic-shield.png', title: 'Shield of the University of Victoria', kind: 'shield', date: '2001 registration', author: 'Robin S. Taylor · Wikimedia Commons', licence: 'CC BY-SA 4.0', licenceUrl: 'https://creativecommons.org/licenses/by-sa/4.0/', page: 'https://commons.wikimedia.org/wiki/File:University_of_Victoria_Escutcheon.png' }]
  },
  'Simon Fraser University': {
    id: 'simon-fraser-university',
    salaries: 'simon-fraser-university',
    subject: 'simon-fraser-university'
  },
  'University of Northern British Columbia': {
    id: 'university-of-northern-bc',
    salaries: 'university-of-northern-bc',
    subject: 'university-of-northern-bc'
  },
  'Royal Roads University': {
    id: 'royal-roads-university',
    salaries: 'royal-roads-university'
  },
  'Thompson Rivers University': { id: 'thompson-rivers-university', salaries: 'thompson-rivers-university' },
  'Vancouver Island University': {
    id: 'vancouver-island-university',
    salaries: 'vancouver-island-university'
  },
  'Kwantlen Polytechnic University': { id: 'kwantlen-polytechnic-university', salaries: 'kwantlen-polytechnic-university' },
  'Emily Carr University of Art and Design': { id: 'emily-carr-university', salaries: 'emily-carr-university' },
  'Capilano University': { id: 'capilano-university', salaries: 'capilano-university' },
  'University of the Fraser Valley': { id: 'university-of-the-fraser-valley', salaries: 'university-of-the-fraser-valley' },
  'British Columbia Institute of Technology': { id: 'bcit', salaries: 'bcit', subject: 'bcit' },
  'Justice Institute of British Columbia': { id: 'justice-institute-of-bc', salaries: 'justice-institute-of-bc' },
  'College of the Rockies': { id: 'college-of-the-rockies', salaries: 'college-of-the-rockies' },
  'College of New Caledonia': { id: 'college-of-new-caledonia', salaries: 'college-of-new-caledonia' },
  'Okanagan College': { id: 'okanagan-college', salaries: 'okanagan-college' },
  'Langara College': { id: 'langara-college', salaries: 'langara-college' },
  'British Columbia Sheriff Service': { id: 'bc-sheriff-service', name: 'B.C. Sheriff Service' },
  'Conservation Officer Service (British Columbia)': { id: 'conservation-officer-service', name: 'Conservation Officer Service' },
  'South Coast British Columbia Transportation Authority Police Service': {
    id: 'metro-vancouver-transit-police',
    name: 'Metro Vancouver Transit Police',
    salaries: 'metro-vancouver-transit-police',
    subject: 'metro-vancouver-transit-police'
  },
  'Vancouver Police Department': { id: 'vancouver-police', salaries: 'vancouver-police' },
  'Victoria Police Department': { id: 'victoria-police', salaries: 'victoria-police' },
  'Surrey Police Service': { id: 'surrey-police', salaries: 'surrey-police' },
  'Saanich Police Department': { id: 'saanich-police', salaries: 'saanich-police' },
  'New Westminster Police Department': { id: 'new-westminster-police', salaries: 'new-west-police' },
  'Port Moody Police Department': { id: 'port-moody-police', salaries: 'port-moody-police' },
  'Central Saanich Police Service': { id: 'central-saanich-police', salaries: 'central-saanich-police' },
  'Nelson Police Department': { id: 'nelson-police', salaries: 'nelson-police' },
  'West Vancouver Police Department': { id: 'west-vancouver-police' },
  'Delta Police Department': { id: 'delta-police', salaries: 'delta-police' },
  'Engineers and Geoscientists British Columbia': { id: 'engineers-and-geoscientists-bc' }
}

const PROVINCE_NAME = 'Province of British Columbia'

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
/** 2015-10-15 → 15 October 2015. */
export const longDate = (iso) => {
  const [year, month, day] = String(iso ?? '').split('-').map(Number)
  if (!year) return null
  if (!month) return String(year)
  return `${day ? `${day} ` : ''}${MONTHS[month - 1]} ${year}`
}

const capital = (text) => text.charAt(0).toUpperCase() + text.slice(1)

// The register's element names, as this site's blazon rows call them.
const BLAZON_KEYS = { shield: 'arms', crest: 'crest', supporters: 'supporters', motto: 'motto', motto_2: 'motto', badge: 'badge', flag: 'flag' }
const byElement = (record) => {
  const out = {}
  for (const [key, text] of Object.entries(record ?? {})) {
    const target = BLAZON_KEYS[key] ?? key
    if (text) out[target] = out[target] ? `${out[target]} ${text}` : text
  }
  return out
}

/**
 * The year the holder first bore these emblems: the register's date, or an earlier College of Arms
 * or Lord Lyon record, or a Governor General's approval, where the register's notes give one.
 */
export const firstYear = (entry) => {
  const registered = Number(entry.date?.slice(0, 4))
  const earlier = [...String(entry.register_notes ?? '').matchAll(/\b(1[89]\d\d|20\d\d)\b/g)].map((match) => Number(match[1]))
  return Math.min(registered, ...earlier.filter((year) => year < registered))
}

const sourceTitle = (url) => {
  const { hostname, pathname } = new URL(url)
  if (hostname === 'www.gg.ca') return 'Canadian Heraldic Authority: public register'
  const file = decodeURIComponent(pathname.split('/').filter(Boolean).at(-1) ?? '')
  return file ? `${hostname.replace(/^www\./, '')}: ${file}` : hostname.replace(/^www\./, '')
}

// The acquisition's artwork records, as the view shows them. `image` is the display copy in
// ./artwork/; `original` is the unchanged file under the acquisition's assets/.
const artworkItem = (id) => {
  const item = acquisition.artwork[id]
  return item ? { id, ...item } : null
}

const acquiredByRegisterUrl = new Map(acquisition.holders.flatMap((held) => held.registerUrls.map((url) => [url, held])))

/** The holder's lead picture: the acquisition's choice, else a file in ./images/. */
const leadImage = (held, extra) => {
  const lead = held?.primary ? artworkItem(held.primary) : null
  if (lead) return { artwork: lead.id, alt: held.primaryAlt ?? null, credit: [lead.author, lead.licence].filter(Boolean).join(' · '), page: lead.page }
  return extra.image ?? null
}

const artworkFor = (held, extra) => [
  ...(held?.artwork ?? []).map(artworkItem).filter(Boolean),
  ...(extra.artwork ?? [])
]

/**
 * Municipal register mottoes carry the register's gloss in the same field ('SALUS ET OPES. This
 * Latin phrase means "Health and wealth".'); the motto is the text before it.
 */
export const motto = (entry) => {
  if (!entry.motto) return null
  const [, text, gloss] = entry.motto.match(/^(.*?)[.;]?\s*\*?\s*(This Latin phrase .*)?$/s)
  const meaning = gloss?.match(/means\s+"([^"]+)"/)?.[1] ?? null
  return {
    text: text.trim(),
    translation: entry.motto_translation ?? meaning,
    note: gloss && !meaning ? gloss.replace(/^This Latin phrase/, 'The motto') : null
  }
}

const holder = (entry) => {
  const extra = EXTRAS[entry.name] ?? {}
  const held = acquiredByRegisterUrl.get(entry.register_url)
  const links = []
  if (extra.subject) links.push({ label: 'Open in the register', to: { view: 'gallery', subject: extra.subject } })
  if (extra.salaries) links.push({ label: 'Open in Salaries', to: { view: 'salaries', employer: extra.salaries } })
  return {
    id: extra.id,
    name: extra.name ?? entry.common_name ?? entry.name,
    registerName: entry.register_name ?? entry.name,
    group: entry.group,
    year: String(firstYear(entry)),
    registered: entry.registered.map(capital),
    grantedLabel: 'In the register',
    granted: `${entry.letters_patent}, ${longDate(entry.date)}`,
    motto: motto(entry),
    description: entry.description ?? null,
    // The register's own notes; the research notes stay in register.json.
    note: entry.register_notes ?? null,
    blazon: byElement(entry.blazon),
    symbolism: byElement(entry.register_symbolism),
    register: { url: entry.register_url, volume: entry.register?.text ?? null },
    related: (entry.related_register_entries ?? []).map((related) => ({
      title: `${related.register_name}: ${related.letters_patent}, ${longDate(related.date)}`,
      url: related.register_url,
      relation: related.relation ?? null
    })),
    image: leadImage(held, extra),
    artwork: artworkFor(held, extra),
    links,
    sources: (entry.sources ?? []).map((url) => ({ title: sourceTitle(url), url }))
  }
}

const entries = register.entries

/** The Province's own register record, merged into its page by armsData.js. */
export const PROVINCE_REGISTER = (() => {
  const entry = entries.find(({ name }) => name === PROVINCE_NAME)
  return entry
    ? { blazon: byElement(entry.blazon), symbolism: byElement(entry.register_symbolism), register: { url: entry.register_url, volume: entry.register?.text ?? null }, granted: `${entry.letters_patent}, ${longDate(entry.date)}`, note: entry.register_notes }
    : null
})()

const GROUP_ORDER = ['crown', 'post-secondary', 'public-body']

export const HOLDERS = entries
  .filter(({ name, group }) => name !== PROVINCE_NAME && GROUP_ORDER.includes(group))
  .map(holder)
  .sort((a, b) => GROUP_ORDER.indexOf(a.group) - GROUP_ORDER.indexOf(b.group) || a.name.localeCompare(b.name))

// "The Corporation of the City of Penticton" → "City of Penticton", filed under Penticton.
const placeName = (name) => name
  .replace(/^Municipal Council of the /, '')
  .replace(/^(The )?Corporation of (the )?/, '')
  .replace(/^The /, '')
const fileUnder = (name) => name.replace(/^(City|District|Town|Township|Village|Resort Municipality) of /, '')

const entryByUrl = new Map(entries.map((entry) => [entry.register_url, entry]))

// Independent, openly licensed drawings extracted from flags. They are supplemental specimens;
// the Canadian Heraldic Authority artwork stays first and remains the holder image.
const MUNICIPAL_SHIELD_SOURCES = {
  'city-of-dawson-creek': {
    place: 'Dawson Creek', file: 'dawson-creek-shield.svg', year: '2008', author: 'Cookieman1.1.1'
  },
  'city-of-kimberley': {
    place: 'Kimberley', file: 'kimberley-shield.svg', year: '2005', author: 'Jack Ryan Morris (vector), António Martins-Tuválkin (flag reference)'
  }
}

const municipalShield = (id) => {
  const source = MUNICIPAL_SHIELD_SOURCES[id]
  return source ? [{
    id: `${id}-shield-from-flag`,
    file: source.file,
    title: 'Independent shield illustration, extracted from a flag SVG',
    kind: 'shield',
    date: `${source.year} grant · later drawing`,
    vector: true,
    author: `${source.author} · Wikimedia Commons`,
    licence: 'CC BY-SA 4.0',
    licenceUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
    page: `https://commons.wikimedia.org/wiki/File:Flag_of_${source.place.replaceAll(' ', '_')},_British_Columbia.svg`
  }] : []
}

/**
 * A local government's page: the acquisition groups its register entries (a district's grant and
 * the city's confirmation, or a later flag), and the newest leads, as the register's current record.
 */
const municipalHolder = (held) => {
  const records = held.registerUrls.map((url) => entryByUrl.get(url)).filter(Boolean)
  const main = [...records].sort((a, b) => (b.date ?? '').localeCompare(a.date ?? ''))[0]
  const base = holder(main)
  const profiles = [...new Map(records.map(({ register_url: url }) => MUNICIPAL_PROFILE_BY_REGISTER[url]).filter(Boolean).map((profile) => [profile[0], profile])).values()]
  return {
    ...base,
    id: held.id,
    name: held.name,
    artwork: [...base.artwork, ...municipalShield(held.id)],
    year: String(Math.min(...records.map(firstYear))),
    related: records.filter((entry) => entry !== main).map((entry) => ({
      title: `${placeName(entry.name)}: ${entry.letters_patent}, ${longDate(entry.date)}`,
      url: entry.register_url,
      relation: null
    })),
    links: profiles.map(([subject, status]) => ({
      label: status === 'predecessor' ? 'The current municipality in the register' : 'Open in the register',
      to: { view: 'gallery', subject }
    }))
  }
}

export const MUNICIPAL_HOLDERS = acquisition.holders
  .filter(({ group }) => group === 'municipal')
  .map(municipalHolder)
  .sort((a, b) => fileUnder(a.name).localeCompare(fileUnder(b.name)) || a.name.localeCompare(b.name))

/** Bodies outside the register whose arms are documented by their own official sources. */
export const ADDITIONAL_HOLDERS = acquisition.additionalHolders.map((extra) => {
  const held = acquisition.holders.find(({ id }) => id === extra.id)
  return {
    ...extra,
    registered: extra.registered ?? [],
    motto: extra.motto ?? null,
    blazon: {},
    symbolism: {},
    register: null,
    related: [],
    image: leadImage(held, {}),
    artwork: artworkFor(held, {}),
    links: [],
    sources: extra.sources ?? []
  }
})

/** The Province's and the Lieutenant Governor's artwork, by holder id. */
export const artworkOf = (id) => artworkFor(acquisition.holders.find((held) => held.id === id), {})
