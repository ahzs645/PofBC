// What each piece of a badge drawing becomes in metal: the part it plays, how far it stands, its
// colour and finish. No DOM and no three.js, so it can be tested alone.
//
// The curved badge trial (14 November 2026) tuned these for one shield, S51-O01. The library's
// other badges are silver ranger shields with green enamel, multi-piece cap badges and a worn copper
// badge, so the parts are read from what every atlas drawing records instead:
//
//   - its own markings: data-caption (lettering), data-role="border" (the rim);
//   - its size: a fill that covers much of the badge is a ground (a plate or field), not relief;
//   - its paint: a gradient is a plate of the badge's own metal, a saturated colour off the metal's
//     hue is enamel, a near-black is a darkened field, and anything else is raised metal;
//   - the medium: a leather badge is tooled leather, not metal.
//
// The body is not one of the drawing's pieces: it is the outline of all of them together (see
// medalBadge.js), so a badge made of a scroll and a plaque has a back to every piece.
//
// Every height and finish here is a modelling choice, not a measurement of a specimen.

export const NOMINAL_SIZE_MM = 65

/**
 * The photo-registered Junior Forest Warden drawing has explicit nested relief. Its light vein
 * faces sit ON its leaf; colour-derived heights alone put them inside the blade. These are display
 * profiles in nominal millimetres, not measured tooling depths. `top` is kept fixed even when a
 * narrow outline needs a smaller bevel. The body retains the ordinary metal profile below.
 */
export const JUNIOR_WARDEN_RELIEF = Object.freeze({
  id: 'junior-warden-copper-v1',
  family: 'junior-warden',
  profiles: Object.freeze({
    'outer-field': { part: 'ground', base: 0, top: 0.035, bevel: 0, roughness: 0.9 },
    field: { part: 'ground', base: 0.015, top: 0.065, bevel: 0, roughness: 0.9 },
    rim: { part: 'rim', base: 0.025, top: 0.31, bevel: 0.065, roughness: 0.76 },
    'letter-shoulder': { part: 'lettering', base: 0.025, top: 0.32, bevel: 0.07, roughness: 0.84 },
    'letter-face': { part: 'lettering', base: 0.275, top: 0.46, bevel: 0.025, roughness: 0.72 },
    'leaf-blade': { part: 'emblem', base: 0.025, top: 0.38, bevel: 0.06, roughness: 0.78 },
    'leaf-veins': { part: 'detail', base: 0.34, top: 0.54, bevel: 0.012, roughness: 0.72 }
  })
})

/** Base metals, and the colours their surfaces take. */
/**
 * Base metals. The reference photographs show the field and the struck relief in different
 * finishes: a darker, satin or stippled field, and polished high points that catch the light. On a
 * silver badge that difference is all that shows a raised letter, so fields are `satin` and raised
 * parts `polish`.
 */
export const METALS = {
  gold: { name: 'Bronze-gilt', body: '#7a5f37', field: '#7d6239', plate: '#b8975e', polish: 0.22, satin: 0.62 },
  silver: { name: 'Silver-finish', body: '#7e8581', field: '#838a86', plate: '#c9cfca', polish: 0.18, satin: 0.6 },
  copper: { name: 'Worn copper tone', body: '#80522e', field: '#895635', plate: '#d09868', polish: 0.4, satin: 0.73 },
  leather: { name: 'Tooled leather', body: '#8a5a30', field: '#a46d38', plate: '#a46d38', polish: 0.7, satin: 0.9 }
}

/** A colour darkened towards black by `factor` (0–1 kept), as '#rrggbb'. */
export function darken (hex, factor) {
  const m = /^#([0-9a-f]{6})$/i.exec(hex)
  if (!m) return hex
  return '#' + [0, 2, 4].map((i) => Math.round(parseInt(m[1].slice(i, i + 2), 16) * factor).toString(16).padStart(2, '0')).join('')
}

/**
 * Each part's relief and finish. A piece's back sits just inside the body, so what shows above the
 * body's face (z = 0) is thickness + bevel: the bevel is the sloped shoulder of a struck letter,
 * and medalBadge.js insets the outline by it so the shoulder's foot lands on the drawn edge.
 * Raised metal is scaled a little by its paint's lightness: the atlas paints a lit face light and a
 * shaded one dark, so the lighter of two overlapping pieces is the one on top.
 *
 * The reference photographs (S07, S21, S51, the S11 rangers, S01) show lettering, rims and emblems
 * struck well up from the field, about the depth of a letter's stroke: lettering stands about
 * 0.9 mm, the arms' boss and detail about 1.4 mm, at 65 mm.
 */
