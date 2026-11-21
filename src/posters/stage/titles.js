// A drawing's <title> elements are the browser's own tooltip: on the stage it pops up over the
// chip that labels the part under the pointer. So the stage lifts them off: each title's words go
// to a data attribute on the element it titled, and to its aria-label, so a screen reader still
// hears them. The export puts them back, so a downloaded drawing keeps its titles.

const SVG_NS = 'http://www.w3.org/2000/svg'
const self = (root, selector) => [root, ...root.querySelectorAll(selector)].filter((el) => el.matches(selector))

/** Removes every <title> from a live drawing, keeping its words on its element. */
export const liftTitles = (svg) => {
  const lifted = new Map()
  for (const title of [...svg.querySelectorAll('title')]) {
    const parent = title.parentNode
    const text = title.textContent.replace(/\s+/g, ' ').trim()
    parent.dataset.pvTitle = title.textContent
    if (title.id) {
      parent.dataset.pvTitleId = title.id
      lifted.set(title.id, text)
    }
    if (text && !parent.hasAttribute('aria-label') && !parent.hasAttribute('aria-labelledby')) {
      parent.setAttribute('aria-label', text)
      parent.dataset.pvAriaLabel = ''
    }
    title.remove()
  }
  // A drawing named by its title through aria-labelledby is named by aria-label instead, and
  // described by whatever else the reference listed (its <desc>).
  for (const el of self(svg, '[aria-labelledby]')) {
    const ids = el.getAttribute('aria-labelledby').split(/\s+/).filter(Boolean)
    if (!ids.some((id) => lifted.has(id))) continue
    el.dataset.pvLabelledby = ids.join(' ')
    el.removeAttribute('aria-labelledby')
    el.setAttribute('aria-label', ids.filter((id) => lifted.has(id)).map((id) => lifted.get(id)).join(' '))
    const rest = ids.filter((id) => !lifted.has(id))
    if (rest.length && !el.hasAttribute('aria-describedby')) {
      el.setAttribute('aria-describedby', rest.join(' '))
      el.dataset.pvDescribedby = ''
    }
  }
}

/** Puts the titles lifted by liftTitles back into a copy of the drawing, and its labels as they were. */
export const restoreTitles = (svg) => {
  for (const el of self(svg, '[data-pv-labelledby]')) {
    el.setAttribute('aria-labelledby', el.dataset.pvLabelledby)
    el.removeAttribute('aria-label')
    if ('pvDescribedby' in el.dataset) el.removeAttribute('aria-describedby')
    delete el.dataset.pvLabelledby
    delete el.dataset.pvDescribedby
  }
  for (const el of self(svg, '[data-pv-title]')) {
    const title = document.createElementNS(SVG_NS, 'title')
    title.textContent = el.dataset.pvTitle
    if (el.dataset.pvTitleId) title.id = el.dataset.pvTitleId
    el.insertBefore(title, el.firstChild)
    if ('pvAriaLabel' in el.dataset) el.removeAttribute('aria-label')
    delete el.dataset.pvTitle
    delete el.dataset.pvTitleId
    delete el.dataset.pvAriaLabel
  }
}
