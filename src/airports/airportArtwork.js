import records from './airportArtwork.json' with { type: 'json' }

export const airportCollectionId = (code) => `collected-airport-${code.toLowerCase()}`

export const AIRPORT_BODIES = records.map(({ code, iata, name, publisher, officialUrl, notes, cover, assets }) => ({
  id: airportCollectionId(code).slice('collected-'.length),
  name,
  kind: 'airport',
  current: true,
  graphNode: null,
  shelf: 'airports',
  officialUrl,
  notes: [`Airport identifiers ${[iata, code].filter(Boolean).join(' and ')}.`, notes].join(' '),
  sources: [{ title: publisher, url: officialUrl }],
  cover,
  assets
}))

export const AIRPORT_IDENTITY_FAMILY = {
  id: 'airport-identities',
  label: 'Airports',
  description: 'Published artwork for airport operators and facilities in British Columbia.'
}

export const AIRPORT_IDENTITY_SUBJECTS = records.map(({ code, iata, name, publisher, officialUrl, notes }) => {
  const collectionId = airportCollectionId(code)
  return {
    id: collectionId.slice('collected-'.length),
    name,
    label: name,
    kind: 'airport',
    family: AIRPORT_IDENTITY_FAMILY.id,
    scope: 'institution',
    priority: 3,
    graphNode: null,
    aliases: [code, iata, publisher].filter(Boolean),
    collectionIds: [collectionId],
    relations: [],
    salaryEmployers: [],
    sources: [{ title: publisher, url: officialUrl }],
    note: notes,
    nextAction: 'Compare dated operator publications for earlier signatures and colourways.'
  }
})
