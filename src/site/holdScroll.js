// Keeping a control where it is on screen while the page under it changes.
//
// A tab, a segmented control or a filter changes what is below it, and the page grows or shrinks.
// Left alone, the browser keeps the scroll offset, so the control the reader just pressed jumps up
// or down (or off the screen); scrolling to the top instead loses their place altogether, which on
// a phone means scrolling all the way back down. Neither is what a tab should do.
//
// Call holdScroll with the control (or the bar it sits in) just before the change. Two things then
// keep the control under the reader's finger:
//
// - The page may not get shorter for a moment. A section that shows "Loading…" while its data or
//   code arrives would otherwise collapse the page, and the browser would clamp the scroll to the
//   top before the content came back.
// - For a moment after, the page is scrolled by however far the control has moved, as the new
//   content draws and loads in.
//
// Whatever the reader does in the meantime (a scroll, a touch, a key) ends the hold at once.

const frame = (callback) => (globalThis.requestAnimationFrame ? globalThis.requestAnimationFrame(callback) : setTimeout(callback, 16))
const now = () => globalThis.performance?.now?.() ?? Date.now()

// How long to keep the control in place while what is below it draws and loads.
const HOLD_MS = 1500
// How long to wait for a control the change replaces (a section loaded on demand) to appear.
const PATIENCE_MS = 2500
const READER = ['wheel', 'touchstart', 'keydown', 'pointerdown']

// The page's height is pinned while any hold is running, and let go when the last one ends.
let pinned = 0
let pinnedBefore = ''
const pin = () => {
  const root = globalThis.document?.documentElement
  if (!root) return
  if (pinned++ === 0) pinnedBefore = root.style.minHeight
  root.style.minHeight = `${Math.max(root.scrollHeight, parseFloat(root.style.minHeight) || 0)}px`
}
const unpin = () => {
  const root = globalThis.document?.documentElement
  if (!root || pinned === 0) return
  if (--pinned === 0) root.style.minHeight = pinnedBefore
}

// Drawn, not merely in the document: while a section loads, React keeps the old one in the page but
// hidden (display: none), where it would report a top of 0 and send the page to the top.
const shown = (node) => Boolean(node?.isConnected && node.getClientRects().length)

/**
 * @param {Element|null|undefined} element The control, or the bar it sits in.
 * @param {object} [options]
 * @param {() => Element|null|undefined} [options.find] Finds the control after the change, where the
 *   change replaces it with another (a different section drawing its own copy of the same bar).
 *   Waits for it to appear, if it is loaded on demand.
 */
export const holdScroll = (element, { find } = {}) => {
  if (!element?.getBoundingClientRect || !globalThis.scrollBy) return
  const before = element.getBoundingClientRect().top
  const started = now()
  let found = null
  let done = false
  pin()

  const finish = () => {
    if (done) return
    done = true
    READER.forEach((type) => globalThis.removeEventListener?.(type, finish, true))
    unpin()
  }
  // Listened for from the next frame, so the press that made the change does not end the hold.
  frame(() => { if (!done) READER.forEach((type) => globalThis.addEventListener?.(type, finish, { capture: true, passive: true })) })

  const target = () => {
    const replacement = find?.()
    return shown(replacement) ? replacement : shown(element) ? element : null
  }
  const tick = () => {
    if (done) return
    const node = target()
    if (!node) {
      // Gone: with `find`, its replacement may still be loading; without, there is nothing to hold.
      if (find && now() - started < PATIENCE_MS) frame(tick)
      else finish()
      return
    }
    found ??= now()
    // Only where it has come to rest: a section still laying out can draw the control somewhere else
    // for a single frame, and following that would flash the page to the top and back. With the
    // page's height pinned, nothing else moves it while it settles.
    const top = node.getBoundingClientRect().top
    const resting = node === last.node && Math.abs(top - last.top) <= 1
    last = { node, top }
    if (resting && Math.abs(top - before) > 1) {
      globalThis.scrollBy({ top: top - before, behavior: 'instant' })
      last = { node, top: before }
    }
    if (now() - found < HOLD_MS) frame(tick)
    else finish()
  }
  let last = { node: null, top: 0 }
  frame(tick)
}

/** holdScroll for the control an event came from: its nearest tab bar, group or toolbar. */
export const holdScrollFrom = (event) => {
  const target = event?.currentTarget ?? event?.target
  holdScroll(target?.closest?.('[role="tablist"], [role="group"], [role="toolbar"], nav') ?? target)
}
