// The historical BC Hydro signatures: what they are, how each application lays them out, and what
// the manual allows.
//
// Four signatures share one symbol and one wordmark: the corporate signature, Gas Operations (the
// flame round the symbol), Rail (a division name after the wordmark) and the full authority name
// on two lines. The manual then sets them out for four applications — the signature itself,
// identification signs with a facility name below, single-colour use on general backgrounds, and
// vehicles — each with rules of its own. A preset is one signature in one application.
//
// Everything here is plain arithmetic over the committed serif table, so it runs in Node as well as
// in the page. Where the manual gives a rule it is followed and named; where it gives none — an
// enlargement factor, the spacing between facility lines — the choice made is said to be one.

import { HYDRO_STANDARDS } from './standards.js'
import { FLAME_RISE, RING_WEIGHT, WORDMARK, WORDMARK_CAP_LETTER, WORDMARK_FIT, WORDMARK_LETTERS } from './hydroMark.js'
import { capHeightAt, missingLetters, setRun, shiftRun, unionBox, xHeightAt } from './hydroType.js'

export const HYDRO_TYPES = {
  standard: 'Corporate',
  gas: 'Gas Operations',
  rail: 'Rail',
  authority: 'Full authority name'
}
export const HYDRO_TYPE_ORDER = ['standard', 'gas', 'rail', 'authority']

export const HYDRO_GROUPS = {
  signature: 'Signatures',
  sign: 'Identification signs',
  general: 'General backgrounds',
  vehicle: 'Vehicles'
}
export const HYDRO_GROUP_ORDER = ['signature', 'sign', 'general', 'vehicle']

export const HYDRO_MODES = {
  colour: 'Corporate colour',
  black: 'Positive · black',
  white: 'Reverse · white',
  single: 'Single coloured ink'
}
export const HYDRO_MODE_ORDER = ['colour', 'black', 'white', 'single']

/** The manual's own examples, one signature in one application each. */
export const HYDRO_PRESETS = {
  standard: { group: 'signature', name: 'Corporate signature', type: 'standard', caption: 'Green + blue symbol; black lettering' },
  gas: { group: 'signature', name: 'Gas Operations', type: 'gas', caption: 'Blue flame and matching blue H' },
  rail: { group: 'signature', name: 'Rail signature', type: 'rail', caption: 'Corporate symbol + Rail suffix' },
  authority: { group: 'signature', name: 'Full authority name', type: 'authority', caption: 'Two editable lines' },
  'sign-office': { group: 'sign', name: 'Office identification', type: 'standard', caption: 'Signature only · ½-cap borders' },
  'sign-gas': { group: 'sign', name: 'Gas identification', type: 'gas', caption: 'Full cap-height above logotype' },
  'sign-freight': { group: 'sign', name: 'Horizontal facility', type: 'rail', caption: 'Editable one-line facility name', facility: 'Huntingdon Freight Office', nameLayout: 'horizontal', mode: 'black' },
  'sign-plant': { group: 'sign', name: 'Vertical facility', type: 'gas', caption: 'Editable stacked facility name', facility: 'Liquefied\nNatural Gas\nPlant', nameLayout: 'vertical' },
  'positive-white': { group: 'general', name: '1 · Black on white', type: 'standard', caption: 'Preferred single-colour form', mode: 'black', bg: '#ffffff', value: 0 },
  'positive-light': { group: 'general', name: '2 · Black on light', type: 'standard', caption: 'Background value ≤20%', mode: 'black', bg: '#e0efcc', value: 20 },
  'positive-ink': { group: 'general', name: '3 · Alternative ink', type: 'standard', caption: 'Ink value ≥70%; white ground', mode: 'single', bg: '#ffffff', value: 0 },
  'reverse-black': { group: 'general', name: '4 · White on black', type: 'standard', caption: 'Preferred reverse form', mode: 'white', bg: '#000000', value: 100 },
  'reverse-dark': { group: 'general', name: '5 · White on dark', type: 'standard', caption: 'Background value ≥80%', mode: 'white', bg: '#333333', value: 80 },
  'vehicle-corporate-positive': { group: 'vehicle', name: 'Corporate · positive', type: 'standard', caption: 'Vehicle value 0–30%', mode: 'black', bg: '#dbecee', value: 20 },
  'vehicle-corporate-reverse': { group: 'vehicle', name: 'Corporate · reverse', type: 'standard', caption: 'Vehicle value 31–100%', mode: 'white', bg: '#00af00', value: 60 },
  'vehicle-gas-positive': { group: 'vehicle', name: 'Gas · positive', type: 'gas', caption: 'Vehicle value 0–30%', mode: 'black', bg: '#dbecee', value: 20 },
  'vehicle-gas-reverse': { group: 'vehicle', name: 'Gas · reverse', type: 'gas', caption: 'Vehicle value 31–100%', mode: 'white', bg: '#0069a2', value: 60 },
  'vehicle-rail-positive': { group: 'vehicle', name: 'Rail · positive', type: 'rail', caption: 'Vehicle value 0–30%', mode: 'black', bg: '#e0efcc', value: 20 },
  'vehicle-rail-reverse': { group: 'vehicle', name: 'Rail · reverse', type: 'rail', caption: 'Vehicle value 31–100%', mode: 'white', bg: '#666666', value: 60 }
}
export const HYDRO_PRESET_ORDER = Object.keys(HYDRO_PRESETS)

