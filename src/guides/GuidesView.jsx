// Visual guides: the families of manuals, a book's pages as a grid, and one page at a time.
//
// The place is in the address — `?view=guides&guide=sign&page=S05` — so a page can be linked to.
// Pages are shown as images of their own SVG files: each is self-contained (its fonts embedded),
// and nothing in one can reach the rest of the page.

import { useCallback, useEffect, useRef, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { GUIDE_FAMILIES, familyOf, findBook, pageUrl } from './guides.js'
import './guides.css'

const BASE = import.meta.env.BASE_URL
const ZOOMS = [
  { id: 'fit', label: 'Fit', scale: 1 },
  { id: 'large', label: '150%', scale: 1.5 },
  { id: 'detail', label: '250%', scale: 2.5 }
]

const readPlace = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const book = findBook(params.get('guide'))
  const page = book?.pages.find((entry) => entry.id === params.get('page')) ?? null
  return { book: book?.id ?? null, page: page?.id ?? null }
}

const writePlace = ({ book, page }) => {
  if (!globalThis.history?.replaceState) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'guides')
  for (const [key, value] of [['guide', book], ['page', page]]) {
    if (value) url.searchParams.set(key, value)
    else url.searchParams.delete(key)
  }
  globalThis.history.replaceState(null, '', url)
}

/** The page's own number as printed ("Page 4"), or what it is when it has none ("Front cover"). */
const pageLabel = ({ printed }) => {
  if (!printed) return ''
  if (/^\d+$/.test(printed)) return `Page ${printed}`
  return printed[0].toUpperCase() + printed.slice(1)
}

const Thumb = ({ book, page, onOpen, buttonRef, shape }) => (
  <button type="button" className="guides__thumb" onClick={onOpen} ref={buttonRef}>
    <span className="guides__thumb-page" style={{ aspectRatio: shape }}>
      <img src={pageUrl(BASE, book.id, page.id, 'webp')} alt="" loading="lazy" width="320" height={Math.round(320 * page.height / page.width)} />
    </span>
    <span className="guides__thumb-title">{page.title}</span>
    {pageLabel(page) && pageLabel(page).toLowerCase() !== page.title.toLowerCase() && <span className="guides__thumb-meta">{pageLabel(page)}</span>}
  </button>
)

const Families = ({ open }) => (
  <>
    <div className="guides__intro">
      <h2>Visual guides</h2>
      <p>Identity manuals, rebuilt page by page as drawings.</p>
    </div>
    {GUIDE_FAMILIES.map((family) => (
      <section key={family.id} className="guides__family" aria-labelledby={`family-${family.id}`}>
        <header className="guides__family-head">
          <h3 id={`family-${family.id}`}>{family.title}</h3>
          <p>{family.kind}</p>
        </header>
        <div className="guides__books">
          {family.books.map(findBook).map((book) => (
            <button key={book.id} type="button" className="guides__book" onClick={() => open({ book: book.id, page: null })}>
              <span className="guides__thumb-page">
                <img src={pageUrl(BASE, book.id, book.pages[0].id, 'webp')} alt="" loading="lazy" />
              </span>
              <span className="guides__book-title">{book.title}</span>
              <span className="guides__thumb-meta">{book.edition} · {book.pages.length} pages</span>
            </button>
          ))}
        </div>
        {family.links.length > 0 && (
          <ul className="guides__links">
            {family.links.map((link) => <li key={link.label}><SiteLink to={link.to}>{link.label} <span aria-hidden="true">→</span></SiteLink></li>)}
          </ul>
        )}
      </section>
    ))}
    <p className="guides__footnote">Reconstructions, not the original printings. The type is set in open-licence stand-ins, and the originals’ photographs and signatures are left out.</p>
  </>
)

/** The shape most of a book's pages share, as an aspect ratio, so its grid of pages is even. */
const usualShape = (pages) => {
  const counts = new Map()
  for (const { width, height } of pages) counts.set(`${width} / ${height}`, (counts.get(`${width} / ${height}`) ?? 0) + 1)
  return [...counts].sort((a, b) => b[1] - a[1])[0]?.[0]
}

