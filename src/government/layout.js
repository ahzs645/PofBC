// Where everything sits on the government diagram.
//
// A fixed radial layout, not a simulation: the same government always draws the same way, so a
// body can be found again where it was last time, and a year's diagram can be told apart from the
// next by what moved rather than by the jitter of a physics engine. The arrangement follows the
// org-graph convention this view is modelled on — the people at the centre, the branches as
// sectors of a disc, and each tier of authority a ring further out.
//
// Angles are radians measured clockwise from three o'clock, which is SVG's own convention with y
// pointing down: twelve o'clock is −π/2 and six o'clock is π/2.

export const VIEWBOX = { x: 0, y: -25, width: 800, height: 840 }
export const CENTRE = { x: 400, y: 375 }

/** One ring step. Every radius below is a multiple of it. */
export const UNIT = 105

/** The radius of each ring, as a multiple of UNIT. */
export const RINGS = {
  seal: 0.5,
  inner: 1.4,
  cabinet: 1.85,
  oversight: 2.2,
  outer: 2.85
}

/**
 * The territory: from just inside the innermost ring to just beyond the outer one. Anything that
 * needs more room than the band gives — a ministry with a row of Crown corporations behind its
 * first — pushes a tooth out of the rim to hold it, so the cog's outline is the shape of the
 * government that year rather than a fixed ornament.
 */
export const BAND_INNER = RINGS.inner * UNIT - 30
export const RIM = RINGS.outer * UNIT + 22

/** The canvas-coloured seam between two branches, in viewBox units: parallel-sided, not a wedge. */
export const SEAM = 7

/** How a family of bodies is packed beyond its ministry: columns along the ring, rows outwards. */
export const CLUSTER = { column: 22, row: 21, rows: 3, gap: 10, pad: 22 }

/**
 * Sub-agencies — a ministry's divisions, a Crown's subsidiaries — are dots, as the model draws its
 * sub-agencies: small, unlabelled until pointed at, in rows of up to three beyond their parent.
 */
export const DOTS = { size: 3.8, column: 5.8, row: 6.4, rows: 3, clearance: 9 }

/** The width of a tooth's rounded shoulder, where the rim rises to it. */
export const SHOULDER = 16

/** The tallest a tooth may grow, so a very large family widens instead of towering. */
const MAX_ROWS_TALL = 3

/** The Crown sits with the executive, which is where it acts; the branches read clockwise from the top. */
export const SECTORS = [
  { id: 'legislative', label: 'LEGISLATIVE', minAngle: deg(52) },
  { id: 'executive', label: 'EXECUTIVE', minAngle: deg(150) },
  { id: 'judicial', label: 'JUDICIAL', minAngle: deg(46) }
]

/** The branches abut; what separates them is the seam, drawn to a constant width. */
export const SECTOR_GAP = 0

/** Padding between a sector's edge and its first node, and the widest spacing nodes are given. */
const EDGE_PADDING = 0.06
const MAX_STEP = 0.35

function deg (value) { return (value * Math.PI) / 180 }

/**
 * Shares out the disc between the branches, by how many bodies each holds.
 *
 * A sector is never narrower than its minimum, so the judiciary — three courts — still reads as a
 * branch beside a hundred executive bodies. The minimums are then renormalised with everything else
 * so the sectors still fill the disc exactly.
 *
 * @param {Record<string, number>} counts  bodies per sector id
 * @returns {{id: string, label: string, start: number, end: number}[]}
 */
export const allocateSectors = (counts) => {
  const available = Math.PI * 2 - SECTOR_GAP * SECTORS.length
  const total = SECTORS.reduce((sum, sector) => sum + (counts[sector.id] ?? 0), 0) || 1
  const raw = SECTORS.map((sector) => Math.max(sector.minAngle, available * ((counts[sector.id] ?? 0) / total)))
  const scale = available / raw.reduce((sum, width) => sum + width, 0)
  const widths = raw.map((width) => width * scale)

  // The legislature is centred at twelve o'clock; the rest follow clockwise.
  let cursor = -Math.PI / 2 - widths[0] / 2
  return SECTORS.map((sector, index) => {
    const start = cursor
    const end = start + widths[index]
    cursor = end + SECTOR_GAP
    return { id: sector.id, label: sector.label, start, end }
  })
}

/**
 * Evenly spaced angles for `count` nodes across [start, end], centred, never further apart than
 * MAX_STEP — so three bodies in a wide sector gather in its middle instead of flying to its edges.
 */
