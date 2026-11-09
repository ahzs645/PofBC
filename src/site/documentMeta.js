// The tab title, description and robots hint follow the page on screen, so a bookmark, a shared
// link's preview or a search result names the salary page (or the view) rather than the logo
// generator every view used to share.

const SITE = 'Province of BC'
export const DEFAULT_TITLE = 'Province of British Columbia — logo generator'

/** A title for a page in a view: "University of Northern BC · Salaries — Province of BC". */
export const documentTitle = (...parts) => {
  const named = parts.map((part) => String(part ?? '').trim()).filter(Boolean)
  return named.length ? `${named.join(' · ')} — ${SITE}` : DEFAULT_TITLE
}

const metaTag = (name) => {
  const doc = globalThis.document
  if (!doc?.head) return null
  let tag = doc.head.querySelector(`meta[name="${name}"]`)
  if (!tag) {
    tag = doc.createElement('meta')
    tag.setAttribute('name', name)
    doc.head.appendChild(tag)
  }
  return tag
}

/**
 * Set the tab title, the description and whether search engines should index this page.
 * `noindex` is used for pages about a named individual: the records are public, but a name's
 * page should not be what a search for that person surfaces.
 */
export const setDocumentMeta = ({ title, description, noindex = false } = {}) => {
  const doc = globalThis.document
  if (!doc) return
  if (title) doc.title = title
  if (description) metaTag('description')?.setAttribute('content', description)
  const robots = metaTag('robots')
  if (robots) robots.setAttribute('content', noindex ? 'noindex, nofollow' : 'index, follow')
}
