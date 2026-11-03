// Story mode: the poster told as one scrolling column of chapters, one per part, with the drawing
// following the reading. Scroll and the chapter that crosses the reading line becomes the open
// part, so the stage glides onto it and lights it; step to a part any other way (the dock, the
// arrow keys, a click on the drawing, the tour) and the column scrolls to its chapter.
//
// A poster opts in by giving its parts a `story`: a list of paragraphs. The chapters are those
// parts, in the poster's order.

import { useEffect, useLayoutEffect, useRef } from 'react'

// Where a chapter takes over, as a share of the column's height from its top.
const READING_LINE = 0.38
// How long a scroll the column makes itself is left alone, if the browser never says it ended.
const SETTLE_MS = 1400

/**
 * @param {object} props
 * @param {string[]} props.chapters  The part ids that have a story, in order.
 * @param {object} props.parts       The poster's parts.
 * @param {string} props.current     The open part.
 * @param {Function} props.onChapter Called with a part id when reading reaches its chapter.
 * @param {Function} props.onDetails Called with a part id to open its full panel instead.
 * @param {Function} props.onLeave   Leaves story mode.
 * @param {string} props.title       The poster's title.
 */
export function StoryRail({ chapters, parts, current, onChapter, onDetails, onLeave, title }) {
  const root = useRef(null)
  const shown = useRef(null)
  const quietUntil = useRef(0)
  const onChapterRef = useRef(onChapter)
  onChapterRef.current = onChapter
  const scroller = () => root.current?.closest('.pv-panel')
  const active = chapters.includes(current) ? current : chapters[0]

  // The column's height sets each chapter's room and the run-out after the last one, so that every
  // chapter, the last included, can be read at the reading line.
  useLayoutEffect(() => {
    const el = scroller()
    if (!el) return undefined
    const measure = () => root.current?.style.setProperty('--pv-rail-h', `${el.clientHeight}px`)
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  // Reading → part.
  useEffect(() => {
    const el = scroller()
    if (!el) return undefined
    let frame = 0
    const read = () => {
      frame = 0
      if (performance.now() < quietUntil.current) return
      const line = el.getBoundingClientRect().top + el.clientHeight * READING_LINE
      let reached = chapters[0]
      for (const chapter of root.current.querySelectorAll('[data-chapter]')) {
        if (chapter.getBoundingClientRect().top <= line) reached = chapter.dataset.chapter
      }
      if (reached !== shown.current) {
        shown.current = reached
        onChapterRef.current(reached)
      }
    }
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(read) }
    const onEnd = () => { quietUntil.current = 0 }
    el.addEventListener('scroll', onScroll, { passive: true })
    el.addEventListener('scrollend', onEnd)
    return () => {
      el.removeEventListener('scroll', onScroll)
      el.removeEventListener('scrollend', onEnd)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [chapters])

  // Part → reading: bring its chapter to the reading line, unless reading put it there.
  useLayoutEffect(() => {
    const el = scroller()
    const chapter = root.current?.querySelector(`[data-chapter="${active}"]`)
    if (!el || !chapter) return
    const first = shown.current === null
    if (active === shown.current) return undefined
    const top = el.scrollTop + chapter.getBoundingClientRect().top - el.getBoundingClientRect().top - el.clientHeight * READING_LINE * 0.35
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
    quietUntil.current = performance.now() + SETTLE_MS
    if (first) {
      // The panel puts its new contents back at the top once they are in, after this has run; the
      // first chapter is found on the frame after that.
      const frame = requestAnimationFrame(() => {
        shown.current = active
        el.scrollTo({ top: Math.max(0, top) })
        quietUntil.current = performance.now() + 150
      })
      return () => cancelAnimationFrame(frame)
    }
    shown.current = active
    el.scrollTo({ top: Math.max(0, top), behavior: reduced ? 'auto' : 'smooth' })
    return undefined
  }, [active])

  return (
    <div className="pv-story" ref={root}>
      <p className="pv-eyebrow">Story · {chapters.filter((id) => id !== 'overview').length} parts</p>
      <p className="pv-story-hint">Scroll to read {title} from top to bottom; the poster follows.</p>
      <ol className="pv-story-chapters">
        {chapters.map((id, i) => {
          const { panel, story, label } = parts[id]
          return (
            <li key={id} data-chapter={id} className={'pv-story-chapter' + (id === active ? ' pv-story-active' : '')} aria-current={id === active ? 'step' : undefined}>
              {/* Numbered as the dock numbers the parts: the whole poster comes first, uncounted. */}
              <p className="pv-eyebrow">{id === 'overview' ? 'The poster' : `${String(i + (chapters[0] === 'overview' ? 0 : 1)).padStart(2, '0')} · ${label}`}</p>
              <h2>{panel.heading}{panel.em && <>, <em>{panel.em}</em></>}</h2>
              {story.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
              {id !== 'overview' && (
                <button type="button" className="pv-story-more" onClick={() => onDetails(id)}>
                  About this part <span aria-hidden="true">→</span>
                </button>
              )}
            </li>
          )
        })}
      </ol>
      <div className="pv-story-end">
        <p className="pv-muted">The end of the story.</p>
        <div className="pv-row">
          <button type="button" className="pv-ghost" onClick={() => onChapterRef.current(chapters[0])}>Back to the top</button>
          <button type="button" className="pv-ghost pv-solid" onClick={onLeave}>Leave the story</button>
        </div>
      </div>
    </div>
  )
}