export const PARTS = {
  // The body's edge is rounded front and back (a broad multi-segment bevel), so the border curves
  // down to the badge's back rather than ending in a flat slab side.
  body: { thickness: 1.2, bevel: 0.5, segments: 4 },
  ground: { thickness: 0.06, bevel: 0.02 },
  plate: { thickness: 0.1, bevel: 0.03 },
  recess: { thickness: 0.16, bevel: 0.01 },
  enamel: { thickness: 0.18, bevel: 0.015 },
  detail: { thickness: 0.45, bevel: 0.07 },
  emblem: { thickness: 0.56, bevel: 0.14 },
  lettering: { thickness: 0.7, bevel: 0.2 },
  rim: { thickness: 0.75, bevel: 0.22 },
  // The mass a struck emblem (the provincial arms, the dogwood) rises as, under its own line work.
  boss: { thickness: 0.9, bevel: 0.28 },
  // The rolled edge: a band just inside the outline that curls up from the field and rounds over
  // and down at the badge's edge, as the photographs' borders do. Its bevel is rounded (several
  // segments), and its side runs on down into the body's rounded edge.
  edge: { thickness: 0.9, bevel: 0.45, widthMm: 1.2, segments: 5 }
}

/** Parts struck up from the field, whose outlines get a sloped shoulder. */
export const RAISED = new Set(['detail', 'emblem', 'lettering', 'rim', 'boss'])

/** A metal badge's rolled edge, polished like the rest of its relief. Leather has none. */
export function edgeFor (metal) {
  const base = METALS[metal] ?? METALS.gold
  return {
    part: 'edge',
    color: base.plate,
    thickness: PARTS.edge.thickness,
    bevel: PARTS.edge.bevel,
    bevelSegments: PARTS.edge.segments,
    metalness: 1,
    roughness: base.polish
  }
}

/**
 * Drawing components struck as a raised mass in the reference photographs: the provincial arms on
 * the Park Ranger shields and cap badges (plateforge-historical-arms, uploaded-bc-modern-arms) and
 * the Parks Branch dogwood (five-petal-dogwood). Matched against data-component.
 */
export const EMBOSSED_COMPONENT = /(^|-)arms(-|$)|dogwood/

/**
 * An emblem's raised mass, with a broad shoulder. In the photographs its low ground, between the
 * modelled details, is shaded and dull while the details stand bright, so the boss is a darker satin
 * of the badge's metal and the emblem's polished line work stands on it.
 */
export function bossFor (metal) {
  const base = METALS[metal] ?? METALS.gold
  return {
    part: 'boss',
    color: darken(base.field, 0.55),
    thickness: PARTS.boss.thickness,
    bevel: PARTS.boss.bevel,
    metalness: metal === 'leather' ? 0 : 1,
    roughness: Math.min(0.9, base.satin + 0.1)
  }
}

/** A darkened field: the trial's oxidized body (S51-O01) was metalness 0.65, roughness 0.8, but on a lighter olive ground under this studio light that reads pale, so it is smoother and more metallic, reflecting the room only where the angle catches it. */
const DARK_FIELD = (leather) => (leather ? { metalness: 0, roughness: 0.85 } : { metalness: 0.85, roughness: 0.5 })

/** A fill covering more than this share of the badge's outline is its ground, not relief. */
export const GROUND_SHARE = 0.35

/** Leather is thicker and its tooling shallower. */
const LEATHER_BODY = { thickness: 1.8, bevel: 0.5, segments: 4 }
const LEATHER_RELIEF = 0.6

/** '#abc', '#aabbcc' → { h (degrees), s, l } (0–1), or null for anything else. */
export function hexToHsl (hex) {
  const m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(String(hex ?? '').trim())
  if (!m) return null
  const full = m[1].length === 3 ? [...m[1]].map((c) => c + c).join('') : m[1]
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16) / 255)
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const l = (max + min) / 2
  const d = max - min
  if (d === 0) return { h: 0, s: 0, l }
  const s = d / (1 - Math.abs(2 * l - 1))
  const h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4
  return { h: (h * 60 + 360) % 360, s, l }
}

