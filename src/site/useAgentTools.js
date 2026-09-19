// Exposes the generator to an agent driving the browser, via WebMCP.
//
// Where the browser implements `navigator.modelContext`, the page registers typed tools — name,
// description, JSON Schema, handler — and the browser offers them to whatever agent is attached.
// The agent then calls set_lockup rather than hunting for the right button, which is both more
// reliable and considerably cheaper than reading the DOM.
//
//   https://webmachinelearning.github.io/webmcp/docs/proposal.html
//
// WebMCP is a draft, currently a Chrome preview. This is written as pure progressive enhancement:
// where the API is absent, nothing here runs and the page behaves exactly as before.
//
// The schemas enumerate their options from the same constants the UI renders from, so a tool can
// never offer a lockup or a format that does not exist.

import { useEffect, useRef } from 'react'
import {
  CLEAR_SPACE_ORDER, LAYOUTS, LAYOUT_ORDER, MARK_ALIGNMENT_ORDER, alignsVertically, getLayout
} from '../logo/layouts.js'
import { BRAND_COLORS, TRANSPARENT, describeContrast } from '../logo/logoColors.js'
import { EXPORT_FORMATS, EXPORT_FORMAT_ORDER, SIZE_PRESETS, exportLogo, isFormatSupported } from '../export/exportLogo.js'
import { resolveLockup } from '../logo/renderLogoSvg.js'
import { CURRENT_VARIANTS, CURRENT_VARIANT_ORDER, LANGUAGE_ORDER } from '../current/currentMarks.js'
import { MINISTRIES as CURRENT_MINISTRIES, findMinistry } from '../current/ministries.js'
import { MINISTRIES, searchMinistries } from '../ministries/ministries.js'
import { buildShareUrl } from './shareLink.js'

/** A tool result in the shape WebMCP expects: human-readable text, plus the data behind it. */
const reply = (text, data) => ({
  content: [{ type: 'text', text }],
  ...(data === undefined ? {} : { structuredContent: data })
})

const colourSchema = (what) => ({
  type: 'string',
  description: `${what}. A palette name (${Object.keys(BRAND_COLORS).join(', ')}), a hex value ` +
    `such as #006837, or any CSS colour notation.`
})

/**
 * Describes the lockup as it currently stands, in the same vocabulary the tools accept back.
 * Sizes come from the resolved artwork rather than the form, so they are what would actually
 * export.
 */
const describeState = ({ state, lockup }) => {
  if (state.era === 'current') {
    // A finished file rather than a drawing, so most of what follows does not apply to it.
    return {
      era: 'current',
      ministryCode: state.currentMinistry,
      wording: state.currentName,
      language: state.language,
      variant: state.currentVariant,
      variantLabel: CURRENT_VARIANTS[state.currentVariant]?.label,
      background: state.background === TRANSPARENT ? 'transparent' : state.background,
      clearSpace: state.clearSpace,
      note: 'Official artwork. The wording is part of the file and cannot be changed.'
    }
  }

  // Resolved here rather than passed in: the geometry is only wanted when an agent asks for it,
  // and recomputing it is cheaper than keeping a second copy in sync with the preview.
  const resolved = resolveLockup(lockup)

  return {
    era: 'historical',
    lockup: state.layout,
    lockupLabel: LAYOUTS[state.layout].label,
    showWordmark: state.wordmark,
    ministry: lockup.ministry,
    secondLine: lockup.program,
    markColor: state.markColor,
    textColor: state.textColor,
    background: state.background === TRANSPARENT ? 'transparent' : state.background,
    clearSpace: state.clearSpace,
    // Only reported where it means something; the stacked and centred lockups ignore it.
    markAlignment: alignsVertically(getLayout(state.layout)) ? state.markAlign : null,
    size: { width: resolved.viewBox.width, height: resolved.viewBox.height, units: 'artwork units' },
    contrast: describeContrast(state.markColor, state.background)
  }
}

