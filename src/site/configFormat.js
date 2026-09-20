// The generator's configuration as plain JSON.
//
// This exists because of a specific failure. An agent asked to produce artwork could read
// capabilities.json and describe exactly what it wanted — lockup, wording, colour, alignment — and
// then had no way to hand that over. It ended up writing the settings out as a table of
// instructions for a person to re-enter by hand.
//
// So: one documented object, in the same vocabulary capabilities.json and the WebMCP tools use,
// which can be pasted into the app or carried in a URL. An agent can produce a link that opens the
// generator already configured, and the person only has to press Download.
//
// The public names deliberately differ from the internal state's. `layout`/`program`/`markAlign`
// are what this code has always called them; `lockup`/`secondLine`/`markAlignment` are what the
// manifest and the tools say. One outward vocabulary is worth a mapping layer.

import { CURRENT_VARIANT_ORDER, LANGUAGE_ORDER } from '../current/currentMarks.js'
import { findMinistry } from '../current/ministries.js'
import { FLAG_PALETTE_ORDER } from '../flag/flagPalettes.js'
import { ALL_FLAG_SYMBOLS, NAME_PLACEMENTS } from '../flag/flagLayout.js'
import { CREST_ALIGNMENTS, CREST_ARRANGEMENTS, CREST_PLACEMENTS } from '../crest/crestLayout.js'
import { CLEAR_SPACE_ORDER, LAYOUT_ORDER, MARK_ALIGNMENT_ORDER } from '../logo/layouts.js'
import { TRANSPARENT } from '../logo/logoColors.js'
import { DEFAULTS } from './lockupDefaults.js'

// ── Validation ───────────────────────────────────────────────────────────────────────────────────
//
// Shared with shareLink.js, which validates the same values arriving by a different route. Both
// treat what they are given as hostile: a configuration can come from a URL, and a URL can come
// from anyone.

const MAX_TEXT = 200

// Newlines are meaningful — they force a line break in the lockup — so only the other control
// characters are stripped.
const CONTROL_CHARACTERS = new RegExp('[\\u0000-\\u0009\\u000b-\\u001f\\u007f]', 'g')

export const cleanText = (value, fallback) => (
  typeof value === 'string' ? value.replace(CONTROL_CHARACTERS, '').slice(0, MAX_TEXT) : fallback
)