/** Screen colours: sampled from the manual's scan, or the earlier reconstruction's. */
export const HYDRO_SCREEN_PALETTES = {
  scan: { label: 'Sampled from the scan', green: '#00af00', blue: '#0069a2' },
  legacy: { label: 'Earlier reconstruction', green: '#40b22b', blue: '#1c84a3' }
}

/** Numeric settings and the range each is held to. */
export const HYDRO_RANGES = {
  emblemScale: [55, 150],
  textScale: [60, 145],
  gap: [0, 180],
  tracking: [-8, 16],
  suffixGap: [0, 160],
  lineGap: [75, 155],
  symbolOffset: [-80, 80],
  ringWeight: [20, 80],
  starScale: [70, 115],
  padding: [0, 120],
  exportWidth: [300, 8000],
  backgroundValue: [0, 100],
  inkValue: [0, 100],
  nameScale: [50, 150],
  nameWidth: [60, 120],
  borderWeight: [0.5, 8]
}

/** The proportions a person may adjust, as [key, label, step, unit]. */
export const HYDRO_SLIDERS = [
  ['emblemScale', 'Emblem size', 1, '%'],
  ['textScale', 'Lettering size', 1, '%'],
  ['gap', 'Symbol-to-text gap', 1, ''],
  ['tracking', 'Extra letter spacing', 0.25, ''],
  ['suffixGap', 'Suffix gap', 1, ''],
  ['lineGap', 'Authority line spacing', 1, ''],
  ['nameScale', 'Facility name size', 1, '%'],
  ['nameWidth', 'Facility name width', 1, '%']
]
export const HYDRO_ADVANCED_SLIDERS = [
  ['symbolOffset', 'Symbol vertical offset', 1, ''],
  ['ringWeight', 'Ring weight', 0.5, ''],
  ['starScale', 'Inner H size', 1, '%'],
  ['padding', 'Artwork padding', 1, ''],
  ['borderWeight', 'Sign border stroke', 0.25, '']
]

const DEFAULT_WORDING = {
  wordmark: WORDMARK,
  suffix: 'Rail',
  line1: 'British Columbia Hydro',
  line2: 'and Power Authority'
}

