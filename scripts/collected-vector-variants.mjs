import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync } from 'node:fs'
import { DOMParser, XMLSerializer } from '@xmldom/xmldom'

const publicRoot = new URL('../public/', import.meta.url)
const heritage = 'historical-bc-heritage-trust-2002'
const burnaby = 'school-district-41-strategic-plan-white-on-blue'
const heritageSilver = 'rgb(84.991229%,85.003436%,84.988177%)'
const heritageWhite = 'rgb(100%,100%,100%)'
const burnabyWhite = 'rgb(100%, 100%, 100%)'
const quickpassInk = 'rgb(13.729858%, 12.159729%, 12.548828%)'
const solutionsInk = { '#B3A9A7': '#B3A9A7', '#FFFFFF': '#FFFFFF' }
const sharedServicesInk = {
  [burnabyWhite]: burnabyWhite,
  'rgb(98.022461%, 71.543884%, 9.829712%)': 'rgb(98.022461%, 71.543884%, 9.829712%)',
  'rgb(97.88208%, 69.723511%, 4.234314%)': 'rgb(97.88208%, 69.723511%, 4.234314%)',
  'rgb(29.931641%, 40.478516%, 66.053772%)': 'rgb(29.931641%, 40.478516%, 66.053772%)',
  'url(#radial-pattern-0)': 'url(#radial-pattern-0)'
}

const usingFill = (kind, fill) => (node) => node.localName === kind && node.getAttribute('fill') === fill
const usingClip = (id) => (node) => node.localName === 'g' && node.getAttribute('clip-path') === `url(#${id})`
const solidBlack = (inks) => Object.fromEntries(inks.map((ink) => [ink, '#000000']))
const blackVersion = (inks, note) => ({
  name: 'black', label: 'Black · transparent', inks: solidBlack(inks), note, sourceGround: 'light'
})
const whiteVersions = (ink, artwork) => [
  { name: 'transparent', label: 'White · transparent', inks: { [ink]: ink }, note: `White ${artwork} on a transparent canvas.` },
  blackVersion([ink], `Solid black ${artwork} on a transparent canvas.`)
]

