// A former department, ministry or government branch, in Departmental Logos.
//
// The marks are the gallery's own records (collections.js), drawn and opened by the gallery's own
// components, so a mark here and the same mark anywhere else in the gallery cannot drift apart. The
// gallery no longer lists these collections; its links to them open here (movedGalleryPlaces.js).

import { useEffect, useRef } from 'react'
import { AboutCollection, AboutMark, EraSection, OpenMark, Tile, Timeline } from '../gallery/GalleryView.jsx'
import { IdentityCollectionLinks } from '../gallery/IdentityCoverage.jsx'
import { collectionById, entriesOf, findGalleryEntry } from '../gallery/collections.js'
import { galleryHistoryOf } from '../gallery/galleryHistory.js'
import { tileArt } from '../gallery/tileArt.js'
import { departmentalPlace } from '../gallery/movedGalleryPlaces.js'
import { SiteLink, useNavigate } from '../site/navigation.jsx'
import { useSiteTheme } from '../site/useTheme.js'

/** A family's card on the first page of Departmental Logos: its cover, as the gallery draws it. */
export function DepartmentCover({ id }) {
  const { name: theme } = useSiteTheme()
  const collection = collectionById(id)
  const cover = findGalleryEntry(collection.cover) ?? entriesOf(collection)[0]
  return (
    <span
      className="gallery__art gallery__art--cover internal-logos__cover"
      data-ground="page"
      // Built by this project's own renderers; every value is escaped where written.
      dangerouslySetInnerHTML={{ __html: tileArt(cover, theme, { cover: true }) }}
    />
  )
}

// Gallery collections that hold copies of a department's marks under their own ids.
const SHARED_WITH = {
  'recreation-conservation': [['royal-bc-museum', 'Royal BC Museum'], ['bc-parks', 'BC Parks']]
}

const Back = ({ to, children }) => (
  <SiteLink className="internal-logos__back" to={to}><span aria-hidden="true">←</span> {children}</SiteLink>
)

export default function DepartmentCollection({ id, markId }) {
  const { name: theme } = useSiteTheme()
  const navigate = useNavigate()
  const heading = useRef(null)
  const collection = collectionById(id)
  const entries = entriesOf(collection)
  const open = markId && entries.some((entry) => entry.id === markId) ? findGalleryEntry(markId) : null
  const place = departmentalPlace(collection.id)
  const openMark = (mark) => navigate(departmentalPlace(collection.id, mark))
  const history = galleryHistoryOf(collection.historyId ?? collection.graphNode)
  const links = (
    <IdentityCollectionLinks collectionId={collection.id} entryId={open?.id} history={history}
      onOpenCollection={(other) => navigate({ view: 'gallery', logos: other })}
      onOpenSubject={(subject) => navigate({ view: 'gallery', subject })}
      onOpenGovernment={(node, year) => navigate({ view: 'government', node, ...(year ? { year } : {}) })} />
  )
  useEffect(() => { heading.current?.focus({ preventScroll: true }) }, [markId])

  if (open) {
    const era = collection.eras?.find((each) => each.entries.some((entry) => entry.id === open.id))
    return (
      <section className="internal-logos gallery" aria-label="Departmental Logos">
        <nav className="gallery__crumbs" aria-label="Departmental Logos">
          <Back to={{ view: 'internal' }}>Departmental Logos</Back>
          <span aria-hidden="true">/</span>
          <SiteLink className="gallery__crumb" to={place}>{collection.label}</SiteLink>
          <span aria-hidden="true">/</span>
          <span aria-current="page" ref={heading} tabIndex={-1}>{open.label}</span>
        </nav>
        <OpenMark entry={open} openId={markId} onChooseVersion={openMark} />
        {era && era.entries.length > 1 && <EraSection era={era} theme={theme} onOpen={openMark} openId={open.id} />}
        {links}
        <AboutMark identity={open.identity} drawing={open.caveat} />
      </section>
    )
  }

  return (
    <section className="internal-logos gallery" aria-label="Departmental Logos">
      <div className="internal-logos__intro">
        <Back to={{ view: 'internal' }}>Departmental Logos</Back>
        <h2 ref={heading} tabIndex={-1}>{collection.label}</h2>
        <p>{collection.body} · {collection.years}</p>
      </div>
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
      {collection.eras
        ? (
          <>
            {collection.eras.length > 1 && (
              <Timeline eras={collection.eras} collectionId={collection.id} history={history}
                onPick={(era) => document.getElementById(`era-${era}`)?.scrollIntoView({ block: 'start' })}
                onChooseCollection={(other) => navigate({ view: 'gallery', logos: other })} />
            )}
            {collection.eras.map((era) => <EraSection key={era.id} era={era} theme={theme} onOpen={openMark} />)}
          </>
          )
        : (
          <div className="gallery__tiles">
            {entries.map((entry) => <Tile key={entry.id} entry={entry} theme={theme} onOpen={() => openMark(entry.id)} />)}
          </div>
          )}
      <AboutCollection collection={collection} />
    </section>
  )
}
