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

/** The current state as the object an agent or a person would write. */
export const toConfig = (state) => ({
  lockup: state.layout,
  showWordmark: state.wordmark,
  ministry: (state.source === 'manual' ? state.manualMinistry : state.ministry).trim(),
  ...(state.program.trim() ? { secondLine: state.program.trim() } : {}),
  markColor: state.markColor,
  textColor: state.textColor,
  background: state.background === TRANSPARENT ? 'transparent' : state.background,
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

  if ('lockup' in config) patch.layout = cleanOneOf(config.lockup, LAYOUT_ORDER, DEFAULTS.layout)
  if ('showWordmark' in config) patch.wordmark = cleanBoolean(config.showWordmark, DEFAULTS.wordmark)
  if ('secondLine' in config) patch.program = cleanText(config.secondLine, '')
  if ('markColor' in config) patch.markColor = cleanColour(config.markColor, DEFAULTS.markColor)
  if ('textColor' in config) {
    patch.textColor = cleanColour(config.textColor, DEFAULTS.textColor)
    // Naming the type's colour separately means the two are no longer meant to move together.
    patch.linkColors = false
  }
  if ('background' in config) {
    const value = cleanColour(config.background, DEFAULTS.background)
    patch.background = /^transparent$/i.test(value) ? TRANSPARENT : value
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
