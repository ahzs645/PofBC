import { useEffect, useMemo, useRef, useState } from 'react'
import { count, loadJson, usePages } from './common.jsx'
import { linkLookup } from './nameLinks.js'
import { nameOnly, personKey } from './people.js'
import { chooseNameSearchBucket, searchNameSearchDocuments } from './nameSearch.js'

const readLinks = (shard, reload) => loadJson(`salaries/links/${shard}.json.gzip`, { reload }).catch((error) => {
  // A surname with no reviewed links deliberately has no link file. Other failures must remain
  // visible/retryable: silently ignoring them would change which records belong on the card.
  if (error.message === '404') return { links: [] }
  throw error
})

/** Discover names independently of surname storage, then hydrate only the current result page. */
export const NameSearchResults = ({ query, index, sector, range, onOpen, renderCard, describeGroup, initials = [], initialsLoading = false, initialsFailed = false, onRetryInitials }) => {
  const [manifest, setManifest] = useState(null)
  const [manifestFailed, setManifestFailed] = useState(false)
  const [contextChanged, setContextChanged] = useState(false)
  const [directoryVersion, setDirectoryVersion] = useState(0)
  const [bucketState, setBucketState] = useState(null)
  const [pageState, setPageState] = useState(null)
  const [pageVersion, setPageVersion] = useState(0)
  const retriedPage = useRef(0)
  const contextKey = JSON.stringify({ years: index.years, employers: index.employers.map((employer) => employer[3]) })

  useEffect(() => {
    let live = true
    setManifestFailed(false)
    setContextChanged(false)
    loadJson('salaries/search/index.json', { reload: directoryVersion > 0 }).then((value) => {
      if (value.schemaVersion !== 1 || !value.buckets) throw new Error('Unsupported name directory')
      // Numeric employer/period references must use the same published tables. An open tab
      // spanning a deployment must reload rather than label a new row with old metadata.
      if (JSON.stringify(value.context) !== contextKey) {
        if (live) { setManifest(null); setContextChanged(true) }
        return
      }
      if (live) setManifest(value)
    }).catch(() => { if (live) setManifestFailed(true) })
    return () => { live = false }
  }, [directoryVersion, contextKey])

  const bucket = manifest ? chooseNameSearchBucket(query, manifest) : null
  const file = bucket ? manifest.buckets[bucket].file : null
  useEffect(() => {
    if (!file) return undefined
    let live = true
    setBucketState({ file, loading: true })
    loadJson(`salaries/search/${file}`, { reload: directoryVersion > 0 }).then((documents) => {
      if (!Array.isArray(documents)) throw new Error('Invalid name directory')
      if (live) setBucketState({ file, documents })
    }).catch(() => { if (live) setBucketState({ file, failed: true }) })
    return () => { live = false }
  }, [file, directoryVersion])

  const directoryFailed = manifestFailed || Boolean(file && bucketState?.file === file && bucketState.failed)
  const directoryReady = Boolean(manifest && (!file || (bucketState?.file === file && bucketState.documents)))
  const employerIds = useMemo(() => sector === 'all' ? null : new Set(index.employers.flatMap((employer, at) => employer[1] === sector ? [at] : [])), [index, sector])
  const rangeKey = range?.join(':') ?? ''
  const yearIds = useMemo(() => range ? new Set(index.years.flatMap((_, at) => at >= range[0] && at <= range[1] ? [at] : [])) : null, [index, rangeKey]) // eslint-disable-line react-hooks/exhaustive-deps
  const matches = useMemo(() => directoryReady && file
    ? searchNameSearchDocuments(bucketState.documents, query, { employerIds, yearIds }) : [],
  [directoryReady, file, bucketState, query, employerIds, yearIds])
  const reset = `${query}|${sector}|${rangeKey}`
  const page = usePages(matches, 24, reset)
  const pageKey = JSON.stringify([reset, page.items.map((item) => [item.key, item.employerIds])])
  const recordShards = [...new Set(page.items.flatMap((item) => item.recordShards))].sort()
  const shardKey = recordShards.join('|')

  useEffect(() => {
    if (!recordShards.length) return undefined
    let live = true
    const reload = retriedPage.current !== pageVersion
    retriedPage.current = pageVersion
    setPageState({ shardKey, loading: true })
    Promise.all(recordShards.map(async (shard) => {
      const [rows, published] = await Promise.all([loadJson(`salaries/people/${shard}.json.gzip`, { reload }), readLinks(shard, reload)])
      return { rows, links: linkLookup(published, index.employers) }
    })).then((parts) => {
      if (live) setPageState({ shardKey, rows: parts.flatMap((part) => part.rows), links: new Map(parts.flatMap((part) => [...part.links])) })
    }).catch(() => { if (live) setPageState({ shardKey, failed: true }) })
    return () => { live = false }
  }, [shardKey, index, pageVersion]) // eslint-disable-line react-hooks/exhaustive-deps

  const hydrated = useMemo(() => {
    if (pageState?.shardKey !== shardKey || !pageState.rows) return []
    const wanted = new Map(page.items.map((item) => [item.key, { item, rows: [] }]))
    for (const row of pageState.rows) {
      const link = pageState.links.get(`${row[4]}|${personKey(row[0])}`)
      const found = wanted.get(link?.key ?? personKey(row[0]))
      if (!found || !found.item.employerIds.includes(row[4]) || (yearIds && !yearIds.has(row[5]))) continue
      found.rows.push(row)
    }
    return [...wanted.values()].map(({ item, rows }) => {
      if (!rows.length) return null
      const linkedName = rows.map((row) => pageState.links.get(`${row[4]}|${personKey(row[0])}`)).find((link) => link?.key === item.key)?.name
      const group = describeGroup(item.key, rows, linkedName, index)
      // A full reviewed name can be displayed beside an initials-only latest record. Its display
      // disclosure comes from its own spelling, not the latest record's abbreviated source.
      const spelling = rows.find((row) => nameOnly(row[0]) === nameOnly(group.name))
      return { ...group, tier: item.tier, displayDisclosure: spelling ? index.sources?.[spelling[6]]?.nameDisclosure : null }
    })
  }, [pageState, shardKey, pageKey, index, yearIds, describeGroup]) // eslint-disable-line react-hooks/exhaustive-deps

  const pageFailed = pageState?.shardKey === shardKey && pageState.failed
  const pageReady = page.items.length === 0 || (hydrated.length === page.items.length && hydrated.every(Boolean))
  const missingRows = hydrated.some((item) => !item)
  const directKeys = new Set(matches.map((item) => item.key))
  const initialsOnly = initials.filter((item) => !directKeys.has(item.key))
  const filtered = Boolean(range) || sector !== 'all'

  return (
    <section aria-labelledby="salaries-people-results" aria-busy={!contextChanged && !directoryFailed && !pageFailed && !missingRows && (!directoryReady || !pageReady)}>
      <div className="salaries__head">
        <h2 id="salaries-people-results" className="salaries__title">People</h2>
        <p className="salaries__meta" role="status">{directoryReady ? count(matches.length, 'name', 'names') : contextChanged ? 'Data updated' : directoryFailed ? 'Search unavailable' : 'Searching names…'}</p>
      </div>
      <p className="salaries__hint salaries__hint--small">Matches any part of a name, in any order. Whole surnames come first, then other complete words, then partial matches.</p>
      {contextChanged && <p className="salaries__hint" role="alert">The salary data has been updated since this page opened. <button type="button" onClick={() => globalThis.location.reload()}>Reload search</button></p>}
      {directoryFailed && <p className="salaries__hint" role="alert">The name search could not be loaded. Employer and position results are still available. <button type="button" onClick={() => setDirectoryVersion((value) => value + 1)}>Retry name search</button></p>}
      {directoryReady && !directoryFailed && matches.length === 0 && !initialsLoading && <p className="salaries__hint">No disclosed name matches “{query.trim()}”{filtered ? ' with these filters' : ''}. Try fewer letters or another part of the name{filtered ? ', or clear the period and sector filters' : ''}.</p>}
      {directoryReady && page.items.length > 0 && !pageReady && !pageFailed && !missingRows && <p className="salaries__hint" role="status">Loading records for this page…</p>}
      {(pageFailed || missingRows) && <p className="salaries__hint" role="alert">The records for this page could not all be loaded. <button type="button" onClick={() => setPageVersion((value) => value + 1)}>Retry these results</button></p>}
      {pageReady && <div className="salaries__grid">{hydrated.map((each) => renderCard(each, onOpen))}</div>}
      {page.pager}
      {initialsFailed && <p className="salaries__hint" role="alert">Some initials-only alternatives could not be loaded. <button type="button" onClick={onRetryInitials}>Retry initials search</button></p>}
      {directoryReady && initialsOnly.length > 0 && (
        <>
          <h3 className="salaries__title salaries__title--spaced">Initials only</h3>
          <p className="salaries__hint salaries__hint--small">These records disclose initials compatible with the name you typed. Each may be the person you mean, or someone else.</p>
          <div className="salaries__grid salaries__grid--spaced">{initialsOnly.slice(0, 12).map((each) => renderCard(each, onOpen))}</div>
          {initialsOnly.length > 12 && <p className="salaries__hint salaries__hint--small">And {initialsOnly.length - 12} more; use “Surname, Given” to narrow them.</p>}
        </>
      )}
    </section>
  )
}
