// Putting a lockup in a URL.
//
// The whole configuration is compressed into a single query parameter by @firstform/json-url
// (vendored as a submodule under vendor/), so a link reproduces exactly what the sender was looking
// at without anything being stored anywhere.
//
// Two of json-url's transforms do the heavy lifting on length:
//
//   createDefaultsTransform  drops every field still at its default, so a link that changes one
//                            thing carries one thing.
//   createKeyMapTransform    renames the survivors to single letters.
//
// Between them, a near-default lockup fits in a token shorter than the word "configuration".

import { CLEAR_SPACE_ORDER, LAYOUT_ORDER, MARK_ALIGNMENT_ORDER } from '../logo/layouts.js'
import { cleanBoolean, cleanColour, cleanOneOf, cleanText } from './configFormat.js'
import { DEFAULTS } from './lockupDefaults.js'

export const SHARE_PARAM = 's'

/** The fields a link carries. `backdrop` is left out: it is how you are viewing, not what you made. */
const SHARED_FIELDS = [
  'layout', 'wordmark', 'source', 'ministry', 'manualMinistry', 'program',
  'markColor', 'textColor', 'linkColors', 'background', 'clearSpace', 'markAlign'
]

const KEY_MAP = {
  layout: 'l',
  wordmark: 'w',
  source: 's',
  ministry: 'm',
  manualMinistry: 'n',
  program: 'p',
  markColor: 'c',
  textColor: 't',
  linkColors: 'k',
  background: 'b',
  clearSpace: 'g',
  markAlign: 'a'
}

// json-url and its codecs are a few tens of kilobytes, and most visits neither arrive with a link
// nor create one — so the engine is built on first use and kept out of the initial bundle.
let enginePromise

const getEngine = () => {
  enginePromise ??= import('@firstform/json-url/web-share').then(({ default: createWebShareEngine }) => (
    createWebShareEngine({
      // lz only, deliberately.
      //
      // json-url's `raw` codec (plain base64) would be the natural choice for the very smallest
      // payloads, but it cannot decode in a browser: its base64 helper reaches for Node's Buffer
      // global, so a raw token compresses happily and then fails to come back. lz-string works
      // everywhere, adds a handful of characters to a tiny token, and is a 5 KB chunk.
      //
      // plainTextThreshold is zeroed so the engine cannot fall back to storing a short payload
      // verbatim and reintroduce the same problem.
      codecs: ['lz'],
      plainTextThreshold: 0,
      version: '1',
      transforms: [
        createWebShareEngine.createDefaultsTransform({
          rules: [{ defaults: Object.fromEntries(SHARED_FIELDS.map((key) => [key, DEFAULTS[key]])) }]
        }),
        createWebShareEngine.createKeyMapTransform({ keys: KEY_MAP })
      ]
    })
  ))

  return enginePromise
}

const pick = (state) => Object.fromEntries(SHARED_FIELDS.map((key) => [key, state[key]]))

/** Compresses a lockup configuration into a URL token. */
export const encodeShare = async (state) => (await getEngine()).compress(pick(state))

// ── Validation ───────────────────────────────────────────────────────────────────────────────────
//
// A decoded token is treated as hostile: it arrives from a URL, which means from whoever wrote the
// URL, not necessarily whoever opens it. The primitives are shared with configFormat.js, which
// validates the same values arriving as plain JSON.

/** Coerces a decoded payload into a state patch, discarding anything unrecognised. */
export const sanitizeShare = (raw) => {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null

  return {
    layout: cleanOneOf(raw.layout, LAYOUT_ORDER, DEFAULTS.layout),
    wordmark: cleanBoolean(raw.wordmark, DEFAULTS.wordmark),
    source: cleanOneOf(raw.source, ['list', 'manual'], DEFAULTS.source),
    ministry: cleanText(raw.ministry, DEFAULTS.ministry),
    manualMinistry: cleanText(raw.manualMinistry, DEFAULTS.manualMinistry),
    program: cleanText(raw.program, DEFAULTS.program),
    markColor: cleanColour(raw.markColor, DEFAULTS.markColor),
    textColor: cleanColour(raw.textColor, DEFAULTS.textColor),
    linkColors: cleanBoolean(raw.linkColors, DEFAULTS.linkColors),
    background: cleanColour(raw.background, DEFAULTS.background),
    clearSpace: cleanOneOf(raw.clearSpace, CLEAR_SPACE_ORDER, DEFAULTS.clearSpace),
    markAlign: cleanOneOf(raw.markAlign, MARK_ALIGNMENT_ORDER, DEFAULTS.markAlign)
  }
}

/** Decodes a token back into a state patch, or null if it is not one of ours. */
export const decodeShare = async (token) => {
  if (!token) return null

  // tryDecompress returns the fallback instead of throwing, so a stale or mangled link opens the
  // generator at its defaults rather than on a blank page.
  const raw = await (await getEngine()).tryDecompress(token, null, { deURI: true })
  return sanitizeShare(raw)
}

/**
 * The token in a URL's query string, if any.
 *
 * Deliberately free of any json-url dependency: this runs on every page load, and the answer is
 * almost always "there isn't one", at which point nothing else here needs to be downloaded.
 */
export const readShareToken = (search = globalThis.location?.search ?? '') => (
  new URLSearchParams(search).get(SHARE_PARAM)
)

/** This page's URL with the given configuration attached. */
export const buildShareUrl = async (state, href = globalThis.location?.href ?? '') => {
  const token = await encodeShare(state)
  const url = new URL(href)
  url.searchParams.set(SHARE_PARAM, token)
  return url.toString()
}
