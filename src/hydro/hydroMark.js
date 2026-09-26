// The parts of the historical BC Hydro signature that are drawn rather than typeset.
//
// The symbol is a ring around a stylized H — two four-pointed stars, the upper half green and the
// lower blue — and for Gas Operations a flame that encloses the same H. Both are reconstructed from
// the manual's printed samples, in a 1000-unit square whose ring touches all four sides; the flame
// rises 720 units above it.
//
// The wordmark is not simply "B.C.Hydro" set in a serif. Its letters were fitted one at a time over
// the printed signature, each with a position and a scale of its own, because the original was
// lettered with the tight, optically adjusted fit no typeface's own spacing reproduces. Those fits
// are kept here; any other wording is set in the serif at the wordmark's size instead.

/** The upper star of the H, in the symbol's 1000-unit square. */
export const STAR = 'M 130 500 L 285 477 C 325 471 340 455 347 411 L 390 138 L 433 411 C 441 459 448 479 500 479 ' +
  'C 552 479 559 459 567 411 L 610 138 L 653 411 C 660 455 675 471 715 477 L 870 500 Z'

/**
 * Both stars as one silhouette. Drawn under the upper star, so the two halves meet without the
 * hairline of background an antialiased seam would leave.
 */
export const FULL_STAR = STAR.replace(/Z\s*$/, '') +
  ' L 715 523 C 675 529 660 545 653 589 L 610 862 L 567 589 C 559 541 552 521 500 521 C 448 521 441 541 433 589 ' +
  'L 390 862 L 347 589 C 340 545 325 529 285 523 L 130 500 Z'

/** The Gas Operations flame, before the ring's counter is cut from it. */
export const FLAME = 'M 475 -720 C 505 -390 244 -52 70 235 C 0 371 0 417 0 500 A 500 500 0 0 0 1000 500 ' +
  'C 1000 145 753 -366 475 -720 Z'

/** How far the flame rises above the ring, as a fraction of the ring's diameter. */
export const FLAME_RISE = 0.72

/** The ring's stroke, in the symbol's units, as fitted to the printed samples. */
export const RING_WEIGHT = 42.29044

/** The wording the fitted wordmark spells. Anything else is typeset. */
export const WORDMARK = 'B.C.Hydro'

/**
 * Each letter of the wordmark as fitted: its pen position and baseline in the fitting's units, and
 * the scale that brings a 1000-unit letter to the printed one.
 */
export const WORDMARK_LETTERS = [
  { char: 'B', x: -4.043403, y: 171, sx: 0.23784722, sy: 0.25679758 },
  { char: '.', x: 118.972973, y: 167.324324, sx: 0.24324324, sy: 0.24324324 },
  { char: 'C', x: 140.965289, y: 169.489855, sx: 0.25123967, sy: 0.25072464 },
  { char: '.', x: 277.603604, y: 169.225225, sx: 0.23423423, sy: 0.25225225 },
  { char: 'H', x: 321.103953, y: 171, sx: 0.25768668, sy: 0.25679758 },
  { char: 'y', x: 476.659436, y: 160.763473, sx: 0.23861171, sy: 0.23502994 },
  { char: 'd', x: 566.19181, y: 171.518038, sx: 0.25215517, sy: 0.24819625 },
  { char: 'r', x: 677.712121, y: 172, sx: 0.25757576, sy: 0.25652174 },
  { char: 'o', x: 739.70068, y: 172.468085, sx: 0.25170068, sy: 0.25319149 }
]

/** Which letter of the wordmark the cap height is read from: the H. */
export const WORDMARK_CAP_LETTER = 4

/** The fitting's units per symbol diameter: a 200-unit symbol sat beside a 193.6-unit fit. */
export const WORDMARK_FIT = 200 / 193.60049
