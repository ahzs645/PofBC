// Visual guides: brandkit's manual library, showing its BC pack, with this site's links.
//
// The place is in the address (`?view=guides&guide=sign&page=S05`) so a page can be linked to;
// the library keeps that format.

import { ManualLibrary } from 'brandkit/manuals'
import { SiteLink } from '../site/navigation.jsx'
import { GUIDE_BOOKS, GUIDE_FAMILIES, GUIDE_FOOTNOTE, pageUrl } from './guides.js'

const BASE = import.meta.env.BASE_URL
const urlOf = (book, page, ext) => pageUrl(BASE, book.id, page.id, ext)
const URL_STATE = { set: { view: 'guides' }, book: 'guide', page: 'page' }
const renderLink = (link) => <SiteLink to={link.to}>{link.label} <span aria-hidden="true">→</span></SiteLink>

export const GuidesView = () => (
  <ManualLibrary
    books={GUIDE_BOOKS}
    families={GUIDE_FAMILIES}
    pageUrl={urlOf}
    urlState={URL_STATE}
    renderLink={renderLink}
    heading="Visual guides"
    intro="Identity manuals, rebuilt page by page as drawings."
    footnote={GUIDE_FOOTNOTE}
    label="Visual guides"
  />
)
