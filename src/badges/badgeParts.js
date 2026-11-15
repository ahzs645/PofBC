// What each piece of a badge drawing becomes in metal: the part it plays, how far it stands, its
// colour and finish. No DOM and no three.js, so it can be tested alone.
//
// The curved badge trial (14 November 2026) tuned these for one shield, S51-O01. The library's
// other badges are silver ranger shields with green enamel, multi-piece cap badges and a leather
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

/** Base metals, and the colours their surfaces take. */
export const METALS = {
  gold: { name: 'Bronze-gilt', body: '#8f7144', plate: '#b8975e', roughness: 0.32 },
  silver: { name: 'Silver-finish', body: '#9aa29d', plate: '#c9cfca', roughness: 0.3 },
  leather: { name: 'Tooled leather', body: '#8a5a30', plate: '#a46d38', roughness: 0.85 }
}

/**
 * Each part's relief, in millimetres above the body's face (which is z = 0), and its finish.
 * Raised metal is scaled by its paint's lightness: the atlas paints a lit face light and a shaded
 * one dark, so the lighter of two overlapping pieces is the one on top.
 */
export const PARTS = {
  body: { thickness: 1.6, bevel: 0.12 },
  ground: { thickness: 0.06, bevel: 0.02 },
  plate: { thickness: 0.1, bevel: 0.03 },
  recess: { thickness: 0.16, bevel: 0.01 },
  enamel: { thickness: 0.16, bevel: 0.015 },
  detail: { thickness: 0.23, bevel: 0.018 },
  emblem: { thickness: 0.32, bevel: 0.035 },
  lettering: { thickness: 0.38, bevel: 0.035 },
  rim: { thickness: 0.42, bevel: 0.045 }
}

/** A darkened field: the trial's oxidized body (S51-O01) was metalness 0.65, roughness 0.8, but on a lighter olive ground under this studio light that reads pale, so it is smoother and more metallic, reflecting the room only where the angle catches it. */
const DARK_FIELD = (leather) => (leather ? { metalness: 0, roughness: 0.85 } : { metalness: 0.85, roughness: 0.5 })

/** A fill covering more than this share of the badge's outline is its ground, not relief. */
export const GROUND_SHARE = 0.35

/** Leather is thicker and its tooling shallower. */
const LEATHER_BODY = { thickness: 2.4, bevel: 0.25 }
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
export function metalOf ({ medium = '', paints = [] }) {
  if (/leather/i.test(medium)) return 'leather'
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
  const metalFinish = leather ? { metalness: 0, roughness: base.roughness } : { metalness: 1, roughness: base.roughness }

  const ground = kind === 'fill' && share > GROUND_SHARE
  if (isGradient(paint) || !hsl) return build(ground ? 'ground' : 'plate', base.plate, metalFinish)
  // A large field in its own colour: dark ones read as an oxidized or enamelled ground.
  if (ground) {
    // Dark grounds are darkened metal, finished as the trial's oxidized field. A matte non-metal
    // takes so much of the room's light that a dark colour reads pale.
    const finish = hsl.l < 0.35 ? DARK_FIELD(leather) : metalFinish
    return build('ground', paint, hsl.s > 0.35 && !isGoldHue(hsl) && !leather ? { metalness: 0, roughness: 0.28 } : finish)
  }
  if (!leather && hsl.s > 0.35 && !isGoldHue(hsl) && hsl.l > 0.08 && hsl.l < 0.9) {
    return build('enamel', paint, { metalness: 0, roughness: 0.28 })
  }
  if (hsl.l < 0.22) return build('recess', paint, DARK_FIELD(leather))
  const part = border ? 'rim' : caption ? 'lettering' : kind === 'stroke' ? 'detail' : 'emblem'
  return build(part, paint, metalFinish, 0.7 + 0.45 * hsl.l)
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
    metalness: metal === 'leather' ? 0 : 0.85,
    roughness: metal === 'leather' ? base.roughness : 0.45
  }
}
