// The Patcher catalogue can be browsed by organization or by an explicitly assigned template
// family. Related templates retain separate designs, variants, source records and stable links.

import { lazy, Suspense, useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from 'react'
import { TEMPLATE_FAMILIES, cardLabel, cardOf, findPatch, isCard, orgsBySector, templateFamilyOf, variantsOf } from 'patcher/library'
import { searchFor } from '../site/navigation.jsx'
import { writeHistory } from '../site/browserHistory.js'
import {
  catalogueCards, filterCatalogue, groupCatalogueByTemplate, isGeneratedColourway,
  patchPlaceParams, patchPlaceUrl, readPatchPlace, sourcePhotoCount, variantCount
} from './patchCatalogue.js'
import './patches.css'

// Browsing needs only metadata and previews. Load the digitizer and export tools when a patch opens.
const PatchViewer = lazy(() => import('./PatchViewer.jsx').then((module) => ({ default: module.PatchViewer })))

const COLLECTIONS = {
  patches: { view: 'patches', title: 'Patches', placeholder: 'Sheriff, rocker, Parks…', noun: 'patches' },
  badges: { view: 'badges', title: 'Badges', placeholder: 'Park Ranger, cap badge…', noun: 'badges' }
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
  const totalVariants = variantCount(catalogue)
  const matchingVariants = variantCount(shown)
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
    return (
      <Suspense fallback={<section className="patches__intro" aria-label="Loading patch">
        <button type="button" className="button button--ghost" onClick={close}>← All {copy.noun}</button>
        <p role="status">Loading the patch viewer…</p>
      </section>}>
        <PatchViewer
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
  const renderCard = (entry) => {
    const { patch, selected, org, members, label, template } = entry
    const generated = members.filter(isGeneratedColourway).length
    const sourceCount = sourcePhotoCount(selected)
    const selectedVariant = selected.id !== patch.id
    return (
      <a
        key={patch.id}
        ref={(element) => { cardElements.current[patch.id] = element }}
        className="patches__card"
        href={hrefFor({ patch: selected.id })}
        onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); go({ patch: selected.id }) } }}
      >
        <span className="patches__thumb">
          {selected.previewUrl && <img src={selected.previewUrl} alt="" loading="lazy" decoding="async" />}
        </span>
        <span className="patches__card-text">
          {place.group === 'template' && <span className="patches__owner">{org.name}</span>}
          <span className="patches__title">{label}</span>
          {selectedVariant && <span className="patches__matched">Showing {selected.variant || selected.label}</span>}
          <span className="patches__medium">
            {selected.medium}
            {members.length > 1 && ` · ${countLabel(members.length, 'variant')}`}
            {sourceCount > 1 && ` · seen in ${sourceCount} sources`}
          </span>
          {place.group !== 'template' && template && <span className="patches__template-name">{template.label}</span>}
          {generated > 0 && <span className="patches__evidence">{isGeneratedColourway(selected) ? 'Generated colourway' : `Includes ${countLabel(generated, 'generated colourway')}`}</span>}
        </span>
      </a>
    )
  }

  return (
    <section className="patches" aria-label={copy.title}>
      <div className="patches__intro">
        <h2>{copy.title}</h2>
        <p>{countLabel(totalVariants, 'variant')} in {countLabel(catalogue.length, 'catalogue card')} · {countLabel(organizations.length, 'organization')}</p>
        <div className="patches__filters">
          <label className="patches__filter patches__filter--compact">
            <span>Group by</span>
            <select value={place.group} onChange={(event) => selectFilter({ group: event.target.value })}>
              <option value="organization">Organization</option>
              <option value="template">Template family</option>
            </select>
          </label>
          <label className="patches__filter">
            <span>Organization</span>
            <select value={place.org ?? ''} onChange={(event) => selectFilter({ org: event.target.value || null })}>
              <option value="">All {organizations.length} organizations</option>
              {sectors.map(({ sector, orgs }) => (
                <optgroup key={sector.id} label={sector.name}>
                  {orgs.map((org) => <option key={org.id} value={org.id}>{org.name} ({org.patches.length} variants)</option>)}
                </optgroup>
              ))}
            </select>
          </label>
          <label className="patches__filter">
            <span>Template family</span>
            <select value={place.family ?? ''} onChange={(event) => selectFilter({ family: event.target.value || null })}>
              <option value="">All template families</option>
              {familySections.map(({ family, cards }) => <option key={family.id} value={family.id}>{family.label} ({variantCount(cards)} variants)</option>)}
            </select>
          </label>
          <label className="patches__filter patches__filter--grow">
            <span>Search</span>
            <input type="search" value={place.q} placeholder={copy.placeholder} onChange={(event) => selectFilter({ q: event.target.value })} />
          </label>
        </div>
        {place.group === 'template' && <p className="patches__group-note">Template families bring related layouts together. Each edition keeps its wording, source evidence and variants.</p>}
        {filtering && <div className="patches__results">
          <span role="status">{countLabel(shown.length, 'card')} · {countLabel(matchingVariants, 'matching variant')}</span>
          <button type="button" className="button button--ghost" onClick={() => selectFilter({ org: null, family: null, q: '' })}>Clear filters</button>
        </div>}
      </div>

      {shown.length === 0 && <p className="patches__empty" role="status">No {copy.noun} match these filters.</p>}

      {place.group === 'template'
        ? templates.map(({ family, cards }) => (
          <section key={family.id} className="patches__sector" aria-labelledby={`template-${family.id}`}>
            <header className="patches__family-head">
              <h3 id={`template-${family.id}`}>{family.label}</h3>
              <span className="patches__count">{countLabel(cards.length, 'card')} · {countLabel(variantCount(cards), 'variant')}</span>
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
                      <a href={hrefFor({ org: org.id, patch: null })} onClick={(event) => { if (isPlainClick(event)) { event.preventDefault(); selectFilter({ org: org.id }) } }}>{org.name}</a>
                    </h4>
                    <span className="patches__count">{countLabel(cards.length, 'card')} · {countLabel(variantCount(cards), 'variant')}</span>
                    {org.description && copy.view === 'patches' && <p>{org.description}</p>}
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
