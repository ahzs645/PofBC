import test from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { PAPER_MODELS, filesOf, sheetWords } from './catalogue.js'
import { STAGE_GROUND, stagesOf, viewerEvent, viewerSrc } from './packcadFrame.js'

const publicFile = (path) => readFileSync(new URL(`../../public/${path}`, import.meta.url))

test('every paper model has a unique id', () => {
  const ids = PAPER_MODELS.map((model) => model.id)
  assert.equal(new Set(ids).size, ids.length)
})

for (const model of PAPER_MODELS) {
  test(`${model.title}: its files are the ones exported, and the catalogue says what they hold`, () => {
    const { json, pdf } = filesOf(model)
    const jsonBytes = publicFile(json)
    const pdfBytes = publicFile(pdf)
    assert.equal(createHash('sha256').update(jsonBytes).digest('hex'), model.sha256.json)
    assert.equal(createHash('sha256').update(pdfBytes).digest('hex'), model.sha256.pdf)
    assert.equal(pdfBytes.subarray(0, 5).toString(), '%PDF-')

    const project = JSON.parse(jsonBytes)
    assert.equal(project.foldModel.facesVertices.length, model.panels)
    // The first step is the flat sheet; the rest are the folds.
    assert.equal(project.foldingSteps.length - 1, model.stages)
    assert.equal(project.foldingSteps[0].id, 'setup')
    // The SVG dieline gives the sheet in millimetres.
    const [, width, height] = /width="([\d.]+)mm" height="([\d.]+)mm"/.exec(project.dieline.text)
    assert.ok(Math.abs(Number(width) - model.sheetMm[0]) < 0.01)
    assert.ok(Math.abs(Number(height) - model.sheetMm[1]) < 0.01)
  })
}

test('the viewer address reaches a project under public/ from packcad/', () => {
  const src = new URL(viewerSrc('/PofBC/', 'paper-models/a/b.packcad.json', { autoplay: true }), 'https://x.test')
  assert.equal(src.pathname, '/PofBC/packcad/viewer.html')
  assert.equal(new URL(src.searchParams.get('project'), src).pathname, '/PofBC/paper-models/a/b.packcad.json')
  assert.equal(src.searchParams.get('autoplay'), '1')
  assert.equal(src.searchParams.get('controls'), '0')
  assert.equal(src.searchParams.get('theme'), 'light')
  // The viewer's own pace and camera unless asked.
  assert.equal(src.searchParams.has('speed'), false)
  assert.equal(new URL(viewerSrc('/', 'a.json', { speed: 0.5 }), 'https://x.test').searchParams.get('speed'), '0.5')
})

test('the viewer opens in the site theme, on the stage colour', () => {
  const src = new URL(viewerSrc('/', 'a.json', { theme: 'dark', background: STAGE_GROUND.dark }), 'https://x.test')
  assert.equal(src.searchParams.get('theme'), 'dark')
  assert.equal(`#${src.searchParams.get('background')}`, STAGE_GROUND.dark)
  assert.match(STAGE_GROUND.light, /^#[0-9a-f]{6}$/)
})

test('only the viewer’s own messages are read', () => {
  assert.deepEqual(viewerEvent({ type: 'packcad:ready', steps: [] }), { type: 'packcad:ready', steps: [] })
  assert.equal(viewerEvent({ type: 'packcad:play' }), null)
  assert.equal(viewerEvent('packcad:ready'), null)
  assert.equal(viewerEvent(null), null)
})

test('stages set the flat sheet apart from the folds', () => {
  assert.deepEqual(stagesOf([{ id: 'setup' }, { id: 'a' }, { id: 'b' }]), { setup: { id: 'setup' }, folds: [{ id: 'a' }, { id: 'b' }] })
  assert.deepEqual(stagesOf(), { setup: null, folds: [] })
  assert.equal(sheetWords([297, 199.837]), '297 × 199.8 mm')
})
