// Marks that are not arrangements of anything.
//
// The generator is built on patterns: an identity, a lockup, a ministry, a colourway. Most of the
// Province's marks are one of those, which is why it can draw them. Some are not — they were drawn
// once, for one body, and follow no rule that generalises. BC Parks is the plain case: the flag
// symbol inside a frame, both words set alike, which is nothing the standards page describes and
// nothing any other ministry got.
//
// They are collected here rather than bent into the generator, because adding "Badge" beside
// "Horizontal" in a list of arrangements would say that any ministry can be set that way, and
// none can.
//
// Most of them come from the Best Place on Earth years, when programs got a mark of their own:
// the BC mark with its shaded sun, a gold divider, and a name in large Garamond with "BC" picked
// out in gold. Those are drawn from their published artwork (src/assets/oneOffMarks.js, built by
// scripts/build-one-offs.mjs), and only their colours are chosen here.

import { ONE_OFF_MARKS } from '../assets/oneOffMarks.js'

const GOLD = '#fdb913'
const BLUE = '#004b8d'

// The colourways these marks were published in. Colour on white is the BC identity's own; the
// reversal is WelcomeBC's, whose mountains lighten so they still read against the blue.
const COLOUR = {
  background: '#ffffff', sun: GOLD, light: '#ffffff', mountains: BLUE, wordmark: BLUE, rule: GOLD,
  tagline: BLUE, divider: GOLD, name: BLUE, accent: GOLD, leaf: '#d52b1e'
}
const REVERSED = {
  ...COLOUR, background: '#0c68a9', mountains: '#4a6ea7', wordmark: '#ffffff', tagline: '#ffffff', name: '#ffffff'
}
const oneInk = (ink, paper) => ({
  background: paper, sun: ink, light: paper, mountains: ink, wordmark: ink, rule: ink,
  tagline: ink, divider: ink, name: ink, descriptor: ink, accent: ink, leaf: ink
})

const isWhite = (colour) => !colour || colour === 'none' || colour.toLowerCase() === '#ffffff' || colour.toLowerCase() === '#fff'

/**
 * Starting points for a mark: as published, then whichever of colour-on-white and the reversal it
 * was not published in, then one ink each way. One ink draws the sun flat, with the rays and core
 * cut out of it, which is how the BC mark is always reduced to a single colour.
 */
const presetsFor = (id, publishedLabel = 'As published') => {
  const printed = ONE_OFF_MARKS[id].printed
  const onWhite = isWhite(printed.background)
  return [
    { id: 'published', label: publishedLabel, sun: 'glow', colours: { ...printed, background: printed.background ?? '#ffffff' } },
    onWhite
      ? { id: 'reversed', label: 'Reversed', sun: 'glow', colours: REVERSED }
      : { id: 'colour', label: 'On white', sun: 'glow', colours: COLOUR },
    { id: 'mono', label: 'One ink', sun: 'flat', colours: oneInk('#000000', '#ffffff') },
    { id: 'mono-reverse', label: 'One ink, reversed', sun: 'flat', colours: oneInk('#ffffff', BLUE) }
  ]
}

const artwork = (entry) => ({ kind: 'artwork', mark: entry.id, presets: presetsFor(entry.id, entry.publishedLabel), ...entry })