/** A preset's starting settings. */
export const hydroDefaults = (id = 'standard') => {
  const presetId = id === 'droplet' ? 'gas' : id
  const preset = HYDRO_PRESETS[presetId] ?? HYDRO_PRESETS.standard
  const { scan } = HYDRO_SCREEN_PALETTES
  return {
    preset: HYDRO_PRESETS[presetId] ? presetId : 'standard',
    type: preset.type,
    usage: preset.group,
    mode: preset.mode || 'colour',
    ...DEFAULT_WORDING,
    facility: preset.facility || '',
    nameLayout: preset.nameLayout || 'none',
    emblemOnly: false,
    ink: '#003b4d',
    green: scan.green,
    blue: scan.blue,
    screenPalette: 'scan',
    process: 'coated',
    background: preset.group === 'signature' ? 'transparent' : 'solid',
    backgroundColour: preset.bg || '#ffffff',
    backgroundValue: preset.value ?? 0,
    inkValue: 80,
    autoTreatment: preset.group === 'vehicle' || (preset.group === 'general' && preset.mode !== 'single'),
    blackUnavailable: preset.mode === 'single',
    linkVehiclePair: true,
    showGuides: false,
    showBorder: true,
    emblemScale: 100,
    textScale: 100,
    gap: preset.type === 'authority' ? 48 : 28,
    tracking: 0,
    suffixGap: 36,
    lineGap: 110,
    symbolOffset: 0,
    ringWeight: RING_WEIGHT,
    starScale: 100,
    padding: preset.group === 'vehicle' ? 85 : 24,
    nameScale: preset.nameLayout === 'vertical' ? 105 : 110,
    nameWidth: preset.nameLayout === 'vertical' ? 88 : 90,
    borderWeight: 2,
    exportWidth: 1800
  }
}

/** Every preset at its defaults. */
export const allHydroDefaults = () => Object.fromEntries(HYDRO_PRESET_ORDER.map((id) => [id, hydroDefaults(id)]))

const CHOICES = {
  type: HYDRO_TYPE_ORDER,
  mode: HYDRO_MODE_ORDER,
  screenPalette: ['scan', 'legacy', 'custom'],
  process: ['coated', 'uncoated', 'non-process'],
  background: ['transparent', 'solid'],
  nameLayout: ['none', 'horizontal', 'vertical']
}
const SWITCHES = ['emblemOnly', 'autoTreatment', 'showGuides', 'showBorder', 'blackUnavailable', 'linkVehiclePair']
const COLOURS = ['ink', 'green', 'blue', 'backgroundColour']
const controlFree = (value) => value.replace(/[\u0000-\u001f\u007f]/g, ' ')

/**
 * Settings from outside — a saved file, a share — brought back within bounds. Anything missing or
 * malformed takes the preset's default; nothing is trusted as given.
 */