export const spreadAngles = (count, start, end) => {
  if (count <= 0) return []
  const width = end - start - EDGE_PADDING * 2
  const step = count > 1 ? Math.min(MAX_STEP, width / (count - 1)) : 0
  const middle = (start + end) / 2
  return Array.from({ length: count }, (_, index) => middle + (index - (count - 1) / 2) * step)
}

/** The size a node is drawn at: half its width, in viewBox units. */
export const nodeSize = (node) => {
  if (node.kind === 'assembly') return scaleSqrt(node.seats ?? 87, [40, 100], [15, 21])
  if (node.kind === 'premier') return 17
  if (node.kind === 'crown') return 15
  if (node.kind === 'ministry') return node.employees ? scaleSqrt(node.employees, [100, 5000], [10, 16]) : 12
  if (node.kind === 'court' && node.ring === 'inner') return 15
  if (node.kind === 'central-agency') return 9
  if (node.kind === 'officer') return 9
  if (node.ring === 'outer') return 8
  return 10
}

const scaleSqrt = (value, [d0, d1], [r0, r1]) => {
  const t = (Math.sqrt(clamp(value, d0, d1)) - Math.sqrt(d0)) / (Math.sqrt(d1) - Math.sqrt(d0))
  return r0 + t * (r1 - r0)
}

const clamp = (value, low, high) => Math.min(high, Math.max(low, value))

/**
 * Packs the outer ring's bodies into families beyond the body each answers to.
 *
 * A family is a small grid — up to three deep, as many columns wide as it needs — centred on its
 * ministry's angle. Families are then swept apart along the ring so none overlaps the next, and
 * squeezed together if the sector cannot hold them all at full width. A body answering to nothing
 * on the diagram joins a family of its own, after the rest.
 *
 * @returns {{positions: object, teeth: {sector, group, start, end, top}[]}}
 */
const packFamilies = (sector, outer, placed, subsOf) => {
  const base = RINGS.outer * UNIT
  const families = []
  for (const node of outer) {
    const group = node.group && placed[node.group] ? node.group : null
    let family = families.find((entry) => entry.group === group)
    if (!family) families.push(family = { group, members: [] })
    family.members.push(node)
  }
  if (!families.length) return { positions: {}, teeth: [] }

  const middle = (sector.start + sector.end) / 2
  const lastAnchor = Math.max(...families.map((family) => (family.group ? placed[family.group].angle : -Infinity)))
  for (const family of families) {
    // A body with sub-agencies takes a column of its own, so its dots can stack beyond it; the
    // rest share columns up to three deep.
    family.parents = family.members.filter((node) => subsOf(node.id).length)
    family.rest = family.members.filter((node) => !subsOf(node.id).length)
    family.rows = Math.max(1, Math.min(MAX_ROWS_TALL, family.rest.length))
    family.columns = family.parents.length + Math.ceil(family.rest.length / family.rows)
    family.anchor = family.group ? placed[family.group].angle : Number.isFinite(lastAnchor) ? lastAnchor + 0.2 : middle
  }
  families.sort((a, b) => a.anchor - b.anchor)

  // Squeeze the columns if the sector cannot hold every family at full width.
  const padding = CLUSTER.pad / base
  const room = sector.end - sector.start - padding * 2
  const gap = CLUSTER.gap / base
  const wanted = families.reduce((sum, family) => sum + family.columns * CLUSTER.column / base, 0) + gap * (families.length - 1)
  const squeeze = Math.min(1, room / wanted)
  const columnAngle = (CLUSTER.column / base) * squeeze
  for (const family of families) family.width = family.columns * columnAngle

  // Sweep right from each anchor, then back left from the sector's end.
  let cursor = sector.start + padding
  for (const family of families) {
    family.start = Math.max(family.anchor - family.width / 2, cursor)
    cursor = family.start + family.width + gap * squeeze
  }
  let limit = sector.end - padding
  for (const family of [...families].reverse()) {
    family.start = Math.min(family.start, limit - family.width)
    limit = family.start - gap * squeeze
  }

  const positions = {}
  const teeth = []
  for (const family of families) {
    let top = base + (family.rest.length ? (family.rows - 1) * CLUSTER.row : 0) + 22
    family.parents.forEach((node, column) => {
      const angle = family.start + (column + 0.5) * columnAngle
      const size = nodeSize(node)
      positions[node.id] = { angle, radius: base, size }
      const dots = placeDots(subsOf(node.id), angle, base + size + DOTS.clearance)
      Object.assign(positions, dots.positions)
      top = Math.max(top, dots.reach + 12)
    })
    family.rest.forEach((node, index) => {
      const column = family.parents.length + Math.floor(index / family.rows)
      const row = index % family.rows
      positions[node.id] = {
        angle: family.start + (column + 0.5) * columnAngle,
        radius: base + row * CLUSTER.row,
        size: nodeSize(node)
      }
    })
    teeth.push({ sector: sector.id, group: family.group ?? 'none', start: family.start, end: family.start + family.width, top })
  }
  return { positions, teeth }
}

