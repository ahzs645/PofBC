// The generator's starting state.
//
// In a module of its own because both useLockupState and shareLink need it, and a share link is
// defined relative to these values — it carries only the fields that differ from them.

import { BCID } from '../current/currentMarks.js'
import { findMinistry } from '../current/ministries.js'
import { DEFAULT_CLEAR_SPACE, DEFAULT_MARK_ALIGNMENT } from '../logo/layouts.js'
import { BRAND_COLORS } from '../logo/logoColors.js'

export const DEFAULTS = {
  // Which identity. 'historical' builds the crest lockups from parts, 'flag' the BC-and-flag
  // lockup from the same wording and colours, and 'current' serves the Province's own ministry
  // marks unchanged — so almost nothing else on this list applies to that one.
  era: 'historical',
  // Current era only. Its background is kept apart from the historical one because the two eras
  // have different palettes — the crest era's forest green is not a BC identity colour, and
  // dragging it across produced blue type on green the moment you switched.
  language: 'en',
  currentMinistry: 'FOR',
  // The mark's wording. Newlines are line breaks, and the official names carry the ones the
  // Province set them with. It follows the ministry and language until edited.
  currentName: findMinistry('FOR').en,
  currentNameTouched: false,
  currentVariant: 'colour',
  currentVariantTouched: false,
  currentBackground: BCID.white,

  // Flag era only. The flag is drawn in its own three colours, or in one ink with the letters.
  flagColour: 'colour',

  layout: 'stacked',
  wordmark: true,
  // Local only, never shared: once the wordmark has been set deliberately, switching lockup stops
  // overriding it. See useLockupState.
  wordmarkTouched: false,
  // 'list' picks from the ministry list; 'manual' is free text. The two keep separate values, so
  // switching back and forth does not destroy whatever the other mode had.
  source: 'list',
  ministry: 'Ministry of Forests',
  manualMinistry: '',
  program: '',
  markColor: BRAND_COLORS.white,
  textColor: BRAND_COLORS.white,
  // Most lockups are one colour throughout, so the two move together until told otherwise.
  linkColors: true,
  background: BRAND_COLORS.green,
  clearSpace: DEFAULT_CLEAR_SPACE,
  // Only the lockups that set the mark beside the type use this; the others ignore it, but it is
  // kept across a switch so going away and coming back does not lose the choice.
  markAlign: DEFAULT_MARK_ALIGNMENT,
  // As with the wordmark: each lockup opens the way its own artwork sits until this is set by
  // hand, after which the choice travels with you. See lockupReducer.
  markAlignTouched: false,
  // Preview only — the surface the lockup is shown against, never part of the export, and not
  // carried in a share link.
  backdrop: 'auto'
}
