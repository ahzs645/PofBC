// The textured fields some badges are struck with, made for each badge as a normal map that covers
// its field. No DOM and no three.js: medalBadge.js supplies the field and its raised parts, and
// badgeScene.js turns the pixels into a texture.
//
// The atlas's drawings leave texture out ("Relief, hammered grain, ageing … are omitted", S11-O01),
// but the reference photographs (vendor/patcher's atlas snapshot, dist/assets/sources/) show it:
//
//   pebbled  S11, S12, S17, S20 (the early Park Ranger shields): close-set, irregular bumps about
//            0.6–1.3 mm across, about a quarter of a capital's height. They stop short of the
//            raised lettering, arms and number plate, thin out near them, and leave a smooth band
//            just inside the badge's edge.
//   frosted  S14, S18 (the green-enamel Park Ranger shields): a fine sandblasted grain, also
//            leaving the edge band and the relief smooth.
//
// How it is made follows common practice for procedural hammered and peened metal (irregular
// overlapping or packed dents, Voronoi-like cells with flattened crowns) and for variable-density
// stippling (Poisson-disk sampling whose spacing follows a sizing field):
//
//   1. The field and the raised parts are rasterized, and two distance fields are measured: to the
//      field's edge, and to the nearest raised part.
//   2. Bumps are placed by dart throwing with a minimum gap that widens near raised parts, and none
//      within the edge band or a halo around the relief.
//   3. Each bump is an irregular blob (elliptical, with a lumpy outline from two low harmonics),
//      of random height, its crown flattened.
//   4. The height field becomes a normal map, slopes measured in millimetres.
//
// Everything is seeded, so a badge looks the same every time.

/**
 * Recipes. Sizes are millimetres on the badge. `tone` darkens the textured field a little, so the
 * smooth polished relief reads brighter against it, as the photographs show.
 */
export const TEXTURES = {
  pebbled: {
    kind: 'bumps',
    pxPerMm: 24,
    minRadiusMm: 0.29,
    maxRadiusMm: 0.66,
    gapMm: 0.03,
    nearGapMm: 0.14,
    nearMm: 1.5,
    haloMm: 0.22,
    bandMm: 1.1,
    irregularity: 0.16,
    attemptsPerMm2: 90,
    flatten: 0.75,
    strength: 2.2,
    roughness: 0.44,
    tone: 0.78,
    seed: 1917
  },
  // Fine irregular grain in the recessed copper field of the Warden photograph.
  'worn-copper': {
    kind: 'grain',
    pxPerMm: 16,
    grainMm: 0.08,
    haloMm: 0.18,
    bandMm: 0.8,
    strength: 0.4,
    roughness: 0.68,
    tone: 0.79,
    seed: 561
  },
  frosted: {
    kind: 'grain',
    pxPerMm: 24,
    grainMm: 0.05,
    haloMm: 0.25,
    bandMm: 1.0,
    strength: 0.35,
    roughness: 0.48,
    seed: 1961
  }
}

/** Which badges' fields are textured, by the library's family. */
export const FIELD_TEXTURES = {
  'ranger-metal-early': 'pebbled',
  'ranger-metal-green-inset': 'frosted',
  'ranger-metal-green-full': 'frosted'
}

/** The largest texture side, in pixels. */
export const MAX_SIZE = 2048

/** A small, fast, seeded random number generator (mulberry32). */
export function random (seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/**
 * Rings ([[x, y], …] in mm, y up) filled with the nonzero rule into a w × h mask (1 inside), at
 * px pixels per millimetre. Row 0 is the bottom (y = 0), as a texture's v = 0 is.
 */
export function rasterize (rings, w, h, px) {
  const rows = Array.from({ length: h }, () => [])
  for (const ring of rings) {
    for (let i = 0; i < ring.length; i++) {
      const [x0, y0] = ring[i]
      const [x1, y1] = ring[(i + 1) % ring.length]
      if (y0 === y1) continue
      const up = y1 > y0
      const lo = Math.min(y0, y1) * px
      const hi = Math.max(y0, y1) * px
      for (let r = Math.max(0, Math.ceil(lo - 0.5)); r < Math.min(h, Math.ceil(hi - 0.5)); r++) {
        const y = (r + 0.5) / px
        rows[r].push({ x: (x0 + ((y - y0) / (y1 - y0)) * (x1 - x0)) * px, dir: up ? 1 : -1 })
      }
    }
  }
  const mask = new Uint8Array(w * h)
  for (let r = 0; r < h; r++) {
    const crossings = rows[r].sort((a, b) => a.x - b.x)
    let winding = 0
    for (let k = 0; k < crossings.length - 1; k++) {
      winding += crossings[k].dir
      if (winding === 0) continue
      const from = Math.max(0, Math.ceil(crossings[k].x - 0.5))
      const to = Math.min(w, Math.ceil(crossings[k + 1].x - 0.5))
      mask.fill(1, r * w + from, r * w + Math.max(from, to))
    }
  }
  return mask
}

/**
 * For every pixel, the distance in mm to the nearest pixel whose mask value is `target` (a
 * two-pass chamfer distance: near enough to Euclidean for spacing bumps).
 */
export function distanceTo (mask, w, h, target, px) {
  const d = new Float32Array(w * h)
  for (let k = 0; k < d.length; k++) d[k] = mask[k] === target ? 0 : 1e9
  const diagonal = Math.SQRT2
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const k = y * w + x
      let v = d[k]
      if (x > 0) v = Math.min(v, d[k - 1] + 1)
      if (y > 0) {
        v = Math.min(v, d[k - w] + 1)
        if (x > 0) v = Math.min(v, d[k - w - 1] + diagonal)
        if (x < w - 1) v = Math.min(v, d[k - w + 1] + diagonal)
      }
      d[k] = v
    }
  }
  for (let y = h - 1; y >= 0; y--) {
    for (let x = w - 1; x >= 0; x--) {
      const k = y * w + x
      let v = d[k]
      if (x < w - 1) v = Math.min(v, d[k + 1] + 1)
      if (y < h - 1) {
        v = Math.min(v, d[k + w] + 1)
        if (x < w - 1) v = Math.min(v, d[k + w + 1] + diagonal)
        if (x > 0) v = Math.min(v, d[k + w - 1] + diagonal)
      }
      d[k] = v
    }
  }
  for (let k = 0; k < d.length; k++) d[k] /= px
  return d
}

