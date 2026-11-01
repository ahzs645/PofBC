// Reading a disclosed name, so one person can be found from year to year.
//
// The disclosures write names as their employers keep them: "Lee, Adelaide", "Wong, Christine,
// OnPui", "Hilde, C". A name is read as a surname and given names; the surname decides which slice
// of the index it is in. All disclosed given names and initials are retained in a result's key:
// "Jennifer J" and "Jennifer N" must not become one person. A shared name is not proof of identity.

const plain = (text) => String(text ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
const letters = (text) => plain(text).replace(/[^a-z]/g, '')

const partsOf = (name) => {
  const [surname = '', ...rest] = String(name ?? '').split(',')
  return { surname: letters(surname), given: rest.join(' ').trim().split(/[\s.]+/).map(letters).filter(Boolean) }
}

/** { surname, given, initial } of a disclosed name. */
export const readName = (name) => {
  const { surname, given } = partsOf(name)
  const first = given[0] ?? ''
  return { surname, given: first, initial: first.slice(0, 1) }
}

/** The index slice a name is filed under: its surname's first two letters. */
export const surnameShard = (name) => readName(name).surname.slice(0, 2).padEnd(2, '_') || '__'

/**
 * Name agreement, never proof of identity. Full disclosed names produce 'name'; an abbreviated
 * first name produces 'initial'; compatible but incomplete middle names produce 'partial'.
 * Conflicting disclosed middle names/initials do not match. Unseparated names are not guessed.
 */
export const nameMatch = (a, b) => {
  const x = partsOf(a)
  const y = partsOf(b)
  if (!x.surname || x.surname !== y.surname || !x.given.length || !y.given.length) return null
  for (let at = 0; at < Math.min(x.given.length, y.given.length); at += 1) {
    const left = x.given[at]
    const right = y.given[at]
    if (left !== right && !(left[0] === right[0] && (left.length === 1 || right.length === 1))) return null
  }
  if (x.given[0].length === 1 || y.given[0].length === 1) return 'initial'
  return x.given.join(' ') === y.given.join(' ') ? 'name' : 'partial'
}

/** Group identical normalized disclosed names, preserving every given name and initial. */
export const personKey = (name) => {
  const { surname, given } = partsOf(name)
  return `${surname}|${given.join(' ')}`
}

/**
 * Browse names once per employer, retaining every ranked observation behind the card/table row.
 * This groups disclosed names, not verified people or proved duplicate payments. Filter before
 * grouping, never sum payments, and prefer an original source when equal payments tie.
 */
export const groupHighestPaidRecords = (rows, { employers, sources = {}, sector = 'all', range = null }) => {
  const groups = new Map()
  const original = (row) => {
    const source = sources[row[6]]
    return Boolean(source?.url && source.sourceKind !== 'compiled' && source.scope !== 'compiled-unverified')
  }
  const better = (candidate, current) => candidate[2] > current[2] || (candidate[2] === current[2] && (
    Number(original(candidate)) > Number(original(current)) || (original(candidate) === original(current) && candidate[5] > current[5])
  ))
  for (const row of rows) {
    if (!row[0] || (range && (row[5] < range[0] || row[5] > range[1]))) continue
    if (sector !== 'all' && employers[row[4]]?.[1] !== sector) continue
    const key = `${personKey(row[0])}|${row[4]}`
    if (!groups.has(key)) groups.set(key, { key, row, records: [], years: [] })
    const group = groups.get(key)
    group.records.push(row)
    if (better(row, group.row)) group.row = row
  }
  return [...groups.values()].map((group) => ({ ...group, years: [...new Set(group.records.map((row) => row[5]))].sort((a, b) => a - b) }))
    .sort((a, b) => b.row[2] - a.row[2] || a.key.localeCompare(b.key))
}

/** A prefix search supports several given names without discarding or concatenating their tokens. */
export const matchesNameQuery = (name, query, nameDisclosure) => {
  const candidate = partsOf(name)
  const wanted = partsOf(query)
  if (nameDisclosure === 'surname-and-initials') {
    return candidate.surname.startsWith(wanted.surname) && candidate.given.join('').startsWith(wanted.given.join(''))
  }
  return candidate.surname.startsWith(wanted.surname) && wanted.given.every((part, at) => candidate.given[at]?.startsWith(part))
}

/**
 * How closely a disclosed name answers a search, best first: 0 the surname typed and every given name
 * typed in full; 1 a surname or given name that only begins as typed ("smit, jo"); 2 the surname typed
 * with initials alone that agree with the given names typed ("Smith, J" for "smith john"), which may
 * or may not be the person meant. null where it does not answer.
 */
export const nameQueryTier = (name, query, nameDisclosure) => {
  const candidate = partsOf(name)
  const wanted = partsOf(query)
  if (!wanted.surname || !candidate.surname.startsWith(wanted.surname)) return null
  const sameSurname = candidate.surname === wanted.surname
  if (matchesNameQuery(name, query, nameDisclosure)) {
    const given = nameDisclosure === 'surname-and-initials' ? [candidate.given.join('')] : candidate.given
    const typed = nameDisclosure === 'surname-and-initials' ? [wanted.given.join('')].filter(Boolean) : wanted.given
    return sameSurname && typed.every((part, at) => given[at] === part) ? 0 : 1
  }
  if (!sameSurname || !wanted.given.length || !candidate.given.length) return null
  const initials = nameDisclosure === 'surname-and-initials' ? [...candidate.given.join('')] : candidate.given
  if (!initials.every((part) => part.length === 1)) return null
  return wanted.given.every((part, at) => !initials[at] || initials[at] === part[0]) ? 2 : null
}

/**
 * The ways a typed name can be read, most likely first. With a comma it is "surname, given names" and
 * nothing else (so "O, J" can name a one-letter surname). Without one, "smith john" is read surname
 * first, then "john smith" surname last, then surnames of more than one word ("de la cruz maria",
 * "maria de la cruz"), and last the whole of it as a surname ("O Brien"). A search tries each in
 * turn. Each is { surname, given, typed }, typed as "surname,given" for the matchers above. These are
 * search alternatives only: they never change a disclosed name or its grouping key.
 */
export const nameReadings = (text) => {
  const value = String(text ?? '').trim()
  if (!value) return []
  const read = (surname, given) => ({ surname: surname.trim(), given: given.trim(), typed: `${surname.trim()},${given.trim()}` })
  if (value.includes(',')) {
    const [surname, ...given] = value.split(',')
    return letters(surname).length >= 1 ? [read(surname, given.join(' '))] : []
  }
  const words = value.split(/\s+/)
  const readings = []
  for (let size = 1; size < Math.max(2, words.length); size += 1) {
    readings.push(read(words.slice(0, size).join(' '), words.slice(size).join(' ')))
    if (words.length > 1) readings.push(read(words.slice(-size).join(' '), words.slice(0, -size).join(' ')))
  }
  if (words.length > 1) readings.push(read(value, ''))
  const seen = new Set()
  return readings.filter((reading) => {
    const key = `${letters(reading.surname)}|${reading.given.toLowerCase()}`
    if (letters(reading.surname).length < 2 || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

const titleCase = (word) => word.replace(/[A-Za-z][A-Za-z']*/g, (part) => part[0].toUpperCase() + part.slice(1).toLowerCase())

/**
 * A disclosed name as a person is called: "Moa, Belaid" as "Belaid Moa", "Hilde, C" as "C. Hilde",
 * "Wong, Christine, OnPui" as "Christine OnPui Wong". A name set all in capitals is set in title case;
 * any other is kept as the employer wrote it.
 */
export const displayName = (name, nameDisclosure) => {
  if (!name) return null
  const [surname, ...rest] = String(name).split(',').map((part) => part.trim()).filter(Boolean)
  const disclosedGiven = rest.join(' ')
  // Only a source explicitly declaring initials can turn BL into B. L.; uppercase full names
  // remain full names. This changes presentation, never the disclosed value or matching key.
  const given = nameDisclosure === 'surname-and-initials' && /^[A-Za-z.\s]+$/.test(disclosedGiven)
    ? [...disclosedGiven.replace(/[.\s]/g, '').toUpperCase()].map((initial) => `${initial}.`)
    : disclosedGiven.split(/\s+/).filter(Boolean)
      .map((part) => (/^[A-Za-z]$/.test(part) ? `${part.toUpperCase()}.` : part))
  const shout = (text) => text === text.toUpperCase() && /[A-Z]{2}/.test(text)
  const tidy = (text) => (shout(text) ? titleCase(text) : text)
  return [...given.map(tidy), tidy(surname ?? '')].filter(Boolean).join(' ')
}

/** One position however its employer spelled it from row to row: case, spacing and stops set aside. */
export const positionKey = (position) => String(position ?? '').toLowerCase().replace(/[^a-z0-9&/+ ]+/g, ' ').replace(/\s+/g, ' ').trim()
