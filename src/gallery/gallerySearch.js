// The gallery's search: every word of a query somewhere in a collection or a logo, as its page
// shows them. A collection matches on its name, what it is, its years and intro; a logo on its
// title, its note, its dates and whose it is. Accents and case are ignored, so "societe" finds
// "Société".

import { GALLERY_COLLECTIONS, entriesOf } from './collections.js'

const fold = (text) => String(text ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

/** The query's words, or none for an empty query. */
export const wordsOf = (query) => fold(query).split(/[^\p{L}\p{N}]+/u).filter(Boolean)

const matches = (words, ...texts) => {
  const haystack = fold(texts.filter(Boolean).join(' '))
  return words.every((word) => haystack.includes(word))
}

/**
 * The collections and logos a query finds, each logo with the collection it opens in. A logo whose
 * collection already matches is not listed again on its own.
 * @returns {{ collections: object[], marks: { entry: object, collection: object }[] }}
 */
export const searchGallery = (query, collections = GALLERY_COLLECTIONS) => {
  const words = wordsOf(query)
  if (!words.length) return { collections: [], marks: [] }
  const found = collections.filter((collection) =>
    matches(words, collection.label, collection.body, collection.years, collection.intro))
  const shown = new Set(found.map((collection) => collection.id))
  const seen = new Set()
  const marks = []
  for (const collection of collections) {
    if (shown.has(collection.id)) continue
    for (const entry of entriesOf(collection)) {
      if (seen.has(entry.id)) continue
      if (matches(words, entry.label, entry.note, entry.years, entry.body, entry.asset?.publisher)) {
        seen.add(entry.id)
        marks.push({ entry, collection })
      }
    }
  }
  return { collections: found, marks }
}

/** Whether a key event is the search shortcut: Cmd-K on a Mac, Ctrl-K elsewhere. */
export const isSearchShortcut = (event) =>
  (event.metaKey || event.ctrlKey) && !event.altKey && !event.shiftKey && String(event.key).toLowerCase() === 'k'
