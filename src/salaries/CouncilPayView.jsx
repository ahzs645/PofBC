// Council pay by municipality, like the employers elsewhere: every municipality as a card with its
// latest mayor and councillor figures; opening one sets out its figures year by year, with the same
// amount from several sources shown once, and any payments to named officials. Where the data come
// from, what is held back and the full source list are on the About page.

import { useEffect, useMemo, useState } from 'react'
import { CompanionShell } from './CompanionShell.jsx'
import { DataTable } from './DataTable.jsx'
import { count, Paged, RoleIcon } from './common.jsx'
import { councilCsv, councilFiguresByYear, councilMeasure, councilMunicipalities, councilNotes, councilSourceMap, councilSourceUrl, describeCouncilYears, loadCouncilPay } from './councilPay.js'
import { formatMoney } from './money.js'
import { saveText } from './exportCsv.js'
import './councilPay.css'

const money = (value, currency = 'CAD') => formatMoney(value, 'Not reported', currency)
const words = (text) => String(text ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().split(/\s+/).filter(Boolean)

/** A source as a short link, with its page; its notes are the link's tooltip. */
export const CouncilSource = ({ source, page }) => {
  const href = councilSourceUrl(source?.url)
  const label = `${source?.title ?? 'Source unavailable'}${page ? ` · p. ${page}` : ''}`
  const notes = councilNotes(source?.notes).join(' ')
  return href ? <a href={href} target="_blank" rel="noreferrer" title={notes || undefined}>{label}</a> : <span title={notes || undefined}>{label}</span>
}

const latestLine = (place) => place.offices.map((office) => `${office.role} ${money(office.amount)}${office.disagree ? '*' : ''}`).join(' · ')

/** A municipality as a card, like an employer: opening it shows its figures year by year. */
const MunicipalityCard = ({ place, onOpen }) => (
  <button type="button" className="salaries__card" onClick={() => onOpen(place.name)}>
    <span className="salaries__lead"><RoleIcon /></span>
    <span className="salaries__text">
      <span className="salaries__name">{place.name}</span>
      {place.offices.length > 0 && <span className="salaries__line">{latestLine(place)}</span>}
      {(place.first !== place.last || place.payments > 0) && <span className="salaries__line">{[place.first !== place.last && `${place.first}–${place.last}`, place.payments > 0 && count(place.payments, 'named payment', 'named payments')].filter(Boolean).join(' · ')}</span>}
    </span>
    <span className="salaries__aside">{place.offices[0]?.year ?? place.last}<span className="salaries__line">latest</span></span>
  </button>
)

/** One municipality: its office figures by year, then any payments to named officials. */
const Municipality = ({ data, place, sources, layout, onEmployer }) => {
  const figures = useMemo(() => data.observations.filter((row) => row.municipality === place.name), [data, place])
  const payments = useMemo(() => data.payments.filter((row) => row.municipality === place.name).sort((a, b) => b.year - a.year || (b.remuneration ?? 0) - (a.remuneration ?? 0)), [data, place])
  const byYear = useMemo(() => councilFiguresByYear(figures), [figures])
  const flat = useMemo(() => byYear.flatMap(({ year, roles }) => roles.flatMap(({ role, figures: list }) => list.map((figure) => ({ year, role, ...figure })))), [byYear])
  const figureColumns = useMemo(() => [
    { id: 'year', header: 'Year', accessorKey: 'year', meta: { kind: 'number' } },
    { id: 'role', header: 'Office', accessorKey: 'role' },
    { id: 'amount', header: 'Amount', accessorFn: (row) => row.amount ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ row }) => money(row.original.amount, row.original.currency) },
    { id: 'measure', header: 'Type of figure', accessorFn: (row) => row.measures.map(councilMeasure).join(', ') },
    { id: 'source', header: 'Sources', accessorFn: (row) => row.rows.map((each) => sources.get(each.sourceId)?.title ?? '').join('; '), cell: ({ row }) => row.original.rows.map((each, at) => <span key={each.id}>{at > 0 ? '; ' : ''}<CouncilSource source={sources.get(each.sourceId)} page={each.pdfPage} /></span>) }
  ], [sources])
  const paymentColumns = useMemo(() => [
    { id: 'year', header: 'Year', accessorKey: 'year', meta: { kind: 'number' } },
    { id: 'name', header: 'Official', accessorKey: 'name' },
    { id: 'role', header: 'Office', accessorKey: 'role' },
    { id: 'remuneration', header: 'Remuneration', accessorFn: (row) => row.remuneration ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ row }) => money(row.original.remuneration, row.original.currency) },
    { id: 'expenses', header: 'Expenses', accessorFn: (row) => row.expenses ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ row }) => money(row.original.expenses, row.original.currency) },
    { id: 'source', header: 'Source', accessorFn: (row) => sources.get(row.sourceId)?.title ?? '', cell: ({ row }) => <CouncilSource source={sources.get(row.original.sourceId)} page={row.original.pdfPage} /> }
  ], [sources])
  const download = () => saveText(councilCsv([...figures, ...payments], 'rates', sources), `council-pay-${place.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.csv`)

  return (
    <div className="council-pay">
      <p className="salaries__meta council-pay__links">
        {place.employerSlug && onEmployer && <><button type="button" className="salaries__link" onClick={() => onEmployer(place.employerSlug)}>Every disclosed salary at {place.name}</button> · </>}
        <button type="button" className="salaries__link" onClick={download}>Download as CSV</button>
      </p>

      <section aria-labelledby="council-figures">
        <div className="salaries__head">
          <h3 id="council-figures" className="salaries__title">Pay for each office</h3>
          <p className="salaries__meta">{count(byYear.length, 'year', 'years')}: {describeCouncilYears(byYear.map(({ year }) => year))}</p>
        </div>
        {layout === 'table'
          ? <DataTable data={flat} columns={figureColumns} sorting={[{ id: 'year', desc: true }]} label={`${place.name} council office figures`} rowHeight={52} />
          : <ol className="salaries-years council-pay__years">
            {byYear.map(({ year, roles }) => (
              <li key={year} className="salaries-years__year">
                <span className="salaries-years__label">{year}</span>
                <span className="salaries-years__records">
                  {roles.flatMap(({ role, figures: list }) => list.map((figure, at) => (
                    <span key={`${role}-${at}`} className="salaries-record">
                      <span className="salaries-record__what">
                        <span className="salaries__name">{role}</span>
                        <span className="salaries__line">{figure.measures.map(councilMeasure).join(' and ')}{list.length > 1 ? ' (sources differ)' : ''}</span>
                      </span>
                      <span className="salaries-row__pay">
                        {money(figure.amount, figure.currency)}
                        <span className="salaries__line">{figure.rows.map((row, index) => <span key={row.id}>{index > 0 ? ' · ' : ''}<CouncilSource source={sources.get(row.sourceId)} page={row.pdfPage} /></span>)}</span>
                      </span>
                    </span>
                  )))}
                </span>
              </li>
            ))}
          </ol>}
      </section>

      {payments.length > 0 && (
        <section aria-labelledby="council-payments">
          <div className="salaries__head">
            <h3 id="council-payments" className="salaries__title">Payments to named officials</h3>
            <p className="salaries__meta">{count(payments.length, 'payment', 'payments')} · what each was paid that year, not a salary rate</p>
          </div>
          <DataTable data={payments} columns={paymentColumns} sorting={[{ id: 'year', desc: true }]} label={`${place.name} payments to named officials`} rowHeight={48} />
        </section>
      )}
    </div>
  )
}