/**
 * A parent's dots: at most DOTS.rows deep, stepping outwards from `radius`, and as many columns
 * along the ring as that takes, centred on the parent's angle — the model's rows of three. Returns
 * where each sits and how far out the last row reaches.
 */
const placeDots = (subs, angle, radius) => {
  const positions = {}
  const rows = Math.min(DOTS.rows, subs.length)
  const columns = Math.ceil(subs.length / Math.max(1, rows))
  subs.forEach((node, index) => {
    const column = Math.floor(index / rows)
    const row = index % rows
    const r = radius + row * DOTS.row
    positions[node.id] = { angle: angle + ((column - (columns - 1) / 2) * DOTS.column) / r, radius: r, size: DOTS.size }
  })
  return { positions, reach: radius + Math.max(0, rows - 1) * DOTS.row + DOTS.size }
}

/**
 * Lays out one year's government.
 *
 * Each node names its sector (`branch`), its ring, and — for the bodies on the outer ring — the
 * ministry it answers to (`group`). The inner rings are spread evenly across their sector; the
 * outer ring is packed into families beyond the body each answers to, and each family that needs
 * more depth than the band gives becomes a tooth of the cog.
 *
 * @param {object[]} nodes  {id, branch, ring, group?, kind, seats?, employees?}
 * @returns {{
 *   sectors: {id, label, start, end}[],
 *   positions: Record<string, {angle: number, radius: number, size: number}>,
 *   teeth: {sector: string, group: string, start: number, end: number, top: number}[]
 * }}
 */
export const layoutGovernment = (nodes) => {
  const counts = {}
  // Sub-agencies do not widen their branch; they sit in the room their parent already has.
  for (const node of nodes) if (node.ring !== 'sub') counts[node.branch] = (counts[node.branch] ?? 0) + 1
  const subsByParent = new Map()
  for (const node of nodes) {
    if (node.ring !== 'sub') continue
    if (!subsByParent.has(node.parent)) subsByParent.set(node.parent, [])
    subsByParent.get(node.parent).push(node)
  }
  const subsOf = (id) => subsByParent.get(id) ?? []
  const sectors = allocateSectors(counts)

  const positions = {}
  const teeth = []

  for (const sector of sectors) {
    const members = nodes.filter((node) => node.branch === sector.id)

    for (const ring of ['inner', 'cabinet', 'oversight']) {
      const onRing = members.filter((node) => node.ring === ring)
      spreadAngles(onRing.length, sector.start, sector.end).forEach((angle, index) => {
        const node = onRing[index]
        positions[node.id] = { angle, radius: RINGS[ring] * UNIT, size: nodeSize(node) }
      })
    }
  }

  // Families are packed once every sector's inner rings are placed, so a body can sit beyond a
  // ministry — or the Premier — whatever order the sectors were laid out in.
  for (const sector of sectors) {
    const outer = nodes.filter((node) => node.branch === sector.id && node.ring === 'outer')
    const packed = packFamilies(sector, outer, positions, subsOf)
    Object.assign(positions, packed.positions)
    teeth.push(...packed.teeth)
  }

  // Every other parent's dots — a ministry's divisions, an officer's offices — just beyond it.
  for (const [parentId, subs] of subsByParent) {
    const parent = positions[parentId]
    const waiting = subs.filter((node) => !positions[node.id])
    if (!parent || !waiting.length) continue
    const node = nodes.find((entry) => entry.id === parentId)
    const from = node?.ring === 'cabinet' ? RINGS.cabinet * UNIT + 22 + DOTS.clearance : parent.radius + parent.size + DOTS.clearance
    Object.assign(positions, placeDots(waiting, parent.angle, from).positions)
  }

  return { sectors, positions, teeth }
}

/**
 * The rim's radius at `angle` within a sector: the band's edge, raised to every tooth whose span
 * reaches it, each with a rounded shoulder. Sampled along the rim this is the cog's outline, and it
 * follows the teeth as they move, grow and merge.
 */
export const rimAt = (angle, teeth) => {
  let radius = RIM
  const shoulder = SHOULDER / RIM
  for (const tooth of teeth) {
    if (tooth.top <= RIM) continue
    let t = 0
    if (angle >= tooth.start && angle <= tooth.end) t = 1
    else if (angle > tooth.start - shoulder && angle < tooth.start) t = (angle - (tooth.start - shoulder)) / shoulder
    else if (angle > tooth.end && angle < tooth.end + shoulder) t = ((tooth.end + shoulder) - angle) / shoulder
    if (t > 0) radius = Math.max(radius, RIM + (tooth.top - RIM) * (1 - Math.cos(Math.PI * t)) / 2)
  }
  return radius
}

