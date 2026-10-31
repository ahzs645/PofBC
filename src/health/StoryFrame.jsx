import React, { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { StorySidecar } from '@pgmaps/geo-toolkit/stories/components/StorySidecar'
import { StoryChapterNavigation } from '@pgmaps/geo-toolkit/stories/components/StoryChapterNavigation'
import { WorkspaceProvider } from '@pgmaps/geo-toolkit/workspace/workspace-context'
import '@pgmaps/geo-toolkit/stories/styles.css'

// Host adaptations only: the pinned PGMaps toolkit owns the sidecar, reading-line
// selection, responsive media placement, expansion and chapter-navigation UI.
const frameStyles = `
.health-story-frame { height: min(920px, calc(100dvh - 100px)); min-height: 440px; width: 100%; border: 1px solid #ccd3da; border-radius: 12px; overflow: hidden; }
/* Expanded media must be fixed to the viewport, outside size containment. */
.health-story-frame:has(.editorial-expandable.is-expanded) > .geo-toolkit { container-type: normal !important; }
.health-story-frame .health-story-reader { height: 100%; font-family: inherit; font-size: 16px; --editorial-bg: #fbfaf7; --editorial-fg: #182b3a; --editorial-muted: #52616c; --editorial-border: #ccd3da; --editorial-card: #fffefaef; --editorial-surface: #f0f1ed; --editorial-control: #fffefa; }
.health-story-frame .health-story-toolbar { position: sticky; top: 0; z-index: 12; background: var(--editorial-bg); border-bottom: 1px solid var(--editorial-border); }
.health-story-frame .health-story-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; padding: 12px 16px 4px; }
.health-story-frame .health-story-heading strong { font-size: 15px; line-height: 1.35; }
.health-story-frame .health-story-progress { color: var(--editorial-muted); white-space: nowrap; font-size: 12px; }
.health-story-frame .health-story-toolbar .editorial-nav-shell { position: relative; top: auto; height: auto; min-height: 48px; border: 0; }
.health-story-frame .health-story-toolbar .editorial-chapters { min-height: 48px; height: auto; justify-content: flex-start; padding: 0 52px 0 16px; gap: 20px; }
.health-story-frame .health-story-toolbar .editorial-chapters button { min-height: 44px; max-width: 230px; flex: 0 0 auto; white-space: normal; line-height: 1.3; font-size: 13px; padding: 7px 0; }
.health-story-frame .health-story-toolbar .editorial-nav-next { min-height: 44px; }
.health-story-frame .health-story-controls { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 4px 16px 10px; }
.health-story-frame .health-story-controls button { min-height: 42px; padding: 7px 12px; border: 1px solid var(--editorial-border); border-radius: 6px; color: var(--editorial-fg); background: var(--editorial-control); font-size: 13px; }
.health-story-frame .health-story-reading-hint { font-size: 12px; color: var(--editorial-muted); text-align: center; }
.health-story-frame .editorial-immersive { margin: 0; }
.health-story-frame .editorial-slide { padding: 30px 26px; }
.health-story-frame .editorial-immersive.is-docked .editorial-slide,
.health-story-frame .editorial-immersive.is-docked .editorial-slide:first-child { padding: 30px 26px; align-items: flex-start; }
.health-story-frame .editorial-slide-copy { width: 100%; max-width: 100%; }
.health-story-frame .editorial-immersive.is-docked .editorial-slide-copy { margin-top: 0; }
.health-story-frame .editorial-slide-copy > :first-child { margin-top: 0; }
.health-story-frame .editorial-immersive-media { min-width: 0; }
.health-story-frame .editorial-immersive-media > .editorial-expandable { height: 100%; }
.health-story-frame .editorial-expand { min-height: 36px; font-family: inherit; }
.health-story-frame .health-story-empty { padding: 24px; }
/* Keep the measured compact layout when expansion temporarily disables queries. */
.health-story-frame [data-compact="true"] .editorial-nav-shell { padding: 0 32px 0 0; }
.health-story-frame [data-compact="true"] .editorial-nav-next { right: 0; width: 32px; }
.health-story-frame [data-compact="true"] .editorial-immersive { display: block; margin: 0; }
.health-story-frame :where([data-compact="true"]) .editorial-immersive-media { height: 210px; min-height: 210px; width: 100%; }
.health-story-frame :where([data-compact="true"]) .editorial-slide { min-height: calc(var(--editorial-viewport, 100dvh) - var(--editorial-top) - 210px); align-items: flex-start; }
.health-story-frame [data-compact="true"] .editorial-immersive.is-docked .editorial-slide { padding: 24px 18px; }
.health-story-frame [data-compact="true"] .editorial-slide-copy { margin: 0; }
@media (max-width: 700px) {
  .health-story-frame { border-radius: 8px; min-height: 420px; height: calc(100dvh - 76px); }
  .health-story-frame .health-story-heading { padding: 10px 12px 0; }
  .health-story-frame .health-story-controls { padding: 2px 12px 8px; gap: 6px; }
  .health-story-frame .health-story-controls button { min-height: 44px; padding: 7px 10px; }
  .health-story-frame .health-story-reading-hint { max-width: 150px; font-size: 11px; }
  .health-story-frame .editorial-slide { padding: 24px 18px; }
}
`

// The shared toolkit handles Escape and restoring focus. Its Tab selector omits
// selects and includes disabled controls, so the host guards this dialog's edges.
function guardExpandedMediaFocus(event) {
  if (event.key !== 'Tab' || event.altKey || event.ctrlKey || event.metaKey) return
  const dialog = event.currentTarget.querySelector('.editorial-expandable.is-expanded[role="dialog"]')
  if (!dialog) return
  const controls = Array.from(dialog.querySelectorAll('button, a[href], input, select, textarea, summary, [tabindex], [contenteditable="true"]'))
    .filter((element) => element.tabIndex >= 0 && !element.matches(':disabled')
      && !element.closest('[hidden], [inert], [aria-hidden="true"]')
      && element.getClientRects().length && getComputedStyle(element).visibility === 'visible')
    .sort((a, b) => (a.tabIndex || Infinity) - (b.tabIndex || Infinity))
  // Prevent the toolkit's window listener from applying its narrower Tab loop.
  // Default browser traversal still handles all controls between these edges.
  event.stopPropagation()
  const active = dialog.ownerDocument.activeElement
  const first = controls[0]
  const last = controls[controls.length - 1]
  if (!first) { event.preventDefault(); return }
  if (!dialog.contains(active) || (event.shiftKey ? active === first : active === last)) {
    event.preventDefault()
    const next = event.shiftKey ? last : first
    next.focus({ preventScroll: true })
  }
}

/**
 * A PGMaps sidecar inside a PofBC reading frame.
 *
 * slides: [{ id, label?, title?, content: ReactNode, media: ReactNode,
 *            imageUrl?, preload? }]
 * onChapterChange(id, index) observes the actual toolkit reading state. The
 * initialChapterId is applied once. Changing requestedChapterId explicitly
 * requests navigation, without coupling passive scroll reports to navigation.
 * Increment navigationRequestKey to request the same chapter again after the
 * reader has scrolled elsewhere. Keep it unchanged for ordinary reading updates.
 * Chapter buttons and Previous/Next remain available on phones and with keyboard input. The host supplies map/media and
 * content; this wrapper neither fetches data nor invents boundary equivalence.
 */
export function StoryFrame({
  id,
  title = 'Health geography story',
  slides = [],
  initialChapterId,
  requestedChapterId,
  navigationRequestKey = 0,
  onChapterChange,
  variant = 'docked',
  side = 'left',
  width = 'medium',
  className = '',
  style,
}) {
  const instanceId = useId()
  const frameId = id || `health-story-${instanceId.replace(/[^a-zA-Z0-9_-]/g, '')}`
  const reader = useRef(null)
  const toolbar = useRef(null)
  const observerHost = useRef(null)
  const callback = useRef(onChapterChange)
  const navigation = useRef(null)
  const notifyReadingState = useRef(null)
  const initialApplied = useRef(false)
  const initialTarget = useRef(null)
  const [activeIndex, setActiveIndex] = useState(0)
  const definitions = useMemo(() => slides.map((slide, index) => ({
    ...slide,
    sourceId: String(slide.id || `chapter-${index + 1}`),
    id: `${frameId}-${String(slide.id || `chapter-${index + 1}`)}`,
    label: slide.label || slide.title || `Chapter ${index + 1}`,
  })), [slides, frameId])
  const chapterKey = definitions.map((slide) => slide.id).join('|')
  const boundedIndex = Math.min(activeIndex, Math.max(0, definitions.length - 1))

  useLayoutEffect(() => { callback.current = onChapterChange }, [onChapterChange])

  // The toolkit measures this scroll root rather than assuming a full viewport.
  // Its mobile sticky-map offsets must include PofBC's two navigation rows.
  useLayoutEffect(() => {
    const root = reader.current
    const navigation = toolbar.current
    if (!root || !navigation) return undefined
    const measure = () => {
      root.dataset.compact = String(root.getBoundingClientRect().width <= 700)
      root.style.setProperty('--editorial-viewport', `${root.clientHeight}px`)
      root.style.setProperty('--editorial-top', `${navigation.getBoundingClientRect().height}px`)
      root.style.setProperty('--editorial-nav', `${navigation.getBoundingClientRect().height}px`)
    }
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(root)
    observer.observe(navigation)
    return () => observer.disconnect()
  }, [chapterKey])

  // StorySidecar publishes its real active slide on the host element. Observing
  // that stable public DOM attribute avoids a competing scroll-selection model.
  useEffect(() => {
    const sidecar = observerHost.current?.querySelector('[data-active-slide]')
    if (!sidecar) return undefined
    let previous = -1
    const readActive = () => {
      const value = Number(sidecar.getAttribute('data-active-slide'))
      if (!Number.isInteger(value) || value < 0 || value >= definitions.length) return
      setActiveIndex(value)
      // The toolkit first mounts at zero. Do not replace a deep-linked URL with
      // chapter zero while the initial, immediate navigation is still pending.
      if (!initialApplied.current) return
      if (initialTarget.current && definitions[value].sourceId !== initialTarget.current) return
      initialTarget.current = null
      if (value === previous) return
      previous = value
      callback.current?.(definitions[value].sourceId, value)
    }
    notifyReadingState.current = readActive
    const observer = new MutationObserver(readActive)
    observer.observe(sidecar, { attributes: true, attributeFilter: ['data-active-slide'] })
    readActive()
    return () => {
      observer.disconnect()
      if (notifyReadingState.current === readActive) notifyReadingState.current = null
    }
  }, [chapterKey])

  // Keep the selected chapter visible in the horizontal rail without moving
  // keyboard focus or scrolling the containing page during passive reading.
  useEffect(() => {
    const rail = toolbar.current?.querySelector('.editorial-chapters')
    const current = rail?.querySelector('[aria-current="location"]')
    if (!rail || !current) return
    const bounds = rail.getBoundingClientRect()
    const selected = current.getBoundingClientRect()
    if (selected.left < bounds.left + 12) rail.scrollLeft += selected.left - bounds.left - 12
    else if (selected.right > bounds.right - 50) rail.scrollLeft += selected.right - bounds.right + 50
  }, [boundedIndex, chapterKey])

  const goToChapter = useCallback((index, behavior) => {
    const root = reader.current
    const slide = definitions[index]
    if (!root || !slide) return
    const section = root.ownerDocument.getElementById(slide.id)
    if (!section || !root.contains(section)) return
    const mobile = root.getBoundingClientRect().width <= 700
    const mediaHeight = mobile
      ? observerHost.current?.querySelector('.editorial-immersive-media')?.getBoundingClientRect().height || 210
      : 0
    const navigationHeight = toolbar.current?.getBoundingClientRect().height || 0
    const offset = navigationHeight + mediaHeight + 16
    const top = Math.max(0, root.scrollTop + section.getBoundingClientRect().top - root.getBoundingClientRect().top - offset)
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    root.scrollTo({ top, behavior: behavior || (reducedMotion ? 'auto' : 'smooth') })
  }, [definitions])

  useLayoutEffect(() => { navigation.current = goToChapter }, [goToChapter])

  // An external "Compare this area" button can request a chapter. The request
  // is separate from onChapterChange so reading never triggers a scroll loop.
  useEffect(() => {
    if (!requestedChapterId || !definitions.length) return undefined
    const index = definitions.findIndex((slide) => slide.sourceId === requestedChapterId)
    if (index < 0) return undefined
    const frame = requestAnimationFrame(() => {
      const firstNavigation = !initialApplied.current
      if (firstNavigation) initialTarget.current = definitions[index].sourceId
      initialApplied.current = true
      navigation.current?.(index, firstNavigation ? 'auto' : undefined)
      notifyReadingState.current?.()
    })
    return () => cancelAnimationFrame(frame)
  }, [requestedChapterId, navigationRequestKey, chapterKey])

  useEffect(() => {
    if (initialApplied.current || requestedChapterId || !definitions.length) return undefined
    const index = definitions.findIndex((slide) => slide.sourceId === initialChapterId)
    if (index <= 0) {
      initialApplied.current = true
      notifyReadingState.current?.()
      return undefined
    }
    const frame = requestAnimationFrame(() => {
      initialTarget.current = definitions[index].sourceId
      initialApplied.current = true
      navigation.current?.(index, 'auto')
      notifyReadingState.current?.()
    })
    return () => cancelAnimationFrame(frame)
  }, [initialChapterId, requestedChapterId, chapterKey])

  return (
    <div className={`health-story-frame ${className}`.trim()} style={style} data-testid="health-story-frame" onKeyDownCapture={guardExpandedMediaFocus}>
      <style>{frameStyles}</style>
      <WorkspaceProvider responsive="container" breakpoint={700} theme="light">
        <div ref={reader} className="editorial-story health-story-reader" aria-label={title} role="region" tabIndex={0}>
          <header ref={toolbar} className="health-story-toolbar">
            <div className="health-story-heading">
              <strong>{title}</strong>
              <span className="health-story-progress" aria-live="polite" aria-atomic="true">
                {definitions.length ? `${boundedIndex + 1} of ${definitions.length}` : 'No chapters'}
              </span>
            </div>
            <StoryChapterNavigation
              chapters={definitions.map((slide) => ({ id: slide.id, label: slide.label }))}
              active={definitions[boundedIndex]?.id || ''}
              onSelect={(chapterId) => goToChapter(definitions.findIndex((slide) => slide.id === chapterId))}
            />
            <nav className="health-story-controls" aria-label="Move through story">
              <button type="button" aria-label="Previous chapter" disabled={boundedIndex === 0} onClick={() => goToChapter(boundedIndex - 1)}>
                ← Previous
              </button>
              <span className="health-story-reading-hint">Scroll the story or choose a chapter.</span>
              <button type="button" aria-label="Next chapter" disabled={boundedIndex >= definitions.length - 1} onClick={() => goToChapter(boundedIndex + 1)}>
                Next →
              </button>
            </nav>
          </header>
          <div ref={observerHost}>
            {definitions.length ? (
              <StorySidecar id={`${frameId}-sidecar`} slides={definitions} scrollRoot={reader} variant={variant} side={side} width={width} />
            ) : <p className="health-story-empty">No story chapters are available.</p>}
          </div>
        </div>
      </WorkspaceProvider>
    </div>
  )
}

export default StoryFrame
