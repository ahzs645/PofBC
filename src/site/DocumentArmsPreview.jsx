import { useId, useState } from 'react'
import { renderDocumentArmsSvg } from '../documentArms/renderDocumentArmsSvg.js'
import { documentArmsReferences, DOCUMENT_ARMS_RESEARCH_URL } from '../documentArms/evidence.js'
import splitReference from '../../research/identity/document-arms-2026-11-13/reference/split-serif.png'
import governmentReference from '../../research/identity/document-arms-2026-11-13/reference/government-caption.png'
import blackletterReference from '../../research/identity/document-arms-2026-11-13/reference/blackletter-grant.png'
import miningCoverDetail from '../../research/identity/document-arms-2026-11-14/reference/mining-1954-cover-detail.png'
import miningCoverPage from '../../research/identity/document-arms-2026-11-14/reference/mining-1954-cover-page.png'
import miningTitleDetail from '../../research/identity/document-arms-2026-11-14/reference/mining-1954-title-detail.png'
import miningTitlePage from '../../research/identity/document-arms-2026-11-14/reference/mining-1954-title-page.png'
import official1906 from '../../research/identity/document-arms-2026-11-14/reference/1906-arms.jpg'
import order1121Detail from '../../research/identity/document-arms-2026-11-14/reference/oic-1121-heading-detail.png'
import order1121Page from '../../research/identity/document-arms-2026-11-14/reference/oic-1121-heading-page.png'
import order832Detail from '../../research/identity/document-arms-2026-11-14/reference/oic-832-heading-detail.png'
import order832Page from '../../research/identity/document-arms-2026-11-14/reference/oic-832-heading-page.png'
import grantDetail from '../../research/identity/document-arms-2026-11-14/reference/oic-1121-grant-detail.png'
import grantPage from '../../research/identity/document-arms-2026-11-14/reference/oic-1121-grant-page.png'

// Assets stay in this lazy preview module; the geometry and export pipeline never import them.
const REFERENCE_IMAGES = {
  'supplied-split-serif': { detail: splitReference },
  'supplied-government': { detail: governmentReference },
  'supplied-blackletter': { detail: blackletterReference },
  'mining-1954-cover': { detail: miningCoverDetail, page: miningCoverPage },
  'mining-1954-title': { detail: miningTitleDetail, page: miningTitlePage },
  'official-1906': { detail: official1906 },
  'oic-1121-heading': { detail: order1121Detail, page: order1121Page },
  'oic-832-heading': { detail: order832Detail, page: order832Page },
  'oic-1121-grant': { detail: grantDetail, page: grantPage },
}

export default function DocumentArmsPreview({ lockup }) {
  const { svg, box } = renderDocumentArmsSvg({
    layout: lockup.documentLayout,
    markColor: lockup.documentMarkColor,
    textColor: lockup.documentTextColor,
    background: lockup.documentBackground,
    clearSpaceFactor: lockup.clearSpaceFactor,
    title: 'British Columbia historical document arms — reconstruction study'
  })
  return (
    <div
      className="current-lockup"
      style={{ aspectRatio: `${box.width} / ${box.height}` }}
      role="img"
      aria-label="Historical document arms reconstruction study"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}

export function DocumentArmsReference({ layout }) {
  const [selected, setSelected] = useState(null)
  const [wholePage, setWholePage] = useState(false)
  const selectId = useId()
  const references = documentArmsReferences(layout)
  const reference = references.find(({ id }) => id === selected) || references[0]
  const images = REFERENCE_IMAGES[reference.id]
  const showPage = wholePage && Boolean(images.page)
  const image = showPage ? images.page : images.detail
  return (
    <div className="document-arms-reference">
      <p className="document-arms-reference__status">Reconstruction study</p>
      <p>The shared plate artwork differs from the original engravings. The lettering and spacing remain studies.</p>
      <details open className="document-arms-source">
        <summary>Compare with source evidence</summary>
        <div className="document-arms-source__controls">
          <label htmlFor={selectId}>Reference specimen</label>
          <select id={selectId} value={reference.id} onChange={(event) => {
            setSelected(event.target.value)
            setWholePage(false)
          }}>
            {references.map(({ id, label }) => <option key={id} value={id}>{label}</option>)}
          </select>
          {images.page && (
            <div className="document-arms-source__view" role="group" aria-label="Reference view">
              <button type="button" className="button button--ghost" aria-pressed={!showPage} onClick={() => setWholePage(false)}>Detail</button>
              <button type="button" className="button button--ghost" aria-pressed={showPage} onClick={() => setWholePage(true)}>Whole page</button>
            </div>
          )}
        </div>
        <div className="document-arms-source__record" data-specimen={reference.id}>
          <p className="document-arms-source__status">{reference.status}</p>
          <p className="document-arms-source__date">{reference.date}</p>
          <figure data-whole-page={showPage || undefined}>
            <a href={image} target="_blank" rel="noreferrer" aria-label="Open full reference image">
              <img src={image} alt={showPage ? reference.fullAlt : reference.alt} loading="lazy" />
            </a>
            <figcaption>{reference.description}</figcaption>
          </figure>
          <p>{reference.limitation}</p>
          {reference.sourceUrl && <a href={reference.sourceUrl} target="_blank" rel="noreferrer">{reference.sourceLabel}</a>}
        </div>
        <p className="document-arms-source__note">Reference images are for comparison only. Downloads contain the vector study shown above. <a href={DOCUMENT_ARMS_RESEARCH_URL} target="_blank" rel="noreferrer">Research and retained originals</a></p>
      </details>
    </div>
  )
}
