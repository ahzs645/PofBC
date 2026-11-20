// How a pin is put together, for its 3D view: a recipe that sits beside the pin's parts (see
// novelty/pins.js) and says what kind of object it is and which of its dimensions are known. Data
// only, no three.js, so a recipe can be checked without a browser. A pin opts in to the 3D view by
// having one; printedButton.js builds the model from it.
//
// A recipe:
//   kind            'printed-button' (the only kind so far)
//   diameterMm      the size the model is built at
//   diameterStatus  'measured' or 'illustrative'
//   dome            the face's rise as a fraction of the diameter, 0 (flat) to 0.15
//   edge            'rolled'
//   back            'tin-back'
//   fitting         'safety-pin'
//   fittingStatus   'seen' or 'generic'
//   face            { svg, background }: the drawing printed on the face, and the face's ground
//                   colour, which the rolled edge carries round to the back
//   evidence        short strings: what the recipe rests on

export const KINDS = ['printed-button']
export const DOME_MAX = 0.15

/** The face's shapes offered in the 3D view. */
export const FACE_SHAPES = [
  { value: 'flat', label: 'Flat', dome: 0, title: 'A flat face' },
  { value: 'slight', label: 'Slight dome', dome: 0.02, title: 'A rise of 2% of the diameter' },
  { value: 'domed', label: 'Domed', dome: 0.06, title: 'A rise of 6% of the diameter' }
]

/** The face shape nearest a recipe's dome. */
export const faceShapeFor = (dome) => FACE_SHAPES.reduce((best, shape) => (Math.abs(shape.dome - dome) < Math.abs(best.dome - dome) ? shape : best))

/** @returns {string[]} what is wrong with a recipe; empty when it is sound. */
export function constructionProblems (recipe) {
  const problems = []
  if (!recipe || typeof recipe !== 'object') return ['no recipe']
  if (!KINDS.includes(recipe.kind)) problems.push(`unknown kind ${recipe.kind}`)
  if (!(recipe.diameterMm > 0 && recipe.diameterMm < 200)) problems.push('diameterMm out of range')
  if (!['measured', 'illustrative'].includes(recipe.diameterStatus)) problems.push('diameterStatus')
  if (!(recipe.dome >= 0 && recipe.dome <= DOME_MAX)) problems.push('dome out of range')
  if (recipe.edge !== 'rolled') problems.push('edge')
  if (recipe.back !== 'tin-back') problems.push('back')
  if (recipe.fitting !== 'safety-pin') problems.push('fitting')
  if (!['seen', 'generic'].includes(recipe.fittingStatus)) problems.push('fittingStatus')
  if (!recipe.face?.svg || !/^#[0-9a-f]{6}$/i.test(recipe.face.background ?? '')) problems.push('face')
  if (!Array.isArray(recipe.evidence) || !recipe.evidence.length || recipe.evidence.some((line) => typeof line !== 'string' || !line.trim())) problems.push('evidence')
  return problems
}

/** A recipe's size, worded for the page: "38 mm (1½ in), illustrative". */
export const diameterWords = ({ diameterMm, diameterStatus }) => {
  const inches = diameterMm / 25.4
  const eighths = Math.round(inches * 8)
  const whole = Math.floor(eighths / 8)
  const fraction = { 0: '', 1: '⅛', 2: '¼', 3: '⅜', 4: '½', 5: '⅝', 6: '¾', 7: '⅞' }[eighths % 8]
  return `${diameterMm} mm (${whole || ''}${fraction || (whole ? '' : '0')} in)${diameterStatus === 'illustrative' ? ', illustrative' : ''}`
}