// Hex, a palette name, or a functional notation — but nothing containing a quote or an angle
// bracket, so a value can never close the attribute it is interpolated into.
const COLOUR_PATTERN = /^[a-zA-Z0-9#(),.%\s/-]{1,64}$/

export const cleanColour = (value, fallback) => (
  typeof value === 'string' && COLOUR_PATTERN.test(value) ? value : fallback
)

export const cleanBoolean = (value, fallback) => (typeof value === 'boolean' ? value : fallback)

export const cleanOneOf = (value, allowed, fallback) => (allowed.includes(value) ? value : fallback)

// ── Public shape ─────────────────────────────────────────────────────────────────────────────────

export const ERAS = ['historical', 'flag', 'crest', 'current']

const backgroundOf = (state) => (
  state.background === TRANSPARENT ? 'transparent' : state.background
)

/**
 * The current state as the object an agent or a person would write.
 *
 * The two eras share almost nothing — one is built from parts and takes any wording and colour, the
 * other is a finished file in one of four colourways — so a configuration describes whichever era
 * is in play rather than carrying a pile of fields that do not apply to it.
 */
export const toConfig = (state) => (state.era === 'crest'
  ? {
      era: 'crest',
      ministry: (state.source === 'manual' ? state.manualMinistry : state.ministry).trim(),
      arrangement: state.crestArrangement,
      ministryPlacement: state.crestPlacement,
      ...(state.crestBold ? { bold: true } : {}),
      ministryLines: state.crestAlign,
      ...(state.crestExtra.trim() ? { secondLine: state.crestExtra.trim() } : {}),
      markColor: state.crestMarkColor,
      textColor: state.crestTextColor,
      background: state.crestBackground === TRANSPARENT ? 'transparent' : state.crestBackground,
      clearSpace: state.clearSpace
    }
  : state.era === 'flag'
  ? {
      era: 'flag',
      ministry: (state.source === 'manual' ? state.manualMinistry : state.ministry).trim(),
      symbol: state.flagSymbol,
      namePlacement: state.flagPlacement,
      ...(state.flagProvince ? { provinceLine: true } : {}),
      ...(state.flagExtra.trim() ? { thirdLine: state.flagExtra.trim() } : {}),
      flagPalette: state.flagPalette,
      markColor: state.flagMarkColor,
      textColor: state.flagTextColor,
      background: state.flagBackground === TRANSPARENT ? 'transparent' : state.flagBackground,
      clearSpace: state.clearSpace
    }
  : state.era === 'current'
  ? {
      era: 'current',
      ministryCode: state.currentMinistry,
      // Only when it differs from the official text; a configuration should say what was chosen,
      // not restate what picking the ministry would have given anyway.
      ...(state.currentName !== (findMinistry(state.currentMinistry)?.[state.language] ?? '')
        ? { wording: state.currentName }
        : {}),
      language: state.language,
      variant: state.currentVariant,
      background: state.currentBackground === TRANSPARENT ? 'transparent' : state.currentBackground,
      clearSpace: state.clearSpace
    }
  : {
      era: 'historical',
      lockup: state.layout,
      showWordmark: state.wordmark,
      ministry: (state.source === 'manual' ? state.manualMinistry : state.ministry).trim(),
      ...(state.program.trim() ? { secondLine: state.program.trim() } : {}),
      markColor: state.markColor,
      textColor: state.textColor,
      background: backgroundOf(state),
      clearSpace: state.clearSpace,
      markAlignment: state.markAlign
    })

/**
 * A configuration object as a state patch, with everything unrecognised discarded.
 *
 * Absent fields are left alone rather than reset, so a partial configuration — "just make it red" —
 * does what it says.
 */
export const fromConfig = (config) => {
  if (!config || typeof config !== 'object' || Array.isArray(config)) return null

  const patch = {}

  if ('era' in config) patch.era = cleanOneOf(config.era, ERAS, DEFAULTS.era)
  if ('ministryCode' in config) patch.currentMinistry = cleanText(config.ministryCode, DEFAULTS.currentMinistry).toUpperCase()
  if ('wording' in config) {
    patch.currentName = cleanText(config.wording, DEFAULTS.currentName)
    // Stated wording is deliberate, so the ministry list must not overwrite it.
    patch.currentNameTouched = true
  }
  if ('language' in config) patch.language = cleanOneOf(config.language, LANGUAGE_ORDER, DEFAULTS.language)
  if ('variant' in config) patch.currentVariant = cleanOneOf(config.variant, CURRENT_VARIANT_ORDER, DEFAULTS.currentVariant)

  if ('lockup' in config) patch.layout = cleanOneOf(config.lockup, LAYOUT_ORDER, DEFAULTS.layout)
  if ('showWordmark' in config) patch.wordmark = cleanBoolean(config.showWordmark, DEFAULTS.wordmark)
  if ('secondLine' in config) patch.program = cleanText(config.secondLine, '')
  // Each era keeps its own ink, so a configuration's colours land on the era it declares.
  const era = config.era ?? DEFAULTS.era
  const forFlag = era === 'flag'
  const forCrest = era === 'crest'
  if ('markColor' in config) {
    const field = forFlag ? 'flagMarkColor' : forCrest ? 'crestMarkColor' : 'markColor'
    patch[field] = cleanColour(config.markColor, DEFAULTS[field])
  }
  if ('textColor' in config) {
    const field = forFlag ? 'flagTextColor' : forCrest ? 'crestTextColor' : 'textColor'
    patch[field] = cleanColour(config.textColor, DEFAULTS[field])
    // Naming the type's colour separately means the two are no longer meant to move together.
    patch.linkColors = false
  }
  if ('background' in config) {
    // Each era keeps its own background, so which one this sets depends on the era the
    // configuration declares — otherwise a current-era object would quietly recolour the crest.
    const field = era === 'current'
      ? 'currentBackground'
      : era === 'flag' ? 'flagBackground' : era === 'crest' ? 'crestBackground' : 'background'
    const value = cleanColour(config.background, DEFAULTS[field])
    patch[field] = /^transparent$/i.test(value) ? TRANSPARENT : value
  }
  if ('arrangement' in config) patch.crestArrangement = cleanOneOf(config.arrangement, CREST_ARRANGEMENTS, DEFAULTS.crestArrangement)
  if ('ministryPlacement' in config) patch.crestPlacement = cleanOneOf(config.ministryPlacement, CREST_PLACEMENTS, DEFAULTS.crestPlacement)
  if ('bold' in config) patch.crestBold = cleanBoolean(config.bold, DEFAULTS.crestBold)
  if ('ministryLines' in config) patch.crestAlign = cleanOneOf(config.ministryLines, CREST_ALIGNMENTS, DEFAULTS.crestAlign)
  if ('symbol' in config) patch.flagSymbol = cleanOneOf(config.symbol, ALL_FLAG_SYMBOLS, DEFAULTS.flagSymbol)
  if ('namePlacement' in config) patch.flagPlacement = cleanOneOf(config.namePlacement, NAME_PLACEMENTS, DEFAULTS.flagPlacement)
  if ('provinceLine' in config) patch.flagProvince = cleanBoolean(config.provinceLine, DEFAULTS.flagProvince)
  if ('thirdLine' in config) patch.flagExtra = cleanText(config.thirdLine, '')
  if ('flagPalette' in config) {
    patch.flagPalette = cleanOneOf(config.flagPalette, FLAG_PALETTE_ORDER, DEFAULTS.flagPalette)
    // Stated deliberately, so the background must not move it.
    patch.flagPaletteTouched = true
  }
  if ('clearSpace' in config) patch.clearSpace = cleanOneOf(config.clearSpace, CLEAR_SPACE_ORDER, DEFAULTS.clearSpace)
  if ('markAlignment' in config) patch.markAlign = cleanOneOf(config.markAlignment, MARK_ALIGNMENT_ORDER, DEFAULTS.markAlign)

  if ('ministry' in config) {
    // Any text is allowed, listed or not, so the form goes to its manual mode — otherwise the
    // dropdown would sit there showing something other than what is drawn.
    patch.source = 'manual'
    patch.manualMinistry = cleanText(config.ministry, '')
  }

  return patch
}

/**
 * Parses pasted JSON into a patch, with a message worth reading when it fails.
 *
 * @returns {{patch: object}|{error: string}}
 */
export const parseConfig = (text) => {
  const trimmed = String(text ?? '').trim()
  if (!trimmed) return { error: 'Nothing to apply.' }

  let parsed
  try {
    parsed = JSON.parse(trimmed)
  } catch (error) {
    return { error: `That is not valid JSON — ${error.message}` }
  }

  const patch = fromConfig(parsed)
  if (!patch) return { error: 'Expected a JSON object, such as { "lockup": "columns" }.' }
  if (!Object.keys(patch).length) {
    return { error: 'No recognised settings. See capabilities.json for the field names.' }
  }

  return { patch }
}

/** The configuration as it would be written into a URL. */
export const CONFIG_PARAM = 'c'

export const readConfigParam = (search = globalThis.location?.search ?? '') => {
  const raw = new URLSearchParams(search).get(CONFIG_PARAM)
  if (!raw) return null

  const { patch } = parseConfig(raw)
  return patch ?? null
}

/** This page's URL carrying a configuration as readable JSON. */
export const buildConfigUrl = (state, href = globalThis.location?.href ?? '') => {
  const url = new URL(href)
  url.searchParams.set(CONFIG_PARAM, JSON.stringify(toConfig(state)))
  return url.toString()
}
