import { useEffect, useState } from 'react'
import { filterProfileRows, loadProfiles, profileAssetUrl } from './workforceProfiles.js'

export default function WorkforceProfiles() {
  const [data, setData] = useState(null)
  const [failed, setFailed] = useState(false)
  const [attempt, setAttempt] = useState(0)
  const [name, setName] = useState('WP2024_EmpCounts')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setFailed(false)
    loadProfiles({ signal: controller.signal }).then(value => { if (!controller.signal.aborted) setData(value) }, () => { if (!controller.signal.aborted) setFailed(true) })
    return () => controller.abort()
  }, [attempt])
  if (failed) return <div className="workforce__error" role="alert"><p>Workforce Profiles could not be loaded.</p><button onClick={() => setAttempt(value => value + 1)}>Try again</button></div>
  if (!data) return <p role="status">Loading Workforce Profiles…</p>
  const table = data.tables.find(item => item.name === name) || data.tables[0]
  const rows = filterProfileRows(table, query)
  const pageCount = Math.max(1, Math.ceil(rows.length / 25))
  const currentPage = Math.min(page, pageCount - 1)
  const displayed = rows.slice(currentPage * 25, currentPage * 25 + 25)
  return <section className="workforce__profiles" aria-labelledby="profile-heading">
    <h3 id="profile-heading">Workforce Profiles archive</h3>
    <p>Browse 30 official source tables from the 2018, 2020, 2022 and 2024 profile editions: employee counts, representation, comparisons, leadership, hiring, workforce flows and ministry keys.</p>
    <aside className="workforce__note"><strong>Aggregate statistics, not a list of people.</strong> The archive contains 10,435 source rows, including ministry lookup rows. Counts, percentages and comparison populations have different denominators. Groups overlap, and population comparators are not employee counts. Do not add the rows together or compare these counts directly with the FOI averages, payment disclosures or FTE series.</aside>
    <div className="workforce__controls">
      <label className="workforce__population"><span>Source table</span><select value={table.name} onChange={event => { setName(event.target.value); setQuery(''); setPage(0) }}>{data.tables.map(item => <option key={item.id} value={item.name}>{item.name.replaceAll('_', ' · ')} ({item.rowCount} rows)</option>)}</select></label>
      <label className="workforce__population"><span>Filter source rows</span><input type="search" value={query} placeholder="Ministry, group or other value" onChange={event => { setQuery(event.target.value); setPage(0) }} /></label>
      <div className="workforce__downloads"><a href={table.url} target="_blank" rel="noreferrer">Official CSV</a><a href={profileAssetUrl()} download="bc-workforce-profiles.json">Complete archive JSON</a></div>
    </div>
    <p className="workforce__scope">All fields retain the original source labels and text. “S”, “NA” and blank cells are not zero; suppressed values are not reconstructed. Edition years do not define every observation period: comparison columns may refer to earlier years. Ministry keys can change between editions; each edition includes its own MinistryKey table.</p>
    <div className="workforce__table-wrap" tabIndex="0" role="region" aria-label={`${table.name} source table`}>
      <table className="workforce__table workforce__profile-table"><caption>{table.name} · {table.recordType === 'ministry-lookup' ? 'Ministry lookup' : 'Aggregate profile'} · {rows.length.toLocaleString('en-CA')} matching source rows</caption><thead><tr>{table.columns.map(column => <th scope="col" key={column}>{column}</th>)}</tr></thead><tbody>{displayed.map((row, i) => <tr key={currentPage * 25 + i}>{row.map((cell, j) => <td key={j}>{cell === '' ? <span role="img" aria-label="Blank source field">—</span> : cell}</td>)}</tr>)}</tbody></table>
      {rows.length === 0 && <p>No matching source rows.</p>}
    </div>
    <div className="workforce__pagination"><button disabled={currentPage === 0} onClick={() => setPage(currentPage - 1)}>Previous</button><span aria-live="polite">Page {currentPage + 1} of {pageCount}</span><button disabled={currentPage + 1 >= pageCount} onClick={() => setPage(currentPage + 1)}>Next</button></div>
    <p className="workforce__scope"><a href={data.catalogueUrl} target="_blank" rel="noreferrer">BC Stats official catalogue and methodology links</a> · {data.license}. Demographic statistics come from corporate surveys; comparator data come from federal reports. No individual identities are inferred.</p>
  </section>
}
