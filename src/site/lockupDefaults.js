// The generator's starting state.
//
// In a module of its own because both useLockupState and shareLink need it, and a share link is
// defined relative to these values — it carries only the fields that differ from them.

import { DEFAULT_CLEAR_SPACE, DEFAULT_MARK_ALIGNMENT } from '../logo/layouts.js'
import { BRAND_COLORS } from '../logo/logoColors.js'

export const DEFAULTS = {
  // Which identity. 'historical' builds the crest lockups from parts; 'current' serves the
  // Province's own ministry marks unchanged, so almost nothing else on this list applies to it.
  era: 'historical',
  // Current era only.
  language: 'en',
  currentMinistry: 'FOR',
  currentVariant: 'colour',

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