export const ONE_OFFS = [
  {
    id: 'bc-parks',
    label: 'BC Parks',
    body: 'BC Parks',
    years: 'from the 1980s',
    note: 'The flag symbol inside a rounded frame, with “Parks” set at the same size as “BC” — ' +
      'both words are the wordmark, not a ministry line under a symbol. The frame is a ' +
      'superellipse, which is what gives it sides that bow where a rounded rectangle’s run ' +
      'straight.',
    caveat: 'Proportions are read off a picture of the mark, not measured from artwork.',
    kind: 'flag',
    draw: { symbol: 'badge', ministry: 'Parks' },
    // Starting points, not separate marks. A mark gets one card in the gallery; these are offered
    // inside it, and every colour is editable from there anyway.
    presets: [
      { id: 'colour', label: 'Colour', ink: '#10069f', palette: 'official', background: '#ffffff' },
      { id: 'mono', label: 'One ink', ink: '#000000', palette: 'ink', background: '#ffffff' },
      { id: 'reverse', label: 'Reversed', ink: '#ffffff', palette: 'ink', background: '#10069f' }
    ]
  },
  artwork({
    id: 'welcome-bc',
    label: 'WelcomeBC',
    body: 'WelcomeBC',
    years: 'Best Place on Earth years',
    note: 'The BC mark beside one word, “WelcomeBC”, in large Garamond with “BC” in gold — ' +
      'where a ministry mark would set a name in the same small size as its own. The wordmark ' +
      'is tracked twice as tight as the ministry marks, at −20/1000 em.',
    caveat: 'Drawn from the published artwork. The sun’s glow is sampled from the print file’s ' +
      'shading into gradients, so it recolours with the rest.'
  }),
  artwork({
    id: 'work-bc',
    label: 'WorkBC',
    body: 'WorkBC',
    years: 'Best Place on Earth years',
    note: 'WelcomeBC’s arrangement, with the tagline under the mark and a larger wordmark. ' +
      'The “rk” pair is opened by hand, a little wider than the typeface’s own kerning.',
    caveat: 'Drawn from a brochure page. The navy it was published on is the page’s, sampled ' +
      'from the photograph behind it, and not part of the mark.'
  }),
  artwork({
    id: 'bc-stats',
    label: 'BC Stats',
    body: 'BC Stats',
    years: 'Best Place on Earth years',
    note: 'No tagline, and one word beside the mark: “BC” in gold running straight into “Stats” ' +
      'in blue, so the S does double duty as the capital of both.',
    caveat: 'Drawn from the published artwork.'
  }),
  artwork({
    id: 'environmental-reporting-bc',
    label: 'Environmental Reporting BC',
    body: 'Environmental Reporting BC',
    years: 'Best Place on Earth years',
    note: 'Two lines beside the mark, with “BC” in gold ending the second — the one mark here ' +
      'where the accent closes a longer name rather than making up half of one word.',
    caveat: 'Drawn from the published artwork, which is in the screen colours (#234075 and ' +
      '#e3a82b) rather than the print ones the others use.'
  }),
  artwork({
    id: 'stronger-bc',
    label: 'StrongerBC',
    body: 'StrongerBC',
    years: 'from 2021',
    note: 'A later mark than the rest, and a different idea of one: the flat sun, a grey divider, ' +
      'and the name in a heavy sans with “BC” in gold, “for everyone” set beneath it in italic.',
    caveat: 'Drawn from the published artwork. Its sun was published flat, so there is no ' +
      'shading to switch on.'
  }),
  artwork({
    id: 'bc-wildfire-service',
    label: 'BC Wildfire Service',
    body: 'BC Wildfire Service',
    years: 'in use today',
    publishedLabel: 'As published, reversed',
    note: 'The later flat sun with a gold divider, and the name in large Garamond on two lines, ' +
      '“BC Wildfire” over “Service”, with “BC” in gold.',
    caveat: 'Drawn from the published artwork, which sets it reversed over a photograph. The ' +
      'ground here is the photograph’s dominant dark tone, not part of the mark.'
  }),
  artwork({
    id: 'bc-wildfire-service-one-line',
    label: 'BC Wildfire Service, one line',
    body: 'BC Wildfire Service',
    years: 'in use today',
    publishedLabel: 'As published, reversed',
    note: 'The same mark with the whole name on one line, for spaces too shallow for two.',
    caveat: 'Drawn from the cover of the 2025 Cultural and Prescribed Fire annual report, where it ' +
      'is reversed on the cover’s navy. The navy is the page’s, not part of the mark.'
  }),
  artwork({
    id: 'environmental-lab-bc',
    label: 'Environmental Lab BC',
    body: 'Environmental Lab BC',
    years: 'date unknown',
    note: 'Environmental Reporting BC’s arrangement — two lines beside the mark, “BC” in gold closing ' +
      'the second — but on the later flat sun, with the gold divider kept.',
    caveat: 'Drawn from the supplied artwork, in the screen colours (#234075 and #e3a82b).'
  }),
  {
    id: 'prepared-bc',
    kind: 'current',
    label: 'PreparedBC',
    body: 'PreparedBC',
    years: 'remade in the current identity',
    // Set, not lifted: the generator's current era draws it, so it opens there.
    text: 'PreparedBC',
    note: 'Set as a ministry mark is today: the BC mark as published, a gold divider, and ' +
      '“PreparedBC” in the Garamond the ministry marks are lettered in. The program’s own mark was ' +
      'the BC mark in outline, in one orange ink — nothing the current identity draws — so it is ' +
      'remade here rather than lifted.',
    caveat: 'A remake, not a published mark. It opens in the generator, in the current era, with ' +
      'the wording already typed.'
  },
  artwork({
    id: 'public-service',
    label: 'BC Public Service',
    body: 'BC Public Service',
    years: 'Best Place on Earth years',
    note: '“BC Public Service” takes the tagline’s place under the mark, and the line beside it ' +
      'is a slogan — “Where ideas work” — rather than a name.',
    caveat: 'Drawn from the published artwork.'
  }),
  artwork({
    id: 'pacific-gateway',
    label: 'Canada’s Pacific Gateway',
    body: 'Canada’s Pacific Gateway',
    years: 'Best Place on Earth years',
    note: 'Two lines beside the mark, with a red maple leaf standing in for the apostrophe in ' +
      '“Canada’s”.',
    caveat: 'Drawn from the published artwork. The leaf was shaded in the print file and is ' +
      'drawn here in its average red.'
  }),
  artwork({
    id: 'best-place-on-earth',
    label: 'The Best Place on Earth',
    body: 'Province of British Columbia',
    years: 'Best Place on Earth years',
    note: 'The BC mark itself, stacked, with a gold rule and the tagline beneath it — the ' +
      'version every mark above sets beside a name.',
    caveat: 'Drawn from the published artwork.'
  })
]

