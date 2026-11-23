// One position title across every employer that disclosed it: how many records each has in a year and
// what they paid, the median of every record by year in one chart that also picks the year, and the
// titles near it; and the people disclosed under it, read from the files of the employers that have it.
//
// A title is grouped however its employers spelled it (positions.js). Titles that only share words
// with it ("Teacher Elementary School" for "Teacher") are not merged into it: they are listed beside
// it, a click away. Employers' positions are not assumed to be the same job because they share a name.

import { useEffect, useMemo, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { titleMedians } from './titleScope.js'
import { displayTitle, keyedTitles, relatedTitles, titleLabel, titleShard } from './positions.js'
import { formatMoney as money, formatSummaryMoney as summary } from './money.js'
import { YearPicker, yearSpan } from './parts.jsx'
import { count, LAYOUTS, loadJson, Paged, PersonIcon, RoleIcon, SalaryPageHeading } from './common.jsx'
import { sourceHref } from './coverage.js'
import { displayName } from './people.js'
import { employerNameKeys } from './nameLinks.js'
import { isCadEmployer } from './recordAnnotations.js'
import { SourceLink } from './DisclosureEvidence.jsx'
import { cellEmployers, employerTotals, loadsUnasked, matchesPerson, PEOPLE_ORDER, scopedCells, titlePeople } from './titlePeople.js'
import { DataTable } from './DataTable.jsx'
import { formatRate, pooledGrowth, seriesGrowth } from './growth.js'
import { GrowthTiles, rateColumn } from './Growth.jsx'

const ORDER = {
  // A year's employers by their median; every year's by their average, since medians do not combine.
  median: (a, b) => (b.median ?? b.mean) - (a.median ?? a.mean) || b.count - a.count,
  records: (a, b) => b.count - a.count || b.median - a.median,
  name: (a, b) => a.name.localeCompare(b.name)
}

/** The figures of several employer/years taken together: records and the range. */
const pool = (cells) => {
  const records = cells.reduce((sum, cell) => sum + cell.count, 0)
  if (!records) return null
  return {
    records,
    low: Math.min(...cells.map((cell) => cell.low)),
    high: Math.max(...cells.map((cell) => cell.high))
  }
}

/** Related titles as cards, a dozen a page. */
const TitleCards = ({ titles, years, onTitle }) => (
  <Paged list={titles} size={12} reset={titles.length}>
    {(page) => <div className="salaries__grid">{page.map((title) => <TitleCard key={title.key} title={title} years={years} onOpen={onTitle} />)}</div>}
  </Paged>
)

/**
 * A title as a card: its commonest spelling, how widely it is used, and the years it spans; at its
 * side its latest average, or with `measure` ('growth' or 'raise') how fast its pay moved.
 */
export const TitleCard = ({ title, years, onOpen, measure }) => (
  <button type="button" className="salaries__card" onClick={() => onOpen(title.key)}>
    <span className="salaries__lead"><RoleIcon /></span>
    <span className="salaries__text">
      <span className="salaries__name">{title.label}</span>
      <span className="salaries__line">{count(title.employers, 'employer', 'employers')} · {count(title.rows, 'record', 'records')}</span>
      <span className="salaries__line">{yearSpan([years[title.first], years[title.last]].filter((label, at, all) => all.indexOf(label) === at))}</span>
    </span>
    {measure && title[measure]
      ? (
        <span className="salaries__aside">
          {formatRate(title[measure].rate, '')}
          <span className="salaries__line">{measure === 'growth' ? `a year, ${years[title.growth.from]}–${years[title.growth.to]}` : `a year, ${count(title.raise.pairs, 'raise', 'raises')}`}</span>
        </span>
      )
      : title.mean != null && <span className="salaries__aside">{summary(title.mean)}<span className="salaries__line">average</span></span>}
  </button>
)

/**
 * The record files of the employers given, with each employer's reviewed name joins (nameLinks.js):
 * { [slug]: { rows, nameKeys } | 'failed' }, and a retry for those that failed. A file already read
 * is not asked for again (loadJson keeps it).
 */
const useEmployerFiles = (slugs) => {
  const [files, setFiles] = useState({})
  const [attempt, setAttempt] = useState(0)
  const wanted = slugs.join('|')
  useEffect(() => {
    let live = true
    for (const slug of wanted ? wanted.split('|') : []) {
      Promise.all([
        loadJson(`salaries/employers/${slug}.json.gzip`),
        // Without its joins an employer's names fold only where they are written alike.
        loadJson(`salaries/links/employers/${slug}.json.gzip`).then((published) => employerNameKeys(published, slug), () => new Map())
      ]).then(
        ([rows, nameKeys]) => live && setFiles((current) => (current[slug]?.rows === rows ? current : { ...current, [slug]: { rows, nameKeys } })),
        () => live && setFiles((current) => ({ ...current, [slug]: 'failed' }))
      )
    }
    return () => { live = false }
  }, [wanted, attempt])
  const retry = () => {
    setFiles((current) => Object.fromEntries(Object.entries(current).filter(([, file]) => file !== 'failed')))
    setAttempt((value) => value + 1)
  }
  return [files, retry]
}

/**
 * Everyone disclosed under the title at its employers, in the sector and year chosen (`year` null
 * for every year): a row a record, with its employer. A name at two employers is two rows; nothing
 * here says they are one person. A title held at many employers waits to be asked, since their
 * files together can be tens of megabytes.
 */
const TitlePeople = ({ titleKey: key, cells, years, sources, year, layout, label, onLayout, onPerson, onEmployerRole }) => {
  const allYears = year === null
  const slugs = useMemo(() => cellEmployers(cells), [cells])
  const entries = useMemo(() => new Map(cells.map((cell) => [cell.entry.slug, cell.entry])), [cells])
  const records = cells.reduce((sum, cell) => sum + cell.count, 0)
  const [asked, setAsked] = useState(false)
  const reading = asked || loadsUnasked(slugs.length)
  const [files, retry] = useEmployerFiles(reading ? slugs : [])
  const failed = slugs.filter((slug) => files[slug] === 'failed')
  const read = slugs.filter((slug) => files[slug] && files[slug] !== 'failed')
  const waiting = reading ? slugs.length - read.length - failed.length : 0
  const settled = reading && waiting === 0
  const [filter, setFilter] = useState('')
  const [order, setOrder] = useState('pay')
  const shownOrder = allYears || order !== 'recent' ? order : 'pay'
  const { people, setAside } = useMemo(() => (settled
    ? titlePeople(read.map((slug) => ({ entry: entries.get(slug), ...files[slug] })), key, { sources, year, keep: (row, entry) => isCadEmployer(row, entry.slug, years, sources) })
    : { people: [], setAside: 0 }), [settled, files, slugs, entries, key, sources, year, years]) // eslint-disable-line react-hooks/exhaustive-deps
  const ranks = useMemo(() => new Map([...people].sort(PEOPLE_ORDER.pay).map((person, at) => [person, at + 1])), [people])
  const matching = useMemo(() => people.filter((person) => matchesPerson(person, filter)).sort(PEOPLE_ORDER[shownOrder]), [people, filter, shownOrder])
  const oneSource = new Set(people.map((person) => person.sourceId)).size <= 1
  const compiled = (person) => sources?.[person.sourceId]?.sourceKind === 'compiled' || sources?.[person.sourceId]?.scope === 'compiled-unverified'
  const columns = useMemo(() => [
    {
      id: 'name', header: 'Name', accessorFn: (person) => (person.name ? displayName(person.name, sources?.[person.sourceId]?.nameDisclosure) : 'Name unavailable'),
      cell: ({ row, getValue }) => (row.original.name ? <button type="button" className="salaries__link salaries-row__name" onClick={() => onPerson(row.original.name, row.original.slug)}>{getValue()}</button> : <span className="salaries__line">{getValue()}</span>)
    },
    { id: 'employer', header: 'Employer', accessorKey: 'employer', cell: ({ row, getValue }) => <button type="button" className="salaries__link" onClick={() => onEmployerRole(row.original.slug, key, row.original.year)}>{getValue()}</button> },
    { id: 'year', header: 'Period', accessorFn: (person) => years[person.year], sortingFn: (a, b) => a.original.year - b.original.year },
    { id: 'position', header: 'As disclosed', accessorFn: (person) => displayTitle(person.position ?? '') },
    { id: 'pay', header: 'Pay', accessorKey: 'pay', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'source', header: 'Source', accessorFn: (person) => person.page ?? '', meta: { filter: false }, cell: ({ row }) => <SourceLink sourceId={row.original.sourceId} sources={sources} pdfPage={row.original.page} /> }
  ], [key, years, sources, onPerson, onEmployerRole])
  const scope = allYears ? 'over every year' : `in ${years[year]}`

  return (
    <section aria-labelledby="salaries-title-people" className="salaries__records">
      <div className="salaries__head">
        <h2 id="salaries-title-people" className="salaries__title">{allYears ? 'People, every year' : `People in ${years[year]}`}</h2>
        <div className="salaries__head-tools">
          <p className="salaries__meta">{count(settled ? people.length : records, 'record', 'records')}</p>
          {settled && people.length > 0 && <Segmented compact ariaLabel="Layout" value={layout} onChange={onLayout} options={LAYOUTS} />}
        </div>
      </div>
      {!reading && (
        <div className="salaries__hint salaries-title-people__ask">
          <p>{count(records, 'record', 'records')} at {count(slugs.length, 'employer', 'employers')} {scope}. The names are in each employer’s own file, and these files are large to download together.</p>
          <button type="button" className="salaries__more" onClick={() => setAsked(true)}>Load people from {count(slugs.length, 'employer', 'employers')}</button>
        </div>
      )}
      {waiting > 0 && (
        <p className="salaries__hint" role="status">
          {slugs.length > 1 ? `Loading people from ${count(slugs.length, 'employer', 'employers')}: ${read.length + failed.length} done…` : 'Loading the people…'}
        </p>
      )}
      {failed.length > 0 && waiting === 0 && (
        <p className="salaries__hint" role="alert">
          The records of {failed.length === slugs.length ? (failed.length === 1 ? 'the employer' : 'these employers') : failed.map((slug) => entries.get(slug).names.at(-1)).join(', ')} could not be loaded
          {failed.length < slugs.length ? '; the others are listed below' : ''}. <button type="button" onClick={retry}>Retry</button>
        </p>
      )}
      {settled && read.length > 0 && !people.length && <p className="salaries__hint">No records under this title were found in the employers’ files {scope}.</p>}
      {settled && people.length > 0 && (
        <>
          {people.length > 12 && (
            <div className="salaries__search salaries__search--one">
              <input type="search" value={filter} placeholder="Find a name, employer or position" aria-label="Find a name, employer or position" onChange={(event) => setFilter(event.target.value)} />
            </div>
          )}
          {filter.trim() !== '' && <p className="salaries__meta">{matching.length ? count(matching.length, 'record matches', 'records match') : `Nothing matches “${filter.trim()}”.`}</p>}
          {layout === 'cards' && people.length > 2 && (
            <div className="salaries__browse-bar">
              <Segmented
                compact ariaLabel="Order people" value={shownOrder} onChange={setOrder}
                options={[{ value: 'pay', label: 'Highest paid' }, ...(allYears ? [{ value: 'recent', label: 'Latest first' }] : []), { value: 'name', label: 'A–Z' }]}
              />
            </div>
          )}
          {layout === 'table' && <DataTable key={allYears ? 'all' : year} data={matching} columns={columns} sorting={[{ id: 'pay', desc: true }]} label={allYears ? 'People under this title, every year' : `People under this title in ${years[year]}`} />}
          {layout === 'cards' && (
            <Paged list={matching} size={50} reset={`${year}|${filter}|${shownOrder}|${people.length}`}>
              {(page) => (
                <ol className="salaries__grid salaries__grid--list">
                  {page.map((person) => {
                    const position = [person.position && displayTitle(person.position) !== label ? displayTitle(person.position) : null, compiled(person) ? 'Compiled position · not independently verified' : null].filter(Boolean).join(' · ')
                    const source = (oneSource && !person.page) || !sourceHref(sources?.[person.sourceId], person.page) ? null : <SourceLink sourceId={person.sourceId} sources={sources} pdfPage={person.page} />
                    return (
                      <li key={person.id} className={`salaries__card salaries-record-card${person.name ? '' : ' salaries__card--still'}`}>
                        <span className="salaries__lead"><PersonIcon /></span>
                        <span className="salaries__text">
                          {person.name
                            ? <button type="button" className="salaries__name salaries-record-card__open" onClick={() => onPerson(person.name, person.slug)}>{displayName(person.name, sources?.[person.sourceId]?.nameDisclosure)}</button>
                            : <span className="salaries__name" data-missing>Name unavailable</span>}
                          <span className="salaries__line">
                            <button type="button" className="salaries__link salaries-title-people__employer" onClick={() => onEmployerRole(person.slug, key, person.year)}>{person.employer}</button>
                            {source && <> · {source}</>}
                          </span>
                          {position && <span className="salaries__line">{position}</span>}
                        </span>
                        <span className="salaries__aside">{money(person.pay)}<span className="salaries__line">{allYears ? years[person.year] : `No. ${ranks.get(person)}`}</span></span>
                      </li>
                    )
                  })}
                </ol>
              )}
            </Paged>
          )}
        </>
      )}
      {settled && (people.length > 0 || setAside > 0) && (
        <p className="salaries__hint salaries__hint--small">
          Names are as each employer disclosed them. The same name at two employers is two rows: it is not assumed to be one person.
          {setAside > 0 ? ` ${count(setAside, 'record in another currency is', 'records in other currencies are')} left out here and listed on the employer’s page.` : ''}
        </p>
      )}
    </section>
  )
}

export const TitlePage = ({ titleKey: key, employers, years, sources, sector, year: wantedYear, layout = 'cards', back, onYear, onLayout, onSector, onEmployerRole, onTitle, onPerson, remember }) => {
  const [detail, setDetail] = useState(null)
  const [index, setIndex] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [order, setOrder] = useState('median')

  useEffect(() => {
    let live = true
    setFailed(false)
    setDetail(null)
    loadJson(`salaries/positions/${titleShard(key)}.json.gzip`).then((shard) => live && setDetail(shard[key] ?? false), () => live && setFailed(true))
    loadJson('salaries/positions/index.json.gzip').then((value) => live && setIndex(value), () => {})
    return () => { live = false }
  }, [key, loadVersion])

  const cells = useMemo(() => (detail ? detail.cells.map(([employer, at, records, mean, median, low, high]) => {
    const entry = employers[employer]
    return { entry, name: entry.names.at(-1), year: at, count: records, mean: Math.round(mean), median, low, high }
  }) : []), [detail, employers])
  const inSector = useMemo(() => scopedCells(cells, sector), [cells, sector])
  const counts = years.map((_, at) => inSector.filter((cell) => cell.year === at).reduce((sum, cell) => sum + cell.count, 0))
  // Every year unless a year is chosen (a bar, or a link that names one).
  const year = wantedYear !== null && wantedYear !== undefined && wantedYear >= 0 ? wantedYear : null
  const allYears = year === null
  const seen = years.map((_, at) => at).filter((at) => counts[at] > 0)
  const latest = seen.at(-1) ?? -1
  const yearCells = useMemo(() => (allYears ? inSector : scopedCells(inSector, 'all', year)), [inSector, allYears, year])
  const chosen = (allYears ? employerTotals(inSector) : [...yearCells]).sort(ORDER[order])
  const overall = pool(yearCells)
  // The median of every record each year. Where several employers share a year it is the build's,
  // since employers' medians do not combine: for the chosen sector where the title spans several,
  // otherwise for all of them. Where one employer has the year, it is that employer's median.
  const medians = useMemo(() => titleMedians(cells, detail?.medians, sector, years), [cells, detail, sector, years])
  // The sector a search was narrowed to stays offered even where this title has none in it, so it can
  // be cleared here.
  const sectors = [...new Set([...cells.map((cell) => cell.entry.sector), ...(sector !== 'all' ? [sector] : [])])].sort()
  const label = detail?.spellings?.[0] ? titleLabel(detail.spellings[0][0]) : key
  remember?.(label)
  const related = useMemo(() => (index ? relatedTitles(keyedTitles(index), key) : null), [index, key])
  // Each employer's own series of this title, for how its pay moved there and across them.
  const series = useMemo(() => {
    const byEmployer = new Map()
    for (const cell of inSector) {
      if (!byEmployer.has(cell.entry.slug)) byEmployer.set(cell.entry.slug, [])
      byEmployer.get(cell.entry.slug).push(cell)
    }
    return [...byEmployer]
  }, [cells, sector]) // eslint-disable-line react-hooks/exhaustive-deps
  const growth = useMemo(() => pooledGrowth(series, years), [series, years])
  const growthAt = useMemo(() => new Map(series.map(([slug, list]) => [slug, seriesGrowth(list, years)])), [series, years])
  // The typical raise is measured over every employer by the build (positions/index.json.gzip).
  const raise = useMemo(() => (index ? keyedTitles(index).find((title) => title.key === key)?.raise ?? null : null), [index, key])
  const employerCount = new Set(inSector.map((cell) => cell.entry.slug)).size
  // A year's employers, or every year's taken together, each opening its position page at that year
  // (every year's at the employer's latest).
  const employerColumns = useMemo(() => [
    { id: 'name', header: 'Employer', accessorKey: 'name', cell: ({ row, getValue }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onEmployerRole(row.original.entry.slug, key, row.original.year)}>{getValue()}</button> },
    { id: 'sector', header: 'Sector', accessorFn: (cell) => cell.entry.sector },
    { id: 'count', header: 'Records', accessorKey: 'count', meta: { kind: 'number' } },
    ...(allYears
      ? [
          { id: 'periods', header: 'Periods', accessorKey: 'periods', meta: { kind: 'number' } },
          { id: 'latest', header: 'Latest', accessorFn: (total) => years[total.latest], sortingFn: (a, b) => a.original.latest - b.original.latest }
        ]
      : []),
    { id: 'mean', header: 'Average', accessorKey: 'mean', meta: { kind: 'money' }, cell: ({ getValue }) => summary(getValue()) },
    ...(allYears ? [] : [{ id: 'median', header: 'Median', accessorKey: 'median', meta: { kind: 'money' }, cell: ({ getValue }) => summary(getValue()) }]),
    { id: 'low', header: 'Lowest', accessorKey: 'low', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    { id: 'high', header: 'Highest', accessorKey: 'high', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) },
    rateColumn('growth', 'Average growth', (cell) => growthAt.get(cell.entry.slug)?.rate)
  ], [key, onEmployerRole, growthAt, allYears, years])

  return (
    <div className="salaries">
      <section className="salaries__person" aria-labelledby="salaries-title">
        <SalaryPageHeading id="salaries-title" back={back}>{label}</SalaryPageHeading>
        {detail && (
          <p className="salaries__note">
            {count(employerCount, 'employer', 'employers')}{sector !== 'all' ? ` in ${sector.toLowerCase()}` : ''} · {count(inSector.reduce((sum, cell) => sum + cell.count, 0), 'record', 'records')}
          </p>
        )}
        {detail?.spellings?.length > 1 && (
          <p className="salaries__hint salaries__hint--small">
            Also written as {detail.spellings.slice(1, 4).map(([text]) => `“${text}”`).join(', ')}{detail.spellings.length > 4 ? ' and others' : ''}. The jobs behind one title can differ between employers.
          </p>
        )}
        {failed && <p className="salaries__hint" role="alert">This title could not be loaded. <button type="button" onClick={() => setLoadVersion((value) => value + 1)}>Retry</button></p>}
        {detail === null && !failed && <p className="salaries__hint" role="status">Loading the title…</p>}
        {detail === false && <p className="salaries__hint">No employer has disclosed a position under this title.</p>}
        {sectors.length > 1 && (
          <div className="salaries__chips" role="group" aria-label="Sector">
            <button type="button" aria-pressed={sector === 'all'} onClick={() => onSector('all')}>All sectors</button>
            {sectors.map((name) => (
              <button key={name} type="button" aria-pressed={sector === name} onClick={() => onSector(sector === name ? 'all' : name)}>
                {name} <span>{new Set(cells.filter((cell) => cell.entry.sector === name).map((cell) => cell.entry.slug)).size}</span>
              </button>
            ))}
          </div>
        )}
        {detail && cells.length > 0 && !inSector.length && (
          <p className="salaries__hint">No employer in {sector.toLowerCase()} disclosed this title. <button type="button" className="salaries__link" onClick={() => onSector('all')}>Show all sectors</button></p>
        )}
        {detail && inSector.length > 0 && (
          <>
            {/* Every year has no bar of its own: no bar is pressed (-1), and on a phone the period
                chooser's empty label reads "Every year" (site.css). */}
            <div className="salaries-title-years" data-all={allYears || undefined}>
              <YearPicker years={years} counts={counts} values={medians} value={allYears ? -1 : year} onChange={onYear} label="Median pay by year" chooseLabel="Year of this title’s records" />
            </div>
            <div className="salaries-title-years__head">
              <h3 className="salaries__year-title">{allYears ? `Every year · ${yearSpan(seen.map((at) => years[at]))}` : years[year]}</h3>
              <Segmented
                compact ariaLabel="Years shown" value={allYears ? 'all' : 'one'}
                onChange={(value) => onYear(value === 'all' ? null : latest)}
                options={[{ value: 'all', label: 'All years' }, { value: 'one', label: allYears ? 'One year' : years[year] }]}
              />
            </div>
            {overall
              ? (
                <dl className="salaries__tiles">
                  <div><dt>Employers</dt><dd>{chosen.length.toLocaleString('en-CA')}</dd></div>
                  <div><dt>Records</dt><dd>{overall.records.toLocaleString('en-CA')}</dd></div>
                  {allYears
                    ? <div><dt>Periods</dt><dd>{seen.length.toLocaleString('en-CA')}</dd></div>
                    : <div><dt>Median</dt><dd>{money(medians[year])}</dd></div>}
                  <div><dt>Range</dt><dd className="salaries__range">{overall.records > 1 ? `${money(overall.low)}–${money(overall.high)}` : money(overall.low)}</dd></div>
                </dl>
              )
              : <p className="salaries__hint">No employer disclosed this title in {years[year]}; the bars above show the years with records.</p>}
            <GrowthTiles
              id="salaries-title-growth" growth={growth} raise={sector === 'all' ? raise : null} years={years}
              raiseNote={sector === 'all' ? undefined : 'measured across all sectors only'}
              extra={growth && <div><dt>Employers measured</dt><dd>{growth.employers.toLocaleString('en-CA')}</dd><dd className="salaries__line">{count(growth.weight, 'record weighs', 'records weigh')} it</dd></div>}
            />
          </>
        )}
      </section>

      {chosen.length > 0 && (
        <section aria-labelledby="salaries-title-employers" className="salaries__records">
          <div className="salaries__head">
            <h2 id="salaries-title-employers" className="salaries__title">{allYears ? 'Employers, every year' : `Employers in ${years[year]}`}</h2>
            <div className="salaries__head-tools">
              <p className="salaries__meta">{count(chosen.length, 'employer', 'employers')}</p>
              <Segmented compact ariaLabel="Layout" value={layout} onChange={onLayout} options={LAYOUTS} />
            </div>
          </div>
          {layout === 'cards' && (
            <div className="salaries__browse-bar">
              <Segmented compact ariaLabel="Order employers" value={order} onChange={setOrder} options={[{ value: 'median', label: allYears ? 'Highest average' : 'Highest median' }, { value: 'records', label: 'Most records' }, { value: 'name', label: 'A–Z' }]} />
            </div>
          )}
          {layout === 'table' && <DataTable key={allYears ? 'all' : year} data={chosen} columns={employerColumns} sorting={[{ id: allYears ? 'mean' : 'median', desc: true }]} label={allYears ? 'Employers, every year' : `Employers in ${years[year]}`} />}
          {layout === 'cards' && (
          <Paged list={chosen} size={24} reset={`${year}|${order}|${sector}`}>
            {(page) => (
          <div className="salaries__grid">
            {page.map((cell) => (
              <button key={cell.entry.slug} type="button" className="salaries__card" onClick={() => onEmployerRole(cell.entry.slug, key, cell.year)}>
                <span className="salaries__lead"><RoleIcon /></span>
                <span className="salaries__text">
                  <span className="salaries__name">{cell.name}</span>
                  <span className="salaries__line">
                    {cell.entry.sector} · {count(cell.count, 'record', 'records')}
                    {allYears ? ` · ${cell.periods > 1 ? `${count(cell.periods, 'period', 'periods')}, ${yearSpan([years[cell.first], years[cell.latest]])}` : years[cell.latest]}` : ''}
                  </span>
                  {cell.count > 1 && <span className="salaries__line">{money(cell.low)}–{money(cell.high)}{allYears ? '' : ` · average ${summary(cell.mean)}`}</span>}
                  {growthAt.get(cell.entry.slug) && <span className="salaries__line">Average {formatRate(growthAt.get(cell.entry.slug).rate)}</span>}
                </span>
                {allYears
                  ? <span className="salaries__aside">{cell.count > 1 ? summary(cell.mean) : money(cell.mean)}<span className="salaries__line">{cell.count > 1 ? 'average' : 'paid'}</span></span>
                  : <span className="salaries__aside">{cell.count > 1 ? summary(cell.median) : money(cell.median)}<span className="salaries__line">{cell.count > 1 ? 'median' : 'paid'}</span></span>}
              </button>
            ))}
          </div>
            )}
          </Paged>
          )}
        </section>
      )}

      {detail && yearCells.length > 0 && (
        <TitlePeople
          titleKey={key} cells={yearCells} years={years} sources={sources} year={year} layout={layout}
          label={label} onLayout={onLayout} onPerson={onPerson} onEmployerRole={onEmployerRole}
        />
      )}

      {related && related.narrower.length > 0 && (
        <section aria-labelledby="salaries-title-narrower">
          <div className="salaries__head">
            <h2 id="salaries-title-narrower" className="salaries__title">Titles that add to “{label}”</h2>
            <p className="salaries__meta">{count(related.narrower.length, 'title', 'titles')}</p>
          </div>
          <TitleCards titles={related.narrower} years={years} onTitle={onTitle} />
        </section>
      )}
      {related && related.broader.length > 0 && (
        <section aria-labelledby="salaries-title-broader">
          <div className="salaries__head">
            <h2 id="salaries-title-broader" className="salaries__title">Broader titles</h2>
            <p className="salaries__meta">{count(related.broader.length, 'title', 'titles')}</p>
          </div>
          <TitleCards titles={related.broader} years={years} onTitle={onTitle} />
        </section>
      )}
    </div>
  )
}
