// A frame meter for the stage's zoom, for checking on a real device whether a drawing glides
// smoothly. Off unless the address has `&frames=1`; then every zoom reports, in a small box in the
// corner, how many frames it drew and how long they took. At 60 frames a second a frame has 16.7
// ms; a zoom whose frames mostly take 30 ms or more, or that has several over 50 ms, will look
// jerky.

const on = () => new URLSearchParams(globalThis.location?.search ?? '').get('frames') === '1'

let box = null
const show = (text) => {
  if (!box) {
    box = document.createElement('output')
    box.setAttribute('aria-live', 'polite')
    Object.assign(box.style, {
      position: 'fixed', left: '8px', bottom: '72px', zIndex: '100', padding: '6px 9px',
      font: '12px/1.4 ui-monospace, monospace', color: '#ecebe4', background: 'rgba(0,0,0,0.78)',
      borderRadius: '8px', pointerEvents: 'none', whiteSpace: 'pre'
    })
    document.body.appendChild(box)
  }
  box.textContent = text
}

/** Starts timing one zoom. Call `frame()` on each of its frames and `done()` when it ends. */
export const meterZoom = () => {
  if (!on()) return { frame: () => {}, done: () => {} }
  const gaps = []
  let last = performance.now()
  return {
    frame: () => {
      const now = performance.now()
      gaps.push(now - last)
      last = now
    },
    done: () => {
      if (gaps.length < 2) return
      const sorted = [...gaps].sort((a, b) => a - b)
      const median = sorted[Math.floor(sorted.length / 2)]
      const slowest = sorted.at(-1)
      const long = gaps.filter((g) => g > 50).length
      show(`last zoom: ${gaps.length} frames\nmedian ${median.toFixed(0)} ms · slowest ${slowest.toFixed(0)} ms\n${long} over 50 ms · ≈${Math.round(1000 / median)} fps`)
    }
  }
}
