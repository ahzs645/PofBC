// The visual guides: identity manuals rebuilt page by page as drawings. The pages, the books and
// the families they belong to are brandkit's BC manual pack (vendor/brandkit, manuals/bc); what
// this site adds is where each family links to here.

// A relative path rather than the 'brandkit' alias: this module is also loaded by Node's test
// runner, which does not see Vite's aliases.
import { BC_BOOKS, BC_FAMILIES, BC_FOOTNOTE } from '../../vendor/brandkit/manuals/bc/index.js'

const LINKS = {
  // One link a family: the piece of this site most directly rebuilt from its manuals.
  'visual-identity-program': [
    { label: 'The 1977 stationery, built from these manuals', to: { view: 'stationery' } }
  ],
  'bc-hydro': [
    { label: 'BC Hydro’s marks, in the Logos gallery', to: { view: 'gallery', logos: 'bc-hydro' } }
  ],
  'bc-parks': [
    { label: 'Each symbol, with its history', to: { view: 'signs', sign: 'proposed-park-symbols' } },
    { label: 'BC Parks’ marks, in the Logos gallery', to: { view: 'gallery', logos: 'bc-parks' } }
  ]
}

/**
 * Guides this site draws itself, beside brandkit's manuals: a page names its drawing (`art`, a
 * path under src/), which GuidesView turns into the page's image.
 */
export const SITE_BOOKS = [
  {
    id: 'park-symbols-1971',
    title: 'Proposed park symbols',
    edition: '1971',
    pages: [{
      id: 'DD67',
      title: 'Proposed park symbols',
      printed: 'DD67',
      width: 1000,
      height: 1500,
      art: 'signs/parks/proposed-park-symbols.svg',
      notes: [
        'Twenty-two pictograms for park facilities and activities, printed on a page of the Department of Recreation and Conservation’s annual report for 1971 (printed 1972, PDF page 68). They are proposals: the report does not say who drew them, whether they were approved, or where any went up.',
        'Each symbol is rebuilt from circles, polygons, strokes and curves, with no tracing, in black as a working master; the report’s ink is not a specification.'
      ]
    }]
  }
]

const SITE_FAMILIES = [
  { id: 'bc-parks', title: 'BC Parks', kind: 'Proposed park symbols, 1971', books: ['park-symbols-1971'] }
]

export const GUIDE_BOOKS = [...BC_BOOKS, ...SITE_BOOKS]
export const GUIDE_FAMILIES = [...BC_FAMILIES, ...SITE_FAMILIES].map((family) => ({ ...family, links: LINKS[family.id] ?? [] }))
export const GUIDE_FOOTNOTE = BC_FOOTNOTE
export const GUIDE_LINKS = LINKS

export const findBook = (id) => GUIDE_BOOKS.find((book) => book.id === id) ?? null
export const familyOf = (bookId) => GUIDE_FAMILIES.find((family) => family.books.includes(bookId)) ?? null

/**
 * A page's files, under the site's base path. The Vite config serves and copies the pack's pages
 * to `visual-guides/` (brandkit's manualPages plugin), where they were before they moved.
 */
export const pageUrl = (base, bookId, pageId, ext = 'svg') => `${base}visual-guides/${bookId}/${pageId}.${ext}`
