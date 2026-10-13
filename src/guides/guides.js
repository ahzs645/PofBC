// The visual guides: identity manuals rebuilt page by page as drawings, grouped by whose identity
// they set out. The books and their pages are generated (guidesData.js); which family a book
// belongs to, and where a family links on the site, is set here.

import { GUIDE_BOOKS } from './guidesData.js'

export const GUIDE_FAMILIES = [
  {
    id: 'visual-identity-program',
    title: 'Province of British Columbia',
    kind: 'Visual Identity Program, 1977 to 1982',
    books: ['general', 'reproduction', 'sign', 'vehicle', 'policy-1982'],
    links: [
      { label: 'The crest lockups, in the generator', to: { view: 'generator' } },
      { label: 'Coastal Forest, a poster signed in this identity', to: { view: 'posters', poster: 'coastal-forest', part: 'logo' } }
    ]
  },
  {
    id: 'bc-hydro',
    title: 'BC Hydro',
    kind: 'Graphic Standards Manual, 1983',
    books: ['hydro'],
    links: [
      { label: 'BC Hydro’s marks, in the Logos gallery', to: { view: 'gallery', logos: 'bc-hydro' } }
    ]
  }
]

export { GUIDE_BOOKS }

export const findBook = (id) => GUIDE_BOOKS.find((book) => book.id === id) ?? null
export const familyOf = (bookId) => GUIDE_FAMILIES.find((family) => family.books.includes(bookId)) ?? null

/** A page's files, under the site's base path. */
export const pageUrl = (base, bookId, pageId, ext = 'svg') => `${base}visual-guides/${bookId}/${pageId}.${ext}`
