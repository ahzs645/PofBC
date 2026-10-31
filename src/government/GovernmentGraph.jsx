// The radial diagram of the government.
//
// Drawn as plain SVG from the layout in layout.js; nothing here decides where anything goes. What
// this adds is motion: choosing a body turns the whole disc until it sits at six o'clock, and
// moving the timeline carries every body from where it stood to where it stands in the new year,
// so a reorganisation can be watched rather than inferred.

import { useEffect, useMemo, useRef, useState } from 'react'
import {
  aroundCentre, arcPath, CENTRE, COMPACT_GEOMETRY, frameAround, GEOMETRY, lerpAngle, layoutGovernment, readsReversed, rimAt,
  rotationToBottom, SEAM, sealPath, territoryPath, toPoint, VIEWBOX
} from './layout.js'
import { colourOf, fillOf, mix } from './theme.js'
import { pathToPeople } from './snapshot.js'

const DURATION = 750

const lerp = (a, b, t) => a + (b - a) * t
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

/**
 * Carries the drawing from one layout to the next.
 *
 * Positions are interpolated per body, and so are the sectors, the teeth and the rotation. Layout
 * angles live in one fixed frame that never wraps, so they move in a straight line — taking the
 * short way round would send a body that moves far within its sector the long way, through the
 * other branches. Only the rotation, which is free to wrap, turns the short way. A body that is new
 * to the year has nowhere to come from and simply appears where it belongs; its entrance is left
 * to CSS.
 */
