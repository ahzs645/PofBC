// Writes public/capabilities.json: what this generator can make, in one fetch.
//
// An agent arriving at the site would otherwise have to infer the option space by reading the DOM
// — which layouts exist, which formats the browser will encode, what a ministry name may contain.
// This states it outright, and states it in the vocabulary the URL and the WebMCP tools use, so a
// value read from here can be passed straight back in.
//
// Generated rather than written by hand, and from the same constants the application imports, so
// the manifest cannot drift from the thing it describes. Adding a lockup updates it for free.
//
// Run: npm run build:capabilities

import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  CLEAR_SPACE, CLEAR_SPACE_ORDER, LAYOUTS, LAYOUT_ORDER, MARK_ALIGNMENTS, MARK_ALIGNMENT_ORDER,
  MARK_BOX, PROVINCE_WORDMARK, defaultMarkAlignment
} from '../src/logo/layouts.js'
import { BRAND_COLORS, TRANSPARENT } from '../src/logo/logoColors.js'
import { EXPORT_FORMATS, EXPORT_FORMAT_ORDER, SIZE_PRESETS } from '../src/export/exportLogo.js'
import { MINISTRY_GROUPS, MINISTRY_LIST_REVIEWED } from '../src/ministries/ministries.js'
import { SHARE_PARAM } from '../src/site/shareLink.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const { name, version, description } = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'))

const manifest = {
  name,
  version,
  description,
  documentation: 'https://github.com/ahzs645/PofBC#readme',

  // The drawing every lockup shares, in the units every measurement below is expressed in.
  mark: {
    width: MARK_BOX.width,
    height: MARK_BOX.height,
    units: 'Artwork units. Every size, gap and margin in this manifest is in the same space.'
  },

  wordmark: {
    text: PROVINCE_WORDMARK,
    note: 'Fixed text. It can be shown or hidden, not edited.'
  },

  lockups: LAYOUT_ORDER.map((id) => ({
    id,
    label: LAYOUTS[id].label,
    description: LAYOUTS[id].description,
    // Where the numbers came from, so a caller knows which are measured and which are inferred.
    derivedFrom: LAYOUTS[id].source ?? null,
    fontSize: LAYOUTS[id].fontSize,
    leading: LAYOUTS[id].leading,
    showsWordmarkByDefault: LAYOUTS[id].wordmarkByDefault,
    // Vertical alignment only means something where the mark sits beside the type.
    markAlignment: LAYOUTS[id].markPlacement === 'below'
      ? null
      : { default: defaultMarkAlignment(id), options: MARK_ALIGNMENT_ORDER }
  })),

  markAlignments: MARK_ALIGNMENT_ORDER.map((id) => ({
    id,
    label: MARK_ALIGNMENTS[id].label,
    description: MARK_ALIGNMENTS[id].description
  })),

  clearSpace: CLEAR_SPACE_ORDER.map((id) => ({
    id,
    label: CLEAR_SPACE[id].label,
    // Stated both ways: the rule, and what it works out to for this mark.
    factorOfMarkWidth: CLEAR_SPACE[id].factor,
    units: CLEAR_SPACE[id].factor * MARK_BOX.width
  })),

  colours: {
    named: BRAND_COLORS,
    transparent: TRANSPARENT,
    accepts: 'A palette name, a hex value such as #006837, or any CSS colour notation. ' +
      'Values containing a quote or an angle bracket are rejected.',
    independent: ['markColor', 'textColor', 'background']
  },

  formats: EXPORT_FORMAT_ORDER.map((id) => ({
    id,
    label: EXPORT_FORMATS[id].label,
    extension: EXPORT_FORMATS[id].extension,
    mimeType: EXPORT_FORMATS[id].mimeType,
    vector: Boolean(EXPORT_FORMATS[id].vector),
    supportsTransparency: EXPORT_FORMATS[id].vector || Boolean(EXPORT_FORMATS[id].alpha),
    // Raster encoders vary by browser; the page probes for them rather than assuming.
    note: EXPORT_FORMATS[id].vector
      ? 'Vector. Text may be kept live with the font embedded, or converted to outlines.'
      : 'Raster. Rendered at one of the pixel widths below.'
  })),

  rasterWidths: SIZE_PRESETS,

  ministries: {
    reviewed: MINISTRY_LIST_REVIEWED,
    note: 'A convenience list, not an authority. Any name may be typed instead, and newlines in it ' +
      'force a line break.',
    maxLength: 200,
    groups: MINISTRY_GROUPS
  },

  shareLinks: {
    parameter: SHARE_PARAM,
    description: 'The whole configuration compressed into one query parameter. Opening a URL ' +
      'carrying it restores that lockup exactly. Nothing is stored server-side.',
    example: `?${SHARE_PARAM}=1.lz.N4IgNiBcIBYPYCcCWAvOA7ALgQwgGhAA`
  },

  agentTools: {
    standard: 'WebMCP',
    specification: 'https://webmachinelearning.github.io/webmcp/docs/proposal.html',
    description: 'Where the browser implements navigator.modelContext, this page registers tools ' +
      'for reading and setting the lockup and for exporting it, so an agent need not drive the ' +
      'controls by hand. Absent that API the page behaves normally.',
    tools: [
      'get_lockup_state', 'set_lockup', 'set_colours', 'export_lockup', 'get_share_link', 'find_ministry'
    ]
  }
}

const target = resolve(root, 'public/capabilities.json')
writeFileSync(target, `${JSON.stringify(manifest, null, 2)}\n`)

const bytes = JSON.stringify(manifest).length
console.log(`  capabilities      ${manifest.lockups.length} lockups, ${manifest.formats.length} formats, ` +
  `${MINISTRY_GROUPS.flatMap((group) => group.options).length} ministries  ${(bytes / 1024).toFixed(1)} KB`)
console.log('  → public/capabilities.json')
