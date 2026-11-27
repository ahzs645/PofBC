// The Department of Recreation and Conservation (1957–1976), in Departmental Logos.
//
// The marks are the gallery's own records (collections.js), drawn by the gallery's renderers, so a
// card here and the same mark's card under the Royal BC Museum or BC Parks cannot drift apart. The
// gallery no longer lists the collection; its links open here (movedGalleryPlaces.js).

import { useEffect, useRef } from 'react'
import { AboutCollection, AboutMark, EraSection, Timeline } from '../gallery/GalleryView.jsx'
import { SuppliedMarkView } from '../gallery/SuppliedMarkView.jsx'
import { CollectedMarkView } from '../gallery/CollectedMarkView.jsx'
import { collectionById, findGalleryEntry } from '../gallery/collections.js'
import { galleryHistoryOf } from '../gallery/galleryHistory.js'
import { tileArt } from '../gallery/tileArt.js'
import { RECREATION_COLLECTION, RECREATION_PLACE } from '../gallery/movedGalleryPlaces.js'
import { SiteLink, useNavigate } from '../site/navigation.jsx'
import { useSiteTheme } from '../site/useTheme.js'

const collection = collectionById(RECREATION_COLLECTION)
const SUBJECT = 'department-of-recreation-and-conservation'
const inCollection = (id) => collection.eras.some((era) => era.entries.some((entry) => entry.id === id))

/** The family's card on the first page of Departmental Logos: its cover, as the gallery drew it. */
export function RecreationCover() {
  const { name: theme } = useSiteTheme()
  return (
    <span
      className="gallery__art gallery__art--cover internal-logos__cover"
      data-ground="page"
      // Built by this project's own renderers; every value is escaped where written.
      dangerouslySetInnerHTML={{ __html: tileArt(findGalleryEntry(collection.cover), theme, { cover: true }) }}
    />
  )
}

const Back = ({ to, children }) => (
  <SiteLink className="internal-logos__back" to={to}><span aria-hidden="true">←</span> {children}</SiteLink>
)

export default function RecreationConservation({ markId }) {
  const { name: theme } = useSiteTheme()
  const navigate = useNavigate()
  const heading = useRef(null)
  const open = markId && inCollection(markId) ? findGalleryEntry(markId) : null
  const openMark = (id) => navigate({ ...RECREATION_PLACE, 'internal-logo': id })
  useEffect(() => { heading.current?.focus({ preventScroll: true }) }, [markId])

  if (open) {
    const era = collection.eras.find((each) => each.entries.some((entry) => entry.id === open.id))
    return (
      <section className="internal-logos gallery" aria-label="Departmental Logos">
        <nav className="gallery__crumbs" aria-label="Departmental Logos">
          <Back to={{ view: 'internal' }}>Departmental Logos</Back>
          <span aria-hidden="true">/</span>
          <SiteLink className="gallery__crumb" to={RECREATION_PLACE}>{collection.label}</SiteLink>
          <span aria-hidden="true">/</span>
          <span aria-current="page" ref={heading} tabIndex={-1}>{open.label}</span>
        </nav>
        {open.kind === 'collected'
          ? <CollectedMarkView key={open.id} entry={open} />
          : <SuppliedMarkView key={open.id} entry={open} family={open} onChooseVersion={openMark} />}
        {era && <EraSection era={era} theme={theme} onOpen={openMark} openId={open.id} />}
        <AboutMark identity={open.identity} drawing={open.caveat} />
      </section>
    )
  }

  return (
    <section className="internal-logos gallery" aria-label="Departmental Logos">
      <div className="internal-logos__intro">
        <Back to={{ view: 'internal' }}>Departmental Logos</Back>
        <h2 ref={heading} tabIndex={-1}>{collection.label}</h2>
        <p>{collection.body} · marks of {collection.years}</p>
      </div>
      <p className="gallery__intro">{collection.intro}</p>
      <p className="gallery__intro">
        <SiteLink to={{ view: 'gallery', subject: SUBJECT }}>The department in the identity register →</SiteLink>
        {' · '}
        <SiteLink to={{ view: 'gallery', logos: 'royal-bc-museum' }}>Royal BC Museum →</SiteLink>
        {' · '}
        <SiteLink to={{ view: 'gallery', logos: 'bc-parks' }}>BC Parks →</SiteLink>
      </p>
      <Timeline
        eras={collection.eras}
        collectionId={collection.id}
        history={galleryHistoryOf(collection.historyId ?? collection.graphNode)}
        onPick={(id) => document.getElementById(`era-${id}`)?.scrollIntoView({ block: 'start' })}
        onChooseCollection={(id) => navigate({ view: 'gallery', logos: id })}
      />
      {collection.eras.map((era) => <EraSection key={era.id} era={era} theme={theme} onOpen={openMark} />)}
      <AboutCollection collection={collection} />
    </section>
  )
}
