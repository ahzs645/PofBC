// Patches: the patch library from the Patcher submodule (vendor/patcher, see README), grouped by
// sector and organization, each patch opening on a viewer that sews it as embroidery. The same view
// shows the library's metal and leather badges as Badges (`?view=badges`).
//
// The place is kept in the address bar (`?view=patches&org=bc-parks`, `?view=patches&patch=S25-O01`),
// so a link to an organization or to one patch opens it there.

import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { cardLabel, cardOf, findPatch, isCard, orgsBySector, variantsOf } from 'patcher/library'
import { searchFor } from '../site/navigation.jsx'
import { PatchViewer, photosOf } from './PatchViewer.jsx'
import './patches.css'

/** Each collection's view and wording. The view id is also the site view (`?view=`). */
const COLLECTIONS = {
  patches: {
    view: 'patches',
    title: 'Patches',
    placeholder: 'Sheriff, rocker, Parks…',
    noun: 'patches'
  },
  badges: {
    view: 'badges',
    title: 'Badges',
    placeholder: 'Park Ranger, cap badge…',
    noun: 'badges'
  }
}

const sectionsOf = (collection) => orgsBySector(collection)

const read = (collection, sections) => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  // findPatch follows an atlas id merged or absorbed into another patch (S27-O01, R22-O01) to it.
  const patch = findPatch(params.get('patch') ?? '')
  const orgs = sections.flatMap((s) => s.orgs)
  return {
    org: orgs.some((o) => o.id === params.get('org')) ? params.get('org') : null,
    patch: patch?.collection === collection ? patch.id : null
  }
}

const write = (view, { org, patch }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', view)
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
    // A card answers for all its variants.
    const designs = variantsOf(patch)?.members ?? [patch]
    const text = `${cardLabel(patch)} ${designs.map((d) => `${d.label} ${d.variant ?? ''} ${d.id}`).join(' ')} ${patch.medium} ${org.name}`.toLowerCase()
    return words.every((word) => text.includes(word))
  }
}

const isPlainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey

/** @param {{ collection?: 'patches' | 'badges' }} props */
export const PatchesView = ({ collection = 'patches' }) => {
  const copy = COLLECTIONS[collection]
  const SECTIONS = useMemo(() => sectionsOf(collection), [collection])
  // Counted as cards: a variant group is one.
  const total = SECTIONS.reduce((n, s) => n + s.orgs.reduce((m, o) => m + o.patches.filter(isCard).length, 0), 0)
  const orgCount = SECTIONS.reduce((n, s) => n + s.orgs.length, 0)
  const [place, setPlace] = useState(() => read(collection, SECTIONS))
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const cards = useRef({})

  const go = useCallback((next) => {
    setPlace(next)
    write(copy.view, next)
  }, [copy.view])

  const sections = useMemo(() => {
    const matches = matcher(deferredQuery)
    return SECTIONS
      .map(({ sector, orgs }) => ({
        sector,
        orgs: orgs
          .filter((org) => !place.org || org.id === place.org)
          .map((org) => {
            const cards = org.patches.filter(isCard)
            return { org, patches: matches ? cards.filter((p) => matches(p, org)) : cards }
          })
          .filter(({ patches }) => patches.length > 0)
      }))
      .filter(({ orgs }) => orgs.length > 0)
  }, [SECTIONS, deferredQuery, place.org])
  const shown = sections.reduce((n, { orgs }) => n + orgs.reduce((m, { patches }) => m + patches.length, 0), 0)

  const open = place.patch ? findPatch(place.patch) : null
  // Stepping goes through the organization's designs in this collection only.
  const openOrg = open ? SECTIONS.flatMap((s) => s.orgs).find((o) => o.id === open.orgId) : null

  // Back from a patch lands on its card.
  const close = useCallback(() => {
    const id = place.patch
    go({ org: place.org, patch: null })
    requestAnimationFrame(() => cards.current[id]?.focus())
  }, [go, place.org, place.patch])

  useEffect(() => { if (!open) return; globalThis.scrollTo?.({ top: 0 }) }, [open])

  if (open) {
    // Stepping goes card to card; a variant sits at its card's place.
    const siblings = openOrg.patches.filter(isCard)
    const at = siblings.findIndex((p) => p.id === cardOf(open).id)
    return (
      <PatchViewer
        key={cardOf(open).id}
        patch={open}
        org={openOrg}
        position={{ index: at, count: siblings.length }}
        previous={at > 0 ? siblings[at - 1] : null}
        next={at < siblings.length - 1 ? siblings[at + 1] : null}
        onOpen={(patch) => go({ org: place.org, patch: patch.id })}
        onClose={close}
        noun={copy.noun}
      />
    )
  }

  return (
    <section className="patches" aria-label={copy.title}>
      <div className="patches__intro">
        <h2>{copy.title} <span className="patches__count">{total}</span></h2>
        <div className="patches__filters">
          <label className="patches__filter">
            <span>Organization</span>
            <select value={place.org ?? ''} onChange={(event) => go({ org: event.target.value || null, patch: null })}>
              <option value="">All {orgCount} organizations</option>
              {SECTIONS.map(({ sector, orgs }) => (
                <optgroup key={sector.id} label={sector.name}>
                  {orgs.map((org) => <option key={org.id} value={org.id}>{org.name} ({org.patches.filter(isCard).length})</option>)}
                </optgroup>
              ))}
            </select>
          </label>
          <label className="patches__filter patches__filter--grow">
            <span>Search</span>
            <input
              type="search"
              value={query}
              placeholder={copy.placeholder}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        </div>
      </div>

      {shown === 0 && <p className="patches__empty" role="status">No {copy.noun} match “{query}”.</p>}

      {sections.map(({ sector, orgs }) => (
        <section key={sector.id} className="patches__sector" aria-labelledby={`sector-${sector.id}`}>
          <h3 id={`sector-${sector.id}`} className="patches__sector-name">{sector.name}</h3>
          {orgs.map(({ org, patches }) => (
            <section key={org.id} className="patches__org" aria-labelledby={`org-${org.id}`}>
              <header className="patches__org-head">
                <h4 id={`org-${org.id}`}>
                  <a
                    href={searchFor({ view: copy.view, org: org.id })}
                    onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ org: org.id, patch: null }) } }}
                  >
                    {org.name}
                  </a>
                </h4>
                <span className="patches__count">{patches.length === org.patches.filter(isCard).length ? patches.length : `${patches.length} of ${org.patches.filter(isCard).length}`}</span>
                {/* The organization's description is written for its patches. */}
                {org.description && copy.view === 'patches' && <p>{org.description}</p>}
              </header>
              <div className="patches__grid">
                {patches.map((patch) => (
                  <a
                    key={patch.id}
                    ref={(element) => { cards.current[patch.id] = element }}
                    className="patches__card"
                    href={searchFor({ view: copy.view, org: place.org, patch: patch.id })}
                    onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ org: place.org, patch: patch.id }) } }}
                  >
                    <span className="patches__thumb">
                      <img src={patch.previewUrl} alt="" loading="lazy" decoding="async" />
                    </span>
                    <span className="patches__card-text">
                      <span className="patches__title">{cardLabel(patch)}</span>
                      <span className="patches__medium">
                        {patch.medium}
                        {variantsOf(patch) && ` · ${variantsOf(patch).members.length} variants`}
                        {photosOf(patch).length > 1 && ` · seen in ${photosOf(patch).length} photos`}
                      </span>
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
