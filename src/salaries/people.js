// Reading a disclosed name, so one person can be found from year to year.
//
// The disclosures write names as their employers keep them: "Lee, Adelaide", "Wong, Christine,
// OnPui", "Hilde, C". A name is read as a surname and given names; the surname decides which slice
// of the index it is in, and the surname with the first given name, or its initial, is what links
// one year's row to another's. A shared name is not proof of one person, so every link says how
// much it rests on.

const plain = (text) => String(text ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

/** { surname, given, initial } of a disclosed name. */
export const readName = (name) => {
  const [surname = '', ...rest] = String(name ?? '').split(',')
  const given = rest.join(' ').trim().split(/[\s.]+/).filter(Boolean)
  const first = plain(given[0] ?? '').replace(/[^a-z]/g, '')
  return { surname: plain(surname).replace(/[^a-z]/g, ''), given: first, initial: first.slice(0, 1) }
}

/** The index slice a name is filed under: its surname's first two letters. */
export const surnameShard = (name) => readName(name).surname.slice(0, 2).padEnd(2, '_') || '__'

/**
 * How strongly two rows' names say they are one person: 'name' when surname and first given name
 * agree in full, 'initial' when one side has only the initial and it agrees, null otherwise.
 */
export const nameMatch = (a, b) => {
  const x = readName(a)
  const y = readName(b)
  if (!x.surname || x.surname !== y.surname || !x.initial || x.initial !== y.initial) return null
  if (x.given.length > 1 && y.given.length > 1) return x.given === y.given ? 'name' : null
  return 'initial'
}

/** A key that groups a search's rows into the people they appear to be: surname and first given name. */
export const personKey = (name) => {
  const { surname, given } = readName(name)
  return `${surname}|${given}`
}

const titleCase = (word) => word.replace(/[A-Za-z][A-Za-z']*/g, (part) => part[0].toUpperCase() + part.slice(1).toLowerCase())

/**
 * A disclosed name as a person is called: "Moa, Belaid" as "Belaid Moa", "Hilde, C" as "C. Hilde",
 * "Wong, Christine, OnPui" as "Christine OnPui Wong". A name set all in capitals is set in title case;
 * any other is kept as the employer wrote it.
 */
export const displayName = (name) => {
  if (!name) return null
  const [surname, ...rest] = String(name).split(',').map((part) => part.trim()).filter(Boolean)
  const given = rest.join(' ').split(/\s+/).filter(Boolean)
    .map((part) => (/^[A-Za-z]$/.test(part) ? `${part.toUpperCase()}.` : part))
  const shout = (text) => text === text.toUpperCase() && /[A-Z]{2}/.test(text)
  const tidy = (text) => (shout(text) ? titleCase(text) : text)
  return [...given.map(tidy), tidy(surname ?? '')].filter(Boolean).join(' ')
}

/** One position however its employer spelled it from row to row: case, spacing and stops set aside. */
export const positionKey = (position) => String(position ?? '').toLowerCase().replace(/[^a-z0-9&/+ ]+/g, ' ').replace(/\s+/g, ' ').trim()
