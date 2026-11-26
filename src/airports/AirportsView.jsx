import { useState } from 'react'
import priorityResearch from '../../research/identity/airports-2026-11-25/branding-sources.json'
import communityResearch from '../../research/identity/airports-2026-11-25/community-branding-sources.json'
import inventory from './facilities.json'
import { AIRPORT_BODIES, airportCollectionId } from './airportArtwork.js'
import { assetUrl, collectedEntriesOf } from '../gallery/collectedCollections.js'
import { collectedDisplay, defaultCollectedAsset } from '../gallery/tileArt.js'
import { SiteLink } from '../site/navigation.jsx'
import { TabList } from '../site/ui/TabList.jsx'
import { useSiteTheme } from '../site/useTheme.js'
import './airports.css'

const research = new Map([...priorityResearch.airports, ...communityResearch.airports]
  .map((record) => [record.locationIdentifier, record]))
const brands = new Map(AIRPORT_BODIES.map((body) => {
  const code = body.id.slice('airport-'.length).toUpperCase()
  const entries = collectedEntriesOf(body.id)
  return [code, { cover: entries.find(({ id }) => id === body.cover), count: entries.length }]
}))

const types = { land: 'Land airport or airstrip', water: 'Water aerodrome', heli: 'Heliport or helipad', other: 'Unclassified' }
const statusLabels = {
  'operator-brand-only': 'Operator identity',
  'shared-identity': 'Shared branding',
  'carrier-brand-only': 'Carrier branding',
  'no-separate-mark-found': 'Separate mark unverified',
  'branding-in-development': 'Branding in development'
}
const tabs = [{ id: 'artwork', label: 'Artwork' }, { id: 'directory', label: 'Directory' }]
const pageSize = 36
const fold = (value) => value.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '')

const facilities = inventory.map(({ code, name, iata, locality, ...site }) => {
  const finding = research.get(code)
  const title = finding?.name ?? name
  const codes = [...new Set([finding?.iata ?? iata, code].filter(Boolean))]
  const search = fold([title, name, locality, ...codes, finding?.publisher].filter(Boolean).join(' '))
  return { ...site, code, title, locality, codes, search, finding, brand: brands.get(code) }
}).sort((a, b) => a.title.localeCompare(b.title))

const published = facilities.filter(({ brand }) => brand)
const listed = facilities.filter(({ lead }) => !lead)
const hasLead = facilities.some(({ lead }) => lead)

const galleryLink = ({ code }) => ({ view: 'gallery', logos: airportCollectionId(code) })

const AirportCard = ({ facility, theme }) => {
  const { brand, codes, finding, title } = facility
  const art = defaultCollectedAsset(brand.cover, theme)
  const display = collectedDisplay(art, theme)
  return (
    <SiteLink className="airport-card" to={galleryLink(facility)}>
      <div className="airport-card__art" data-plate={display?.plate ? 'light' : !display ? art.darkBackground ? 'dark' : 'light' : undefined}>
        <img src={assetUrl(display?.file ?? art.preview ?? art.file)} alt="" loading="lazy" />
      </div>
      <div className="airport-card__description">
        <span className="airport-card__code">{codes.join(' · ')}</span>
        <strong>{title}</strong>
        <span className="airport-card__detail">
          {statusLabels[finding?.brandingStatus] ?? (brand.count === 1 ? '1 design' : `${brand.count} designs`)}
        </span>
      </div>
    </SiteLink>
  )
}

const DirectoryRow = ({ facility }) => {
  const { codes, finding, brand, group, lead, locality, title } = facility
  const shared = finding?.relatedLocationIdentifier
  const link = brand ? galleryLink(facility) : shared && brands.has(shared) ? galleryLink({ code: shared }) : null
  return (
    <tr>
      <th scope="row">
        {link ? <SiteLink to={link}>{title}</SiteLink> : title}
        {locality && <span className="airports__location">{locality}</span>}
      </th>
      <td className="airports__codes">{codes.join(' · ') || '—'}</td>
      <td>{types[group]}{lead && <span className="airports__location">Supplemental listing</span>}</td>
      <td>
        {link ? <SiteLink to={link}>{statusLabels[finding?.brandingStatus] ?? 'Artwork'}</SiteLink>
          : finding ? <a href={finding.sourcePageUrl}>{statusLabels[finding.brandingStatus] ?? 'Source lead'}</a>
            : '—'}
      </td>
    </tr>
  )
}

export const AirportsView = () => {
  const { name: theme } = useSiteTheme()
  const [tab, setTab] = useState('artwork')
  const [query, setQuery] = useState('')
  const [type, setType] = useState('')
  const [includeLeads, setIncludeLeads] = useState(false)
  const [limit, setLimit] = useState(pageSize)
  const update = (setter) => (value) => {
    setter(value)
    setLimit(pageSize)
  }
  const words = fold(query).trim().split(/\s+/)
  const candidates = tab === 'artwork' ? published : includeLeads ? facilities : listed
  const matches = candidates.filter(({ search, group }) => (!type || group === type) && words.every((word) => search.includes(word)))
  const visible = matches.slice(0, limit)

  return (
    <main className="airports">
      <header className="airports__header">
        <div>
          <h2>British Columbia airports</h2>
          <p>Published airport identities, with original artwork, colourways and a province-wide facility directory.</p>
        </div>
        <div className="airports__totals">
          <span><strong>{published.length}</strong> with artwork</span>
          <span><strong>{listed.length}</strong> provincial records</span>
        </div>
      </header>
      <TabList idPrefix="airport-view" label="Airport collection" tabs={tabs} selected={tab} onChange={update(setTab)} />
      <section role="tabpanel" id={`airport-view-panel-${tab}`} aria-labelledby={`airport-view-tab-${tab}`}>
        <div className="airports__tools">
          <label>Search airports
            <input type="search" placeholder="Name, community or airport code" value={query} onChange={(event) => update(setQuery)(event.target.value)} />
          </label>
          <label>Facility type
            <select value={type} onChange={(event) => update(setType)(event.target.value)}>
              <option value="">All types</option>
              {Object.entries(types).map(([key, label]) => <option value={key} key={key}>{label}</option>)}
            </select>
          </label>
          {tab === 'directory' && hasLead && (
            <label className="airports__supplement">
              <input type="checkbox" checked={includeLeads} onChange={(event) => update(setIncludeLeads)(event.target.checked)} />
              Include supplemental listings
            </label>
          )}
          <p role="status">{matches.length} {matches.length === 1 ? 'facility' : 'facilities'}</p>
        </div>
        {visible.length ? (tab === 'artwork'
          ? <div className="airports__grid">{visible.map((facility) => <AirportCard key={facility.id} facility={facility} theme={theme} />)}</div>
          : <div className="airports__table-wrap">
            <table className="airports__table">
              <thead><tr><th scope="col">Facility</th><th scope="col">Codes</th><th scope="col">Type</th><th scope="col">Branding</th></tr></thead>
              <tbody>{visible.map((facility) => <DirectoryRow key={facility.id} facility={facility} />)}</tbody>
            </table>
          </div>) : <p className="airports__empty">No airports match these filters.</p>}
        {visible.length < matches.length && (
          <button className="button button--ghost airports__more" type="button" onClick={() => setLimit(limit + pageSize)}>Show more airports</button>
        )}
      </section>
      <footer className="airports__source">
        Facility records from the <a href="https://catalogue.data.gov.bc.ca/dataset/bc-airports">BC Airports data catalogue</a>.
        Supplemental listings from <a href="https://ourairports.com/data/">OurAirports</a> may include duplicate locations.
      </footer>
    </main>
  )
}
