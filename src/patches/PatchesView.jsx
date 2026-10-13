// Patches: the patch library from the Patcher submodule (vendor/patcher, see README), grouped by
// sector and organization, each patch opening on a viewer that sews it as embroidery.
//
// The place is kept in the address bar (`?view=patches&org=bc-parks`, `?view=patches&patch=S25-O01`),
// so a link to an organization or to one patch opens it there.

import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { LIBRARY, findOrg, findPatch, orgsBySector } from 'patcher/library'
import { searchFor } from '../site/navigation.jsx'
import { PatchViewer } from './PatchViewer.jsx'
import './patches.css'

const SECTIONS = orgsBySector(LIBRARY)

const read = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const patch = findPatch(params.get('patch') ?? '') ? params.get('patch') : null
  const org = findOrg(params.get('org') ?? '') ? params.get('org') : null
  return { org, patch }
}

const write = ({ org, patch }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'patches')
  for (const [key, value] of Object.entries({ org, patch })) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  globalThis.history.replaceState(null, '', url)
}

/** Every word of the query somewhere in the patch's label, medium, organization or id. */
const matcher = (query) => {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean)
  if (!words.length) return null
  return (patch, org) => {
    const text = `${patch.label} ${patch.medium} ${org.name} ${patch.id}`.toLowerCase()
    return words.every((word) => text.includes(word))
  }
}

const isPlainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey

export const PatchesView = () => {
  const [place, setPlace] = useState(read)
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const cards = useRef({})

  const go = useCallback((next) => {
    setPlace(next)
    write(next)
  }, [])

  const sections = useMemo(() => {
    const matches = matcher(deferredQuery)
    return SECTIONS
      .map(({ sector, orgs }) => ({
        sector,
        orgs: orgs
          .filter((org) => !place.org || org.id === place.org)
          .map((org) => ({ org, patches: matches ? org.patches.filter((p) => matches(p, org)) : org.patches }))
          .filter(({ patches }) => patches.length > 0)
      }))
      .filter(({ orgs }) => orgs.length > 0)
  }, [deferredQuery, place.org])
  const shown = sections.reduce((n, { orgs }) => n + orgs.reduce((m, { patches }) => m + patches.length, 0), 0)

  const open = place.patch ? findPatch(place.patch) : null
  const openOrg = open ? findOrg(open.orgId) : null

  // Back from a patch lands on its card.
  const close = useCallback(() => {
    const id = place.patch
    go({ org: place.org, patch: null })
    requestAnimationFrame(() => cards.current[id]?.focus())
  }, [go, place.org, place.patch])

  useEffect(() => { if (!open) return; globalThis.scrollTo?.({ top: 0 }) }, [open])

  if (open) {
    const siblings = openOrg.patches
    const at = siblings.findIndex((p) => p.id === open.id)
    return (
      <PatchViewer
        key={open.id}
        patch={open}
        org={openOrg}
        position={{ index: at, count: siblings.length }}
        previous={at > 0 ? siblings[at - 1] : null}
        next={at < siblings.length - 1 ? siblings[at + 1] : null}
        onOpen={(patch) => go({ org: place.org, patch: patch.id })}
        onClose={close}
      />
    )
  }

  return (
    <section className="patches" aria-label="Patches">
      <div className="patches__intro">
        <h2>Patches</h2>
        <p>
          {LIBRARY.summary.patches} patches, badges and emblems from the {LIBRARY.source.name}, grouped by
          organization. Open one to see it sewn as an embroidered patch, and to download it for an
          embroidery machine.
        </p>
        <div className="patches__filters">
          <label className="patches__filter">
            <span>Organization</span>
            <select value={place.org ?? ''} onChange={(event) => go({ org: event.target.value || null, patch: null })}>
              <option value="">All {LIBRARY.summary.orgs} organizations</option>
              {SECTIONS.map(({ sector, orgs }) => (
                <optgroup key={sector.id} label={sector.name}>
                  {orgs.map((org) => <option key={org.id} value={org.id}>{org.name} ({org.count})</option>)}
                </optgroup>
              ))}
            </select>
          </label>
          <label className="patches__filter patches__filter--grow">
            <span>Search</span>
            <input
              type="search"
              value={query}
              placeholder="Sheriff, rocker, metal badge…"
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        </div>
        <p className="patches__note">{LIBRARY.source.note}</p>
      </div>

      {shown === 0 && <p className="patches__empty" role="status">No patches match “{query}”.</p>}

      {sections.map(({ sector, orgs }) => (
        <section key={sector.id} className="patches__sector" aria-labelledby={`sector-${sector.id}`}>
          <h3 id={`sector-${sector.id}`} className="patches__sector-name">{sector.name}</h3>
          {orgs.map(({ org, patches }) => (
            <section key={org.id} className="patches__org" aria-labelledby={`org-${org.id}`}>
              <header className="patches__org-head">
                <h4 id={`org-${org.id}`}>
                  <a
                    href={searchFor({ view: 'patches', org: org.id })}
                    onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ org: org.id, patch: null }) } }}
                  >
                    {org.name}
                  </a>
                </h4>
                <span className="patches__count">{patches.length === org.count ? org.count : `${patches.length} of ${org.count}`}</span>
                {org.description && <p>{org.description}</p>}
              </header>
              <div className="patches__grid">
                {patches.map((patch) => (
                  <a
                    key={patch.id}
                    ref={(element) => { cards.current[patch.id] = element }}
                    className="patches__card"
                    href={searchFor({ view: 'patches', org: place.org, patch: patch.id })}
                    onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ org: place.org, patch: patch.id }) } }}
                  >
                    <span className="patches__thumb">
                      <img src={patch.previewUrl} alt="" loading="lazy" decoding="async" />
                    </span>
                    <span className="patches__card-text">
                      <span className="patches__title">{patch.label}</span>
                      <span className="patches__medium">{patch.medium}</span>
                    </span>
                  </a>
                ))}
              </div>
            </section>
          ))}
        </section>
      ))}
    </section>
  )
}