/**
 * Bumps over the field, in pixels: { x, y, r, aspect, angle, h2, p2, h3, p3, height }.
 * `edge` and `raised` are distance fields in mm (to the field's edge, to the relief).
 */
export function placeBumps (recipe, { w, h, px, edge, raised }) {
  const { minRadiusMm, maxRadiusMm, gapMm, nearGapMm, nearMm, haloMm, bandMm, irregularity, attemptsPerMm2, seed } = recipe
  const rand = random(seed)
  const cell = Math.max(1, Math.ceil(2 * (maxRadiusMm + gapMm + nearGapMm) * px))
  const cols = Math.ceil(w / cell)
  const grid = new Map()
  const bumps = []
  const attempts = Math.round(((w * h) / (px * px)) * attemptsPerMm2)
  for (let i = 0; i < attempts; i++) {
    const x = rand() * w
    const y = rand() * h
    // Smaller bumps are commoner, as on the photographs; late attempts only fill the gaps left,
    // so they draw from the small end, which packs the field as tightly as a struck die does.
    const late = i / attempts
    const rMm = minRadiusMm + (maxRadiusMm - minRadiusMm) * rand() ** (1.6 + 3 * late)
    const k = Math.floor(y) * w + Math.floor(x)
    if (edge[k] < rMm + bandMm || raised[k] < rMm + haloMm) continue
    const gap = (gapMm + nearGapMm * Math.exp(-raised[k] / nearMm)) * px
    const r = rMm * px
    const cx = Math.floor(x / cell)
    const cy = Math.floor(y / cell)
    let fits = true
    for (let dy = -1; dy <= 1 && fits; dy++) {
      for (let dx = -1; dx <= 1 && fits; dx++) {
        for (const b of grid.get((cy + dy) * cols + cx + dx) ?? []) {
          if (Math.hypot(b.x - x, b.y - y) < b.r + r + gap) { fits = false; break }
        }
      }
    }
    if (!fits) continue
    const bump = {
      x, y, r,
      aspect: 0.72 + 0.28 * rand(),
      angle: rand() * Math.PI,
      h2: irregularity * rand(), p2: rand() * 2 * Math.PI,
      h3: irregularity * 0.7 * rand(), p3: rand() * 2 * Math.PI,
      height: 0.65 + 0.35 * rand()
    }
    bumps.push(bump)
    const key = cy * cols + cx
    if (!grid.has(key)) grid.set(key, [])
    grid.get(key).push(bump)
  }
  return bumps
}

/** The bumps' height field (0 on the field, up to 1), each an irregular blob with a flattened crown. */
export function stampBumps (bumps, { w, h, flatten = 0.75 }) {
  const height = new Float32Array(w * h)
  for (const b of bumps) {
    const reach = Math.ceil(b.r * (1 + b.h2 + b.h3))
    const cos = Math.cos(b.angle)
    const sin = Math.sin(b.angle)
    const x0 = Math.floor(b.x)
    const y0 = Math.floor(b.y)
    for (let j = -reach; j <= reach; j++) {
      const y = y0 + j
      if (y < 0 || y >= h) continue
      for (let i = -reach; i <= reach; i++) {
        const x = x0 + i
        if (x < 0 || x >= w) continue
        const dx = x + 0.5 - b.x
        const dy = y + 0.5 - b.y
        const u = dx * cos + dy * sin
        const v = (-dx * sin + dy * cos) / b.aspect
        const theta = Math.atan2(v, u)
        const rr = b.r * (1 + b.h2 * Math.cos(2 * theta + b.p2) + b.h3 * Math.cos(3 * theta + b.p3))
        const d2 = (u * u + v * v) / (rr * rr)
        if (d2 >= 1) continue
        const value = b.height * Math.min(1, Math.sqrt(1 - d2) / flatten)
        const k = y * w + x
        if (value > height[k]) height[k] = value
      }
    }
  }
  return height
}

