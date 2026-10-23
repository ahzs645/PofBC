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

/** A prefix search supports several given names without discarding or concatenating their tokens. */
export const matchesNameQuery = (name, query, nameDisclosure) => {
  const candidate = partsOf(name)
  const wanted = partsOf(query)
  if (nameDisclosure === 'surname-and-initials') {
    return candidate.surname.startsWith(wanted.surname) && candidate.given.join('').startsWith(wanted.given.join(''))
  }
  return candidate.surname.startsWith(wanted.surname) && wanted.given.every((part, at) => candidate.given[at]?.startsWith(part))
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
