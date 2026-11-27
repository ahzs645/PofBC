// Departmental Logos: the index of departments, and each department's pages.
//
// Every page is an address (internalPlaces.js), reached through the site's navigation, so Back,
// Forward, a new tab and a reload all return to it. The view reads its page from the address when
// it opens — the App opens it afresh on every visit — and rewrites an older form of the address to
// the page's own, in place.

import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { ForestLogo } from './ForestArtwork.jsx'
import { FOREST_LOGOS } from './forestLogos.js'
import { DEPARTMENT_INDEX, departmentPlace, FORESTS, internalPlaceUrl, resolveInternalPlace } from './internalPlaces.js'
import { SiteLink } from '../site/navigation.jsx'
import './internal.css'

// The departments' marks are the gallery's own records, so they and their renderers load with it.
const DepartmentCollection = lazy(() => import('./DepartmentCollection.jsx'))
const DepartmentCover = lazy(() => import('./DepartmentCollection.jsx').then((module) => ({ default: module.DepartmentCover })))
const ForestsCollection = lazy(() => import('./ForestsCollection.jsx'))

const FOREST_COVER = FOREST_LOGOS.find(({ id }) => id === FORESTS)

/** A department on the index: its cover, its name, and what it holds, as one link. */
const DepartmentCard = ({ id, title, note }) => (
  <SiteLink to={departmentPlace(id)} className="gallery__collection" aria-label={`Open ${title}`}>
    <span className="gallery__art gallery__art--cover" data-ground="page">
      {id === FORESTS
        ? <ForestLogo item={FOREST_COVER} name={title} decorative />
        : <Suspense fallback={<span role="status">Loading logo…</span>}><DepartmentCover id={id} /></Suspense>}
    </span>
    <span className="gallery__collection-text">
      <span className="gallery__collection-title">{title} <span aria-hidden="true">→</span></span>
      <span className="gallery__note">{note}</span>
    </span>
  </SiteLink>
)

const DepartmentIndex = () => {
  const heading = useRef(null)
  useEffect(() => { heading.current?.focus({ preventScroll: true }) }, [])
  return (
    <section className="internal-logos gallery" aria-label="Departmental Logos">
      <div className="gallery__collection-head">
        <div>
          <h2 className="gallery__collection-heading" ref={heading} tabIndex={-1}>Departmental Logos</h2>
          <p className="gallery__note">Former departments, ministries and government branches · {DEPARTMENT_INDEX.length} departments</p>
        </div>
      </div>
      <div className="gallery__collections">
        {DEPARTMENT_INDEX.map((department) => <DepartmentCard key={department.id} {...department} />)}
      </div>
    </section>
  )
}

/** The page the address names; an older form of its address is rewritten to its own, in place. */
const placeInAddress = () => {
  const href = globalThis.location?.href
  const rewritten = href && internalPlaceUrl(href)
  if (rewritten) globalThis.history?.replaceState(globalThis.history.state, '', rewritten)
  return resolveInternalPlace(Object.fromEntries(new URLSearchParams(globalThis.location?.search ?? '')))
}

export const InternalLogosView = () => {
  // Read once: the App opens this view afresh for every page.
  const [{ department, mark, variant }] = useState(placeInAddress)
  if (department === FORESTS) {
    return <Suspense fallback={<p className="gallery__intro" role="status">Loading logos…</p>}><ForestsCollection logoId={mark} variantId={variant} /></Suspense>
  }
  if (department) {
    return <Suspense fallback={<p className="gallery__intro" role="status">Loading logos…</p>}><DepartmentCollection id={department} markId={mark} /></Suspense>
  }
  return <DepartmentIndex />
}