const useTween = (target) => {
  const [frame, setFrame] = useState(target)
  const shown = useRef(target)

  useEffect(() => {
    const from = shown.current
    const reduced = globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (reduced) {
      shown.current = target
      setFrame(target)
      return undefined
    }

    let raf = 0
    const start = performance.now()
    const tick = (now) => {
      const t = ease(Math.min(1, (now - start) / DURATION))
      const positions = {}
      for (const [id, to] of Object.entries(target.positions)) {
        const was = from.positions[id]
        positions[id] = was
          ? { ...to, angle: lerp(was.angle, to.angle, t), radius: lerp(was.radius, to.radius, t) }
          : to
      }
      const sectors = target.sectors.map((to) => {
        const was = from.sectors.find((sector) => sector.id === to.id) ?? to
        return { ...to, start: lerp(was.start, to.start, t), end: lerp(was.end, to.end, t) }
      })
      const teeth = target.teeth.map((to) => {
        const was = from.teeth.find((tooth) => tooth.sector === to.sector && tooth.group === to.group) ?? to
        return { ...to, start: lerp(was.start, to.start, t), end: lerp(was.end, to.end, t), top: lerp(was.top ?? to.top, to.top, t) }
      })
      const next = { ...target, positions, sectors, teeth, rotation: lerpAngle(from.rotation, target.rotation, t) }
      shown.current = next
      setFrame(next)
      if (t < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target])

  return frame
}

/**
 * A fitted frame widened or deepened about its middle to the wide frame's proportions, which the
 * page keeps for the diagram, so a phone's frame always spans the screen and the page below it
 * never moves as the years go by. The 28 below the cog is room for the chosen body's name.
 */
const toAspect = (box) => {
  const ratio = VIEWBOX.width / VIEWBOX.height
  if (box.width / box.height < ratio) {
    const width = box.height * ratio
    return { ...box, x: box.x - (width - box.width) / 2, width }
  }
  const height = box.width / ratio
  return { ...box, y: box.y - (height - box.height) / 2, height }
}

// ── Zoom ───────────────────────────────────────────────────────────────────────────────────────

const MAX_ZOOM = 6
const UNZOOMED = { s: 1, x: 0, y: 0 }

/** Keeps the scale in range, and the drawing covering the whole frame — it is never panned off. */
const bound = ({ s, x, y }, box) => {
  const scale = Math.min(MAX_ZOOM, Math.max(1, s))
  const { x: left, y: top, width, height } = box
  return {
    s: scale,
    x: Math.min(left - scale * left, Math.max(left + width - scale * (left + width), x)),
    y: Math.min(top - scale * top, Math.max(top + height - scale * (top + height), y))
  }
}

/** The view after scaling by `factor` about `focus`, a point in the frame's own units. */
const zoomAbout = (view, factor, focus, box) => {
  const s = Math.min(MAX_ZOOM, Math.max(1, view.s * factor))
  const content = { x: (focus.x - view.x) / view.s, y: (focus.y - view.y) / view.s }
  return bound({ s, x: focus.x - content.x * s, y: focus.y - content.y * s }, box)
}

/**
 * Pinch and pan for the diagram, which on a phone is drawn too small to pick the smaller bodies
 * from. Two fingers zoom about their midpoint; once zoomed, one finger pans. Unzoomed, one finger
 * is left to the page, so the diagram never traps a scroll. A trackpad's pinch, which a browser
 * reports as a wheel with Ctrl held, zooms too.
 *
 * Native listeners, not React's, because they must be able to cancel the page's own scroll and
 * zoom, and iOS honours little of CSS touch-action. A drag that moved is not also a tap.
 */
const useZoom = (svg, frameBox) => {
  const [view, setView] = useState(UNZOOMED)
  const live = useRef(view)
  live.current = view

  useEffect(() => {
    const element = svg.current
    if (!element) return undefined
    const toFrame = (clientX, clientY) => {
      const m = element.getScreenCTM()?.inverse()
      return m ? { x: m.a * clientX + m.c * clientY + m.e, y: m.b * clientX + m.d * clientY + m.f } : { x: 0, y: 0 }
    }
    const pointsOf = (touches) => [...touches].map((touch) => ({ ...toFrame(touch.clientX, touch.clientY), cx: touch.clientX, cy: touch.clientY }))
    const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y)
    const middle = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 })
    let gesture = null
    let moved = false
    // Until when a click is taken for the end of a drag. Most browsers send none after a drag, so
    // the window is short, and a new touch closes it: any click after that is the new touch's.
    let swallowUntil = 0

    const panFrom = (point) => ({ kind: 'pan', view: live.current, from: point })
    const start = (event) => {
      swallowUntil = 0
      const points = pointsOf(event.touches)
      if (points.length >= 2) {
        event.preventDefault()
        gesture = { kind: 'pinch', view: live.current, span: distance(points[0], points[1]) || 1, focus: middle(points[0], points[1]) }
      } else if (live.current.s > 1) {
        gesture = panFrom(points[0])
        moved = false
      } else {
        gesture = null
      }
    }
    const move = (event) => {
      if (!gesture) return
      const points = pointsOf(event.touches)
      if (gesture.kind === 'pinch' && points.length >= 2) {
        event.preventDefault()
        const { view: was, span, focus } = gesture
        const content = { x: (focus.x - was.x) / was.s, y: (focus.y - was.y) / was.s }
        const s = Math.min(MAX_ZOOM, Math.max(1, (was.s * distance(points[0], points[1])) / span))
        const now = middle(points[0], points[1])
        setView(bound({ s, x: now.x - content.x * s, y: now.y - content.y * s }, frameBox.current))
        moved = true
      } else if (gesture.kind === 'pan' && points.length === 1) {
        event.preventDefault()
        const [point] = points
        if (!moved && Math.hypot(point.cx - gesture.from.cx, point.cy - gesture.from.cy) < 6) return
        moved = true
        setView(bound({ ...gesture.view, x: gesture.view.x + point.x - gesture.from.x, y: gesture.view.y + point.y - gesture.from.y }, frameBox.current))
      }
    }
    const end = (event) => {
      if (event.touches.length === 0) {
        if (moved) swallowUntil = performance.now() + 350
        gesture = null
        moved = false
      } else if (event.touches.length === 1 && gesture?.kind === 'pinch') {
        // One finger lifted from a pinch: the other carries on as a pan.
        gesture = live.current.s > 1 ? panFrom(pointsOf(event.touches)[0]) : null
        moved = true
      }
    }
    const click = (event) => {
      if (performance.now() > swallowUntil) return
      swallowUntil = 0
      event.stopPropagation()
      event.preventDefault()
    }
    const wheel = (event) => {
      if (!event.ctrlKey) return
      event.preventDefault()
      setView((current) => zoomAbout(current, Math.exp(-event.deltaY * 0.01), toFrame(event.clientX, event.clientY), frameBox.current))
    }
    const noPageZoom = (event) => event.preventDefault()

    element.addEventListener('touchstart', start, { passive: false })
    element.addEventListener('touchmove', move, { passive: false })
    element.addEventListener('touchend', end)
    element.addEventListener('touchcancel', end)
    element.addEventListener('click', click, true)
    element.addEventListener('wheel', wheel, { passive: false })
    element.addEventListener('gesturestart', noPageZoom)
    return () => {
      element.removeEventListener('touchstart', start)
      element.removeEventListener('touchmove', move)
      element.removeEventListener('touchend', end)
      element.removeEventListener('touchcancel', end)
      element.removeEventListener('click', click, true)
      element.removeEventListener('wheel', wheel)
      element.removeEventListener('gesturestart', noPageZoom)
    }
  }, [svg, frameBox])

  // The buttons zoom about the middle of what is on screen.
  const zoomBy = (factor) => setView((current) => {
    const box = frameBox.current
    return zoomAbout(current, factor, { x: box.x + box.width / 2, y: box.y + box.height / 2 }, box)
  })
  return { view, zoomBy, reset: () => setView(UNZOOMED) }
}

const PlusMinus = ({ plus }) => (
  <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
    <path d={plus ? 'M3 7h8M7 3v8' : 'M3 7h8'} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
)

// ── Glyphs: shape says what kind of body, colour which branch ─────────────────────────────────────

const polygon = (sides, radius, offset = -Math.PI / 2) => Array.from({ length: sides }, (_, index) => {
  const theta = offset + (index / sides) * Math.PI * 2
  return `${(Math.cos(theta) * radius).toFixed(2)},${(Math.sin(theta) * radius).toFixed(2)}`
}).join(' ')

