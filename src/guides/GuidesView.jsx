// Visual guides: brandkit's manual library, showing its BC pack, with this site's links.
//
// The place is in the address (`?view=guides&guide=sign&page=S05`) so a page can be linked to;
// the library keeps that format.

import { ManualLibrary } from 'brandkit/manuals'
import { SiteLink } from '../site/navigation.jsx'
import { GUIDE_BOOKS, GUIDE_FAMILIES, GUIDE_FOOTNOTE, pageUrl } from './guides.js'
import './guides.css'
import parkSymbols from '../signs/parks/proposed-park-symbols.svg?url'

const BASE = import.meta.env.BASE_URL
// The site's own guide pages are drawings under src/, each imported here for its URL and used as
// both the page and its thumbnail (the library would otherwise look for brandkit's files).
const ART = { 'signs/parks/proposed-park-symbols.svg': parkSymbols }
const BOOKS = GUIDE_BOOKS.map((book) => book.pages.some((page) => page.art)
  ? { ...book, pages: book.pages.map((page) => page.art ? { ...page, src: ART[page.art], thumb: ART[page.art] } : page) }
  : book)
const urlOf = (book, page, ext) => pageUrl(BASE, book.id, page.id, ext)
const URL_STATE = { set: { view: 'guides' }, book: 'guide', page: 'page' }
const renderLink = (link) => <SiteLink to={link.to}>{link.label} <span aria-hidden="true">→</span></SiteLink>

export const GuidesView = () => (
  <ManualLibrary
    books={BOOKS}
    families={GUIDE_FAMILIES}
    pageUrl={urlOf}
    urlState={URL_STATE}
    renderLink={renderLink}
    // The heading names the way back from a book; on the index the site's own header already says
    // Visual Guides, so the index opens straight on the families (guides.css).
    heading="Visual guides"
    footnote={GUIDE_FOOTNOTE}
    label="Visual guides"
  />
)
