import assert from 'node:assert/strict'
import test from 'node:test'
import { labelPlan } from './labelPlan.js'

const boxes = (plan, count, width, gap) => {
  const column = (width - gap * (count - 1)) / count
  return plan.map((each, at) => ({ ...each, at })).filter((each) => each.shown).map(({ at, edge }) => {
    const start = at * (column + gap)
    return edge === 'start' ? start : edge === 'end' ? start + column - 28 : start + column / 2 - 14
  })
}

test('every label shows while the width is unknown', () => {
  assert.ok(labelPlan(38, 0).every((each) => each.shown))
})

test('labels never touch, stay inside the row, and the chosen one always shows', () => {
  for (const [count, width, gap] of [[38, 303, 2], [38, 1193, 2], [32, 303, 4], [20, 295, 2], [7, 303, 4]]) {
    for (const chosen of [0, 1, Math.floor(count / 2), count - 2, count - 1]) {
      const plan = labelPlan(count, width, chosen, gap)
      assert.ok(plan[chosen].shown, `chosen ${chosen} of ${count} at ${width}px`)
      const lefts = boxes(plan, count, width, gap).sort((a, b) => a - b)
      lefts.forEach((left, at) => {
        assert.ok(left >= 0 && left + 28 <= width + 0.5, `label inside ${width}px`)
        if (at) assert.ok(left - lefts[at - 1] >= 32, `labels apart at ${width}px`)
      })
    }
  }
})

test('a row with room labels every year', () => {
  assert.ok(labelPlan(20, 1193, -1, 2).every((each) => each.shown))
})
