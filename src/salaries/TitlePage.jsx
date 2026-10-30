// One position title across every employer that disclosed it: how many records each has in a year and
// what they paid on average, the average across them all by year, and the titles near it.
//
// A title is grouped however its employers spelled it (positions.js). Titles that only share words
// with it ("Teacher Elementary School" for "Teacher") are not merged into it: they are listed beside
// it, a click away. Employers' positions are not assumed to be the same job because they share a name.

import { useEffect, useMemo, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { keyedTitles, relatedTitles, titleLabel, titleShard } from './positions.js'
import { formatMoney as money } from './money.js'
import { PayChart, YearPicker, yearSpan } from './parts.jsx'
import { count, loadJson, More, RoleIcon } from './common.jsx'

const ORDER = {
  average: (a, b) => b.mean - a.mean || b.count - a.count,
  records: (a, b) => b.count - a.count || b.mean - a.mean,
  name: (a, b) => a.name.localeCompare(b.name)
}

/** The figures of several employer/years taken together: records, their mean, and the range. */
const pool = (cells) => {
  const records = cells.reduce((sum, cell) => sum + cell.count, 0)
  if (!records) return null
  return {
    records,
    mean: Math.round(cells.reduce((sum, cell) => sum + cell.mean * cell.count, 0) / records),
    low: Math.min(...cells.map((cell) => cell.low)),
    high: Math.max(...cells.map((cell) => cell.high))
  }
}

/** Related titles as cards, a dozen at a time. */
const TitleCards = ({ titles, years, onTitle }) => {
  const [shown, setShown] = useState(12)
  return (
    <>
      <div className="salaries__grid">
        {titles.slice(0, shown).map((title) => <TitleCard key={title.key} title={title} years={years} onOpen={onTitle} />)}
      </div>
      <More shown={shown} total={titles.length} step={24} onMore={() => setShown((value) => value + 24)} />
    </>
  )
}

/** A title as a card: its commonest spelling, how widely it is used, and the years it spans. */
export const TitleCard = ({ title, years, onOpen }) => (
  <button type="button" className="salaries__card" onClick={() => onOpen(title.key)}>
    <span className="salaries__lead"><RoleIcon /></span>
    <span className="salaries__text">
      <span className="salaries__name">{title.label}</span>
      <span className="salaries__line">{count(title.employers, 'employer', 'employers')} · {count(title.rows, 'record', 'records')}</span>
      <span className="salaries__line">{yearSpan([years[title.first], years[title.last]].filter((label, at, all) => all.indexOf(label) === at))}</span>
    </span>
  </button>
)

export const TitlePage = ({ titleKey: key, employers, years, sector, year: wantedYear, back, onYear, onSector, onEmployerRole, onTitle, remember }) => {
  const [detail, setDetail] = useState(null)
  const [index, setIndex] = useState(null)
  const [failed, setFailed] = useState(false)
  const [loadVersion, setLoadVersion] = useState(0)
  const [order, setOrder] = useState('average')
  const [shown, setShown] = useState(24)

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
  const inSector = cells.filter((cell) => sector === 'all' || cell.entry.sector === sector)
  const counts = years.map((_, at) => inSector.filter((cell) => cell.year === at).reduce((sum, cell) => sum + cell.count, 0))
  const year = wantedYear !== null && wantedYear !== undefined ? wantedYear : counts.findLastIndex((value) => value > 0)
  const chosen = inSector.filter((cell) => cell.year === year).sort(ORDER[order])
  const overall = pool(chosen)
  const points = years.map((_, at) => ({ year: at, pooled: pool(inSector.filter((cell) => cell.year === at)) }))
    .filter(({ pooled }) => pooled).map(({ year: at, pooled }) => ({ year: at, pay: pooled.mean }))
  // The sector a search was narrowed to stays offered even where this title has none in it, so it can
  // be cleared here.
  const sectors = [...new Set([...cells.map((cell) => cell.entry.sector), ...(sector !== 'all' ? [sector] : [])])].sort()
  const label = detail?.spellings?.[0] ? titleLabel(detail.spellings[0][0]) : key
  remember?.(label)
  const related = useMemo(() => (index ? relatedTitles(keyedTitles(index), key) : null), [index, key])
  const employerCount = new Set(inSector.map((cell) => cell.entry.slug)).size

  return (
    <div className="salaries">
      <section className="salaries__person" aria-labelledby="salaries-title">
        {back}
        <h2 id="salaries-title" className="salaries__heading">{label}</h2>
        {detail && (
          <p className="salaries__note">
            {count(employerCount, 'employer', 'employers')}{sector !== 'all' ? ` in ${sector.toLowerCase()}` : ''} · {count(inSector.reduce((sum, cell) => sum + cell.count, 0), 'record', 'records')}
          </p>
        )}
        {detail?.spellings?.length > 1 && (
          <p className="salaries__hint salaries__hint--small">
            Written as {detail.spellings.slice(0, 6).map(([text]) => `“${text}”`).join(', ')}{detail.spellings.length > 6 ? ', and other ways' : ''}. Capitals,
            stops, plurals, common abbreviations and departments are set aside to gather these; the jobs behind one title can still differ between employers.
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
            <YearPicker years={years} counts={counts} value={year} onChange={(at) => { onYear(at); setShown(24) }} label="Year of this title’s records" />
            <h3 className="salaries__year-title">{years[year]}</h3>
            {overall
              ? (
                <dl className="salaries__tiles">
                  <div><dt>Employers</dt><dd>{chosen.length.toLocaleString('en-CA')}</dd></div>
                  <div><dt>Records</dt><dd>{overall.records.toLocaleString('en-CA')}</dd></div>
                  <div><dt>Average</dt><dd>{money(overall.mean)}</dd></div>
                  <div><dt>Range</dt><dd className="salaries__range">{overall.records > 1 ? `${money(overall.low)}–${money(overall.high)}` : money(overall.low)}</dd></div>
                </dl>
              )
              : <p className="salaries__hint">No employer disclosed this title in {years[year]}; the bars above show the years with records.</p>}
            {points.length > 1 && <PayChart years={years} points={points} label="Average pay by year, all employers together" />}
          </>
        )}
      </section>

      {chosen.length > 0 && (
        <section aria-labelledby="salaries-title-employers" className="salaries__records">
          <div className="salaries__head">
            <h2 id="salaries-title-employers" className="salaries__title">Employers in {years[year]}</h2>
            <p className="salaries__meta">{count(chosen.length, 'employer', 'employers')}</p>
          </div>
          <Segmented compact ariaLabel="Order employers" value={order} onChange={setOrder} options={[{ value: 'average', label: 'Highest average' }, { value: 'records', label: 'Most records' }, { value: 'name', label: 'A–Z' }]} />
          <div className="salaries__grid salaries__grid--spaced">
            {chosen.slice(0, shown).map((cell) => (
              <button key={cell.entry.slug} type="button" className="salaries__card" onClick={() => onEmployerRole(cell.entry.slug, key, year)}>
                <span className="salaries__lead"><RoleIcon /></span>
                <span className="salaries__text">
                  <span className="salaries__name">{cell.name}</span>
                  <span className="salaries__line">{cell.entry.sector} · {count(cell.count, 'record', 'records')}</span>
                  {cell.count > 1 && <span className="salaries__line">Median {money(cell.median)} · {money(cell.low)}–{money(cell.high)}</span>}
                </span>
                <span className="salaries__aside">{money(cell.mean)}<span className="salaries__line">{cell.count > 1 ? 'average' : 'paid'}</span></span>
              </button>
            ))}
          </div>
          <More shown={shown} total={chosen.length} step={48} onMore={() => setShown((value) => value + 48)} />
        </section>
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