export const GLYPHS = {
  circle: (size, props) => <circle r={size} {...props} />,
  square: (size, props) => <rect x={-size * 0.8} y={-size * 0.8} width={size * 1.6} height={size * 1.6} rx={2.5} {...props} />,
  diamond: (size, props) => <rect x={-size * 0.62} y={-size * 0.62} width={size * 1.24} height={size * 1.24} rx={2} transform="rotate(45)" {...props} />,
  double: (size, props) => (
    <g>
      <rect x={-size * 0.8} y={-size * 0.8} width={size * 1.6} height={size * 1.6} rx={2} {...props} />
      <rect x={-size * 0.42} y={-size * 0.42} width={size * 0.84} height={size * 0.84} rx={1} {...props} fill="none" />
    </g>
  ),
  octagon: (size, props) => <polygon points={polygon(8, size * 0.9, Math.PI / 8)} {...props} />,
  pentagon: (size, props) => <polygon points={polygon(5, size * 0.9)} {...props} />,
  hexagon: (size, props) => <polygon points={polygon(6, size * 0.9)} {...props} />,
  triangle: (size, props) => <polygon points={polygon(3, size)} {...props} />,
  // A sub-agency: a dot in its branch colour, without an outline, as the model draws its own.
  dot: (size, { stroke }) => <circle r={size} fill={stroke} fillOpacity={0.75} />
}

export const KINDS = {
  assembly: { glyph: 'circle', label: 'The Legislative Assembly', one: 'The legislature' },
  crown: { glyph: 'circle', label: 'The Crown', one: 'The Crown' },
  premier: { glyph: 'circle', label: 'The Premier', one: 'Head of government' },
  ministry: { glyph: 'square', label: 'Ministries', one: 'Ministry' },
  'central-agency': { glyph: 'square', label: 'Central agencies', one: 'Central agency' },
  officer: { glyph: 'diamond', label: 'Officers of the Legislature', one: 'Officer of the Legislature' },
  'crown-corporation': { glyph: 'double', label: 'Crown corporations', one: 'Crown corporation' },
  agency: { glyph: 'octagon', label: 'Agencies and boards', one: 'Agency or board' },
  tribunal: { glyph: 'pentagon', label: 'Tribunals', one: 'Tribunal' },
  'health-authority': { glyph: 'hexagon', label: 'Health authorities', one: 'Health authority' },
  court: { glyph: 'pentagon', label: 'Courts', one: 'Court' },
  sub: { glyph: 'dot', label: 'Sub-agencies', one: 'Sub-agency' },
  'regional-hospital-district': { glyph: 'triangle', label: 'Regional hospital districts', one: 'Regional hospital district (local)' },
  'hospital-improvement-district': { glyph: 'triangle', label: 'Hospital improvement districts', one: 'Hospital improvement district (local)' }
}

/** Relationship kinds: how each is drawn, and what it is called in the legend and the panel. */
export const RELATIONS = {
  elects: { label: 'Elects', marker: 'double', dash: null, curve: false },
  appoints: { label: 'Appoints', marker: 'filled', dash: null, curve: false },
  confidence: { label: 'Holds the confidence of', legend: 'Confidence', marker: 'hollow', dash: null, curve: true },
  responsible: { label: 'Answers for', legend: 'Answers for', marker: 'chevrons', dash: null, curve: true },
  part: { label: 'Includes', legend: 'Part of', marker: null, dash: '4 2', curve: false },
  // Working with a ministry without answering to it, as the First Nations Health Authority does.
  partner: { label: 'Partner of', legend: 'Partner of', marker: null, dash: '1.5 3', curve: true },
  // Owning a subsidiary, which is not answering for it: not a line to the people.
  owned: { label: 'Owns', legend: 'Owned by', marker: null, dash: '6 2 1 2', curve: false }
}

const MARKERS = {
  double: 'M0,-3 L3,0 L0,3 Z M3,-3 L6,0 L3,3 Z',
  filled: 'M0,-3 L6,0 L0,3 Z',
  hollow: 'M0,-3 L6,0 L0,3 Z',
  chevrons: 'M0,-3 L2,0 L0,3 M3,-3 L5,0 L3,3'
}

export const MarkerPath = ({ kind, colour, fill }) => kind && (
  <path
    d={MARKERS[kind]}
    fill={kind === 'chevrons' ? 'none' : kind === 'hollow' ? fill : colour}
    stroke={colour}
    strokeWidth={kind === 'chevrons' ? 1.1 : 0.8}
    strokeLinejoin="round"
    transform="translate(-3,0)"
  />
)

/**
 * A bean round the Assembly: a stadium lying along the ring, like the pill the model draws round
 * the two chambers of Congress. BC's Legislature has one elected chamber, so the bean holds one.
 */
const beanPath = ({ angle, radius, size }, sector = null) => {
  let reach = (size * 1.9) / radius
  let thick = size + 9
  // Kept inside its branch: each round end stays clear of the seam (a parallel-sided band half a
  // seam either side of the sector's edge), so the bean never reaches into the executive's band.
  if (sector) {
    const margin = SEAM / 2 + 3
    const room = Math.min(angle - sector.start, sector.end - angle)
    thick = Math.max(size + 2, Math.min(thick, radius * Math.sin(Math.max(0, room)) - margin))
    reach = Math.max(0, Math.min(reach, room - Math.asin(Math.min(1, (thick + margin) / radius))))
  }
  const a = toPoint(angle - reach, radius + thick)
  const b = toPoint(angle + reach, radius + thick)
  const c = toPoint(angle + reach, radius - thick)
  const d = toPoint(angle - reach, radius - thick)
  const outer = radius + thick
  const inner = radius - thick
  return `M${a.x},${a.y}A${outer},${outer} 0 0 1 ${b.x},${b.y}A${thick},${thick} 0 0 1 ${c.x},${c.y}A${inner},${inner} 0 0 0 ${d.x},${d.y}A${thick},${thick} 0 0 1 ${a.x},${a.y}Z`
}

const PEOPLE = 'people-of-british-columbia'
const NO_RELATIONS = new Set()

