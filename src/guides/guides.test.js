// The visual guides as this site shows them: brandkit's BC pack (its own tests check the pages
// themselves), every family linked somewhere here, and every link to a view that exists.

import { test } from 'node:test'
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { GUIDE_BOOKS, GUIDE_FAMILIES, GUIDE_LINKS, familyOf, pageUrl } from './guides.js'

// The menu's views, read from its source: Node's test runner cannot load a .jsx module.
const VIEWS = [...readFileSync(new URL('../site/ViewSwitcher.jsx', import.meta.url), 'utf8').matchAll(/\{ id: '([\w-]+)', label:/g)].map(([, id]) => ({ id }))

test('the BC pack is checked out, with every page the books list', () => {
  const pages = GUIDE_BOOKS.flatMap((book) => book.pages.map((page) => ({ book, page })))
  assert.equal(pages.length, 156)
  for (const { book, page } of pages) {
    assert.ok(existsSync(new URL(`../../vendor/brandkit/manuals/bc/pages/${book.id}/${page.id}.svg`, import.meta.url)), `${page.id}.svg`)
  }
})

test('every book is in a family, and every family links into this site', () => {
  for (const book of GUIDE_BOOKS) assert.ok(familyOf(book.id), `${book.id} has no family`)
  for (const family of GUIDE_FAMILIES) assert.ok(family.links.length > 0, `${family.id} has no links`)
  assert.deepEqual(Object.keys(GUIDE_LINKS).sort(), GUIDE_FAMILIES.map(({ id }) => id).sort())
})

test('links go to views that exist, and read without em dashes', () => {
  const views = new Set(VIEWS.map(({ id }) => id))
  for (const family of GUIDE_FAMILIES) {
    for (const link of family.links) {
      assert.ok(views.has(link.to.view), `${link.label}: no view ${link.to.view}`)
      assert.ok(!link.label.includes('—'), link.label)
    }
  }
})

test('pages are addressed where the site serves them', () => {
  assert.equal(pageUrl('/PofBC/', 'sign', 'S05'), '/PofBC/visual-guides/sign/S05.svg')
  assert.equal(pageUrl('/', 'sign', 'S05', 'webp'), '/visual-guides/sign/S05.webp')
})
