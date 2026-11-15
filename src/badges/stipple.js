// The textured fields some badges are struck with, made as tileable normal maps. No DOM and no
// three.js: badgeScene.js turns the pixels into a texture.
//
// The atlas's drawings leave texture out ("Relief, hammered grain, ageing … are omitted", S11-O01),
// but the reference photographs (vendor/patcher's atlas snapshot, dist/assets/sources/) show it:
//
//   pebbled  S11, S12, S17, S20 (the early Park Ranger shields): a field of close-set round bumps,
//            about 1–1.5 mm across, as die-struck stipple is.
//   frosted  S14, S18 (the green-enamel Park Ranger shields): a fine sandblasted grain.
//
// Bumps are placed by dart throwing on a torus, so the tile repeats without a seam, from a fixed
// seed, so a badge looks the same every time.

/**
 * Texture recipes. Sizes are millimetres on the badge. `tone` darkens the textured field a little,
 * so smooth polished relief reads brighter against it, as the photographs show it.
 */
export const TEXTURES = {
  pebbled: { tileMm: 12, size: 512, minRadiusMm: 0.42, maxRadiusMm: 0.78, gapMm: 0.04, attempts: 24000, strength: 2.2, roughness: 0.44, tone: 0.78, seed: 1917 },
  frosted: { tileMm: 4, size: 512, minRadiusMm: 0.03, maxRadiusMm: 0.08, gapMm: -0.01, attempts: 60000, strength: 1.8, roughness: 0.48, seed: 1961 }
}

/** Which badges' fields are textured, by the library's family. */
export const FIELD_TEXTURES = {
  'ranger-metal-early': 'pebbled',
  'ranger-metal-green-inset': 'frosted',
  'ranger-metal-green-full': 'frosted'
}

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
 * The bumps on one tile: { x, y, r } in pixels, none overlapping (closer than the gap allows),
 * wrapping at the tile's edges.
 */
export function placeBumps (recipe) {
  const { size, tileMm, minRadiusMm, maxRadiusMm, gapMm, attempts, seed } = recipe
  const px = size / tileMm
  const rand = random(seed)
  const cell = Math.max(1, Math.floor(2 * maxRadiusMm * px))
  const cells = Math.max(1, Math.floor(size / cell))
  const grid = Array.from({ length: cells * cells }, () => [])
  const bumps = []
  const wrap = (d) => d - size * Math.round(d / size)
  for (let i = 0; i < attempts; i++) {
    const r = (minRadiusMm + (maxRadiusMm - minRadiusMm) * rand()) * px
    const x = rand() * size
    const y = rand() * size
    const cx = Math.floor(x / size * cells)
    const cy = Math.floor(y / size * cells)
    let fits = true
    for (let dy = -2; dy <= 2 && fits; dy++) {
      for (let dx = -2; dx <= 2 && fits; dx++) {
        for (const b of grid[((cy + dy + cells) % cells) * cells + ((cx + dx + cells) % cells)]) {
          if (Math.hypot(wrap(b.x - x), wrap(b.y - y)) < b.r + r + gapMm * px) { fits = false; break }
        }
      }
    }
    if (!fits) continue
    const bump = { x, y, r }
    bumps.push(bump)
    grid[cy * cells + cx].push(bump)
  }
  return bumps
}

/** The tile's height field (0 at the field, up to 1 at a bump's crown), wrapping at the edges. */
export function heightField (recipe, bumps = placeBumps(recipe)) {
  const { size } = recipe
  const h = new Float32Array(size * size)
  for (const { x, y, r } of bumps) {
    const reach = Math.ceil(r)
    for (let j = -reach; j <= reach; j++) {
      for (let i = -reach; i <= reach; i++) {
        const d2 = (i * i + j * j) / (r * r)
        if (d2 >= 1) continue
        // A rounded dome, highest at the centre.
        const v = Math.sqrt(1 - d2)
        const k = ((Math.floor(y) + j + size) % size) * size + ((Math.floor(x) + i + size) % size)
        if (v > h[k]) h[k] = v
      }
    }
  }
  return h
}

/**
 * The height field as an RGBA normal map in tangent space (OpenGL convention: green is +v), each
 * slope measured in millimetres so a bump's steepness does not depend on the tile's resolution.
 */
export function normalMap (recipe, height = heightField(recipe)) {
  const { size, tileMm, maxRadiusMm, strength } = recipe
  const out = new Uint8Array(size * size * 4)
  // A crown of height 1 stands about half a bump's radius above the field.
  const lift = maxRadiusMm * 0.5 * strength
  const mmPerPx = tileMm / size
  const at = (i, j) => height[((j + size) % size) * size + ((i + size) % size)]
  for (let j = 0; j < size; j++) {
    for (let i = 0; i < size; i++) {
      const dx = ((at(i + 1, j) - at(i - 1, j)) * lift) / (2 * mmPerPx)
      const dy = ((at(i, j + 1) - at(i, j - 1)) * lift) / (2 * mmPerPx)
      const len = Math.hypot(dx, dy, 1)
      const k = (j * size + i) * 4
      out[k] = Math.round(((-dx / len) * 0.5 + 0.5) * 255)
      out[k + 1] = Math.round(((-dy / len) * 0.5 + 0.5) * 255)
      out[k + 2] = Math.round(((1 / len) * 0.5 + 0.5) * 255)
      out[k + 3] = 255
    }
  }
  return out
}
