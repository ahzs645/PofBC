import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFile, readdir } from 'node:fs/promises'
import { loadInitiative } from './initiatives.js'

for (const [id, count] of [['tourism', 75], ['rainforest-to-rockies', 38]]) {
  test(`${id} guide exposes every original page and its text in order`, async () => {
    const initiative = await loadInitiative(id)
    const { guide } = initiative.sections.find((section) => section.guide)
    const pages = guide.chapters.flatMap((chapter) => chapter.pages)
    assert.equal(pages.length, count)
    assert.ok(initiative.sources.some((source) => source.id === guide.sourceId && source.url.endsWith('.pdf')))
    const folder = new URL('../../public/tourism/guides/' + guide.folder + '/', import.meta.url)
    const images = (await readdir(folder)).filter((file) => file.endsWith('.webp'))
    const text = JSON.parse(await readFile(new URL('text.json', folder), 'utf8'))
    assert.equal(images.length, count)
    assert.equal(text.length, count)
    pages.forEach((title, i) => {
      assert.ok(title && images.includes((i + 1) + '.webp') && text[i]?.length, `Missing material on page ${i + 1}`)
    })
  })
}
