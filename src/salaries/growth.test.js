import assert from 'node:assert/strict'
import test from 'node:test'
import { annualRate, formatRate, listChanges, payBands, pooledGrowth, seriesGrowth, stayerRaises, typicalRaise, yearNumber } from './growth.js'

const YEARS = ['2017/18', '2018/19', '2019/20', '2020/21', '2021', '2022']

test('a period label is read as its first year', () => {
  assert.equal(yearNumber('2023/24'), 2023)
  assert.equal(yearNumber('2025'), 2025)
})

test('a change is a rate a year, compounded', () => {
  assert.ok(Math.abs(annualRate(100, 121, 2) - 0.1) < 1e-9)
  assert.equal(annualRate(0, 100, 2), null)
  assert.equal(annualRate(100, 110, 0), null)
})

test('average growth needs enough records at both ends, years apart', () => {
  const cells = [{ year: 0, count: 5, mean: 100 }, { year: 1, count: 2, mean: 500 }, { year: 3, count: 6, mean: 133.1 }]
  const growth = seriesGrowth(cells, YEARS)
  assert.equal(growth.span, 3)
  assert.equal(growth.weight, 5)
  assert.ok(Math.abs(growth.rate - 0.1) < 1e-6, 'the thin middle year is passed over')
  assert.equal(seriesGrowth([{ year: 0, count: 9, mean: 1 }, { year: 1, count: 9, mean: 2 }], YEARS), null, 'one year apart is too close')
  assert.equal(seriesGrowth([{ year: 0, count: 4, mean: 1 }, { year: 3, count: 9, mean: 2 }], YEARS), null, 'too few records at one end')
})

test('across employers, each employer is measured on its own and weighed by records', () => {
  // A better-paying employer starting to disclose does not make the title grow.
  const pooled = pooledGrowth([
    ['a', [{ year: 0, count: 10, mean: 100 }, { year: 3, count: 10, mean: 100 }]],
    ['b', [{ year: 3, count: 50, mean: 300 }]]
  ], YEARS)
  assert.equal(pooled.rate, 0)
  assert.equal(pooled.employers, 1)
  const mixed = pooledGrowth([
    ['a', [{ year: 0, count: 10, mean: 100 }, { year: 3, count: 30, mean: 100 }]],
    ['b', [{ year: 0, count: 30, mean: 100 }, { year: 3, count: 30, mean: 133.1 }]]
  ], YEARS)
  assert.ok(Math.abs(mixed.rate - 0.075) < 1e-6)
})

test('raises follow one name in one group, leaving out years it has two records and long gaps', () => {
  const raises = stayerRaises([
    { name: 'Lee, A', group: 'x', pay: 100, year: 0 },
    { name: 'LEE, A.', group: 'x', pay: 110, year: 1 },
    { name: 'Lee, A', group: 'y', pay: 500, year: 1 },
    { name: 'Wong, B', group: 'x', pay: 100, year: 0 },
    { name: 'Wong, B', group: 'x', pay: 90, year: 1 },
    { name: 'Wong, B', group: 'x', pay: 95, year: 1 },
    { name: 'Wong, B', group: 'x', pay: 120, year: 2 },
    { name: 'Kim, C', group: 'x', pay: 100, year: 0 },
    { name: 'Kim, C', group: 'x', pay: 200, year: 5 }
  ], YEARS)
  assert.equal(raises.length, 2)
  assert.ok(raises.some((raise) => raise.name === 'Lee, A' && Math.abs(raise.rate - 0.1) < 1e-9))
  assert.ok(raises.some((raise) => raise.name === 'Wong, B' && Math.abs(raise.rate - (Math.sqrt(1.2) - 1)) < 1e-9))
  const typical = typicalRaise(raises)
  assert.equal(typical.pairs, 2)
  assert.equal(typical.people, 2)
  assert.equal(typicalRaise([]), null)
})

test('rates read as signed percentages', () => {
  assert.equal(formatRate(0.0321), '+3.2% a year')
  assert.equal(formatRate(-0.004, ''), '−0.4%')
  assert.equal(formatRate(0.0001, ''), '0.0%')
  assert.equal(formatRate(null), '—')
})

test('pay bands cover every record, the last open-ended', () => {
  const bands = payBands([76000, 99000, 100000, 180000, 450000])
  assert.equal(bands[0].from, 75000)
  assert.equal(bands.at(-1).to, null)
  assert.equal(bands.reduce((sum, band) => sum + band.count, 0), 5)
  assert.equal(bands.find((band) => band.from === 100000).count, 1)
})

test('who came onto and went off the list is counted against the last period of the same kind', () => {
  const changes = listChanges([
    { name: 'Lee, A', year: 0 }, { name: 'Wong, B', year: 0 },
    { name: 'Lee, A', year: 1 }, { name: 'Kim, C', year: 1 },
    { name: 'Lee, A', year: 4 }
  ], YEARS)
  assert.equal(changes.has(0), false)
  assert.deepEqual(changes.get(1), { before: 0, joined: 1, left: 1, stayed: 1 })
  assert.equal(changes.has(4), false, 'a calendar year is not compared with a fiscal one')
})
