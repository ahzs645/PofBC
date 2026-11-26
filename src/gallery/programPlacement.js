// All spacing factors are relative to visible artwork height, before adding a margin.
// CleanBC measurements use the first lowercase c in each trimmed source layout.
const cleanClearance = {
  'base-endorsed': .49, 'base-wordmark': .721, 'tagline-endorsed': .471, 'tagline-wordmark': .472,
  'better-buildings-endorsed': .49, 'better-buildings-wordmark': .489,
  'better-homes-endorsed': .49, 'better-homes-wordmark': .491,
  'active-transportation-endorsed': .49, 'active-transportation-wordmark': .491,
  'go-electric-endorsed': .49, 'go-electric-wordmark': .49, 'supported-by': .47, financeit: .484
}
const cleanMinima = { 'base-endorsed': [50, .46], 'base-wordmark': [45, .4], 'tagline-wordmark': [50, .46] }

export function cleanPlacement(layout, treatment, guide) {
  const [px, print] = cleanMinima[layout.id] ?? []
  let spacing = cleanClearance[layout.id]
  if (layout.id === 'base-wordmark' && treatment === 'reverse') spacing = .72
  if (layout.id === 'go-electric-wordmark' && treatment === 'white') spacing = .488
  return { px, print, printUnit: 'in', spacing, companion: layout.form === 'wordmark',
    reference: 'Height of the lowercase “c” in “clean”', guide: guide + '#page=5', citation: 'CleanBC · April 2024, p. 5' }
}

// StrongerBC p. 4 specifies the clearance graphically. Divide the reference corner
// square by the ink height in the same diagram (PDF points, excluding the frame).
const strongerLayouts = {
  A: [50, .46, 13.17 / 42.799], B: [25, .23, 12.595 / 26.658],
  C: [50, .46, 13.17 / 39.165], D: [40, .35, 12.595 / 39.05]
}
export function strongerPlacement(layout, guide) {
  const [px, print, spacing] = strongerLayouts[layout]
  return { px, print, printUnit: 'in', spacing, companion: layout === 'B' || layout === 'D',
    reference: 'Clear-space square in diagram ' + layout, guide: guide + '#page=4', citation: 'StrongerBC · March 2024, p. 4' }
}

export function endorsedPlacement(layout, treatment, guide) {
  return { ...(layout === 'lockup' ? { px: 30, print: 10, spacing: treatment === 'blue-positive' ? .316 : .313 } : {}),
    printUnit: 'mm', companion: layout === 'wordmark', reference: 'Height of the program capital letters',
    guide: guide + '#page=' + (layout === 'province' ? 2 : 1), citation: 'Endorsed marks · June 2019, p. ' + (layout === 'province' ? 2 : 1) }
}

export function checkPlacement(rule, medium, heightInput, marginInput) {
  const height = Number(heightInput)
  const minimum = medium === 'screen' ? rule.px : rule.print
  if (!Number.isFinite(height) || height <= 0) return { minimum }
  const required = rule.spacing == null ? null : height * rule.spacing
  const margin = marginInput === null ? required : String(marginInput).trim() === '' ? NaN : Number(marginInput)
  // Round a suggested margin up for placement. Check entered measurements at full precision.
  const scale = medium === 'print' && rule.printUnit === 'in' ? 1000 : 100
  const target = required == null ? null : Math.ceil(required * scale - 1e-9) / scale
  const available = marginInput === null ? target : Number.isFinite(margin) && margin >= 0 ? margin : null
  return { height, minimum, target, available,
    sizeOK: minimum == null ? null : height >= minimum,
    spacingOK: target == null || available == null ? null : available + Number.EPSILON * Math.max(available, required) >= required }
}
