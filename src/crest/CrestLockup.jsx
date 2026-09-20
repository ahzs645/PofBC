// Shows a crest-identity lockup.
//
// Drawn from parts on every render, like the flag and the crest-era lockups and unlike the current
// era's marks, so it has no loading state and any wording works.

import { renderCrestSvg } from './renderCrestSvg.js'

export const CrestLockup = ({
  arrangement, placement, ministry, extra, bold, align, ministrySize, extraStep,
  markColor, textColor, background, clearSpaceFactor = 0, title, ...rest
}) => {
  const { svg, box } = renderCrestSvg({
    arrangement, placement, ministry, extra, bold, align, ministrySize, extraStep,
    markColor, textColor, background, clearSpaceFactor, title
  })

  return (
    <div
      className="current-lockup"
      style={{ aspectRatio: `${box.width} / ${box.height}` }}
      role="img"
      aria-label={title}
      // Built here from this project's own artwork; every value is escaped where it is written.
      dangerouslySetInnerHTML={{ __html: svg }}
      {...rest}
    />
  )
}
