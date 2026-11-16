// Which body a finger meant.
//
// On a phone the diagram is some 360 pixels across and holds a hundred bodies, so each is drawn
// about as large as a fingertip is precise, and its neighbours start where it ends. A tap is taken
// for the body whose centre it landed nearest, if that is within reach; a tap out in the open is
// still a tap on the background.

/** How far from a body's centre, in CSS pixels, a tap still counts as a tap on it. */
export const TAP_REACH = 26

/**
 * The id of the candidate nearest `point`, or null if none is within `reach`.
 * @param {{x: number, y: number}} point
 * @param {Array<{id: string, x: number, y: number}>} candidates  Centres, in the same units.
 */
export const nearestWithin = (point, candidates, reach = TAP_REACH) => {
  let best = null
  let bestDistance = reach
  for (const candidate of candidates) {
    const distance = Math.hypot(candidate.x - point.x, candidate.y - point.y)
    // Ties go to the first, so the answer does not depend on float noise between equal distances.
    if (distance < bestDistance || (distance === bestDistance && best === null)) {
      best = candidate.id
      bestDistance = distance
    }
  }
  return best
}
