// How a pin is put together, for its 3D view: a recipe that sits beside the pin's parts (see
// novelty/pins.js) and says what kind of object it is and which of its dimensions are known. Data
// only, no three.js, so a recipe can be checked without a browser. A pin opts in to the 3D view by
// having one; printedButton.js builds the model from it.
//
// A recipe:
//   kind            'printed-button' (the only kind so far)
//   shape           'round' (the default) or 'oval'
//   diameterMm      the size the model is built at: a round button's diameter, an oval's height
//   aspect          an oval's width over its height, 1 to 2 (an oval only)
//   diameterStatus  'measured' or 'illustrative'
//   dome            the face's rise as a fraction of the diameter (an oval's height), 0 (flat) to 0.15
//   finish          'printed' (matte ink, the default) or 'celluloid' (a glossy clear face)
//   edge            'rolled'
//   back            'tin-back'
//   fitting         'safety-pin'
//   fittingStatus   'seen' or 'generic'
//   face            { svg, background, view?, rim? }: the drawing printed on the face, the face's
//                   ground colour, which the rolled edge carries round to the back, and for an oval
//                   the drawing's size as { w, h } and its drawn rim as { cx, cy, rx, ry }, both in
//                   the drawing's units (a round face fills its square drawing)
//   evidence        short strings: what the recipe rests on
//   note            optional: the one line shown under the 3D view, in place of the usual one

export const KINDS = ['printed-button']
export const SHAPES = ['round', 'oval']
export const FINISHES = ['printed', 'celluloid']
export const DOME_MAX = 0.15
export const ASPECT_MAX = 2

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
  if (!SHAPES.includes(recipe.shape ?? 'round')) problems.push(`unknown shape ${recipe.shape}`)
  if (!(recipe.diameterMm > 0 && recipe.diameterMm < 200)) problems.push('diameterMm out of range')
  if (recipe.shape === 'oval') {
    if (!(recipe.aspect > 1 && recipe.aspect <= ASPECT_MAX)) problems.push('aspect out of range')
    const { rim, view } = recipe.face ?? {}
    if (!(view?.w > 0 && view?.h > 0)) problems.push('face view')
    if (!rim || !['cx', 'cy', 'rx', 'ry'].every((key) => rim[key] > 0)) problems.push('face rim')
    else if (view && (rim.cx + rim.rx > view.w + 1e-9 || rim.cy + rim.ry > view.h + 1e-9 || rim.cx < rim.rx || rim.cy < rim.ry)) problems.push('face rim outside the drawing')
    else if (Math.abs(rim.rx / rim.ry - recipe.aspect) > 0.01) problems.push('aspect is not the drawn rim\'s')
  } else if (recipe.aspect !== undefined) problems.push('aspect on a round button')
  if (!FINISHES.includes(recipe.finish ?? 'printed')) problems.push(`unknown finish ${recipe.finish}`)
  if (!['measured', 'illustrative'].includes(recipe.diameterStatus)) problems.push('diameterStatus')
  if (!(recipe.dome >= 0 && recipe.dome <= DOME_MAX)) problems.push('dome out of range')
  if (recipe.edge !== 'rolled') problems.push('edge')
  if (recipe.back !== 'tin-back') problems.push('back')
  if (recipe.fitting !== 'safety-pin') problems.push('fitting')
  if (!['seen', 'generic'].includes(recipe.fittingStatus)) problems.push('fittingStatus')
  if (!recipe.face?.svg || !/^#[0-9a-f]{6}$/i.test(recipe.face.background ?? '')) problems.push('face')
  if (!Array.isArray(recipe.evidence) || !recipe.evidence.length || recipe.evidence.some((line) => typeof line !== 'string' || !line.trim())) problems.push('evidence')
  if (recipe.note !== undefined && (typeof recipe.note !== 'string' || !recipe.note.trim())) problems.push('note')
  return problems
}

const inchWords = (mm) => {
  const eighths = Math.round((mm / 25.4) * 8)
  const whole = Math.floor(eighths / 8)
  const fraction = { 0: '', 1: '⅛', 2: '¼', 3: '⅜', 4: '½', 5: '⅝', 6: '¾', 7: '⅞' }[eighths % 8]
  return `${whole || ''}${fraction || (whole ? '' : '0')}`
}

/** An oval's width in whole millimetres; a round button's diameter. */
export const widthMm = ({ shape, diameterMm, aspect }) => (shape === 'oval' ? Math.round(diameterMm * aspect) : diameterMm)

/**
 * A recipe's size, worded for the page: "38 mm (1½ in), illustrative", or for an oval, width by
 * height: "70 × 42 mm (2¾ × 1⅝ in), illustrative".
 */
export const diameterWords = (recipe) => {
  const { diameterMm, diameterStatus } = recipe
  const tail = diameterStatus === 'illustrative' ? ', illustrative' : ''
  if (recipe.shape === 'oval') {
    const width = widthMm(recipe)
    return `${width} × ${diameterMm} mm (${inchWords(width)} × ${inchWords(diameterMm)} in)${tail}`
  }
  return `${diameterMm} mm (${inchWords(diameterMm)} in)${tail}`
}