/** What a line says when pointed at, read the way it runs: who does what to whom. */
export const edgeTitle = (edge, from, to) => {
  const a = from?.shortName ?? from?.name ?? edge.from
  const b = to?.shortName ?? to?.name ?? edge.to
  switch (edge.kind) {
    case 'elects': return `${a} elect the ${b}${edge.seats ? ` (${edge.seats} members)` : ''}`
    case 'appoints': return to?.kind === 'ministry' ? `${a} chooses the minister of the ${b}` : `${a} appoints the ${b}`
    case 'confidence': return `${b} governs with the confidence of the ${a}`
    case 'responsible': return `${a} answers for ${b}`
    case 'part': return `${b} is part of ${a}`
    case 'partner': return `${b} is a partner of the ${a}`
    case 'owned': return `${b} is a subsidiary of ${a}: owned, which is not answering to it`
    default: return `${a} — ${b}`
  }
}
const clockwise = (angle) => ((angle + Math.PI / 2) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2)

/** Where a head — minister, chief justice, chair — hangs from its body: just outside it, facing out. */
const headPoint = (angle, radius, size) => toPoint(angle, radius + size * 0.95)

// ── The diagram ───────────────────────────────────────────────────────────────────────────────────

/**
 * @param {object} props
 * @param {object} props.government   A snapshot from governmentIn().
 * @param {string|null} props.selectedId
 * @param {(id: string|null) => void} props.onSelect
 * @param {Set<string>} props.hiddenKinds       Node kinds hidden, and 'heads' for the head circles.
 * @param {Set<string>} [props.hiddenRelations] Relation kinds whose lines are not drawn.
 * @param {object} props.theme        One of THEMES.
 * @param {boolean} [props.compact]   Drawn small, as on a phone: the targets grow to stay tappable.
 */
