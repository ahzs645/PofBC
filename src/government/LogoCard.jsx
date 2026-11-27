// Source vectors are previewed as before. Registered subjects also have a route to their evidence
// and acquisition work when only raster specimens, shared identity or source leads are held.

import { useEffect, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'

export const LogoCard = ({ node, theme }) => {
  const [record, setRecord] = useState(null)

  useEffect(() => {
    let live = true
    setRecord(null)
    Promise.all([import('../gallery/galleryLogos.js'), import('../gallery/identityCoverage.js')])
      .then(([{ logosFor }, { identitySubjectById }]) => live && setRecord({ logos: logosFor(node.id, theme), subject: identitySubjectById(node.id) }), () => {})
    return () => { live = false }
  }, [node.id, theme])

  const logos = record?.logos
  const subject = record?.subject
  if (!logos && !subject) return null
  return (
    <section className="gov-card gov-logos" aria-labelledby="gov-logos-heading">
      <div className="gov-salaries__head">
        <h2 id="gov-logos-heading" className="gov-card__heading">{logos ? 'Logos' : 'Identity collection'}</h2>
        {logos && <SiteLink className="gov-salaries__open" to={{ view: 'gallery', logos: logos.collection }}>
          {logos.collections.length === 1 && logos.total > logos.entries.length ? `All ${logos.total} in Logos →` : 'Open in Logos →'}
        </SiteLink>}
      </div>
      {logos && <div className="gov-logos__grid">
        {logos.entries.map((entry) => (
          <SiteLink key={entry.id} className="gov-logos__tile" to={{ view: 'gallery', logos: entry.collection, mark: entry.id }} title={entry.label} aria-label={`${entry.label} in Logos`}>
            <span
              className="gallery__art gov-logos__art"
              data-ground={entry.ground}
              data-image={entry.image || undefined}
              // Built by the gallery's own renderers; every value is escaped where written.
              dangerouslySetInnerHTML={{ __html: entry.html }}
            />
          </SiteLink>
        ))}
      </div>}
      {subject && <p className="gov-muted">
        {!logos && <>{subject.stateLabel}. </>}
        <SiteLink to={{ view: 'gallery', subject: subject.id }}>Open in the register →</SiteLink>
      </p>}
    </section>
  )
}