// The colour SVG lays the sun highlight over the gold sun. In one ink the highlight must
// cut through the gold beneath it. Apply the original gradient and clips as a luminance mask
// on the sun layers. The mountain path is drawn outside the mask and stays solid.
function knockOutSunHighlight(document, svg, gradientId) {
  const gradient = document.getElementById(gradientId)
  const sun = Array.from(svg.childNodes).filter((node) => node.nodeType === 1 &&
    /^url\(#clip-(?:2[02468]|3[02468]|4[02])\)$/.test(node.getAttribute('clip-path')))
  if (gradient?.localName !== 'radialGradient' || sun.length !== 12) throw new Error('Unexpected Shared Services BC sun structure')

  const highlight = sun.at(-1).cloneNode(true)
  highlight.getElementsByTagName('path')[0].setAttribute('fill', `url(#${gradientId})`)
  for (const stop of Array.from(gradient.getElementsByTagName('stop'))) {
    stop.setAttribute('stop-color', stop.getAttribute('stop-color') === burnabyWhite ? '#000000' : '#ffffff')
  }

  const create = (name, attributes) => {
    const element = document.createElementNS(svg.namespaceURI, name)
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value)
    return element
  }
  const [x, y, width, height] = svg.getAttribute('viewBox').split(/\s+/)
  const bounds = { x, y, width, height }
  const mask = create('mask', { id: 'sun-highlight', maskUnits: 'userSpaceOnUse', ...bounds })
  mask.appendChild(create('rect', { ...bounds, fill: '#ffffff' }))
  mask.appendChild(highlight)
  svg.getElementsByTagName('defs')[0].appendChild(mask)

  const group = create('g', { mask: 'url(#sun-highlight)' })
  svg.insertBefore(group, sun[0])
  for (const layer of sun) group.appendChild(layer)
}

export const galleryVectorTreatments = {
  'source-recovered-bcic-2008-09': {
    designLabel: 'British Columbia Innovation Council full-name logo',
    originalLabel: 'White on blue · 2008/09', preferred: 'transparent',
    field: usingFill('path', '#00aeef'), remove: 'Removed the blue rectangle from the 2008/09 service plan.',
    choices: whiteVersions('#ffffff', 'full-name logo from the 2008/09 service plan')
  },
  'bcic-horizontal-2011': {
    designLabel: 'BCIC horizontal initials',
    originalLabel: 'White on blue · 2011/12', preferred: 'transparent',
    field: usingFill('path', '#00aeef'), remove: 'Removed the blue rectangle from the 2011/12 service plan.',
    choices: whiteVersions('#ffffff', 'BCIC initials and emblem from the 2011/12 service plan')
  },
  'ogc-2000-monogram': {
    designLabel: 'OGC monogram between horizontal rules',
    originalLabel: 'Red panel · 1999/2000', preferred: 'transparent',
    field: usingFill('path', '#d73648'), remove: 'Removed the rounded red panel from the 1999/2000 annual report cover.',
    choices: [
      { name: 'transparent', label: 'Original ink · transparent', inks: { '#162c36': '#162c36' }, note: 'The original dark monogram and two rules from the annual report cover, on a transparent canvas.' },
      blackVersion(['#162c36'], 'Solid black monogram and rules on a transparent canvas.')
    ]
  },
  'shared-services-bc-2015-brochure-vector': {
    originalLabel: 'On navy · brochure', preferred: 'transparent',
    field: usingClip('clip-0'), fieldDefinitions: ['clip-0'], remove: 'Removed the brochure’s navy footer artwork behind the signature.',
    choices: [
      { name: 'transparent', label: 'Colour · transparent', inks: sharedServicesInk, note: 'The brochure’s native reversed signature with its sun gradient, gold divider and lettering on a transparent canvas.' },
      {
        ...blackVersion(Object.keys(sharedServicesInk), 'Black signature with the pale sun highlight opened to transparency.'),
        knockoutGradient: 'radial-pattern-0'
      }
    ]
  },
  'quickpass-2009-black-vector': {
    originalLabel: 'Black on white · handout', preferred: 'colour',
    field: usingClip('clip-0'), fieldDefinitions: ['clip-0'], remove: 'Removed the white paper shape from the PDF extract.',
    choices: [
      {
        name: 'colour', label: 'Grey and blue · transparent', inks: { [quickpassInk]: '#5f6062' },
        accents: { '#0061ac': ['M 96.914062 22.773438', 'M 110.023438 28.265625', 'M 126.515625 20.332031', 'M 137.824219 20.332031'] },
        colourReference: 'https://buzzer.translink.ca/wp-content/uploads/2009/11/2009-11-19-quickpass-geb-media-tour-handout.pdf#page=2',
        note: 'The native handout outlines with grey and blue sampled from its page 2 colour image, on a transparent canvas.'
      },
      { name: 'transparent', label: 'Black · transparent', inks: { [quickpassInk]: quickpassInk }, sourceGround: 'light', note: 'The handout’s original black ink on a transparent canvas.' }
    ]
  },
  'school-district-38-strategic-plan-reverse': {
    originalLabel: 'White on blue · brochure',
    field: (node) => usingClip('clip-0')(node) || usingClip('clip-1')(node), fieldCount: 2,
    fieldDefinitions: ['clip-0', 'clip-1'], remove: 'Removed the blue field and clipped gold page panel from the planning brochure.',
    choices: whiteVersions(burnabyWhite, 'Richmond wordmark and district subline')
  },
  'solutions-bc-2003-vector': {
    designLabel: 'Solutions BC', originalLabel: 'On teal · reconstruction', preferred: 'transparent',
    field: (node) => node.localName === 'rect' && node.getAttribute('id') === 'background',
    remove: 'Removed the teal rectangle behind the reconstructed artwork.',
    choices: [{ name: 'transparent', label: 'Silver and white · transparent', inks: solutionsInk, note: 'The reconstructed silver emblem and white lettering on a transparent canvas.' }]
  },
  'urban-transit-authority-commons-rebuilt': {
    originalLabel: 'White on orange · reconstruction', preferred: 'transparent',
    field: usingFill('path', '#d54d12'), remove: 'Removed the orange rectangle from the reconstructed Commons drawing.',
    choices: whiteVersions('#ffffff', 'reconstructed double-arrow signature')
  }
}

// These are the separate background layers in the reviewed PDF extracts. Match them by
// geometry or clipping reference so an updated source cannot silently drop a logo path.
const treatments = {
  [heritage]: {
    field: (node) => node.localName === 'path' && node.getAttribute('d') ===
      'M 164.52 108 L 447.47998 108 L 447.47998 326.16 L 164.52 326.16 Z',
    remove: 'Removed the black rectangle behind the lettering.',
    choices: [
      {
        name: 'transparent', label: 'Greyscale · transparent',
        inks: { [heritageSilver]: '#262626', [heritageWhite]: '#000000' },
        note: 'Positive greyscale version of the annual-report lettering on a transparent canvas.'
      },
      {
        name: 'black', label: 'Black · transparent', sourceGround: 'light',
        inks: { [heritageSilver]: '#000000', [heritageWhite]: '#000000' },
        note: 'Solid black version of the annual-report lettering on a transparent canvas.'
      }
    ]
  },
  [burnaby]: {
    field: (node) => node.localName === 'g' && node.getAttribute('clip-path') === 'url(#clip-0)',
    fieldDefinitions: ['clip-0', 'clip-1', 'clip-2', 'filter-remove-color', 'linear-pattern-0', 'mask-0', 'source-5'],
    remove: 'Removed the blue publication field and its clipped underlay.',
    choices: [
      {
        name: 'transparent', label: 'White · transparent',
        inks: { [burnabyWhite]: burnabyWhite },
        note: 'The 2021 report’s white emblem and lettering on a transparent canvas.'
      },
      {
        name: 'black', label: 'Black · transparent', sourceGround: 'light',
        inks: { [burnabyWhite]: '#000000' },
        note: 'Solid black version of the 2021 report’s emblem and lettering on a transparent canvas.'
      }
    ]
  }
}

export function collectedVectorVariants(source, { check = false, treatment = treatments[source.id] } = {}) {
  if (!treatment) return []

  const original = readFileSync(new URL(source.file, publicRoot), 'utf8')
  return treatment.choices.map(({ name, label, inks, note, sourceGround, accents, colourReference, knockoutGradient }) => {
    const document = new DOMParser().parseFromString(original, 'image/svg+xml')
    const svg = document.documentElement
    const fields = Array.from(svg.getElementsByTagName('*')).filter(treatment.field)
    if (fields.length !== (treatment.fieldCount ?? 1)) throw new Error(`Unexpected source background in ${source.file}`)
    for (const field of fields) field.parentNode.removeChild(field)
    for (const id of treatment.fieldDefinitions ?? []) {
      const definition = document.getElementById(id)
      if (!definition) throw new Error(`Missing background definition ${id} in ${source.file}`)
      definition.parentNode.removeChild(definition)
    }

    const used = new Set()
    for (const shape of Array.from(svg.getElementsByTagName('*'))) {
      const ink = shape.getAttribute('fill')
      if (!ink || ink === 'none') continue
      if (!Object.hasOwn(inks, ink)) throw new Error(`Unexpected foreground fill ${ink} in ${source.file}`)
      shape.setAttribute('fill', inks[ink])
      used.add(ink)
    }
    if (used.size !== Object.keys(inks).length) throw new Error(`Missing foreground ink in ${source.file}`)
    for (const [colour, prefixes] of Object.entries(accents ?? {})) for (const prefix of prefixes) {
      const matches = Array.from(svg.getElementsByTagName('path')).filter((path) => path.getAttribute('d').startsWith(prefix))
      if (matches.length !== 1) throw new Error(`Missing or ambiguous colour accent in ${source.file}: ${prefix}`)
      matches[0].setAttribute('fill', colour)
    }
    if (knockoutGradient) knockOutSunHighlight(document, svg, knockoutGradient)

    const desc = svg.getElementsByTagName('desc')[0] ?? svg.appendChild(document.createElementNS(svg.namespaceURI, 'desc'))
    desc.textContent = note
    const content = new XMLSerializer().serializeToString(document)
    const file = source.file.replace(/\.svg$/, `-${name}.svg`)
    const path = new URL(file, publicRoot)
    if (check) {
      if (readFileSync(path, 'utf8') !== content) throw new Error(`${file} is stale`)
    } else {
      writeFileSync(path, content)
    }

    return {
      id: `${source.id}-${name}`,
      label: `${source.publisher} — ${label}`,
      versionLabel: label,
      variantOf: source.variantOf ?? source.id,
      derivedFrom: source.id,
      file,
      format: 'svg',
      isVector: true,
      containsRaster: false,
      darkBackground: false,
      ...(sourceGround && { sourceGround }),
      publisher: source.publisher,
      sourceUrl: source.sourceUrl ?? source.sourcePage,
      sourcePage: source.sourcePage,
      sourceLocator: source.sourceLocator,
      sourceDate: source.sourceDate,
      observedDate: source.observedDate,
      role: source.role,
      status: source.status,
      sourceKind: source.sourceKind,
      sourceTitle: source.sourceTitle,
      ...(source.reconstruction && { reconstruction: true, reconstructionDate: source.reconstructionDate }),
      ...(colourReference && { alsoSeen: [{ label: 'Colour reference in the original handout', source: colourReference }] }),
      evidenceType: 'adaptation-of-source-vector',
      notes: note,
      fidelityNote: `${treatment.remove} Retained the original vector outlines and clipping.${knockoutGradient ? ' The white stops in the sun gradient become transparent for the black version.' : ''}`,
      bytes: Buffer.byteLength(content),
      sha256: createHash('sha256').update(content).digest('hex')
    }
  })
}