export const GovernmentGraph = ({ government, selectedId, onSelect, hiddenKinds, hiddenRelations = NO_RELATIONS, theme, compact = false }) => {
  const [pointed, setHovered] = useState(null)
  const svg = useRef(null)
  // On a phone the disc is laid out smaller with the same glyphs, and framed (below) to run to the edges.
  const geometry = compact ? COMPACT_GEOMETRY : GEOMETRY
  const frameBox = useRef(VIEWBOX)
  const { view, zoomBy, reset } = useZoom(svg, frameBox)
  const zoomed = view.s > 1
  const nodes = government.nodes
  const byId = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes])
  // A body under the pointer can leave the diagram without the pointer leaving it — the year moves
  // on beneath it — so a hover is only honoured while its body is still drawn.
  const hovered = byId.has(pointed) ? pointed : null

  // Sub-agencies are folded into their parent until it is chosen — or one of them is — and then laid
  // out round it, the cog growing to hold them, as the model opens a department's own bodies.
  const expanded = useMemo(() => {
    const chosen = selectedId ? byId.get(selectedId) : null
    if (!chosen) return null
    return chosen.ring === 'sub' ? chosen.parent : chosen.id
  }, [selectedId, byId])
  const folded = useMemo(() => {
    const counts = new Map()
    for (const node of nodes) if (node.ring === 'sub' && node.parent !== expanded) counts.set(node.parent, (counts.get(node.parent) ?? 0) + 1)
    return counts
  }, [nodes, expanded])
  const layout = useMemo(() => layoutGovernment(nodes.filter((node) => node.branch && (node.ring !== 'sub' || node.parent === expanded)), geometry), [nodes, geometry, expanded])

  // The body the disc turns to. A head's own body stands in for it, and the people turn nothing.
  const pivot = selectedId && layout.positions[selectedId] ? layout.positions[selectedId].angle : null
  const target = useMemo(() => ({
    positions: layout.positions,
    sectors: layout.sectors,
    teeth: layout.teeth,
    rotation: pivot === null ? 0 : rotationToBottom(pivot)
  }), [layout, pivot])
  const frame = useTween(target)
  // A wide screen keeps one frame for every year; a phone's follows the cog as it grows and shrinks.
  const fitted = compact ? frameAround(frame.teeth, frame.rotation, geometry) : null
  const box = fitted ? toAspect({ ...fitted, height: fitted.height + 28 }) : VIEWBOX
  frameBox.current = box

  const at = (id) => {
    const position = frame.positions[id]
    if (!position) return null
    const angle = position.angle + frame.rotation
    return { ...toPoint(angle, position.radius), angle, radius: position.radius, size: position.size }
  }

  // What the chosen body is connected to, and the whole of its line up to the people — not only
  // the first step of it.
  const selectedEdges = useMemo(() => {
    if (!selectedId) return []
    const path = pathToPeople(government, selectedId)
    const near = government.edges.filter((edge) => edge.from === selectedId || edge.to === selectedId)
    return [...near, ...path.filter((step) => !near.some((edge) => edge.from === step.from && edge.to === step.to && edge.kind === step.kind))]
      .filter((edge) => !hiddenRelations.has(edge.kind))
  }, [government, selectedId, hiddenRelations])
  const connected = useMemo(() => new Set(selectedEdges.flatMap((edge) => [edge.from, edge.to])), [selectedEdges])
  // The people are lit whenever the chosen body's line reaches them, not only when they are chosen.
  const peopleLit = selectedId === PEOPLE || connected.has(PEOPLE)

  const selected = selectedId ? byId.get(selectedId) : null
  const r = frame.rotation
  const teethOf = (sectorId) => frame.teeth.filter((tooth) => tooth.sector === sectorId)
  // A branch's territory, its band and teeth together, inset by half a seam at every radius.
  const territoryOf = (sector) => territoryPath(
    { start: sector.start + r, end: sector.end + r },
    teethOf(sector.id).map((tooth) => ({ ...tooth, start: tooth.start + r, end: tooth.end + r })),
    geometry
  )
  const executiveSector = frame.sectors.find((sector) => sector.id === 'executive')
  // The executive's family of bodies with no stated ministry, when it is wide enough to name.
  const unattachedLane = frame.teeth.find((tooth) => tooth.sector === 'executive' && tooth.group === 'none' && tooth.end - tooth.start > 0.18) ?? null
  // A lane's name, set along its tooth: the arc is lengthened past a narrow tooth (as on a phone's
  // smaller disc) rather than the name being cut off where the arc ends.
  // Where it would run into its branch's own name (a lane on the plain rim, as in 1900), it is set
  // a line further out instead.
  const laneArc = (lane, text) => {
    let radius = Math.max(lane.top, geometry.rim) + 14
    const middle = (lane.start + lane.end) / 2 + r
    const length = text.length * 6.4 + 12
    const sector = frame.sectors.find((entry) => entry.id === lane.sector)
    if (sector) {
      const named = (sector.start + sector.end) / 2 + r
      const nameRadius = labelRadius(sector, named - r, Math.min((sector.end - sector.start) / 2, 0.5))
      const nameLength = sector.label.length * 10.5
      if (Math.abs(nameRadius - radius) < 14 && Math.abs(middle - named) * radius < (length + nameLength) / 2 + 8) radius = nameRadius + 14
    }
    const half = Math.max((lane.end - lane.start) / 2, length / 2 / radius)
    return arcPath(middle - half, middle + half, radius)
  }
  // The local bodies' lane, when they are shown.
  const localLane = frame.teeth.find((tooth) => tooth.group === 'local' && tooth.end - tooth.start > 0.12) ?? null
  // The branch label sits just beyond the highest part of the rim it spans.
  const labelRadius = (sector, middle, span) => {
    let top = geometry.rim
    for (let angle = middle - span; angle <= middle + span; angle += 0.02) top = Math.max(top, rimAt(angle, teethOf(sector.id), geometry.rim))
    return top + 16
  }
  // The Legislature's bean, drawn round the Assembly as the model draws Congress round its chambers.
  const assemblyPoint = at('legislative-assembly')
  const legislature = assemblyPoint ? { ...assemblyPoint } : null
  const legislativeSector = frame.sectors.find((sector) => sector.id === 'legislative')
  const legislativeBounds = legislativeSector ? { start: legislativeSector.start + r, end: legislativeSector.end + r } : null

  // The ministries' band: an arc across the span the cabinet occupies, drawn as one thick stroke.
  const ministries = nodes.filter((node) => node.ring === 'cabinet').map((node) => frame.positions[node.id]).filter(Boolean)
  const cabinetSpan = ministries.length
    ? [Math.min(...ministries.map((p) => p.angle)) + r, Math.max(...ministries.map((p) => p.angle)) + r]
    : null
  // Keyboard order: the people, then round the disc clockwise from twelve o'clock. One body is
  // the tab stop — the chosen one, else the Premier — and the arrow keys move between the rest.
  const order = useMemo(() => [
    PEOPLE,
    ...nodes
      .filter((node) => layout.positions[node.id] && !hiddenKinds.has(node.kind))
      .sort((a, b) => clockwise(layout.positions[a.id].angle) - clockwise(layout.positions[b.id].angle))
      .map((node) => node.id)
  ], [nodes, layout, hiddenKinds])
  const anchor = order.includes(selectedId) ? selectedId : 'premier'
  const moveFocus = (event, id) => {
    const steps = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }
    let next = null
    if (event.key in steps) next = order[(order.indexOf(id) + steps[event.key] + order.length) % order.length]
    else if (event.key === 'Home') next = order[0]
    else if (event.key === 'End') next = order.at(-1)
    else if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onSelect(id); return }
    if (!next) return
    event.preventDefault()
    svg.current?.querySelector(`[data-id="${next}"]`)?.focus()
  }

  const executive = frame.sectors.find((sector) => sector.id === 'executive')
  const innerCrowded = cabinetSpan && nodes.some((node) => node.ring === 'inner' && node.branch === 'executive' &&
    frame.positions[node.id] && Math.abs(frame.positions[node.id].angle + r - (cabinetSpan[0] + 0.35)) < 0.55)
  const cabinetLabelRadius = geometry.ring.cabinet + (innerCrowded ? 29 : -30)

  return (
    <>
      <svg
        ref={svg}
        className="gov-graph"
        viewBox={`${box.x} ${box.y} ${box.width} ${box.height}`}
        role="group"
        aria-label={`The Government of British Columbia in ${government.year}`}
        data-zoomed={zoomed || undefined}
        onClick={(event) => { if (event.target === event.currentTarget) onSelect(null) }}
      >
        {/* Everything but the caption is zoomed; the caption stays where it can be read. */}
        <g transform={zoomed ? `translate(${view.x} ${view.y}) scale(${view.s})` : undefined}>
          {/* Territory: each branch's sector, and a tooth beyond the rim for each ministry's family. */}
          <g className="gov-graph__territory" onClick={() => onSelect(null)}>
            {/* One path per branch: the band and its teeth together, filled with an opaque tint so
                nothing doubles where they meet, and inset by half a seam at every radius. */}
            {frame.sectors.map((sector) => (
              <path
                key={sector.id}
                d={territoryOf(sector)}
                fill={mix(theme.branch[sector.id], theme.canvas, theme.territoryAlpha)}
              />
            ))}
            {[geometry.ring.inner, geometry.ring.oversight, geometry.ring.outer].map((radius) => (
              <circle key={radius} cx={CENTRE.x} cy={CENTRE.y} r={radius} fill="none" stroke={theme.seam} strokeDasharray="4 3" />
            ))}
            {/* The ministries' band is clipped to the executive's own territory, so its round ends
                never reach across a seam into the Legislature's band. */}
            {executiveSector && (
              <clipPath id="gov-executive-territory">
                <path d={territoryOf(executiveSector)} />
              </clipPath>
            )}
            {cabinetSpan && (
              <path
                d={arcPath(cabinetSpan[0] - 0.04, cabinetSpan[1] + 0.04, geometry.ring.cabinet)}
                clipPath="url(#gov-executive-territory)"
                fill="none"
                stroke={mix(theme.branch.executive, theme.canvas, theme.territoryAlpha + theme.pillAlpha)}
                strokeWidth={44}
                strokeLinecap="round"
              />
            )}
            {legislature && (
              <path
                d={beanPath(legislature, legislativeBounds)}
                fill={mix(theme.branch.legislative, theme.canvas, theme.territoryAlpha + theme.pillAlpha)}
                stroke={theme.branch.legislative}
                strokeWidth={1.5}
              />
            )}
          </g>

          {/* Labels on arcs: the branches outside the rim, the cabinet along its band. */}
          <g className="gov-graph__labels" aria-hidden="true">
            {frame.sectors.map((sector) => {
              const width = sector.end - sector.start
              const middle = (sector.start + sector.end) / 2 + r
              const span = Math.min(width / 2, 0.5)
              const id = `sector-label-${sector.id}`
              return (
                <g key={sector.id}>
                  <path id={id} d={arcPath(middle - span, middle + span, labelRadius(sector, middle - r, span))} fill="none" />
                  <text className="gov-graph__sector-label" fill={theme.branch[sector.id]}>
                    <textPath href={`#${id}`} startOffset="50%" textAnchor="middle">{sector.label}</textPath>
                  </text>
                </g>
              )
            })}
            {cabinetSpan && executive && (
              <g>
                {/* At the band's leading end: inside it, unless the Premier or the Crown sits there — as in
                    the early years, when a handful of departments gather mid-sector — and then outside.
                    The arc is reversed when it would read upside down, so the anchor follows it. */}
                <path id="cabinet-label" d={arcPath(cabinetSpan[0] - 0.05, cabinetSpan[0] + 0.75, cabinetLabelRadius)} fill="none" />
                <text className="gov-graph__ring-label" fill={theme.branch.executive}>
                  <textPath
                    href="#cabinet-label"
                    startOffset={readsReversed(cabinetSpan[0] - 0.05, cabinetSpan[0] + 0.75) ? '96%' : '4%'}
                    textAnchor={readsReversed(cabinetSpan[0] - 0.05, cabinetSpan[0] + 0.75) ? 'end' : 'start'}
                  >
                    {government.year < 1976 ? 'DEPARTMENTS' : 'CABINET'}
                  </textPath>
                </text>
              </g>
            )}
          </g>

          {/* The rings, named along the bottom as the model names them — while the disc is at rest. Once
              a body is chosen it turns to the bottom, and the names would only cross it. */}
          <g className="gov-graph__labels gov-graph__ring-names" data-hidden={selectedId ? true : undefined} aria-hidden="true">
            {[
              { id: 'ring-inner', radius: geometry.bandInner + 6, wide: GEOMETRY.bandInner + 6, text: 'HIGHEST AUTHORITY' },
              { id: 'ring-oversight', radius: geometry.ring.oversight + 14, wide: GEOMETRY.ring.oversight + 14, text: 'OVERSIGHT' },
              { id: 'ring-outer', radius: geometry.ring.outer - 16, wide: GEOMETRY.ring.outer - 16, text: 'CROWN CORPORATIONS AND AGENCIES' }
            ].map((ring) => (
              <g key={ring.id}>
                <path id={ring.id} d={arcPath(Math.PI / 2 - (0.6 * ring.wide) / ring.radius, Math.PI / 2 + (0.6 * ring.wide) / ring.radius, ring.radius)} fill="none" />
                <text className="gov-graph__ring-label gov-graph__ring-label--halo" fill={theme.inkMuted} stroke={theme.canvas}>
                  <textPath href={`#${ring.id}`} startOffset="50%" textAnchor="middle">{ring.text}</textPath>
                </text>
              </g>
            ))}
            {/* Bodies known to have stood with no ministry named for them in the sources: labelled as
                such along their tooth, rather than attached to a plausible ministry. */}
            {unattachedLane && (
              <g>
                <path id="unattached-label" d={laneArc(unattachedLane, 'NO MINISTRY ESTABLISHED')} fill="none" />
                <text className="gov-graph__ring-label gov-graph__ring-label--lane" fill={theme.inkMuted}>
                  <textPath href="#unattached-label" startOffset="50%" textAnchor="middle">NO MINISTRY ESTABLISHED</textPath>
                </text>
              </g>
            )}
            {localLane && (
              <g>
                <path id="local-label" d={laneArc(localLane, 'LOCAL BODIES')} fill="none" />
                <text className="gov-graph__ring-label gov-graph__ring-label--lane" fill={theme.inkMuted}>
                  <textPath href="#local-label" startOffset="50%" textAnchor="middle">LOCAL BODIES</textPath>
                </text>
              </g>
            )}
            {legislature && (
              <g>
                <path id="legislature-label" d={arcPath(legislature.angle - 0.4, legislature.angle + 0.4, legislature.radius + legislature.size + 22)} fill="none" />
                <text className="gov-graph__ring-label" fill={theme.branch.legislative}>
                  <textPath href="#legislature-label" startOffset="50%" textAnchor="middle">LEGISLATURE</textPath>
                </text>
              </g>
            )}
          </g>

          {/* Edges, only for the body chosen, drawn once it has come to rest. */}
          <g className="gov-graph__edges">
            {selectedEdges.map((edge) => {
              const a = edge.from === 'people-of-british-columbia' ? { ...CENTRE } : at(edge.from)
              const b = edge.to === 'people-of-british-columbia' ? { ...CENTRE } : at(edge.to)
              if (!a || !b) return null
              const relation = RELATIONS[edge.kind] ?? RELATIONS.appoints
              const source = byId.get(edge.from)
              const colour = colourOf(source, theme)
              const dx = b.x - a.x
              const dy = b.y - a.y
              const length = Math.hypot(dx, dy) || 1
              // Curved relations bow to one side, so they read apart from the straight ones; a line
              // that would cross the people bows round them instead.
              const bend = relation.curve ? 0.2 * length : 0
              const around = aroundCentre(a, b)
              const cx = around ? around.x : (a.x + b.x) / 2 - (dy / length) * bend
              const cy = around ? around.y : (a.y + b.y) / 2 + (dx / length) * bend
              const mid = { x: 0.25 * a.x + 0.5 * cx + 0.25 * b.x, y: 0.25 * a.y + 0.5 * cy + 0.25 * b.y }
              // The marker follows the curve at its midpoint: along b − a for a symmetric bow, which
              // is what the curve's own tangent there is.
              const tangent = Math.atan2(b.y - a.y, b.x - a.x) * (180 / Math.PI)
              const title = edgeTitle(edge, source, byId.get(edge.to))
              return (
                <g key={`${edge.from}-${edge.to}-${edge.kind}`} className="gov-graph__edge">
                  <title>{title}</title>
                  {/* A wide clear stroke, so the line can be pointed at. */}
                  <path d={`M${a.x},${a.y}Q${cx},${cy} ${b.x},${b.y}`} fill="none" stroke="transparent" strokeWidth={10} />
                  <path
                    d={`M${a.x},${a.y}Q${cx},${cy} ${b.x},${b.y}`}
                    fill="none"
                    stroke={colour}
                    strokeWidth={1}
                    strokeDasharray={relation.dash ?? undefined}
                  />
                  <g transform={`translate(${mid.x},${mid.y}) rotate(${tangent})`}>
                    <MarkerPath kind={relation.marker} colour={colour} fill={theme.nodeFill} />
                  </g>
                </g>
              )
            })}
          </g>

          {/* The people, at the centre: the sun, rippled like a seal. */}
          <g
            className="gov-graph__seal"
            data-id={PEOPLE}
            role="button"
            tabIndex={anchor === PEOPLE ? 0 : -1}
            aria-label="People of British Columbia"
            aria-pressed={selectedId === PEOPLE}
            onClick={() => onSelect(PEOPLE)}
            onKeyDown={(event) => moveFocus(event, PEOPLE)}
          >
            <path
              d={sealPath()}
              fill={peopleLit ? theme.people : mix(theme.people, theme.blendBase, 0.3)}
              stroke={theme.people}
              strokeWidth={1.5}
            />
            {/* The label follows the fill: dark on the full sun, whether the people are chosen or
                joined to what is, so it stays legible against the bright yellow. */}
            <text x={CENTRE.x} y={CENTRE.y - 3}className="gov-graph__seal-label" fill={peopleLit ? theme.sealInkLit : theme.sealInk}>People of</text>
            <text x={CENTRE.x} y={CENTRE.y + 11} className="gov-graph__seal-label" fill={peopleLit ? theme.sealInkLit : theme.sealInk}>British Columbia</text>
          </g>

          {/* Bodies. */}
          <g className="gov-graph__nodes">
            {nodes.map((node) => {
              const point = at(node.id)
              if (!point) return null
              const kind = KINDS[node.kind] ?? KINDS.agency
              const colour = colourOf(node, theme)
              const isSelected = node.id === selectedId
              const isConnected = !isSelected && connected.has(node.id)
              const hidden = hiddenKinds.has(node.kind)
              const size = point.size * (isSelected ? 1.3 : 1)
              const fill = fillOf(colour, theme, { selected: isSelected || hovered === node.id, connected: isConnected })
              const facing = (point.angle * 180) / Math.PI + 90
              const hasHead = ['ministry', 'crown-corporation', 'officer', 'health-authority', 'court'].includes(node.kind)
              const isDot = node.kind === 'sub'
              const head = hasHead && !hiddenKinds.has('heads') ? headPoint(point.angle, point.radius, size) : null
              const vacant = !node.head?.person
              const select = () => onSelect(node.id)
              return (
                <g
                  key={node.id}
                  className="gov-graph__node"
                  data-id={node.id}
                  data-hidden={hidden || undefined}
                  data-uncertain={node.uncertain || undefined}
                  role="button"
                  tabIndex={!hidden && anchor === node.id ? 0 : -1}
                  aria-label={node.name}
                  aria-pressed={isSelected}
                  onClick={select}
                  onKeyDown={(event) => moveFocus(event, node.id)}
                  onPointerEnter={() => setHovered(node.id)}
                  onPointerLeave={() => setHovered((current) => (current === node.id ? null : current))}
                  onFocus={() => setHovered(node.id)}
                  onBlur={() => setHovered((current) => (current === node.id ? null : current))}
                >
                  {head && (
                    <circle
                      cx={head.x}
                      cy={head.y}
                      r={Math.max(3.2, size * 0.26)}
                      fill={isSelected ? colour : theme.nodeFill}
                      stroke={colour}
                      strokeWidth={1}
                      strokeDasharray={vacant ? '2 2.4' : undefined}
                    />
                  )}
                  <g transform={`translate(${point.x},${point.y}) rotate(${facing})`}>
                    {/* The target a finger needs is a size on the screen, so zooming in does not grow it. */}
                    <circle r={isDot ? (compact ? 9 : 5) / view.s : Math.max(size * 1.5, (compact ? 22 : 12) / view.s)} fill="transparent" />
                    <circle className="gov-graph__focus" r={Math.max(size * 1.55, 11)} />
                    {GLYPHS[kind.glyph](size, {
                      fill,
                      stroke: colour,
                      strokeWidth: node.ring === 'inner' ? 2 : 1,
                      vectorEffect: 'non-scaling-stroke'
                    })}
                  </g>
                  {/* How many sub-agencies are folded into it, until it is chosen. */}
                  {folded.has(node.id) && !hiddenKinds.has('sub') && (() => {
                    const badge = toPoint(point.angle, point.radius + size + (head ? 10 : 7))
                    return (
                      <text className="gov-graph__folded" x={badge.x} y={badge.y} fill={colour} aria-hidden="true">
                        +{folded.get(node.id)}
                      </text>
                    )
                  })()}
                </g>
              )
            })}
          </g>

          {/* A tooltip for the body under the pointer, and a caption for the chosen one. */}
          {hovered && hovered !== selectedId && byId.get(hovered) && at(hovered) && (
            <Tooltip node={byId.get(hovered)} point={at(hovered)} theme={theme} box={box} />
          )}
        </g>
        {selected && selected.kind !== 'people' && (
          <Caption text={selected.shortName ?? selected.name} colour={colourOf(selected, theme)} theme={theme} x={box.x + box.width / 2} y={box.y + box.height - 20} chars={Math.floor((box.width - 40) / 7.6)} />
        )}
      </svg>
      {/* On a phone, buttons for what a pinch does, so that it can be found; anywhere, a way back. */}
      {(compact || zoomed) && (
        <div className="gov-zoom" role="group" aria-label="Zoom">
          <span className="gov-button-group">
            <button type="button" className="gov-button gov-button--icon" disabled={!zoomed} onClick={() => zoomBy(1 / 1.6)} aria-label="Zoom out"><PlusMinus /></button>
            <button type="button" className="gov-button gov-button--icon" disabled={view.s >= MAX_ZOOM} onClick={() => zoomBy(1.6)} aria-label="Zoom in"><PlusMinus plus /></button>
          </span>
          {zoomed && <button type="button" className="gov-button gov-button--text" onClick={reset}>Reset</button>}
        </div>
      )}
    </>
  )
}

