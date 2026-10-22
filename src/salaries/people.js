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