/** A sandblasted grain: blurred seeded noise, fading out over the edge band and the relief's halo. */
export function grainHeight (recipe, { w, h, px, edge, raised }) {
  const rand = random(recipe.seed)
  const noise = new Float32Array(w * h)
  for (let k = 0; k < noise.length; k++) noise[k] = rand()
  const radius = Math.max(1, Math.round(recipe.grainMm * px))
  const blurred = boxBlur(noise, w, h, radius)
  const smooth = (t) => (t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t))
  for (let k = 0; k < blurred.length; k++) {
    blurred[k] *= smooth((edge[k] - recipe.bandMm) / 0.3) * smooth((raised[k] - recipe.haloMm) / 0.2)
  }
  return blurred
}

function boxBlur (src, w, h, r) {
  const tmp = new Float32Array(w * h)
  const out = new Float32Array(w * h)
  const n = 2 * r + 1
  for (let y = 0; y < h; y++) {
    let sum = 0
    for (let x = -r; x <= r; x++) sum += src[y * w + Math.min(w - 1, Math.max(0, x))]
    for (let x = 0; x < w; x++) {
      tmp[y * w + x] = sum / n
      sum += src[y * w + Math.min(w - 1, x + r + 1)] - src[y * w + Math.max(0, x - r)]
    }
  }
  for (let x = 0; x < w; x++) {
    let sum = 0
    for (let y = -r; y <= r; y++) sum += tmp[Math.min(h - 1, Math.max(0, y)) * w + x]
    for (let y = 0; y < h; y++) {
      out[y * w + x] = sum / n
      sum += tmp[Math.min(h - 1, y + r + 1) * w + x] - tmp[Math.max(0, y - r) * w + x]
    }
  }
  return out
}

/**
 * A height field as an RGBA normal map in tangent space (OpenGL convention: green is +v), each
 * slope measured in millimetres. `liftMm` is how high a height of 1 stands.
 */
export function normalFromHeight (height, w, h, px, liftMm) {
  const out = new Uint8Array(w * h * 4)
  const at = (i, j) => height[Math.min(h - 1, Math.max(0, j)) * w + Math.min(w - 1, Math.max(0, i))]
  for (let j = 0; j < h; j++) {
    for (let i = 0; i < w; i++) {
      const dx = ((at(i + 1, j) - at(i - 1, j)) * liftMm * px) / 2
      const dy = ((at(i, j + 1) - at(i, j - 1)) * liftMm * px) / 2
      const len = Math.hypot(dx, dy, 1)
      const k = (j * w + i) * 4
      out[k] = Math.round(((-dx / len) * 0.5 + 0.5) * 255)
      out[k + 1] = Math.round(((-dy / len) * 0.5 + 0.5) * 255)
      out[k + 2] = Math.round(((1 / len) * 0.5 + 0.5) * 255)
      out[k + 3] = 255
    }
  }
  return out
}

/**
 * A badge's field texture.
 * @param {keyof TEXTURES} name
 * @param {{ width: number, height: number, field: number[][][], raised: number[][][] }} frame
 *   The field's box in mm, and the field's and the relief's rings ([[x, y], …], mm, y up, from the
 *   box's lower left).
 * @returns {{ data: Uint8Array, width: number, height: number, roughness: number, tone?: number, bumps?: number }}
 */
export function fieldTexture (name, { width, height, field, raised }) {
  const recipe = TEXTURES[name]
  if (!recipe) throw new Error(`No field texture "${name}"`)
  const px = Math.min(recipe.pxPerMm, MAX_SIZE / Math.max(width, height))
  const w = Math.max(2, Math.ceil(width * px))
  const h = Math.max(2, Math.ceil(height * px))
  const edge = distanceTo(rasterize(field, w, h, px), w, h, 0, px)
  const relief = distanceTo(rasterize(raised, w, h, px), w, h, 1, px)
  let heights
  let lift
  let bumps
  if (recipe.kind === 'bumps') {
    const placed = placeBumps(recipe, { w, h, px, edge, raised: relief })
    heights = stampBumps(placed, { w, h, flatten: recipe.flatten })
    lift = recipe.maxRadiusMm * 0.5 * recipe.strength
    bumps = placed.length
  } else {
    heights = grainHeight(recipe, { w, h, px, edge, raised: relief })
    lift = recipe.strength
  }
  return { data: normalFromHeight(heights, w, h, px, lift), width: w, height: h, roughness: recipe.roughness, tone: recipe.tone, bumps }
}