const Book = ({ book, open, focusPage }) => {
  const family = familyOf(book.id)
  const shape = usualShape(book.pages)
  const thumbs = useRef({})
  useEffect(() => { if (focusPage) thumbs.current[focusPage]?.focus() }, [focusPage])
  return (
    <>
      <div className="guides__intro">
        <button type="button" className="guides__back" onClick={() => open({ book: null, page: null })}>← Visual guides</button>
        <h2>{book.title}</h2>
        <p>{family.title} · {book.edition} · {book.pages.length} pages</p>
      </div>
      <div className="guides__pages">
        {book.pages.map((page) => (
          <Thumb key={page.id} book={book} page={page} shape={shape} onOpen={() => open({ book: book.id, page: page.id })} buttonRef={(element) => { thumbs.current[page.id] = element }} />
        ))}
      </div>
    </>
  )
}

const Page = ({ book, page, open }) => {
  const index = book.pages.findIndex((entry) => entry.id === page.id)
  const previous = book.pages[index - 1]
  const next = book.pages[index + 1]
  const [zoom, setZoom] = useState('fit')
  const [loaded, setLoaded] = useState(false)
  const title = useRef(null)
  const scale = ZOOMS.find((entry) => entry.id === zoom).scale
  useEffect(() => { setLoaded(false); title.current?.focus() }, [page.id])

  useEffect(() => {
    const onKey = (event) => {
      if (event.target.matches?.('input, textarea, select, [contenteditable]') || event.metaKey || event.ctrlKey || event.altKey) return
      if (event.key === 'ArrowLeft' && previous) open({ book: book.id, page: previous.id })
      else if (event.key === 'ArrowRight' && next) open({ book: book.id, page: next.id })
      else if (event.key === 'Escape') open({ book: book.id, page: null, from: page.id })
      else return
      event.preventDefault()
    }
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  }, [book.id, page.id, previous, next, open])

  return (
    <>
      <div className="guides__intro guides__page-head">
        <button type="button" className="guides__back" onClick={() => open({ book: book.id, page: null, from: page.id })}>← {book.title}</button>
        <h2 ref={title} tabIndex={-1}>{page.title}</h2>
        <p>{[pageLabel(page), `${index + 1} of ${book.pages.length}`].filter(Boolean).join(' · ')}</p>
        <div className="guides__toolbar">
          <div className="guides__step">
            <button type="button" disabled={!previous} onClick={() => open({ book: book.id, page: previous.id })} aria-label={previous ? `Previous page: ${previous.title}` : 'Previous page'}>←</button>
            <button type="button" disabled={!next} onClick={() => open({ book: book.id, page: next.id })} aria-label={next ? `Next page: ${next.title}` : 'Next page'}>→</button>
          </div>
          <div className="guides__zoom" role="group" aria-label="Zoom">
            {ZOOMS.map((entry) => <button key={entry.id} type="button" aria-pressed={zoom === entry.id} onClick={() => setZoom(entry.id)}>{entry.label}</button>)}
          </div>
          <a className="guides__download" href={pageUrl(BASE, book.id, page.id)} download={`${page.id}.svg`} aria-label="Download SVG"><span aria-hidden="true">↓ </span><span className="guides__download-word">Download </span>SVG</a>
        </div>
      </div>
      <div className="guides__viewer" data-zoom={zoom}>
        <img
          key={page.id}
          className="guides__page"
          src={pageUrl(BASE, book.id, page.id)}
          alt={`${book.title}: ${page.title}, rebuilt`}
          width={page.width}
          height={page.height}
          style={{ width: `${scale * 100}%`, aspectRatio: `${page.width} / ${page.height}`, opacity: loaded ? 1 : 0.35 }}
          onLoad={() => setLoaded(true)}
        />
      </div>
      {page.notes.length > 0 && (
        <details className="guides__notes">
          <summary>Reconstruction notes</summary>
          <ul>{page.notes.map((note) => <li key={note}>{note}</li>)}</ul>
        </details>
      )}
    </>
  )
}

export const GuidesView = () => {
  const [place, setPlace] = useState(readPlace)
  const [focusPage, setFocusPage] = useState(null)
  const open = useCallback(({ book, page, from = null }) => {
    const next = { book, page }
    setPlace(next)
    writePlace(next)
    setFocusPage(from)
    globalThis.scrollTo?.({ top: 0 })
  }, [])
  const book = place.book ? findBook(place.book) : null
  const page = book && place.page ? book.pages.find((entry) => entry.id === place.page) : null

  return (
    <section className="guides" aria-label="Visual guides">
      {page ? <Page book={book} page={page} open={open} />
        : book ? <Book book={book} open={open} focusPage={focusPage} />
          : <Families open={open} />}
    </section>
  )
}