const buildTools = (latest) => [
  {
    name: 'get_lockup_state',
    description:
      'Read what is currently on screen. There are two identities: the historical era builds crest ' +
      'lockups from parts and reports wording, colours, alignment and size; the current era serves ' +
      'the Province’s official ministry marks and reports which one. Call this before changing ' +
      'anything.',
    inputSchema: { type: 'object', properties: {} },
    execute: () => {
      const state = describeState(latest.current)
      const summary = state.era === 'current'
        ? `${state.ministryCode} mark (${state.language}): “${String(state.wording).replace(/\n/g, ' / ')}”, ` +
          `${state.variantLabel} on ${state.background}.`
        : `${state.lockupLabel} lockup, ${state.ministry || 'wordmark only'}, ${state.markColor} on ${state.background}.`

      return reply(summary, state)
    }
  },

  {
    name: 'set_lockup',
    description:
      'Change what is shown. Every field is optional — pass only what should change. In the ' +
      'historical era the ministry may be any text, listed or not, and a newline in it forces a ' +
      'line break. In the current era the wording is fixed artwork: choose a ministry by its code ' +
      '(see list_current_marks), a language, and one of the four official colourways.',
    inputSchema: {
      type: 'object',
      properties: {
        era: {
          type: 'string',
          enum: ['historical', 'current'],
          description: 'historical: crest lockups built from parts, any wording and colour. ' +
            'current: the Province’s official ministry marks, used exactly as published.'
        },
        ministryCode: {
          type: 'string',
          description: 'Current era. A ministry abbreviation such as FOR or ENV.'
        },
        wording: {
          type: 'string',
          description:
            'The wording of a current-era mark, overriding the ministry’s official text. A ' +
            'newline is a line break, as in the published artwork. Use this for a ministry that ' +
            'has been renamed or never had a mark published.'
        },
        language: {
          type: 'string',
          enum: [...LANGUAGE_ORDER],
          description: 'Current era. The official marks exist in English and French.'
        },
        variant: {
          type: 'string',
          enum: [...CURRENT_VARIANT_ORDER],
          description: 'Current era. ' + CURRENT_VARIANT_ORDER
            .map((id) => `${id}: ${CURRENT_VARIANTS[id].description}`).join(' ')
        },
        lockup: {
          type: 'string',
          enum: [...LAYOUT_ORDER],
          description: LAYOUT_ORDER.map((id) => `${id}: ${LAYOUTS[id].description}`).join(' ')
        },
        ministry: { type: 'string', maxLength: 200, description: 'The ministry, agency or office.' },
        secondLine: { type: 'string', maxLength: 200, description: 'An optional line beneath it, such as a programme.' },
        showWordmark: { type: 'boolean', description: 'Whether to show "Province of British Columbia".' },
        markAlignment: {
          type: 'string',
          enum: [...MARK_ALIGNMENT_ORDER],
          description: 'Where the mark sits against the type. Only used by the horizontal and side-by-side lockups.'
        },
        clearSpace: {
          type: 'string',
          enum: [...CLEAR_SPACE_ORDER],
          description: 'Margin around the lockup. The background colour fills it.'
        }
      }
    },
    execute: (input) => {
      const { update } = latest.current
      const patch = {}

      if (input.era !== undefined) patch.era = input.era
      if (input.ministryCode !== undefined) patch.currentMinistry = String(input.ministryCode).toUpperCase()
      if (input.wording !== undefined) patch.currentName = String(input.wording)
      if (input.language !== undefined) patch.language = input.language
      if (input.variant !== undefined) patch.currentVariant = input.variant
      if (input.lockup !== undefined) patch.layout = input.lockup
      if (input.showWordmark !== undefined) patch.wordmark = input.showWordmark
      if (input.markAlignment !== undefined) patch.markAlign = input.markAlignment
      if (input.clearSpace !== undefined) patch.clearSpace = input.clearSpace
      if (input.secondLine !== undefined) patch.program = input.secondLine
      if (input.ministry !== undefined) {
        // Typed text rather than a list choice, so the form switches to its manual mode — otherwise
        // the ministry dropdown would still be showing something else.
        patch.source = 'manual'
        patch.manualMinistry = input.ministry
      }

      update(patch)
      return reply(`Updated: ${Object.keys(input).join(', ') || 'nothing'}.`)
    }
  },

  {
    name: 'set_colours',
    description:
      'Set the mark, the type and the background independently. Pass only what should change. ' +
      'Use "transparent" for a background with no colour at all. The reply reports the resulting ' +
      'contrast, which is worth checking before exporting.',
    inputSchema: {
      type: 'object',
      properties: {
        markColor: colourSchema('The mark'),
        textColor: colourSchema('The type'),
        background: {
          ...colourSchema('The background'),
          description: `${colourSchema('The background').description} Or "transparent".`
        }
      }
    },
    execute: (input) => {
      const { update } = latest.current
      const patch = {}

      if (input.markColor !== undefined) patch.markColor = input.markColor
      if (input.textColor !== undefined) {
        patch.textColor = input.textColor
        // An explicit type colour means the two are no longer meant to move together.
        patch.linkColors = false
      }
      if (input.background !== undefined) {
        patch.background = /^transparent$/i.test(input.background) ? TRANSPARENT : input.background
      }

      update(patch)

      const next = { ...latest.current.state, ...patch }
      const contrast = describeContrast(next.markColor, next.background)
      return reply(`Colours updated. Contrast ${contrast.ratio ?? '?'}:1 — ${contrast.message}`, { contrast })
    }
  },

  {
    name: 'export_lockup',
    description:
      'Download the lockup as it currently stands. This saves a file to the browser’s downloads; ' +
      'set the lockup up first and check the state if unsure. Vector formats may keep their text ' +
      'live with the font embedded, or convert it to outlines, which is what a printer usually wants.',
    inputSchema: {
      type: 'object',
      properties: {
        format: {
          type: 'string',
          enum: [...EXPORT_FORMAT_ORDER],
          description: EXPORT_FORMAT_ORDER
            .map((id) => `${id}: ${EXPORT_FORMATS[id].vector ? 'vector' : 'raster'}`).join(', ')
        },
        pixelWidth: {
          type: 'integer',
          enum: [...SIZE_PRESETS],
          description: 'Raster formats only. Ignored for SVG and PDF.'
        },
        outlineText: {
          type: 'boolean',
          description: 'Vector formats only. Converts the type to paths so the file needs no font.'
        }
      },
      required: ['format']
    },
    execute: async (input) => {
      const { lockup } = latest.current
      const spec = EXPORT_FORMATS[input.format]

      if (!spec) return reply(`No such format: ${input.format}.`)
      if (!isFormatSupported(input.format)) {
        return reply(`This browser cannot encode ${spec.label}. Try SVG or PNG.`)
      }

      const saved = await exportLogo({
        ...lockup,
        format: input.format,
        pixelWidth: input.pixelWidth ?? 2048,
        outlineText: Boolean(input.outlineText) && spec.vector
      })

      return reply(`Downloaded ${saved}.`, { fileName: saved })
    }
  },

  {
    name: 'get_share_link',
    description:
      'A URL that reproduces the current lockup exactly. The whole configuration travels in the ' +
      'link, so nothing is stored anywhere and it can be handed to someone else or reopened later.',
    inputSchema: { type: 'object', properties: {} },
    execute: async () => {
      const url = await buildShareUrl(latest.current.state)
      return reply(url, { url })
    }
  },

  {
    name: 'list_current_marks',
    description:
      'The Province’s ministries and the official wording of their marks, in English and French, ' +
      'with the code to pass to set_lockup. Newlines in the wording are the line breaks the ' +
      'published artwork uses. A ministry not listed has no published mark, but set_lockup takes ' +
      'any wording, so one can still be set.',
    inputSchema: { type: 'object', properties: {} },
    execute: () => {
      const lines = CURRENT_MINISTRIES
        .map((entry) => `${entry.code} — ${entry.en.replace(/\n/g, ' ')}`)
      return reply(lines.join('\n'), {
        ministries: CURRENT_MINISTRIES.map(({ code, en, fr }) => ({ code, en, fr }))
      })
    }
  },

  {
    name: 'find_ministry',
    description:
      `Search the ${MINISTRIES.length} listed ministries and agencies. The search ignores case and ` +
      'punctuation, so "citizens services" finds "Ministry of Citizens’ Services". The list is a ' +
      'convenience only — in the historical era set_lockup accepts any name, listed or not. For ' +
      'the current era use list_current_marks instead; its marks are fixed artwork.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Part of a name. Omit to list everything.' }
      }
    },
    execute: (input) => {
      const matches = searchMinistries(input.query ?? '').flatMap((group) => group.options)
      return reply(
        matches.length ? matches.join('\n') : `Nothing matches "${input.query}". Any name can be typed instead.`,
        { matches }
      )
    }
  }
]

/**
 * Registers the tools for as long as the component is mounted.
 *
 * The handlers read through a ref rather than closing over state, so the tools are registered once
 * and still see current values. Re-registering on every keystroke would be both wasteful and — for
 * an agent watching the tool list — noisy.
 */
export const useAgentTools = (context) => {
  const latest = useRef(context)
  latest.current = context

  useEffect(() => {
    const modelContext = globalThis.navigator?.modelContext
    if (typeof modelContext?.provideContext !== 'function') return

    try {
      modelContext.provideContext({ tools: buildTools(latest) })
    } catch (error) {
      // An unsupported shape or a page-level policy refusing it: the site still works by hand.
      console.warn('Could not register agent tools.', error)
      return
    }

    return () => {
      try {
        modelContext.provideContext({ tools: [] })
      } catch {
        // Nothing useful to do on the way out.
      }
    }
  }, [])
}

export { buildTools }
