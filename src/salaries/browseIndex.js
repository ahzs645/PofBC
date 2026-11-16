// The two published salary indexes, packed as one file for the browser.
//
// public/salaries/people/index.json and employers/index.json are the published record: each is
// about fifteen megabytes and they are read by the build, the checks and the audits. A browser
// opening the Salaries view needs both, and between them they say most things twice or more:
//
//   - the same 1,500 source records are in each, and two thirds of every record is the importer's
//     validation trail, which no screen shows;
//   - every employer's year-by-year coverage is in each, and of its 14,000 cells some 1,400 are
//     distinct (most say only that nothing was imported for that year).
//
// Packing keeps one copy of the sources without the fields below, and one table of the distinct
// coverage cells that each employer's years point into. Unpacking gives back the two indexes as the
// screens have always read them. Nothing else is dropped or reworded, and the published files are
// not touched: scripts/build-salary-browse-index.mjs writes the packed file beside them, and
// browseIndex.test.js holds the round trip to the published indexes.

/** Source fields no screen reads: the importer's validation trail and the hash of its extracted rows. */
export const UNSHOWN_SOURCE_FIELDS = ['validation', 'dataSha256']

export const BROWSE_INDEX_PATH = 'salaries/browse-index.json.gzip'

const withoutUnshown = (source) => Object.fromEntries(Object.entries(source).filter(([key]) => !UNSHOWN_SOURCE_FIELDS.includes(key)))

/** The sources as the packed file carries them. */
export const shownSources = (sources) => Object.fromEntries(Object.entries(sources).map(([id, source]) => [id, withoutUnshown(source)]))

/** One file from the two indexes. Throws if they disagree where they should be saying the same thing. */
export const packBrowseIndex = (people, employers) => {
  if (JSON.stringify(people.years) !== JSON.stringify(employers.years)) throw new Error('The people and employer indexes list different reporting periods')
  if (JSON.stringify(people.sources) !== JSON.stringify(employers.sources)) throw new Error('The people and employer indexes carry different sources')
  if (people.employers.length !== employers.employers.length) throw new Error('The people and employer indexes list different employers')
  const cells = []
  const at = new Map()
  const cellOf = (cell) => {
    const key = JSON.stringify(cell)
    if (!at.has(key)) { at.set(key, cells.length); cells.push(cell) }
    return at.get(key)
  }
  const packedEmployers = employers.employers.map((entry, i) => {
    if (people.employers[i][3] !== entry.slug) throw new Error(`Employer ${i} is ${people.employers[i][3]} in the people index and ${entry.slug} in the employer index`)
    if (JSON.stringify(people.coverage[entry.slug]) !== JSON.stringify(entry.coverage)) throw new Error(`The two indexes give ${entry.slug} different coverage`)
    return { ...entry, coverage: entry.coverage.map(cellOf) }
  })
  const { sources: _sources, employers: _employers, years: _years, ...employersRest } = employers
  const { sources: _peopleSources, coverage: _coverage, years: _peopleYears, ...peopleRest } = people
  return {
    schemaVersion: 1,
    note: 'A packed copy of people/index.json and employers/index.json for the browser. Those two files are the published record; this one is derived from them and adds nothing.',
    years: people.years,
    sources: shownSources(people.sources),
    cells,
    employers: { ...employersRest, employers: packedEmployers },
    people: peopleRest
  }
}

/** The two indexes back from the packed file. Equal cells are one shared object, as are the sources. */
export const unpackBrowseIndex = (packed) => {
  const employers = packed.employers.employers.map((entry) => ({ ...entry, coverage: entry.coverage.map((cell) => packed.cells[cell]) }))
  return {
    people: {
      ...packed.people,
      years: packed.years,
      sources: packed.sources,
      coverage: Object.fromEntries(employers.map((entry) => [entry.slug, entry.coverage]))
    },
    employers: { ...packed.employers, years: packed.years, sources: packed.sources, employers }
  }
}

/**
 * Both indexes, from the packed file where it has been built and from the published pair where it
 * has not (a checkout served without `npm run build:assets`, say).
 */
export const loadSalaryIndexes = (loadJson, options) => loadJson(BROWSE_INDEX_PATH, options).then(unpackBrowseIndex).catch(() => Promise.all([
  loadJson('salaries/people/index.json', options),
  loadJson('salaries/employers/index.json', options)
]).then(([people, employers]) => ({ people, employers })))
