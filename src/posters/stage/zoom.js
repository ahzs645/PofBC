// Fitting a box into the stage, and tweening the viewBox there.
//
// CSS cannot transition an SVG viewBox, so the zoom is a small hand-rolled tween: one object of
// four numbers eased between two states on requestAnimationFrame.

/** The viewBox that shows `box` with `pad` (a fraction of its size) around it, at the stage's aspect. */
export const fit = (box, pad, rect) => {
  const aspect = rect.width / Math.max(rect.height, 1)
  let w = box.w * (1 + 2 * pad)
  let h = box.h * (1 + 2 * pad)
  if (w / h < aspect) w = h * aspect
  else h = w / aspect
  return { x: box.x + box.w / 2 - w / 2, y: box.y + box.h / 2 - h / 2, w, h }
}

const easeInOutQuint = (p) => (p < 0.5 ? 16 * p ** 5 : 1 - (-2 * p + 2) ** 5 / 2)

/**
 * Tweens `from` to `to`, calling onUpdate with a fresh object each frame. Returns a stop function.
 * A zero duration jumps straight to the end.
 */
export const tween = (from, to, { duration = 900, onUpdate, onComplete } = {}) => {
  if (duration <= 0) {
    onUpdate?.({ ...to })
    onComplete?.()
    return () => {}
  }
  const start = performance.now()
  let frame = 0
  const step = (now) => {
    const p = Math.min(1, (now - start) / duration)
    const e = easeInOutQuint(p)
    onUpdate?.({
      x: from.x + (to.x - from.x) * e,
      y: from.y + (to.y - from.y) * e,
      w: from.w + (to.w - from.w) * e,
      h: from.h + (to.h - from.h) * e
    })
    if (p < 1) frame = requestAnimationFrame(step)
    else onComplete?.()
  }
  frame = requestAnimationFrame(step)
  return () => cancelAnimationFrame(frame)
}

/** The union of the bounding boxes of some SVG elements, in their parent's units. */
export const unionBox = (elements) => {
  const boxes = elements.map((el) => el.getBBox())
  const x = Math.min(...boxes.map((b) => b.x))
  const y = Math.min(...boxes.map((b) => b.y))
  const x2 = Math.max(...boxes.map((b) => b.x + b.width))
  const y2 = Math.max(...boxes.map((b) => b.y + b.height))
  return { x, y, w: x2 - x, h: y2 - y }
}