/** Shortens a label to what fits in `chars`, so no pill is ever narrower than its text. */
const fit = (text, chars) => (text.length > chars ? `${text.slice(0, chars - 1).trimEnd()}…` : text)

const Caption = ({ text: full, colour, theme, x, y, chars = 72 }) => {
  const text = fit(full, Math.min(72, chars))
  const width = text.length * 7.6 + 16
  return (
    <g className="gov-graph__caption" pointerEvents="none">
      <rect x={x - width / 2} y={y - 13} width={width} height={20} rx={4} fill={theme.nodeFill} />
      <text x={x} y={y + 2} textAnchor="middle" fill={colour}>{text}</text>
    </g>
  )
}

const Tooltip = ({ node, point, theme, box = VIEWBOX }) => {
  // The full name, with the short form after it when there is room: “BCMHSUS” alone says nothing.
  const full = node.shortName && node.shortName !== node.name ? `${node.name} (${node.shortName})` : node.name
  const text = fit(full.length <= 54 ? full : node.name, 54)
  const width = text.length * 6.4 + 14
  const x = Math.min(Math.max(point.x, box.x + width / 2 + 4), box.x + box.width - width / 2 - 4)
  const y = point.y - point.size - 16
  return (
    <g className="gov-graph__tooltip" pointerEvents="none">
      <rect x={x - width / 2} y={y - 12} width={width} height={18} rx={4} fill={colourOf(node, theme)} />
      <text x={x} y={y + 1} textAnchor="middle" fill={theme.accentInk}>{text}</text>
    </g>
  )
}