const isGradient = (paint) => /^url\(/i.test(String(paint ?? ''))
/** Gold, brass and bronze sit between orange and yellow. */
const isGoldHue = ({ h, s }) => h >= 22 && h <= 62 && s >= 0.18

/**
 * The badge's base metal, from its medium and paints. `paints` is the drawing's pieces as
 * { paint, area }; a gradient's id says which metal it imitates when it can.
 */
export function metalOf ({ medium = '', finish = '', paints = [] }) {
  if (/leather/i.test(medium)) return 'leather'
  if (/copper/i.test(finish)) return 'copper'
  for (const { paint } of paints) {
    if (/silver|steel|chrome|nickel/i.test(paint)) return 'silver'
    if (/gold|brass|bronze|gilt/i.test(paint)) return 'gold'
  }
  // Vote by area among the lit metal tones; dark grounds and shadows say little about the metal.
  let gold = 0
  let other = 0
  for (const { paint, area = 1 } of paints) {
    const hsl = hexToHsl(paint)
    if (!hsl || hsl.l < 0.35) continue
    if (isGoldHue(hsl)) gold += area
    else if (hsl.s < 0.2) other += area
  }
  return gold >= other && gold > 0 ? 'gold' : 'silver'
}

/**
 * The part a piece plays and how it is built.
 * @param {{ paint: string, kind?: 'fill' | 'stroke', caption?: string | null, border?: boolean, share?: number, metal: keyof METALS }} piece
 *   share: the piece's area as a share of the badge's outline (0–1).
 * @returns {{ part: string, color: string, thickness: number, bevel: number, metalness: number, roughness: number }}
 */
export function partFor ({ paint, kind = 'fill', caption = null, border = false, share = 0, metal }) {
  const base = METALS[metal] ?? METALS.gold
  const leather = metal === 'leather'
  const hsl = hexToHsl(paint)
  const build = (part, color, finish, scale = 1) => {
    const profile = PARTS[part]
    const thickness = leather && !['ground', 'plate', 'recess'].includes(part) ? profile.thickness * LEATHER_RELIEF : profile.thickness
    return { part, color, thickness: thickness * scale, bevel: profile.bevel, ...finish }
  }
  const polished = { metalness: leather ? 0 : 1, roughness: base.polish }
  const satin = { metalness: leather ? 0 : 1, roughness: base.satin }

  const ground = kind === 'fill' && share > GROUND_SHARE
  if (isGradient(paint) || !hsl) return ground ? build('ground', base.field, satin) : build('plate', base.plate, polished)
  // A large field in its own colour: dark ones read as an oxidized or enamelled ground.
  if (ground) {
    // Dark grounds are darkened metal, finished as the trial's oxidized field. A matte non-metal
    // takes so much of the room's light that a dark colour reads pale.
    if (hsl.s > 0.35 && !isGoldHue(hsl) && !leather) return build('ground', paint, { metalness: 0, roughness: 0.28 })
    // The photographs' dark fields are deeper than the drawing's paint, which keeps lettering legible on screen.
    return hsl.l < 0.35 ? build('ground', darken(paint, 0.62), DARK_FIELD(leather)) : build('ground', darken(paint, 0.82), satin)
  }
  if (!leather && hsl.s > 0.35 && !isGoldHue(hsl) && hsl.l > 0.08 && hsl.l < 0.9) {
    return build('enamel', paint, { metalness: 0, roughness: 0.28 })
  }
  if (hsl.l < 0.22) return build('recess', paint, DARK_FIELD(leather))
  const part = border ? 'rim' : caption ? 'lettering' : kind === 'stroke' ? 'detail' : 'emblem'
  return build(part, paint, polished, 0.85 + 0.25 * hsl.l)
}

/** The body of a badge made of `metal`. */
export function bodyFor (metal) {
  const base = METALS[metal] ?? METALS.gold
  const profile = metal === 'leather' ? LEATHER_BODY : PARTS.body
  return {
    part: 'body',
    color: base.body,
    thickness: profile.thickness,
    bevel: profile.bevel,
    bevelSegments: profile.segments,
    metalness: metal === 'leather' ? 0 : 1,
    roughness: base.satin
  }
}
