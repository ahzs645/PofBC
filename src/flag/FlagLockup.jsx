// Shows the flag identity's lockup.
//
// Like the crest era and unlike the current one, this is drawn from parts on every render — the
// flag artwork, the BC letters and the ministry wording — so it has no loading state and any
// wording works.

import { renderFlagSvg } from './renderFlagSvg.js'

/**
 * @param {object} props
 * @param {string} props.ministry      The wording beneath the letters. Newlines break lines.
 * @param {string} props.letterColor   The BC letters.
 * @param {string} props.textColor     The wording.
 * @param {string} [props.flagColour]  'colour' for the flag's own three, 'ink' for one.
 * @param {string} [props.background]
 * @param {number} [props.clearSpaceFactor]
 * @param {string} [props.title]
 */
export const FlagLockup = ({
  ministry, letterColor, textColor, flagColour, background, clearSpaceFactor = 0, title, ...rest
}) => {
  const { svg, box } = renderFlagSvg({
    ministry, letterColor, textColor, flagColour, background, clearSpaceFactor, title
  })

  return (
    <div
      className="current-lockup"
      style={{ aspectRatio: `${box.width} / ${box.height}` }}
      role="img"
      aria-label={title}
      // Built here from this project's own artwork and metrics; every interpolated value is
      // escaped where it is written.
      dangerouslySetInnerHTML={{ __html: svg }}
      {...rest}
    />
  )
}
