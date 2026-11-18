// The rules that keep the generator's state coherent.
//
// Pure functions, deliberately free of React, so the behaviour that is easy to get subtly wrong —
// when one field should drag another along, and when it should stop — can be tested directly
// rather than through a rendered component.

import { recommendedVariant } from '../current/currentVariants.js'
import { findMinistry } from '../current/ministries.js'
import { recommendedPalette } from '../flag/flagPalettes.js'
import { defaultMarkAlignment, getLayout } from '../logo/layouts.js'
import { BRAND_COLORS, TRANSPARENT, resolveColor } from '../logo/logoColors.js'
import { codeForName, wordingFor } from './ministryLink.js'

const COLOUR_FIELDS = {
  historical: ['markColor', 'textColor'],
  flag: ['flagMarkColor', 'flagTextColor'],
  crest: ['crestMarkColor', 'crestTextColor'],
  document: ['documentMarkColor', 'documentTextColor']
}

// Keep the public `linkColors` control for the active identity, remembering its setting when
// leaving. This local map is not part of shared configurations: a link carries only its identity.
// Remembering the link is as important as retaining the two colours. Otherwise linking another
// identity would hide the independently chosen lettering colour on return.
const mergeColourLinks = (current, patch) => {
  const next = { ...current, ...patch }
  const previousEra = current.era ?? 'historical'
  const era = next.era ?? 'historical'
  const colourLinks = { ...current.colourLinks, [previousEra]: current.linkColors }
  next.linkColors = patch.linkColors ?? (era === previousEra
    ? current.linkColors
    : colourLinks[era] ?? true)
  next.colourLinks = { ...colourLinks, [era]: next.linkColors }
  return next
}

/**
 * Applies a patch, then the rules that follow from it.
 *
 * @param {object} current
 * @param {object} patch
 * @returns {object} The next state.
 */
export const applyUpdate = (current, patch) => {
  const next = mergeColourLinks(current, patch)

  // Linking is a one-way pull from the mark, so setting the mark colour carries the type with it,
  // and re-linking after a divergence resolves to the mark rather than to whichever field happened
  // to be edited last. Each era has its own pair, so the link applies to whichever is in play.
  const colourFields = COLOUR_FIELDS[next.era ?? 'historical']
  if (next.linkColors && colourFields) {
    const [markField, textField] = colourFields
    if (patch[markField] !== undefined || patch.linkColors) next[textField] = next[markField]
  }

  // The three lockups disagree about the province wordmark — the centred one is drawn without it —
  // so switching lockup adopts what that artwork does. Only until the wordmark has been set by
  // hand, though: after that it is the person's decision, and changing lockup must not silently
  // reverse it.
  if (patch.wordmark !== undefined) next.wordmarkTouched = true
  else if (patch.layout !== undefined && !next.wordmarkTouched) {
    next.wordmark = getLayout(patch.layout).wordmarkByDefault
  }

  // The same rule for where the mark sits against the type. Side by side hangs it from the first
  // cap height, as the signage it came from does; the horizontal lockup centres it, as its source
  // artwork draws it. Once set by hand the choice is yours and follows you between lockups.
  if (patch.markAlign !== undefined) next.markAlignTouched = true
  else if (patch.layout !== undefined && !next.markAlignTouched) {
    next.markAlign = defaultMarkAlignment(patch.layout)
  }

  // The Province pairs a colourway with each background it sanctions, so changing the background
  // moves the colourway to match rather than leaving an unreadable combination on screen. Once the
  // colourway is chosen by hand it stays put, as the wordmark and the alignment do.
  if (patch.currentVariant !== undefined) next.currentVariantTouched = true
  else if (patch.currentBackground !== undefined && !next.currentVariantTouched) {
    next.currentVariant = recommendedVariant(patch.currentBackground) ?? next.currentVariant
  }

  // The flag's white is the page showing through it, so on anything but a white or transparent
  // ground the full-colour flag shows the background through its every gap. That is what the
  // documents do too: on colour they set the whole thing in one ink. So the palette follows the
  // background until it is chosen by hand, as the current era's colourway does.
  if (patch.flagPalette !== undefined) next.flagPaletteTouched = true
  else if (patch.flagBackground !== undefined && !next.flagPaletteTouched) {
    next.flagPalette = recommendedPalette(patch.flagBackground) ?? next.flagPalette
  }

  // The ministry is one choice across all four identities. Picking from the list, typing a name,
  // or switching between the two modes therefore reaches the current era's wording as well — it
  // was the one era holding its own copy, so switching into it lost whatever had been typed.
  //
  // Choosing a ministry, or switching language, loads that mark's official wording — but only
  // until the wording has been edited. After that it is the person's text, and picking a different
  // ministry must not silently throw it away. Restoring the official wording clears the flag and
  // puts the link back.
  const nameMoved = patch.ministry !== undefined || patch.manualMinistry !== undefined ||
    patch.source !== undefined
  const markMoved = patch.currentMinistry !== undefined || patch.language !== undefined

  if (patch.currentMinistry !== undefined) {
    const named = findMinistry(next.currentMinistry)?.en
    if (named) {
      next.source = 'list'
      next.ministry = named
    }
  }
  if (patch.currentNameTouched === false) {
    // Clearing the override puts the choice back on the list and lets the wording recompute,
    // rather than writing a value back — after a hand edit the "official" wording *was* the edit.
    next.source = 'list'
    next.currentName = wordingFor(next)
  } else if (patch.currentName !== undefined && patch.currentNameTouched === undefined) {
    // Editing the wording by hand makes it this person's name for the ministry rather than the
    // Province's, so every era shows it — which is the whole point of holding one choice.
    next.currentNameTouched = true
    next.source = 'manual'
    next.manualMinistry = patch.currentName
  } else if (nameMoved || markMoved) {
    // The current era's code follows the chosen name, where a published mark answers to it. Where
    // none does the code is left alone and the name is simply typeset.
    if (nameMoved && next.source === 'list') {
      next.currentMinistry = codeForName(next.ministry) ?? next.currentMinistry
    }
    if (!next.currentNameTouched) next.currentName = wordingFor(next)
  }

  return next
}

/**
 * Exchanges the ink and the background.
 *
 * The one colour operation people reach for constantly — a green mark on white is the same design
 * decision as a white mark on green, and nobody wants to re-pick both. A transparent background has
 * no colour to move into the foreground, so the brand green stands in for it.
 */
export const swapColours = (current) => {
  const era = current.era ?? 'historical'
  const [mark] = COLOUR_FIELDS[era] ?? []
  if (!mark) return current
  const background = era === 'historical' ? 'background' : `${era}Background`
  const incoming = resolveColor(current[background], TRANSPARENT) === TRANSPARENT
    ? (era === 'historical' ? BRAND_COLORS.green : BRAND_COLORS.white)
    : current[background]

  return applyUpdate(current, { [mark]: incoming, [background]: current[mark] })
}

/** A restored share link states its fields deliberately, so they all count as chosen. */
export const applyShare = (current, patch) => ({
  ...applyUpdate({ ...current, currentNameTouched: false }, patch),
  wordmarkTouched: true,
  markAlignTouched: true
})
