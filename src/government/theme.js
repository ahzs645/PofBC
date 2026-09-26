// The diagram's colours, in JavaScript because the SVG is drawn from them.
//
// The surfaces follow the org-graph convention this view is modelled on: warm stone rather than
// grey, flat cards, colour reserved for meaning. The meaning is the Province's own, though — each
// branch takes a colour from the BC identity palette this generator already draws with, and the
// people at the centre are the sun.

export const THEMES = {
  light: {
    canvas: '#eceae4',
    nodeFill: '#ffffff',
    blendBase: '#ffffff',
    seam: '#c9c4ba',
    inkMuted: '#8f8a80',
    accentInk: '#ffffff',
    territoryAlpha: 0.08,
    pillAlpha: 0.14,
    idleAlpha: null,
    connectedAlpha: 0.35,
    branch: { legislative: '#c23e1d', executive: '#2f5f9e', judicial: '#8f6508' },
    people: '#e8a412',
    sealInk: '#6b4800',
    sealInkSelected: '#2a1d00'
  },
  dark: {
    canvas: '#161310',
    nodeFill: '#272220',
    blendBase: '#221e1a',
    seam: '#3d362e',
    inkMuted: '#8a8378',
    accentInk: '#1c1814',
    territoryAlpha: 0.14,
    pillAlpha: 0.2,
    idleAlpha: 0.26,
    connectedAlpha: 0.55,
    branch: { legislative: '#e2603c', executive: '#6d97e0', judicial: '#d6a52a' },
    people: '#fcba19',
    sealInk: '#fcd36b',
    sealInkSelected: '#2a1d00'
  }
}

/** Party colours for the timeline's premiers. Conventional, not official. */
export const PARTY_COLOURS = {
  'Non-partisan': '#a8a29a',
  Conservative: '#1f4e96',
  Liberal: '#d02a2a',
  Coalition: '#8a6fb8',
  'Social Credit': '#2f8f4e',
  NDP: '#f07c1b',
  CCF: '#c9661a',
  Labour: '#a8452c',
  Socialist: '#8b1e3f',
  Provincial: '#6f8a3a',
  Reform: '#2a9d8f',
  Green: '#3a9b3a',
  Government: '#5b6b77',
  'Non-government': '#b8b2a8',
  Other: '#b8b2a8'
}

/** Names the sources give the same party under — the BC Liberals renamed themselves BC United in 2023. */
const PARTY_ALIASES = {
  'BC Liberal': 'Liberal',
  'BC United': 'Liberal',
  'New Democratic': 'NDP',
  'New Democratic Party': 'NDP',
  'Progressive Conservative': 'Conservative',
  'Conservative Party of BC': 'Conservative'
}

export const partyColour = (party) => PARTY_COLOURS[PARTY_ALIASES[party] ?? party] ?? '#a8a29a'

const parse = (hex) => {
  const value = hex.replace('#', '')
  return [0, 2, 4].map((offset) => parseInt(value.slice(offset, offset + 2), 16))
}

/** A straight RGB mix: `t` of `colour` over `base`. */
export const mix = (colour, base, t) => {
  const a = parse(colour)
  const b = parse(base)
  return `#${a.map((channel, index) => Math.round(b[index] + (channel - b[index]) * t).toString(16).padStart(2, '0')).join('')}`
}

/** A node's colour: its branch's, or the sun's for the people. */
export const colourOf = (node, theme) => (node.kind === 'people' ? theme.people : theme.branch[node.branch] ?? theme.inkMuted)

/** The fill for a node in each state — the selected one solid, its neighbours tinted, the rest quiet. */
export const fillOf = (colour, theme, { selected, connected }) => {
  if (selected) return colour
  if (connected) return mix(colour, theme.blendBase, theme.connectedAlpha)
  return theme.idleAlpha ? mix(colour, theme.blendBase, theme.idleAlpha) : theme.nodeFill
}
