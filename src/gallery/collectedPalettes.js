// Reviewed colourways share a drawing; files remain separate source evidence and downloads.
// Only geometrically compared families belong here. In particular, the endorsed StrongerBC
// marks and the standalone RGB/solid drawings are not interchangeable geometries.

const knowledgeKit = 'https://about.knowledge.ca/wp-content/uploads/2026/04/kn-brand-assets.zip'
const strongerKit = 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/web-content-development-guides/corporate-identity-assets/visid-files/strongerbc_wordmark.zip?forcedownload=true'
const knowledge = 'source-knowledge-network-knowledge-network-'
const northern = 'source-northern-health-northern-health-'

export const COLLECTED_PALETTES = {
  [`${knowledge}colour-eps`]: {
    label: 'Knowledge Network',
    masterId: `${knowledge}svg`,
    defaultId: 'colour',
    palettes: [
      {
        id: 'colour', label: 'Full colour', inks: { '#ffffff': '#000000' }, darkBackground: false,
        sourceIds: [`${knowledge}colour-eps`, `${knowledge}colour-png`],
        sourceUrl: knowledgeKit, sourceLabel: 'RGB/BCKN_WordPos_RGB.png',
      },
      {
        id: 'white-lettering', label: 'White lettering', inks: {}, darkBackground: true,
        sourceIds: [`${knowledge}svg`],
        sourceUrl: 'https://about.knowledge.ca/wp-content/uploads/2025/02/knowledge-logo.svg', sourceLabel: 'Original website version',
      },
      {
        id: 'black', label: 'All black', inks: { '#ffffff': '#000000', '#00adee': '#000000' }, darkBackground: false,
        sourceIds: [], sourceUrl: knowledgeKit, sourceLabel: 'All Black/BCKN_WordPos_BLK_RGB.png',
      },
      {
        id: 'white', label: 'All white', inks: { '#00adee': '#ffffff' }, darkBackground: true,
        sourceIds: [], sourceUrl: knowledgeKit, sourceLabel: 'All White/BCKN_WordRev_WHT_CMYK.png',
      },
    ],
    note: 'Choose from the four colourways in Knowledge Network’s official wordmark kit.',
  },
  [`${northern}colour-tagline-svg`]: {
    label: 'Northern Health with tagline',
    masterId: `${northern}colour-tagline-svg`,
    defaultId: 'colour',
    palettes: [
      { id: 'colour', label: 'Full colour', inks: {}, darkBackground: false, sourceIds: [`${northern}colour-tagline-svg`] },
      {
        id: 'black', label: 'Black', inks: { '#005699': '#000000', '#3197b9': '#000000', '#6d7071': '#000000' },
        darkBackground: false, sourceIds: [`${northern}black-tagline-svg`],
      },
      {
        id: 'white', label: 'White', inks: { '#005699': '#ffffff', '#3197b9': '#ffffff', '#6d7071': '#ffffff' },
        darkBackground: true, sourceIds: [`${northern}white-tagline-svg`],
      },
    ],
    note: 'Choose the supplied full-colour, black or white mark with its tagline.',
  },
  'vector-StrongerBC_RGB_pos': {
    label: 'StrongerBC wordmark, full colour',
    masterId: 'vector-StrongerBC_RGB_pos',
    defaultId: 'colour',
    palettes: [
      { id: 'colour', label: 'Full colour', inks: {}, darkBackground: false, sourceIds: ['vector-StrongerBC_RGB_pos'], sourceUrl: strongerKit },
      { id: 'reversed', label: 'Reversed', inks: { '#234075': '#ffffff' }, darkBackground: true, sourceIds: ['vector-StrongerBC_RGB_rev'], sourceUrl: strongerKit },
    ],
    note: 'Choose the original full-colour wordmark or its reversed version with white lettering and gold BC.',
  },
  'vector-StrongerBC_Solid_pos': {
    label: 'StrongerBC wordmark, solid colour',
    masterId: 'vector-StrongerBC_Solid_pos',
    defaultId: 'black',
    palettes: [
      { id: 'black', label: 'Black', inks: {}, darkBackground: false, sourceIds: ['vector-StrongerBC_Solid_pos'], sourceUrl: strongerKit },
      { id: 'white', label: 'White', inks: { '#231f20': '#ffffff' }, darkBackground: true, sourceIds: ['vector-StrongerBC_Solid_rev'], sourceUrl: strongerKit },
    ],
    note: 'Choose the original solid wordmark in black or white.',
  },
}