export const cleanHydroSettings = (input, id) => {
  const settings = hydroDefaults(id)
  if (!input || typeof input !== 'object' || Array.isArray(input)) return settings

  for (const key of ['wordmark', 'suffix', 'line1', 'line2']) {
    if (typeof input[key] === 'string') settings[key] = controlFree(input[key]).slice(0, 120)
  }
  if (typeof input.facility === 'string') {
    settings.facility = input.facility.replace(/[\u0000-\u0009\u000b-\u001f\u007f]/g, ' ')
      .slice(0, 720).split('\n').slice(0, 6).join('\n')
  }
  for (const key of COLOURS) {
    if (typeof input[key] === 'string' && /^#[0-9a-f]{6}$/i.test(input[key])) settings[key] = input[key]
  }
  for (const [key, [low, high]] of Object.entries(HYDRO_RANGES)) {
    if (typeof input[key] === 'number' && Number.isFinite(input[key])) settings[key] = Math.max(low, Math.min(high, input[key]))
  }
  settings.backgroundValue = Math.round(settings.backgroundValue)
  settings.inkValue = Math.round(settings.inkValue)
  for (const [key, values] of Object.entries(CHOICES)) {
    if (values.includes(input[key])) settings[key] = input[key]
  }
  for (const key of SWITCHES) {
    if (typeof input[key] === 'boolean') settings[key] = input[key]
  }
  if (!['general', 'vehicle'].includes(settings.usage)) settings.autoTreatment = false
  return settings
}

/**
 * The treatment the manual prescribes for a declared background value, or null where it prescribes
 * none. Vehicles and general backgrounds have different thresholds, and the manual is explicit that
 * one must not stand in for the other.
 */
export const recommendedMode = (settings) => {
  if (settings.background === 'transparent') return null
  const { vehicles, generalBackgrounds } = HYDRO_STANDARDS
  if (settings.usage === 'vehicle') return settings.backgroundValue <= vehicles.positiveBackgroundValue[1] ? 'black' : 'white'
  if (settings.usage === 'general') {
    if (settings.backgroundValue <= generalBackgrounds.blackOnTint.backgroundValueMax) return 'black'
    if (settings.backgroundValue >= generalBackgrounds.reverseMinimum.backgroundValueMin) return 'white'
  }
  return null
}

/** The treatment actually drawn: the rule's, where it is asked for and there is one. */
export const effectiveMode = (settings) =>
  settings.autoTreatment ? recommendedMode(settings) || settings.mode : settings.mode

/**
 * The colours of each part. In corporate colour only the symbol is green and blue — the lettering
 * and the ring are black; the Gas flame and its H are both blue. Every single-colour form is one
 * colour throughout.
 */
export const hydroPalette = (settings) => {
  const mode = effectiveMode(settings)
  if (mode === 'black') return { ink: '#000000', upper: '#000000', lower: '#000000' }
  if (mode === 'white') return { ink: '#ffffff', upper: '#ffffff', lower: '#ffffff' }
  if (mode === 'single') return { ink: settings.ink, upper: settings.ink, lower: settings.ink }
  return { ink: '#000000', upper: settings.green, lower: settings.blue }
}

/** The printing recipe the manual gives for the chosen process, kept apart from screen colour. */
export const productionSpec = (settings) => {
  const colours = HYDRO_STANDARDS.colours
  const nonProcess = settings.process === 'non-process'
  const key = settings.process === 'uncoated' ? 'processUncoated' : 'processCoated'
  return {
    method: nonProcess ? 'Non-process system' : `Process / ${settings.process} stock`,
    green: nonProcess ? { number: colours.green.nonProcessSystem } : colours.green[key],
    blue: nonProcess ? { number: colours.blue.nonProcessSystem } : colours.blue[key],
    black: colours.black.process,
    colourApplication: HYDRO_STANDARDS.identity,
    source: 'corporate-colours',
    note: `${colours.interpretation} ${colours.productionCaution}`
  }
}

/** A recipe entry as a line: a CMYK mix, or the non-process number. */
export const formatRecipe = (entry) => ('number' in entry ? `Non-process ${entry.number}` : `C${entry.C} M${entry.M} Y${entry.Y} K${entry.K}`)

/** Which of the manual's pages a setting's rules come from. */
export const sourceKeys = (settings) => {
  if (settings.usage === 'sign') return ['identification-signs', settings.type === 'gas' ? 'gas-colours' : 'corporate-colours']
  if (settings.usage === 'vehicle') return ['vehicle-signatures']
  if (settings.usage === 'general') return ['general-backgrounds']
  return [settings.type === 'gas' ? 'gas-colours' : 'corporate-colours']
}

/** The rule, in a sentence or two, for what the settings are. */
export const ruleDescription = (settings) => {
  if (settings.usage === 'sign') {
    return 'Borders are measured in cap-heights; facility names start one x-height below the signature baseline. ' +
      'The flame needs one full cap-height above the lettering. The source spells the rail facility “Huntingdon Freight Office”.'
  }
  if (settings.usage === 'vehicle') {
    return 'For a given vehicle type, preserve the logotype height in positive and reverse forms. ' +
      'The vehicle threshold is 30/31%, not the general-background 20/80% limits.'
  }
  if (settings.usage === 'general') {
    return 'Black on white is preferred. Light backgrounds are limited to 20% value; reverse backgrounds need at least 80%. ' +
      'Alternative coloured ink needs at least 70% value on white, when black is unavailable. ' +
      'Enlargement is required in several examples, but no numerical factor is given.'
  }
  return settings.type === 'gas'
    ? 'The source names this the Gas Operations symbol: a flame enclosing the stylized H. Flame and H always match in colour and value.'
    : 'The source specifies green, blue, and black. Green and blue appear in the symbol only; the logotype is black in the corporate multicolour signature.'
}

/** The facility name's lines, as the layout will set them. */
const facilityLines = (settings) => {
  if (settings.nameLayout === 'none') return []
  if (settings.nameLayout === 'horizontal') return [settings.facility.replace(/\s+/g, ' ').trim()].filter(Boolean)
  return settings.facility.split('\n').map((line) => line.trim()).filter(Boolean).slice(0, 6)
}

/**
 * Lays a signature out: the symbol, every run of type, and for a sign its border — with the box
 * the whole occupies and the measurements a sign is laid out in.
 */
export const hydroScene = (input) => {
  const settings = { ...input }
  const colours = hydroPalette(settings)
  const isGas = settings.type === 'gas'
  const diameter = 200 * settings.emblemScale / 100
  const symbolY = 100 - diameter / 2 + settings.symbolOffset
  const symbol = {
    variant: isGas ? 'gas' : 'circle',
    x: 0,
    y: symbolY,
    size: diameter,
    ring: settings.ringWeight,
    star: settings.starScale / 100,
    colours
  }

  const scene = {
    settings,
    symbols: [symbol],
    runs: [],
    box: { x: 0, y: symbolY - (isGas ? FLAME_RISE * diameter : 0), right: diameter, bottom: symbolY + diameter },
    border: null,
    guides: [],
    metrics: null
  }

  let baseline = 190
  let capTop = 14
  let capHeight = 176
  let xHeight = 119

  if (!settings.emblemOnly) {
    const x = diameter + settings.gap
    const t = settings.textScale / 100

    if (settings.type === 'authority') {
      const size = 132 * t
      const base = 87.4 * t
      const tracking = (-3.6 + settings.tracking) * t
      scene.runs.push(setRun(settings.line1, { x, y: base, size, sx: 0.84, tracking, id: 'authority-line-1' }))
      scene.runs.push(setRun(settings.line2, { x, y: base + settings.lineGap * t, size, sx: 0.84, tracking, id: 'authority-line-2' }))
      capHeight = capHeightAt(size)
      xHeight = xHeightAt(size)
      capTop = base - capHeight
      baseline = base + settings.lineGap * t
    } else {
      const f = WORDMARK_FIT * t
      const top = 14
      const fitted = settings.wordmark === WORDMARK
      if (fitted) {
        WORDMARK_LETTERS.forEach((letter, i) => scene.runs.push(setRun(letter.char, {
          x: x + (letter.x + i * settings.tracking) * f,
          y: top + letter.y * f,
          size: 1000,
          sx: letter.sx * f,
          sy: letter.sy * f,
          optical: true,
          id: `wordmark-letter-${i + 1}`
        })))
      } else {
        scene.runs.push(setRun(settings.wordmark, {
          x, y: top + 171 * f, size: 257 * f, tracking: (-3 + settings.tracking) * f, id: 'custom-wordmark'
        }))
      }
      const reference = scene.runs[fitted ? WORDMARK_CAP_LETTER : 0]
      capHeight = capHeightAt(reference.size) * reference.sy
      xHeight = xHeightAt(reference.size) * reference.sy
      baseline = reference.y
      capTop = baseline - capHeight

      if (settings.type === 'rail' && settings.suffix) {
        const end = Math.max(x, ...scene.runs.map((run) => run.box.right))
        scene.runs.push(setRun(settings.suffix, {
          x: end + settings.suffixGap, y: top + 171 * f, size: 257 * f, sx: 0.88, tracking: (-5 + settings.tracking) * t, id: 'division-suffix'
        }))
      }
    }
    for (const run of scene.runs) scene.box = unionBox(scene.box, run.box)
  }

  scene.signatureBox = { ...scene.box }
  scene.metrics = { capHeight, xHeight, capTop, baseline, facilityFirstTop: null, facilityLastBaseline: null, facilityLineBoxes: [] }

  if (settings.usage === 'sign' && !settings.emblemOnly) {
    const lines = facilityLines(settings)
    // Set so the name's capitals stand at the chosen fraction of the signature's.
    const nominal = 1000 * (capHeight * settings.nameScale / 100) / capHeightAt(1000)
    const signs = HYDRO_STANDARDS.identificationSigns
    let lineTop = baseline + signs.signatureBaselineToNameTopXHeights * xHeight
    let lastBaseline = baseline

    lines.forEach((line, i) => {
      const run = setRun(line, { x: 0, y: 0, size: nominal, sx: settings.nameWidth / 100, tracking: -3.3 * nominal / 260, id: `facility-line-${i + 1}` })
      shiftRun(run, -run.box.x, lineTop - run.box.y)
      scene.runs.push(run)
      scene.box = unionBox(scene.box, run.box)
      if (i === 0) scene.metrics.facilityFirstTop = run.box.y
      scene.metrics.facilityLineBoxes.push({ ...run.box })
      // No added leading: descenders just clear the line below. The clearance is a choice.
      lineTop = run.box.bottom + 0.015 * capHeight
      lastBaseline = run.y
    })
    if (lines.length) scene.metrics.facilityLastBaseline = lastBaseline

    const side = signs.sideBorderCapHeights * capHeight
    const above = (isGas ? signs.gasTopBorderCapHeights : signs.standardTopBorderCapHeights) * capHeight
    scene.border = {
      x: scene.box.x - side,
      y: capTop - above,
      right: scene.box.right + side,
      bottom: lastBaseline + signs.bottomBorderCapHeights * capHeight,
      stroke: settings.borderWeight,
      visible: settings.showBorder
    }
    scene.metrics.borderMargins = {
      sideCapHeights: signs.sideBorderCapHeights,
      topCapHeights: isGas ? signs.gasTopBorderCapHeights : signs.standardTopBorderCapHeights,
      bottomCapHeights: signs.bottomBorderCapHeights
    }
    const half = scene.border.stroke / 2
    scene.box = unionBox(scene.box, {
      x: scene.border.x - half, y: scene.border.y - half, right: scene.border.right + half, bottom: scene.border.bottom + half
    })
    scene.guides = [{ y: capTop, label: 'cap top' }, { y: baseline, label: 'signature baseline' }]
    if (scene.metrics.facilityFirstTop !== null) scene.guides.push({ y: scene.metrics.facilityFirstTop, label: 'name top = baseline + x-height' })
  }

  const pad = settings.padding
  scene.view = {
    x: scene.box.x - pad,
    y: scene.box.y - pad,
    width: Math.max(1, scene.box.right - scene.box.x + 2 * pad),
    height: Math.max(1, scene.box.bottom - scene.box.y + 2 * pad)
  }
  return scene
}

/** Whether the wording is the manual's own, rather than something typed in. */
export const isHistoricalWording = (settings) => settings.type === 'authority'
  ? settings.line1 === DEFAULT_WORDING.line1 && settings.line2 === DEFAULT_WORDING.line2
  : settings.wordmark === WORDMARK && (settings.type !== 'rail' || settings.suffix === DEFAULT_WORDING.suffix)

/** Every piece of wording the settings will set. */
const wordingOf = (settings) => settings.type === 'authority'
  ? [settings.line1, settings.line2]
  : [settings.wordmark, settings.type === 'rail' ? settings.suffix : '', settings.usage === 'sign' ? settings.facility : '']

/**
 * Checks the settings against the manual. Each note is 'info' (what the rule is), 'warning' (a
 * departure worth knowing about) or 'error' (something the manual rules out).
 */
export const validateHydro = (settings, scene = hydroScene(settings)) => {
  const notes = []
  const add = (kind, text) => notes.push({ kind, text })
  const mode = effectiveMode(settings)
  const recommended = recommendedMode(settings)
  const transparent = settings.background === 'transparent'

  if (settings.usage === 'general' || settings.usage === 'vehicle') {
    if (transparent) add('warning', 'Background is transparent. Confirm the final surface before using any value rule.')
    if (settings.usage === 'vehicle') {
      add('info', 'Vehicle rule: black at declared value 0–30%; white at 31–100%. Keep the same logotype height on a given vehicle type.')
      if (!transparent && mode !== recommended) add('error', 'Selected treatment does not match the vehicle rule for the declared background value.')
    } else {
      if (mode === 'single') {
        if (!settings.blackUnavailable) add('warning', 'Alternative coloured ink is described only when black is unavailable.')
        if (transparent || settings.backgroundColour.toLowerCase() !== '#ffffff' || settings.backgroundValue !== 0) {
          add('error', 'The alternative single-ink form requires a white background.')
        }
        if (settings.inkValue < HYDRO_STANDARDS.generalBackgrounds.colouredInkAlternative.inkValueMin) {
          add('error', 'Alternative single-colour ink must have a declared value of at least 70%.')
        }
      } else if (!transparent) {
        if (!recommended) add('error', 'No general single-colour form is prescribed here for values 21–79%. The vehicle threshold must not be used instead.')
        else if (mode !== recommended) add('error', 'Selected treatment does not match the general background rule for the declared value.')
      }
      if (mode === 'white') {
        add('warning', settings.backgroundValue === 100
          ? 'Reverse use calls for considerable enlargement. No numerical scale factor is supplied.'
          : 'Reverse use at the 80% limit needs further enlargement. No numerical scale factor is supplied.')
      } else if (mode === 'black' && settings.backgroundValue > 0) {
        add('warning', 'Black on a light tinted background needs enlargement relative to black on white. No exact factor is supplied.')
      } else if (mode === 'black') {
        add('info', 'Black on white is the manual’s preferred general single-colour form.')
      }
    }
    add('info', '“Value” is your declared historical print/surface value. HEX preview colours do not establish or verify it.')
  }

  if (settings.usage === 'sign') {
    if (settings.emblemOnly) {
      add('error', 'Identification signs require a full signature, not an emblem alone.')
    } else {
      add('info', `Sign grid: ½-cap side and bottom borders; ${settings.type === 'gas' ? '1 cap' : '½ cap'} above the logotype. Facility names begin one x-height below its baseline.`)
      if (!settings.showBorder) add('warning', 'The reference examples show a border; it is currently hidden.')
      if (settings.nameLayout !== 'none' && !settings.facility.trim()) add('warning', 'This facility template has no facility name.')
      if (scene.border && (scene.signatureBox.y < scene.border.y || scene.signatureBox.bottom > scene.border.bottom)) {
        add('error', 'The adjusted emblem or lettering extends beyond the reference-based sign border. Restore proportions or inspect the layout.')
      }
      if (settings.type === 'authority') add('warning', 'The two-line authority signature is not illustrated on the identification-sign page; this combination is exploratory.')
    }
  }

  if (mode === 'colour') {
    add('info', settings.type === 'gas'
      ? 'Gas Operations: flame and central H share blue; lettering stays black.'
      : 'Corporate colour: only the symbol uses green/blue; lettering stays black.')
  }
  if (settings.screenPalette !== 'scan') add('warning', 'The screen palette is customized or carried over. It does not change the historical print recipe.')
  if (!isHistoricalWording(settings)) add('warning', 'Custom wording is not an authenticated historical signature.')

  const missing = missingLetters(wordingOf(settings).join(''))
  if (missing.length) add('warning', `The serif has no letter for ${missing.join(' ')}; that wording is kept as live text.`)

  return notes
}

/** The other half of a vehicle pair — positive for reverse and back — or null. */
export const pairedPreset = (id) => {
  if (id.endsWith('-positive')) return id.replace(/-positive$/, '-reverse')
  if (id.endsWith('-reverse') && id.startsWith('vehicle-')) return id.replace(/-reverse$/, '-positive')
  return null
}

/** What a linked vehicle pair shares, so both halves keep one logotype height. */
export const VEHICLE_LINK_KEYS = [
  'type', 'wordmark', 'suffix', 'line1', 'line2', 'emblemScale', 'textScale', 'gap', 'tracking', 'suffixGap',
  'symbolOffset', 'ringWeight', 'starScale', 'padding', 'exportWidth'
]

/**
 * One setting changed, with what follows from it: picking a screen palette sets its colours,
 * editing a colour makes the palette custom, and a linked vehicle pair moves together.
 *
 * @param {Record<string, object>} all  Every preset's settings.
 * @returns {Record<string, object>}    A new map; the old one is untouched.
 */
export const updateHydroSettings = (all, id, key, value) => {
  const next = { ...all, [id]: { ...all[id], [key]: value } }
  const settings = next[id]
  if (key === 'backgroundValue' || key === 'inkValue') settings[key] = Math.round(value)
  if (key === 'green' || key === 'blue') settings.screenPalette = 'custom'
  if (key === 'screenPalette' && HYDRO_SCREEN_PALETTES[value]) {
    settings.green = HYDRO_SCREEN_PALETTES[value].green
    settings.blue = HYDRO_SCREEN_PALETTES[value].blue
  }
  if (key === 'mode') settings.autoTreatment = false

  const other = pairedPreset(id)
  if (settings.usage === 'vehicle' && settings.linkVehiclePair && other && next[other]) {
    const partner = { ...next[other], linkVehiclePair: true }
    if (VEHICLE_LINK_KEYS.includes(key)) partner[key] = settings[key]
    if (key === 'linkVehiclePair' && value) for (const shared of VEHICLE_LINK_KEYS) partner[shared] = settings[shared]
    next[other] = partner
  }
  return next
}

/** Every preset's settings, as a file. */
export const HYDRO_SETTINGS_SCHEMA = 'bc-hydro-templates/v2'

export const hydroProject = (all, active) => ({ schema: HYDRO_SETTINGS_SCHEMA, active, templates: all })

/**
 * Reads a settings file back: this studio's own, or the original studio's v1 and v2 files, whose
 * "droplet" signature is Gas Operations here.
 */
export const readHydroProject = (input) => {
  const schemas = ['bc-hydro-templates/v1', HYDRO_SETTINGS_SCHEMA]
  if (!input || !schemas.includes(input.schema) || !input.templates || typeof input.templates !== 'object' || Array.isArray(input.templates)) {
    throw new Error('Not a supported BC Hydro settings file.')
  }
  const templates = allHydroDefaults()
  let note = ''
  if (input.schema === 'bc-hydro-templates/v1') {
    for (const old of ['standard', 'droplet', 'rail', 'authority']) {
      const id = old === 'droplet' ? 'gas' : old
      const saved = input.templates[old]
      if (!saved) continue
      templates[id] = cleanHydroSettings({
        ...saved,
        type: id,
        screenPalette: 'legacy',
        background: saved.background === 'transparent' ? 'transparent' : 'solid',
        backgroundColour: saved.background === 'dark' ? '#18323d' : '#ffffff'
      }, id)
    }
    note = 'Imported a v1 file. “Droplet” is now Gas Operations; its wording, geometry and screen colours were kept.'
  } else {
    for (const id of HYDRO_PRESET_ORDER) templates[id] = cleanHydroSettings(input.templates[id], id)
  }
  const active = input.active === 'droplet' ? 'gas' : input.active
  return { templates, active: HYDRO_PRESETS[active] ? active : 'standard', note }
}
