// Shows a current-era ministry mark.
//
// This used to fetch a finished file per ministry and so had states the historical lockup never
// had — loading, and failing to load. The mark and the alphabet now ship in the bundle, so it has
// neither: it draws from the wording it is given, synchronously, like every other lockup here.

import { renderCurrentSvg } from './currentMarks.js'
import { layoutLockup } from './currentLayout.js'

/**
 * @param {object} props
 * @param {string} props.text       The ministry name. A newline is a line break.
 * @param {string} props.language   'en' | 'fr'
 * @param {string} props.variant    One of the four official colourways.
 * @param {string} [props.background]
 * @param {number} [props.clearSpaceFactor]  Margin as a fraction of the lockup's own width.
 * @param {string} [props.title]    Accessible name.
 */
export const CurrentLockup = ({
  text, language, variant, background, clearSpaceFactor = 0, title, ...rest
}) => {
  const { box } = layoutLockup({ text, language })
  const padding = clearSpaceFactor * box.width
  const svg = renderCurrentSvg({ text, language, variant, background, clearSpaceFactor, title })

  return (
    <div
      className="current-lockup"
      style={{
        aspectRatio: `${box.width + padding * 2} / ${box.height + padding * 2}`
      }}
      role="img"
      aria-label={title}
      // Built here from this project's own artwork and metrics; there is no author-supplied markup
      // anywhere in it, and every interpolated value is escaped at the point it is written.
      dangerouslySetInnerHTML={{ __html: svg }}
      {...rest}
    />
  )
}
