// The visual guides: identity manuals rebuilt page by page as drawings. The pages, the books and
// the families they belong to are brandkit's BC manual pack (vendor/brandkit, manuals/bc); what
// this site adds is where each family links to here.

// A relative path rather than the 'brandkit' alias: this module is also loaded by Node's test
// runner, which does not see Vite's aliases.
import { BC_BOOKS, BC_FAMILIES, BC_FOOTNOTE } from '../../vendor/brandkit/manuals/bc/index.js'

const LINKS = {
  'visual-identity-program': [
    { label: 'The crest lockups, in the generator', to: { view: 'generator' } },
    { label: 'The 1977 stationery: calling cards, letterhead, envelopes', to: { view: 'stationery' } },
    { label: 'Coastal Forest, a poster signed in this identity', to: { view: 'posters', poster: 'coastal-forest', part: 'logo' } }
  ],
  'bc-hydro': [
    { label: 'BC Hydro’s marks, in the Logos gallery', to: { view: 'gallery', logos: 'bc-hydro' } }
  ]
}

export const GUIDE_BOOKS = BC_BOOKS
export const GUIDE_FAMILIES = BC_FAMILIES.map((family) => ({ ...family, links: LINKS[family.id] ?? [] }))
export const GUIDE_FOOTNOTE = BC_FOOTNOTE
export const GUIDE_LINKS = LINKS

export const findBook = (id) => GUIDE_BOOKS.find((book) => book.id === id) ?? null
export const familyOf = (bookId) => GUIDE_FAMILIES.find((family) => family.books.includes(bookId)) ?? null

/**
 * A page's files, under the site's base path. The Vite config serves and copies the pack's pages
 * to `visual-guides/` (brandkit's manualPages plugin), where they were before they moved.
 */
export const pageUrl = (base, bookId, pageId, ext = 'svg') => `${base}visual-guides/${bookId}/${pageId}.${ext}`
