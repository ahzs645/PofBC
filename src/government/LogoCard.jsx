// A body's logos, where the gallery holds them as vectors: a few drawn here, each a link to its page
// in Logos, and a link to the rest. A body with none — or only raster scans — shows no card.

import { useEffect, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'

export const LogoCard = ({ node, theme }) => {
  const [logos, setLogos] = useState(null)

  useEffect(() => {
    let live = true
    setLogos(null)
    import('../gallery/galleryLogos.js').then(({ logosFor }) => live && setLogos(logosFor(node.id, theme)), () => {})
    return () => { live = false }
  }, [node.id, theme])

  if (!logos) return null
  return (
    <section className="gov-card gov-logos" aria-labelledby="gov-logos-heading">
      <div className="gov-salaries__head">
        <h2 id="gov-logos-heading" className="gov-card__heading">Logos</h2>
        <SiteLink className="gov-salaries__open" to={{ view: 'gallery', logos: logos.collection }}>
          {logos.total > logos.entries.length ? `All ${logos.total} in Logos →` : 'Open in Logos →'}
        </SiteLink>
      </div>
      <div className="gov-logos__grid">
        {logos.entries.map((entry) => (
          <SiteLink key={entry.id} className="gov-logos__tile" to={{ view: 'gallery', logos: logos.collection, mark: entry.id }} title={entry.label} aria-label={`${entry.label} in Logos`}>
            <span
              className="gallery__art gov-logos__art"
              data-ground={entry.ground}
              data-image={entry.image || undefined}
              // Built by the gallery's own renderers; every value is escaped where written.
              dangerouslySetInnerHTML={{ __html: entry.html }}
            />
          </SiteLink>
        ))}
      </div>
    </section>
  )
}
