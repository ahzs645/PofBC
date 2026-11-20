// The Patcher catalogue can be browsed by organization or by an explicitly assigned template
// family. Related templates retain separate designs, variants, source records and stable links.

import { lazy, Suspense, useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { TEMPLATE_FAMILIES, cardLabel, cardOf, findPatch, isCard, orgsBySector, templateFamilyOf, variantsOf } from 'patcher/library'
import { searchFor } from '../site/navigation.jsx'
import { writeHistory } from '../site/browserHistory.js'
import {
  catalogueCards, filterCatalogue, groupCatalogueByTemplate,
  patchPlaceParams, patchPlaceUrl, plainLabel, readPatchPlace, sourcePhotoCount, splitLabel
} from './patchCatalogue.js'
import './patches.css'
import '../posters/shelfTools.css'
import { Select } from '../site/ui/Select.jsx'
import { holdScroll } from '../site/holdScroll.js'

// Browsing needs only metadata and previews. Load the digitizer and export tools when a patch opens.
const PatchViewer = lazy(() => import('./PatchViewer.jsx').then((module) => ({ default: module.PatchViewer })))
// Badges are built in 3D rather than sewn (src/badges, preliminary).
const BadgeViewer = lazy(() => import('../badges/BadgeViewer.jsx').then((module) => ({ default: module.BadgeViewer })))

const COLLECTIONS = {
  patches: { view: 'patches', title: 'Patches', placeholder: 'Sheriff, rocker, Parks…', noun: 'patches', one: 'patch' },
  badges: { view: 'badges', title: 'Badges', placeholder: 'Park Ranger, cap badge…', noun: 'badges', one: 'badge' }
}

const isPlainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
const countLabel = (count, noun) => `${count} ${noun}${count === 1 ? '' : 's'}`

/** @param {{ collection?: 'patches' | 'badges' }} props */
export const PatchesView = ({ collection = 'patches' }) => {
  const copy = COLLECTIONS[collection]
  const sectors = useMemo(() => orgsBySector(collection), [collection])
  const catalogue = useMemo(() => catalogueCards(sectors, { isCard, variantsOf, cardLabel, templateFamilyOf }), [sectors])
  const allCards = useMemo(() => filterCatalogue(catalogue), [catalogue])
  const familySections = useMemo(() => groupCatalogueByTemplate(allCards, TEMPLATE_FAMILIES), [allCards])
  const organizations = useMemo(() => sectors.flatMap(({ orgs }) => orgs), [sectors])
  const read = useCallback(() => readPatchPlace(globalThis.location?.search ?? '', {
    collection,
    orgIds: organizations.map(({ id }) => id),
    familyIds: familySections.map(({ family }) => family.id),
    findPatch
  }), [collection, organizations, familySections])
  const [place, setPlace] = useState(read)
  const currentPlace = useRef(place)
  const deferredQuery = useDeferredValue(place.q)
  const cardElements = useRef({})
  const tools = useRef(null)

  const go = useCallback((update, { replace = false } = {}) => {
    const next = { ...currentPlace.current, ...update }
    currentPlace.current = next
    setPlace(next)
    if (globalThis.location?.href) writeHistory(patchPlaceUrl(globalThis.location.href, copy.view, next), { replace })
  }, [copy.view])

  useEffect(() => {
    const restore = () => {
      const next = read()
      currentPlace.current = next
      setPlace(next)
    }
    restore()
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [read])

  const shown = useMemo(() => filterCatalogue(catalogue, { q: deferredQuery, org: place.org, family: place.family }), [catalogue, deferredQuery, place.org, place.family])
  const templates = useMemo(() => groupCatalogueByTemplate(shown, TEMPLATE_FAMILIES), [shown])
  const open = place.patch ? findPatch(place.patch) : null
  const openOrg = open ? organizations.find((org) => org.id === open.orgId) : null
  const filtering = Boolean(place.org || place.family || deferredQuery.trim())

  const close = useCallback(() => {
    const selected = findPatch(currentPlace.current.patch)
    const id = selected ? cardOf(selected).id : currentPlace.current.patch
    go({ patch: null })
    requestAnimationFrame(() => cardElements.current[id]?.focus())
  }, [go])

  // Opening a patch starts at its top; switching between a card's variants stays where it is.
  const openCard = open ? cardOf(open).id : null
  useEffect(() => { if (!openCard) return; globalThis.scrollTo?.({ top: 0 }) }, [openCard])

  if (open && openOrg) {
    // Preserve organization-based stepping, scoped to the current filters when the open card is
    // among them. A direct link outside those filters can still navigate its organization.
    const cardId = cardOf(open).id
    const visibleSiblings = shown.filter(({ org }) => org.id === openOrg.id)
    const siblings = visibleSiblings.some(({ patch }) => patch.id === cardId)
      ? visibleSiblings
      : allCards.filter(({ org }) => org.id === openOrg.id)
    const at = siblings.findIndex(({ patch }) => patch.id === cardId)
    const Viewer = collection === 'badges' ? BadgeViewer : PatchViewer
    return (
      <Suspense fallback={<section className="patches__intro" aria-label="Loading patch">
        <button type="button" className="button button--ghost" onClick={close}>← All {copy.noun}</button>
        <p role="status">Loading the {collection === 'badges' ? 'badge' : 'patch'} viewer…</p>
      </section>}>
        <Viewer
          key={cardId}
          patch={open}
          org={openOrg}
          position={{ index: at, count: siblings.length }}
          previous={at > 0 ? siblings[at - 1].selected : null}
          next={at < siblings.length - 1 ? siblings[at + 1].selected : null}
          onOpen={(patch) => go({ patch: patch.id })}
          onClose={close}
          noun={copy.noun}
        />
      </Suspense>
    )
  }

  const hrefFor = (update) => searchFor(patchPlaceParams(copy.view, { ...place, ...update }))
  const selectFilter = (update) => go({ ...update, patch: null }, { replace: true })
  const regroup = (group) => {
    if (group !== place.group) holdScroll(tools.current)
    selectFilter({ group })
  }
  const clear = () => {
    holdScroll(tools.current)
    selectFilter({ org: null, family: null, q: '' })
  }
  const renderCard = (entry) => {
    const { patch, selected, org, members, label, template } = entry
    const name = splitLabel(label)
    const sourceCount = sourcePhotoCount(selected)
    const selectedVariant = selected.id !== patch.id
    return (
      <a
        key={patch.id}
        ref={(element) => { cardElements.current[patch.id] = element }}
        className="patches__card"
        // The template family and the count of source photographs are on the patch's own page; a
        // card says them only when asked.
        title={[place.group !== 'template' && template?.label, sourceCount > 1 && `seen in ${sourceCount} sources`].filter(Boolean).join(' · ') || undefined}
        href={hrefFor({ patch: selected.id })}
        onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ patch: selected.id }) } }}
      >
        <span className="patches__thumb">
          {selected.previewUrl && <img src={selected.previewUrl} alt="" loading="lazy" decoding="async" />}
        </span>
        <span className="patches__card-text">
          {place.group === 'template' && <span className="patches__owner">{org.name}</span>}
          {/* The library's "Wording — what it is" as a title over a smaller line. */}
          <span className="patches__title">{name.title}</span>
          {name.detail && <span className="patches__detail">{name.detail}</span>}
          {selectedVariant && <span className="patches__matched">Showing {selected.variant || plainLabel(selected.label)}</span>}
          <span className="patches__medium">
            {[selected.medium, selected.finish].filter(Boolean).join(' · ')}
            {members.length > 1 && ` · ${countLabel(members.length, 'variant')}`}
          </span>
        </span>
      </a>
    )
  }

  return (
    <section className="patches" aria-label={copy.title}>
      {/* The same toolbar as the posters' (shelfTools.css): grouping, filters, search, count. */}
      <div className="shelf-tools" role="group" aria-label={`Browse the ${copy.noun}`} ref={tools}>
        <div className="shelf-tools__toggle" role="group" aria-label="Group by">
          <button type="button" aria-pressed={place.group !== 'template'} onClick={() => regroup('organization')}>By organization</button>
          <button type="button" aria-pressed={place.group === 'template'} onClick={() => regroup('template')}>By template</button>
        </div>
        <label className="shelf-tools__filter">
          <span>Organization</span>
          <Select keepPlace value={place.org ?? ''} onChange={(value) => selectFilter({ org: value || null })}>
            <option value="">All</option>
            {sectors.map(({ sector, orgs }) => (
              <optgroup key={sector.id} label={sector.name}>
                {orgs.map((org) => <option key={org.id} value={org.id}>{org.name}</option>)}
              </optgroup>
            ))}
          </Select>
        </label>
        <label className="shelf-tools__filter">
          <span>Template</span>
          <Select keepPlace value={place.family ?? ''} onChange={(value) => selectFilter({ family: value || null })}>
            <option value="">All</option>
            {familySections.map(({ family }) => <option key={family.id} value={family.id}>{family.label}</option>)}
          </Select>
        </label>
        <input type="search" className="shelf-tools__search" aria-label={`Search the ${copy.noun}`} value={place.q} placeholder={copy.placeholder} onChange={(event) => selectFilter({ q: event.target.value })} />
        <p className="shelf-tools__count" role="status">
          {filtering ? `${shown.length} of ${catalogue.length}` : catalogue.length} {shown.length === 1 && filtering ? copy.one : copy.noun}
          {filtering && <> · <button type="button" className="shelf-tools__clear" onClick={clear}>Clear filters</button></>}
        </p>
      </div>

      {shown.length === 0 && <p className="patches__empty" role="status">No {copy.noun} match these filters.</p>}

      {place.group === 'template'
        ? templates.map(({ family, cards }) => (
          <section key={family.id} className="patches__sector" aria-labelledby={`template-${family.id}`}>
            <header className="patches__family-head">
              <h3 id={`template-${family.id}`}>{family.label}</h3>
              <span className="patches__count">{cards.length}</span>
              {family.description && <p>{family.description}</p>}
            </header>
            <div className="patches__grid">{cards.map(renderCard)}</div>
          </section>
        ))
        : sectors.map(({ sector, orgs }) => {
          const visibleOrgs = orgs.map((org) => ({ org, cards: shown.filter((entry) => entry.org.id === org.id) })).filter(({ cards }) => cards.length)
          if (!visibleOrgs.length) return null
          return (
            <section key={sector.id} className="patches__sector" aria-labelledby={`sector-${sector.id}`}>
              <h3 id={`sector-${sector.id}`} className="patches__sector-name">{sector.name}</h3>
              {visibleOrgs.map(({ org, cards }) => (
                <section key={org.id} className="patches__org" aria-labelledby={`org-${org.id}`}>
                  <header className="patches__org-head">
                    <h4 id={`org-${org.id}`}>
                      {/* Narrows the catalogue to this organization: the ones above it go, and its
                          heading stays under the finger as far as the page allows (holdScroll.js). */}
                      <a href={hrefFor({ org: org.id, patch: null })} onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); holdScroll(event.currentTarget); selectFilter({ org: org.id }) } }}>{org.name}</a>
                    </h4>
                    <span className="patches__count">{cards.length}</span>
                  </header>
                  <div className="patches__grid">{cards.map(renderCard)}</div>
                </section>
              ))}
            </section>
          )
        })}
    </section>
  )
}
