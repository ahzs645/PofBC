// The gallery's search: every word of a query somewhere in a collection or a logo, as its page
// shows them. A collection matches on its name, what it is, its years and intro; a logo on its
// title, its note, its dates and whose it is. Accents and case are ignored, so "societe" finds
// "Société".

import { GALLERY_COLLECTIONS, collectionById, entriesOf } from './collections.js'
import { IDENTITY_COVERAGE, searchIdentitySubjects } from './identityCoverage.js'
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

const ownCollection = (subject, collection) => subject.collectionIds?.includes(collection.id) ||
  collection.id === `collected-${subject.id}` || nodesOf(collection).includes(subject.entryOwner ?? subject.id)

const collectionsBySubject = new Map(IDENTITY_COVERAGE.map((subject) => [
  subject.id, subject.collections.filter((collection) => ownCollection(subject, collection))
]))
const ownedCollectionIds = new Set([...collectionsBySubject.values()].flat().map(({ id }) => id))
const parentsWithNestedServices = new Set(['collected-translink', 'collected-metro-vancouver'])
const isNestedService = (collection) => parentsWithNestedServices.has(collection.foldedUnder)

const organizationTypes = [
  { value: 'crowns', label: 'Crown corporations', matchesSubject: ({ kind }) => kind === 'crown-corporation' },
  { value: 'schools', label: 'School districts', matchesSubject: ({ schoolDistrict }) => Boolean(schoolDistrict) },
  { value: 'local', label: 'Cities and municipalities', matchesSubject: ({ family }) => family === 'municipalities' },
  { value: 'regional-districts', label: 'Regional districts', matchesSubject: ({ family }) => family === 'regional-districts' || family === 'regional-government' },
  { value: 'postsecondary', label: 'Universities and colleges', matchesSubject: ({ family, kind }) =>
    family === 'postsecondary-history' || ['public-university', 'public-college', 'public-institute'].includes(kind) },
  { value: 'health', label: 'Health authorities and services', matchesSubject: ({ family, kind }) =>
    family === 'specialist-health' || ['health-authority', 'health-agency', 'health-service'].includes(kind) },
  { value: 'transport', label: 'Transit and ferries', matchesSubject: ({ family }) => family === 'transit' || family === 'ferries' },
  { value: 'airports', label: 'Airports', matchesSubject: () => false },
  { value: 'provincial', label: 'Provincial departments and programs', matchesSubject: ({ family, kind }) =>
    family === 'provincial-programs' || family === 'provincial-administration' || kind === 'government-branch' },
  { value: 'commissions', label: 'Commissions', matchesSubject: ({ family }) => family === 'commissions' },
  { value: 'affiliates', label: 'Affiliated organizations', matchesSubject: ({ family }) => family === 'affiliated-organizations' },
  { value: 'tourism', label: 'Tourism and destination management', matchesSubject: ({ family, kind }) =>
    family === 'tourism-destination-management' && kind !== 'crown-corporation' },
  { value: 'partners', label: 'Program delivery partners', matchesSubject: ({ family, programDeliveryPartner }) => family === 'agricultural-partners' || programDeliveryPartner }
]

const typeResults = new Map([...organizationTypes, {
  value: 'other', label: 'Other public bodies and organizations',
  matchesSubject: (subject) => !organizationTypes.some(({ matchesSubject }) => matchesSubject(subject))
}].map(({ value, label, matchesSubject }) => {
  const subjects = IDENTITY_COVERAGE.filter(matchesSubject)
  const ids = new Set(subjects.flatMap(({ id }) => collectionsBySubject.get(id)).map(({ id }) => id))
  const collections = GALLERY_COLLECTIONS.filter(({ id, shelf }) => ids.has(id) || (
    shelf === 'airports' ? value === 'airports'
      : id === 'bc-mark' ? value === 'provincial' : value === 'other' && !ownedCollectionIds.has(id)
  ))
  const records = subjects.filter(({ id }) => !collectionsBySubject.get(id).length)
  return [value, { value, label, subjects, collections, records }]
}))

export const GALLERY_TYPE_OPTIONS = [
  { value: '', label: 'All' },
  ...Array.from(typeResults, ([value, { label }]) => ({ value, label }))
]

const collectionIds = new Set()
const transitIds = new Set(typeResults.get('transport').collections.map(({ id }) => id))
const visibleCollections = (collections) => collections.filter((collection) => !isNestedService(collection))
const indexCollections = (collections) => visibleCollections(collections).filter(({ showInGalleryIndex }) => showInGalleryIndex !== false)
const allSections = Array.from(typeResults.values(), ({ value, label, collections, records }) => {
  const firstCollections = indexCollections(collections).filter(({ id }) =>
    !collectionIds.has(id) && (value === 'transport' || !transitIds.has(id)))
  firstCollections.forEach(({ id }) => collectionIds.add(id))
  return { value, label, collections: firstCollections, records }
})

export const gallerySections = (type) => {
  const scope = typeResults.get(type)
  return scope ? [{ ...scope, collections: indexCollections(scope.collections) }] : allSections
}

export const galleryCategoryRecords = (type) => {
  const scope = typeResults.get(type)
  return scope && { label: scope.label, records: scope.records }
}

/**
 * The collections and logos a query finds, each logo with the collection it opens in. A logo whose
 * collection already matches is not listed again on its own.
 */
export const searchGallery = (query, collections = GALLERY_COLLECTIONS, subjects = searchIdentitySubjects(query)) => {
  const words = wordsOf(query)
  if (!words.length) return { collections: [], marks: [] }
  // An alias opens the subject's own collections, not a shared shelf it has one mark on.
  const aliases = new Set(subjects.flatMap((subject) => subject.collections
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
      if (matches(words, entry.id, entry.label, entry.note, entry.years, entry.body, entry.asset?.publisher,
        ...(entry.versions ?? []).flatMap((v) => [v.id, v.label, v.versionLabel]),
        ...(entry.editorVersions ?? []).flatMap((v) => [v.id, v.label]))) {
        seen.add(entry.id)
        marks.push({ entry, collection })
      }
    }
  }
  return { collections: found, marks }
}

export const browseGallery = (query, type) => {
  const scope = typeResults.get(type)
  if (scope && !query.trim()) {
    return { collections: indexCollections(scope.collections), marks: [], subjects: scope.records }
  }
  const subjects = searchIdentitySubjects(query, scope?.subjects)
  const { collections, marks } = searchGallery(query, scope?.collections, subjects)
  const results = new Set(visibleCollections(collections))
  for (const collection of [...collections, ...marks.map((match) => match.collection)]) {
    if (isNestedService(collection)) results.add(collectionById(collection.foldedUnder))
  }
  return {
    collections: [...results],
    marks: marks.filter(({ collection }) => !isNestedService(collection)),
    subjects: subjects.filter(({ id }) => !collectionsBySubject.get(id).some(isNestedService))
  }
}

/** Whether a key event is the search shortcut: Cmd-K on a Mac, Ctrl-K elsewhere. */
export const isSearchShortcut = (event) =>
  (event.metaKey || event.ctrlKey) && !event.altKey && !event.shiftKey && String(event.key).toLowerCase() === 'k'