export default function CouncilPayView({ place, setPlace, onBrowse, onOpen, onEmployer, back }) {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const query = place.q ?? ''
  const layout = place.layout === 'table' ? 'table' : 'cards'
  const chosen = place.councilMunicipality && place.councilMunicipality !== 'all' ? place.councilMunicipality : null

  useEffect(() => {
    const controller = new AbortController()
    setFailed(false)
    loadCouncilPay({ signal: controller.signal }).then((value) => { if (!controller.signal.aborted) setData(value) }, () => { if (!controller.signal.aborted) setFailed(true) })
    return () => controller.abort()
  }, [attempt])

  const sources = useMemo(() => data ? councilSourceMap(data) : new Map(), [data])
  const places = useMemo(() => data ? councilMunicipalities(data) : [], [data])
  const wanted = words(query)
  const shown = useMemo(() => places.filter((each) => wanted.every((word) => words(each.name).some((part) => part.startsWith(word)))), [places, query]) // eslint-disable-line react-hooks/exhaustive-deps
  const current = chosen ? places.find((each) => each.name === chosen) : null
  const update = (key, value) => setPlace((value_) => ({ ...value_, [key]: value }))
  const columns = useMemo(() => [
    { id: 'name', header: 'Municipality', accessorKey: 'name', cell: ({ row }) => <button type="button" className="salaries__link salaries-row__name" onClick={() => onOpen(row.original.name)}>{row.original.name}</button> },
    ...['Mayor', 'Councillor'].map((role) => ({ id: role, header: `${role}, latest`, accessorFn: (row) => row.offices.find((office) => office.role === role)?.amount ?? undefined, sortUndefined: 'last', meta: { kind: 'money' }, cell: ({ getValue }) => money(getValue()) })),
    { id: 'last', header: 'Latest year', accessorKey: 'last', meta: { kind: 'number' } },
    { id: 'first', header: 'First year', accessorKey: 'first', meta: { kind: 'number' } },
    { id: 'payments', header: 'Named payments', accessorKey: 'payments', meta: { kind: 'number', filter: false } }
  ], [onOpen])

  const yearsAll = data ? [...data.observations, ...data.payments].map((row) => Number(row.year)).filter(Number.isFinite) : []
  const tiles = !data ? []
    : current ? current.offices.map((office) => ({ label: `${office.role}, ${office.year}`, value: money(office.amount), note: office.disagree ? 'highest of the sources' : councilMeasure(data.observations.find((row) => row.municipality === current.name && row.role === office.role && row.year === office.year)?.measure) }))
      .concat([{ label: 'Years', value: current.first === current.last ? String(current.first) : `${current.first}–${current.last}`, note: count(current.years.length, 'year with figures', 'years with figures') }])
      : [
        { label: 'Municipalities', value: places.length.toLocaleString('en-CA'), note: 'with council pay figures' },
        { label: 'Office figures', value: data.observations.length.toLocaleString('en-CA'), note: 'mayor and councillor rates and reported pay' },
        { label: 'Named payments', value: data.payments.length.toLocaleString('en-CA'), note: 'to council members' },
        { label: 'Years', value: yearsAll.length ? `${Math.min(...yearsAll)}–${Math.max(...yearsAll)}` : '—', note: `${data.sources.length} sources` }
      ]

  return (
    <CompanionShell
      browse="council" onBrowse={onBrowse}
      layout={layout} onLayout={(next) => update('layout', next)}
      query={query} onSearch={chosen ? null : (value) => update('q', value)}
      searchLabel="Find a municipality" placeholder="Kamloops, Saanich, Kelowna…" searchHelp="Type the start of any word in a municipality’s name."
      heading={current ? current.name : chosen ?? 'Council pay'}
      back={chosen ? back : null}
      intro={current ? null : !chosen && <p>Mayor and councillor pay in each municipality: office rates from salary schedules and surveys, and payments to named officials, each with its source. Amounts are in Canadian dollars as published.</p>}
      tiles={tiles}
    >
      {failed ? <p className="salaries__hint" role="alert">Council pay could not be loaded. <button type="button" className="salaries__link" onClick={() => setAttempt((value) => value + 1)}>Retry</button></p>
        : !data ? <p className="salaries__hint" role="status">Loading council pay…</p>
          : chosen
            ? current
              ? <Municipality data={data} place={current} sources={sources} layout={layout} onEmployer={onEmployer} />
              : <p className="salaries__hint" role="alert">No council pay figures for “{chosen}”.</p>
            : <div className="council-pay">
              <div className="salaries__head">
                <h3 className="salaries__title">Municipalities</h3>
                <p className="salaries__meta" role="status">{count(shown.length, 'municipality', 'municipalities')}{wanted.length ? ` matching “${query.trim()}”` : ''} · latest figures{places.some((each) => each.offices.some((office) => office.disagree)) ? ' (* sources differ; the highest is shown)' : ''}</p>
              </div>
              {!shown.length
                ? <p className="salaries__hint">No municipality matches “{query.trim()}”.</p>
                : layout === 'table'
                  ? <DataTable data={shown} columns={columns} sorting={[{ id: 'name', desc: false }]} label="Municipalities with council pay" />
                  : <Paged list={shown} size={24} reset={query}>
                    {(page) => <div className="salaries__grid">{page.map((each) => <MunicipalityCard key={each.name} place={each} onOpen={onOpen} />)}</div>}
                  </Paged>}
            </div>}
    </CompanionShell>
  )
}
