import { test } from 'node:test'
import assert from 'node:assert/strict'
import { sentencesOf, storySteps } from './storySteps.js'

test('sentences break at full stops, not at initials or section numbers', () => {
  assert.deepEqual(
    sentencesOf('It was created under s. 351 of the Act. The B.C. Ferries name came later. Its continuation under SBC 2003 c. 53 is not dated here.'),
    ['It was created under s. 351 of the Act.', 'The B.C. Ferries name came later.', 'Its continuation under SBC 2003 c. 53 is not dated here.']
  )
})

test('a closing quote or bracket stays with its sentence', () => {
  assert.deepEqual(sentencesOf('It said “held.” Then it moved (in 1982.) After that, nothing.'), ['It said “held.”', 'Then it moved (in 1982.)', 'After that, nothing.'])
})

test('a short passage is one step', () => {
  assert.deepEqual(storySteps('One sentence. Two sentences.'), ['One sentence. Two sentences.'])
  assert.deepEqual(storySteps(''), [])
})

test('a long passage is packed into steps of whole sentences, losing nothing', () => {
  const sentence = (n) => `Sentence ${n} has some words in it to make it about sixty characters.`
  const passage = Array.from({ length: 10 }, (_, n) => sentence(n + 1)).join(' ')
  const steps = storySteps(passage)
  assert.ok(steps.length > 1)
  assert.equal(steps.join(' '), passage)
  for (const step of steps) assert.ok(step.length <= 220, step)
})

test('a sentence longer than a step is a step of its own', () => {
  const long = `Word ${'word '.repeat(60).trim()}.`
  const steps = storySteps(`Short one. ${long} Another short one. ${'More words here. '.repeat(10).trim()}`)
  assert.ok(steps.includes(long))
})
