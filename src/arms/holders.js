// The register's other holders: the Crown's offices, universities and colleges, public bodies and
// local governments in British Columbia, from the Canadian Heraldic Authority's public register.
//
// The records are read from research/identity/arms-register-2026-11-16/register.json, as collected
// (every project page of the register, kept where the recipient is a civil institution in B.C.).
// This file adds only what the register cannot: a short name and id, the image held in ./images/,
// and the holder's pages elsewhere on this site.

import register from '../../research/identity/arms-register-2026-11-16/register.json' with { type: 'json' }

export const REGISTER_DIR = 'research/identity/arms-register-2026-11-16'

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
    image: { file: 'ubc-shield.svg', alt: 'Shield', credit: 'Wikimedia Commons · public domain (arms of 1915)', page: 'https://commons.wikimedia.org/wiki/File:British_columbia_univ_coat_arms.svg' }
  },
  'Faculty of Law, University of British Columbia': { id: 'ubc-faculty-of-law', name: 'UBC Faculty of Law' },
  'Green College, University of British Columbia': { id: 'ubc-green-college', name: 'Green College, UBC' },
  'University of Victoria': {
    id: 'university-of-victoria',
    salaries: 'university-of-victoria',
    subject: 'university-of-victoria',
    image: { file: 'uvic-shield.png', alt: 'Shield', credit: 'Robin S. Taylor, Wikimedia Commons · CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:University_of_Victoria_Escutcheon.png' }
  },
  'Simon Fraser University': {
    id: 'simon-fraser-university',
    salaries: 'simon-fraser-university',
    subject: 'simon-fraser-university',
    image: { file: 'sfu-arms.png', alt: 'Coat of arms', credit: 'Robin S. Taylor, Wikimedia Commons · CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Simon_Fraser_University_Achievement.png' }
  },
  'University of Northern British Columbia': {
    id: 'university-of-northern-bc',
    salaries: 'university-of-northern-bc',
    subject: 'university-of-northern-bc',
    image: { file: 'unbc-shield.png', alt: 'Shield', credit: 'Robin S. Taylor, Wikimedia Commons · CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:University_of_Northern_British_Columbia_Escutcheon.png' }
  },
  'Royal Roads University': {
    id: 'royal-roads-university',
    salaries: 'royal-roads-university',
    image: { file: 'royal-roads-shield.png', alt: 'Shield', credit: 'Robin S. Taylor, Wikimedia Commons · CC BY-SA 4.0', page: 'https://commons.wikimedia.org/wiki/File:Royal_Roads_University_Escutcheon.png' }
  },
  'Thompson Rivers University': { id: 'thompson-rivers-university', salaries: 'thompson-rivers-university' },
  'Vancouver Island University': {
    id: 'vancouver-island-university',
    salaries: 'vancouver-island-university',
    image: { file: 'viu-arms.png', alt: 'Coat of arms', credit: 'SheLikesHeraldry, Wikimedia Commons · CC BY 4.0', page: 'https://commons.wikimedia.org/wiki/File:Coat_of_Arms_of_Vancouver_Island_University.png' }
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

const holder = (entry) => {
  const extra = EXTRAS[entry.name] ?? {}
  const links = []
  if (extra.subject) links.push({ label: 'Its logos and identity, in Logos', to: { view: 'gallery', subject: extra.subject } })
  if (extra.salaries) links.push({ label: 'Its published salaries', to: { view: 'salaries', employer: extra.salaries } })
  return {
    id: extra.id,
    name: extra.name ?? entry.common_name ?? entry.name,
    registerName: entry.register_name ?? entry.name,
    group: entry.group,
    year: String(firstYear(entry)),
    registered: entry.registered.map(capital),
    granted: `${entry.letters_patent}, ${longDate(entry.date)}`,
    motto: entry.motto ? { text: entry.motto, translation: entry.motto_translation ?? null } : null,
    description: entry.description ?? null,
    note: [entry.register_notes, entry.note].filter(Boolean).join(' ') || null,
    blazon: byElement(entry.blazon),
    symbolism: byElement(entry.register_symbolism),
    register: { url: entry.register_url, volume: entry.register?.text ?? null },
    related: (entry.related_register_entries ?? []).map((related) => ({
      title: `${related.register_name}: ${related.letters_patent}, ${longDate(related.date)}`,
      url: related.register_url,
      relation: related.relation ?? null
    })),
    image: extra.image ?? null,
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

export const MUNICIPAL_HOLDERS = entries
  .filter(({ group }) => group === 'municipal')
  .map((entry) => ({
    name: placeName(entry.name),
    date: entry.date?.slice(0, 4) ?? null,
    kind: entry.letters_patent,
    motto: entry.motto ?? null,
    url: entry.register_url
  }))
  .sort((a, b) => fileUnder(a.name).localeCompare(fileUnder(b.name)) || a.name.localeCompare(b.name) || (a.date ?? '').localeCompare(b.date ?? ''))
