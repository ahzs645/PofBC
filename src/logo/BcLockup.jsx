// React wrapper around the string renderer.
//
// The markup is produced by exactly the same call the exporter makes and injected wholesale,
// rather than being rebuilt as React elements. That is deliberate: two implementations of the same
// drawing would eventually disagree, and the one thing this component must guarantee is that what
// someone approves on screen is what lands in their download.
//
// The injected string is generated — the mark from artwork/, the type escaped by escapeXml — so
// there is no path for author-supplied text to become markup.

import { renderLockupMarkup, resolveLockup } from './renderLogoSvg.js'
import { TRANSPARENT } from './logoColors.js'

/** The attributes a caller may reasonably want to put on the <svg> itself. */
const DOM_PROPS = new Set(['className', 'style', 'id', 'width', 'height', 'onClick', 'tabIndex', 'role'])

/**
 * @param {object} props
 * @param {'stacked'|'centred'|'horizontal'} [props.layout]
 * @param {boolean} [props.wordmark]     Show "Province of British Columbia".
 * @param {string} [props.ministry]
 * @param {string} [props.program]
 * @param {string} [props.color]         Mark and text colour, when they share one.
 * @param {string} [props.markColor]     The mark on its own.
 * @param {string} [props.textColor]     The type on its own.
 * @param {string} [props.background]    'none' for transparent, or any colour.
 * @param {number} [props.padding]       Margin around the lockup, in artwork units.
 * @param {string} [props.markAlign]     'top' | 'centre' | 'bottom', where the lockup sets the
 *                                       mark beside the type.
 * @param {string} [props.title]         Accessible name; pass null for a decorative lockup.
 */
export const BcLockup = ({
  layout = 'stacked',
  wordmark = true,
  ministry = '',
  program = '',
  color,
  markColor,
  textColor,
  background,
  padding,
  markAlign,
  title,
  ...rest
}) => {
  // Only genuine DOM attributes reach the element. Callers pass this component a state object, and
  // twice now a field added to that object has ended up as a stray attribute on the <svg> — so
  // unrecognised props are dropped here rather than forwarded on trust.
  const passthrough = Object.fromEntries(
    Object.entries(rest).filter(([key]) => DOM_PROPS.has(key) || key.startsWith('aria-') || key.startsWith('data-'))
  )

  const options = {
    layout, wordmark, ministry, program, color, markColor, textColor, background, padding, markAlign
  }
  const resolved = resolveLockup(options)
  const { viewBox } = resolved

  const markup = renderLockupMarkup({ ...options, resolved })
  const hasBackground = resolved.background && resolved.background !== TRANSPARENT

  // A decorative lockup (title === null) is hidden from assistive technology entirely; otherwise
  // the <title> is what a screen reader announces in place of the image.
  const label = title === undefined ? resolved.description : title

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`}
      role={label ? 'img' : 'presentation'}
      aria-hidden={label ? undefined : 'true'}
      {...passthrough}
    >
      {label ? <title>{label}</title> : null}
      {hasBackground
        ? (
          <rect
            x={viewBox.x}
            y={viewBox.y}
            width={viewBox.width}
            height={viewBox.height}
            fill={resolved.background}
          />
          )
        : null}
      <g dangerouslySetInnerHTML={{ __html: markup }} />
    </svg>
  )
}
