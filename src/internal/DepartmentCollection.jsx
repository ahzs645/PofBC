// A former department, ministry or government branch, in Departmental Logos.
//
// The marks are the gallery's own records (collections.js), drawn and opened by the gallery's own
// components, so a mark here and the same mark anywhere else in the gallery cannot drift apart. The
// gallery no longer lists these collections; its links to them open here (movedGalleryPlaces.js).
//
// The pages are the gallery's pages, in the gallery's order: the trail, the collection's head, its
// links and history, its timeline and eras, and its account; a mark's page has the trail, the
// timeline with the mark's era marked, the mark, its links, its history and its account. Only the
// trail's first step differs: Departmental Logos, not All logos.

import { useEffect, useRef } from 'react'
import { AboutCollection, AboutMark, CollectionHead, EraSection, GalleryHistory, OpenMark, Tile, Timeline } from '../gallery/GalleryView.jsx'
import { IdentityCollectionLinks } from '../gallery/IdentityCoverage.jsx'
import { collectionById, entriesOf, findGalleryEntry } from '../gallery/collections.js'
import { galleryHistoryOf } from '../gallery/galleryHistory.js'
import { tileArt } from '../gallery/tileArt.js'
import { DEPARTMENTAL_ROOT, departmentalPlace } from '../gallery/movedGalleryPlaces.js'
import { Breadcrumbs } from '../site/Breadcrumbs.jsx'
import { searchFor, SiteLink, useNavigate } from '../site/navigation.jsx'
import { useSiteTheme } from '../site/useTheme.js'

/** A department's cover on the first page of Departmental Logos, as the gallery draws it. */
export function DepartmentCover({ id }) {
  const { name: theme } = useSiteTheme()
  const collection = collectionById(id)
  const cover = findGalleryEntry(collection.cover) ?? entriesOf(collection)[0]
  return (
    <span
      className="internal-logos__cover"
      // Built by this project's own renderers; every value is escaped where written.
      dangerouslySetInnerHTML={{ __html: tileArt(cover, theme, { cover: true }) }}
    />
  )
}

// Gallery collections that hold copies of a department's marks under their own ids.
const SHARED_WITH = {
  'recreation-conservation': [['royal-bc-museum', 'Royal BC Museum'], ['bc-parks', 'BC Parks']]
}

export default function DepartmentCollection({ id, markId }) {
  const { name: theme } = useSiteTheme()
  const navigate = useNavigate()
  const heading = useRef(null)
  // An era picked on a mark's timeline opens the collection's page at that era.
  const eraWanted = useRef(null)
  const collection = collectionById(id)
  const entries = entriesOf(collection)
  const open = markId && entries.some((entry) => entry.id === markId) ? findGalleryEntry(markId) : null
  const place = departmentalPlace(collection.id)
  const openMark = (mark) => navigate(departmentalPlace(collection.id, mark))
  const markHref = (mark) => searchFor(departmentalPlace(collection.id, mark))
  const historyId = collection.historyId ?? collection.graphNode
  const history = galleryHistoryOf(historyId)
  const openCollection = (other) => navigate({ view: 'gallery', logos: other })
  const openSubject = (subject) => navigate({ view: 'gallery', subject })
  const openGovernment = (node, year) => navigate({ view: 'government', node, ...(year ? { year } : {}) })
  const showEra = (era) => document.getElementById(`era-${era}`)?.scrollIntoView({ block: 'start' })
  useEffect(() => {
    if (!open && eraWanted.current) {
      showEra(eraWanted.current)
      eraWanted.current = null
    } else heading.current?.focus({ preventScroll: true })
  }, [markId, open])

  const timeline = collection.eras && (
    <Timeline eras={collection.eras} collectionId={collection.id} history={history} opensCollection={Boolean(open)}
      current={open ? collection.eras.find((era) => era.entries.some((entry) => entry.id === open.id))?.id : undefined}
      onPick={(era) => {
        if (!open) return showEra(era)
        eraWanted.current = era
        navigate(place)
      }}
      onChooseCollection={openCollection} />
  )
  const links = (
    <IdentityCollectionLinks collectionId={collection.id} entryId={open?.id} graphShown={open ? undefined : collection.graphNode} history={history}
      onOpenCollection={openCollection} onOpenSubject={openSubject} onOpenGovernment={openGovernment} />
  )

  if (open) {
    return (
      <section className="internal-logos gallery" aria-label="Departmental Logos">
        <Breadcrumbs label="Departmental Logos" currentRef={heading}
          // A department's one mark under the department's own name is named once, as the gallery does.
          steps={open.label === collection.label
            ? [DEPARTMENTAL_ROOT, { label: collection.label }]
            : [DEPARTMENTAL_ROOT, { label: collection.label, to: place }, { label: open.label }]} />
        {timeline}
        <OpenMark entry={open} openId={markId} onChooseVersion={openMark} />
        {links}
        <GalleryHistory hasTimeline={Boolean(collection.eras)} id={historyId} theme={theme} onChooseCollection={openCollection} onOpenSubject={openSubject} successorsOnly />
        <AboutMark identity={open.identity} drawing={open.caveat} />
      </section>
    )
  }

  return (
    <section className="internal-logos gallery" aria-label="Departmental Logos">
      <Breadcrumbs label="Departmental Logos" steps={[DEPARTMENTAL_ROOT, { label: collection.label }]} />
      <CollectionHead collection={collection} onOpenGovernment={openGovernment} headingRef={heading} />
      <p className="gallery__intro">{collection.intro}</p>
      {links}
      {SHARED_WITH[collection.id] && (
        <p className="gallery__intro">
          Also in the gallery:{' '}
          {SHARED_WITH[collection.id].map(([other, label], at) => (
            <span key={other}>{at > 0 && ' · '}<SiteLink to={{ view: 'gallery', logos: other }}>{label} →</SiteLink></span>
          ))}
        </p>
      )}
      <GalleryHistory id={historyId} theme={theme} onChooseCollection={openCollection} onOpenSubject={openSubject} hasTimeline={Boolean(collection.eras)} showPreviews />
      {timeline}
      {collection.eras
        ? collection.eras.map((era) => <EraSection key={era.id} era={era} theme={theme} onOpen={openMark} hrefFor={markHref} />)
        : (
          <div className="gallery__tiles">
            {entries.map((entry) => <Tile key={entry.id} entry={entry} theme={theme} href={markHref(entry.id)} onOpen={() => openMark(entry.id)} />)}
          </div>
          )}
      <AboutCollection collection={collection} />
    </section>
  )
}
