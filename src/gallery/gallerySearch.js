// The gallery's search: every word of a query somewhere in a collection or a logo, as its page
// shows them. A collection matches on its name, what it is, its years and intro; a logo on its
// title, its note, its dates and whose it is. Accents and case are ignored, so "societe" finds
// "Société".

import { GALLERY_COLLECTIONS, entriesOf } from './collections.js'
import { searchIdentitySubjects } from './identityCoverage.js'
import { nodesOf } from './collectedCollections.js'
import { initiativeById } from '../initiatives/initiatives.js'

// Related initiative names remain discoverable without loading its full evidence inventory.
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
const ownCollection = (subject, collection) => subject.collectionIds?.includes(collection.id) ||
  collection.id === `collected-${subject.id}` || nodesOf(collection).includes(subject.entryOwner ?? subject.id)

export const searchGallery = (query, collections = GALLERY_COLLECTIONS) => {
  const words = wordsOf(query)
  if (!words.length) return { collections: [], marks: [] }
  // An alias opens the subject's own collections, not a shared shelf it has one mark on.
  const aliases = new Set(searchIdentitySubjects(query).flatMap((subject) => subject.collections
    .filter((collection) => ownCollection(subject, collection)).map((collection) => collection.id)))
  const found = collections.filter((collection) =>
    aliases.has(collection.id) || matches(words, collection.label, collection.body, collection.years, collection.intro,
      ...(initiativeById(collection.initiativeId)?.searchTerms ?? [])))
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