export const findOneOff = (id) => ONE_OFFS.find((entry) => entry.id === id)

// ── BC Timber Sales ──────────────────────────────────────────────────────────────────────────────

// Its initials have been published in two greens: forest green on white, and a lighter teal where
// the mark is reversed. Either can start any of its marks.
export const BCTS_FOREST = '#016a37'
export const BCTS_TEAL = '#009979'

// The reversed mark, as its picture shows it: white type, the lighter mountains the Province's
// reversed marks use, the print gold, and the initials in teal. The picture has no ground of its
// own, so this dark is the mark's own near-black, not part of the mark.
const BCTS_REVERSED = {
  background: '#231f20', sun: '#fdb813', mountains: '#4d5d92', wordmark: '#ffffff', name: BCTS_TEAL, descriptor: '#ffffff'
}

/** The published colours, then each green on the rest of the published mark, then one ink. */
const bctsPresets = (id, greens) => {
  const printed = { ...ONE_OFF_MARKS[id].printed }
  printed.background ??= '#ffffff'
  return [
    ...greens.map(({ id: presetId, label, colours }) => ({ id: presetId, label, sun: 'glow', colours: { ...printed, ...colours } })),
    { id: 'mono', label: 'One ink', sun: 'flat', colours: oneInk('#000000', '#ffffff') },
    { id: 'mono-reverse', label: 'One ink, reversed', sun: 'flat', colours: oneInk('#ffffff', BCTS_FOREST) }
  ]
}

const bcts = (entry) => ({ kind: 'artwork', mark: entry.id, ...entry, presets: bctsPresets(entry.id, entry.presets) })

export const BCTS_ENTRIES = {
  earlier: [
    bcts({
      id: 'bcts-wordmark-earlier',
      label: 'BCTS, BC Timber Sales in a slab serif',
      body: 'BC Timber Sales',
      years: 'earlier',
      note: 'The initials in a heavy green sans over the name in a slab serif, set without the BC mark.',
      caveat: 'Drawn from the supplied artwork. Its green, #008450, sits between the two the later ' +
        'marks use.',
      presets: [
        { id: 'published', label: 'As published', colours: {} },
        { id: 'forest', label: 'Forest green', colours: { name: BCTS_FOREST } },
        { id: 'teal', label: 'Teal', colours: { name: BCTS_TEAL } }
      ]
    })
  ],
  current: [
    bcts({
      id: 'bcts',
      label: 'BCTS, BC Timber Sales',
      body: 'BC Timber Sales',
      years: 'in use today',
      note: 'The BC mark with its flat sun, a grey divider, and the initials over the name in a sans — ' +
        'forest green over black on white, or teal over white reversed.',
      caveat: 'Drawn from the published artwork. The reversed colours are sampled from a picture of ' +
        'the reversed mark, which lines up with this artwork to within a pixel; its ground is ' +
        'transparent, so the dark behind it here is not part of the mark.',
      presets: [
        { id: 'forest', label: 'Forest green, as published', colours: {} },
        { id: 'teal-reversed', label: 'Teal, reversed, as published', colours: BCTS_REVERSED },
        { id: 'teal', label: 'Teal on white', colours: { name: BCTS_TEAL } }
      ]
    })
  ]
}