/** Explicit choice, then an old source-file link, then this drawing's documented default. */
export const paletteFor = (group, { paletteId, sourceId } = {}) => group?.palettes?.find((palette) => palette.id === paletteId)
  ?? group?.palettes?.find((palette) => palette.sourceIds?.includes(sourceId))
  ?? group?.palettes?.find((palette) => palette.id === group.defaultId)
  ?? group?.palettes?.[0]
  ?? null

/** SVG can be displayed directly, including an honestly labelled SVG containing bitmap artwork. */
export const collectedPreviewFile = (asset) => asset?.format?.toLowerCase() === 'svg'
  ? asset.file
  : asset?.preview || asset?.file

const normalHex = (value) => {
  if (typeof value !== 'string' || !/^#[\da-f]{3}(?:[\da-f]{3})?$/i.test(value)) throw new TypeError('Palette inks must be three- or six-digit hex colours')
  const hex = value.toLowerCase()
  return hex.length === 4 ? `#${[...hex.slice(1)].map((digit) => digit + digit).join('')}` : hex
}

// Tokenize XML instead of replacing colours throughout the document: identifiers, path data,
// descriptions and comments must not change. Source formatting is retained too.
const XML_TOKEN = /<!--[\s\S]*?-->|<\?[\s\S]*?\?>|<!\[CDATA\[[\s\S]*?\]\]>|<\/?[A-Za-z_][\w:.-]*(?:[^<>"']|"[^"<]*"|'[^'<]*')*>/g
const ATTRIBUTE = /(\s+)([A-Za-z_][\w:.-]*)(\s*=\s*)(["'])([\s\S]*?)\4/g
const ELEMENTS = new Set(['svg', 'g', 'defs', 'path', 'polygon', 'polyline', 'rect', 'circle', 'ellipse', 'line', 'style', 'title', 'desc', 'clipPath', 'linearGradient', 'radialGradient', 'stop', 'symbol', 'use', 'text', 'tspan'])

const checkCss = (css) => {
  if (/\\|@import\b|expression\s*\(|(?:javascript|data)\s*:|behavior\s*:/i.test(css)
    || [...css.matchAll(/url\s*\(([^)]*)\)/gi)].some(([, target]) => !/^#[\w:.-]+$/.test(target.trim()))) throw new TypeError('Palette artwork must contain only local, static SVG styles')
}

/**
 * Recolour reviewed static SVG by changing fill/stroke values only. Unknown source colours,
 * "none", local paint servers and other properties are left alone. Mapping keys/values must be
 * literal hex colours; active content and external references are rejected. This is deliberately
 * not a general SVG sanitizer. Drawings with masks are refused because recolouring shared or
 * inherited paint can change mask semantics. An optional defaultFill supplies an absent root
 * fill for drawings whose black shapes rely on SVG's default.
 */
export const renderCollectedPalette = (svg, palette) => {
  if (typeof svg !== 'string' || !svg.trim()) throw new TypeError('Palette artwork must be an SVG string')
  if (!palette || typeof palette.inks !== 'object' || palette.inks === null || Array.isArray(palette.inks)) throw new TypeError('Palette inks must be a colour mapping')
  const inks = new Map()
  for (const [from, to] of Object.entries(palette.inks)) {
    const colour = normalHex(from)
    const replacement = normalHex(to)
    if (inks.has(colour) && inks.get(colour) !== replacement) throw new TypeError('Palette contains conflicting colour mappings')
    inks.set(colour, replacement)
  }
  const defaultFill = palette.defaultFill === undefined ? null : normalHex(palette.defaultFill)
  const paint = (value) => {
    const trimmed = value.trim()
    if (!/^#[\da-f]{3}(?:[\da-f]{3})?$/i.test(trimmed)) return value
    const colour = normalHex(trimmed)
    const replacement = inks.get(colour)
    return replacement && replacement !== colour ? value.replace(trimmed, replacement) : value
  }
  const declarations = (css) => {
    checkCss(css)
    const change = (part) => part.replace(/((?:^|[;{])\s*(?:fill|stroke)\s*:\s*)(#[\da-f]{3}(?:[\da-f]{3})?)(?=\s*(?:!important\s*)?(?:[;}]|$))/gi,
      (_, prefix, value) => prefix + paint(value))
    // Comments and quoted strings are content, not declarations (including a CSS content value).
    let end = 0
    let result = ''
    for (const match of css.matchAll(/\/\*[\s\S]*?\*\/|"[^"\\]*"|'[^'\\]*'/g)) {
      result += change(css.slice(end, match.index)) + match[0]
      end = match.index + match[0].length
    }
    return result + change(css.slice(end))
  }
  const stack = []
  let rootSeen = false
  let end = 0
  let result = ''
  const text = (value) => {
    if (value.includes('<') || (!stack.length && value.trim())) throw new TypeError('Malformed SVG artwork')
    return stack.at(-1)?.split(':').at(-1) === 'style' ? declarations(value) : value
  }
  for (const match of svg.matchAll(XML_TOKEN)) {
    result += text(svg.slice(end, match.index))
    end = match.index + match[0].length
    const token = match[0]
    if (token.startsWith('<!--')) { result += token; continue }
    if (token.startsWith('<?')) {
      if (rootSeen || !/^<\?xml\s/.test(token)) throw new TypeError('Only the SVG XML declaration is supported')
      result += token; continue
    }
    if (token.startsWith('<![CDATA[')) {
      if (!stack.length) throw new TypeError('Malformed SVG artwork')
      result += stack.at(-1)?.split(':').at(-1) === 'style'
        ? `<![CDATA[${declarations(token.slice(9, -3))}]]>` : token
      continue
    }
    const [, closing, name, attributes, selfClosing] = token.match(/^<(\/?)([A-Za-z_][\w:.-]*)([\s\S]*?)(\/?)>$/)
    const localName = name.split(':').at(-1)
    if (!ELEMENTS.has(localName)) throw new TypeError(`Unsupported palette SVG element: ${localName}`)
    if (closing) {
      if (selfClosing || attributes.trim() || stack.pop() !== name) throw new TypeError('Malformed SVG artwork')
      result += token; continue
    }
    const isRoot = !rootSeen
    if (!stack.length && (!isRoot || localName !== 'svg')) throw new TypeError('Palette artwork must have one SVG root')
    rootSeen = true
    const seen = new Set()
    let attrEnd = 0
    let rewritten = ''
    for (const attr of attributes.matchAll(ATTRIBUTE)) {
      if (attributes.slice(attrEnd, attr.index).trim()) throw new TypeError('Malformed SVG attributes')
      const [, space, attrName, equal, quote, value] = attr
      if (seen.has(attrName) || /^on/i.test(attrName) || attrName === 'xml:base') throw new TypeError('Unsupported SVG attribute')
      seen.add(attrName)
      if (attrName.split(':').at(-1) === 'href' && !/^#[\w:.-]+$/.test(value)) throw new TypeError('Palette artwork cannot reference external files')
      if (['style', 'fill', 'stroke', 'filter', 'clip-path'].includes(attrName)) checkCss(value)
      if (attrName === 'xmlns' && value !== 'http://www.w3.org/2000/svg') throw new TypeError('Palette artwork must use the SVG namespace')
      const next = ['fill', 'stroke'].includes(attrName) ? paint(value) : attrName === 'style' ? declarations(value) : value
      rewritten += attributes.slice(attrEnd, attr.index) + space + attrName + equal + quote + next + quote
      attrEnd = attr.index + attr[0].length
    }
    if (attributes.slice(attrEnd).trim()) throw new TypeError('Malformed SVG attributes')
    rewritten += attributes.slice(attrEnd)
    if (isRoot && defaultFill && !seen.has('fill')) rewritten += ` fill="${defaultFill}"`
    result += `<${name}${rewritten}${selfClosing}>`
    if (!selfClosing) stack.push(name)
  }
  result += text(svg.slice(end))
  if (!rootSeen || stack.length) throw new TypeError('Malformed SVG artwork')
  return result
}
