import { renderDocumentArmsSvg } from '../documentArms/renderDocumentArmsSvg.js'
import splitReference from '../../research/identity/document-arms-2026-11-13/reference/split-serif.png'
import governmentReference from '../../research/identity/document-arms-2026-11-13/reference/government-caption.png'
import blackletterReference from '../../research/identity/document-arms-2026-11-13/reference/blackletter-grant.png'

const REFERENCES = {
  'split-serif': {
    src: splitReference,
    alt: 'Supplied document heading: BRITISH and COLUMBIA on either side of the earlier arms.',
    caption: 'Supplied document heading · date not established'
  },
  government: {
    src: governmentReference,
    alt: 'Supplied Order in Council 1121 heading with arms and the government caption, dated 4 May 1978.',
    caption: 'Supplied Order in Council 1121 · 4 May 1978 visible on the scan'
  },
  'split-blackletter': {
    src: blackletterReference,
    alt: 'Supplied Crown grant heading: British Columbia in blackletter, with arms between the words.',
    caption: 'Supplied Crown grant heading · date not established'
  }
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
  const reference = REFERENCES[layout]
  return (
    <div className="document-arms-reference">
      <p className="document-arms-reference__status">Reconstruction study</p>
      <p>The shared plate artwork differs from the original engravings. The lettering and spacing are studies, not verified period specifications.</p>
      {reference && (
        <details open>
          <summary>Compare with the supplied reference</summary>
          <figure>
            <a href={reference.src} target="_blank" rel="noreferrer" aria-label="Open full reference image">
              <img src={reference.src} alt={reference.alt} loading="lazy" />
            </a>
            <figcaption>{reference.caption}. Reference only; not included in the export.</figcaption>
          </figure>
        </details>
      )}
    </div>
  )
}