/**
 * One branch's territory: the band from BAND_INNER out to the rim, with its teeth, inset at both
 * edges by half a seam at every radius so the seams between branches keep a constant width.
 *
 * @param {{start: number, end: number}} sector  Angles as drawn (rotation already applied).
 * @param {object[]} teeth  This sector's teeth, also as drawn.
 */
export const territoryPath = (sector, teeth) => {
  const half = SEAM / 2
  const span = sector.end - sector.start
  const steps = Math.max(24, Math.ceil(span / 0.006))
  const outer = []
  for (let index = 0; index <= steps; index += 1) {
    const raw = sector.start + (span * index) / steps
    const radius = rimAt(raw, teeth)
    const angle = Math.min(Math.max(raw, sector.start + half / radius), sector.end - half / radius)
    const point = toPoint(angle, radius)
    outer.push(`${f(point.x)},${f(point.y)}`)
  }
  const innerStart = sector.start + half / BAND_INNER
  const innerEnd = sector.end - half / BAND_INNER
  const a = toPoint(innerEnd, BAND_INNER)
  const b = toPoint(innerStart, BAND_INNER)
  const large = innerEnd - innerStart > Math.PI ? 1 : 0
  return `M${outer.join('L')}L${f(a.x)},${f(a.y)}A${BAND_INNER},${BAND_INNER} 0 ${large} 0 ${f(b.x)},${f(b.y)}Z`
}

/** Cartesian coordinates of a polar position, about the diagram's centre. */
export const toPoint = (angle, radius) => ({
  x: CENTRE.x + Math.cos(angle) * radius,
  y: CENTRE.y + Math.sin(angle) * radius
})

/**
 * The rotation that brings `angle` to six o'clock, the diagram's reading position.
 *
 * Normalised to (−π, π] so the view turns the short way round.
 */
export const rotationToBottom = (angle) => normaliseAngle(Math.PI / 2 - angle)

export const normaliseAngle = (angle) => {
  let value = angle % (Math.PI * 2)
  if (value <= -Math.PI) value += Math.PI * 2
  if (value > Math.PI) value -= Math.PI * 2
  return value
}

/** Interpolates between two angles the short way round. */
export const lerpAngle = (from, to, t) => from + normaliseAngle(to - from) * t

/** SVG path for an annulus sector: the band between two radii across [start, end]. */
export const bandPath = (start, end, inner, outer) => {
  const large = end - start > Math.PI ? 1 : 0
  const a = toPoint(start, outer)
  const b = toPoint(end, outer)
  const c = toPoint(end, inner)
  const d = toPoint(start, inner)
  return [
    `M${f(a.x)},${f(a.y)}`,
    `A${f(outer)},${f(outer)} 0 ${large} 1 ${f(b.x)},${f(b.y)}`,
    `L${f(c.x)},${f(c.y)}`,
    `A${f(inner)},${f(inner)} 0 ${large} 0 ${f(d.x)},${f(d.y)}`,
    'Z'
  ].join('')
}

/** SVG path for an arc along `radius`, for text to follow. Reversed when it would read upside down. */
export const readsReversed = (start, end) => {
  const middle = normaliseAngle((start + end) / 2)
  return middle > 0 && middle < Math.PI
}

export const arcPath = (start, end, radius) => {
  const upsideDown = readsReversed(start, end)
  const [from, to] = upsideDown ? [end, start] : [start, end]
  const a = toPoint(from, radius)
  const b = toPoint(to, radius)
  const large = Math.abs(end - start) > Math.PI ? 1 : 0
  return `M${f(a.x)},${f(a.y)}A${f(radius)},${f(radius)} 0 ${large} ${upsideDown ? 0 : 1} ${f(b.x)},${f(b.y)}`
}

/**
 * The wavy seal at the centre: a circle with `lobes` ripples, as a closed path.
 */
export const sealPath = (radius = RINGS.seal * UNIT, lobes = 16, amplitude = 4, steps = 120) => {
  const points = Array.from({ length: steps }, (_, index) => {
    const theta = (index / steps) * Math.PI * 2
    const r = radius + Math.sin(theta * lobes) * amplitude
    const p = toPoint(theta, r)
    return `${f(p.x)},${f(p.y)}`
  })
  return `M${points.join('L')}Z`
}

const f = (value) => Math.round(value * 100) / 100
