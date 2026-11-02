import test from 'node:test'
import assert from 'node:assert/strict'
import { compatibleNames, findNameLinks, linkLookup, nameOnly } from './nameLinks.js'

const years = ['2017/18', '2018/19', '2019/20', '2020/21', '2023/24', '2030/31']
const employers = [['BCI', 'Crown corporations', null, 'bci'], ['Other', 'Crown corporations', null, 'other']]
const run = (rows, reviewed) => findNameLinks(rows, { years, employers, reviewed })
const decision = (result, name) => result.decisions.find((entry) => entry.name === name)

test('an initial joins the one full name at its employer that agrees, as likely', () => {
  const result = run([
    ['Garant, D.', 'Senior Vice President', 1961537, 0, 0, 0, 's'],
    ['Garant, Daniel', 'Executive Vice President', 3686064, 0, 0, 4, 's'],
    ['Garant, D.', null, 100, 0, 1, 0, 's']
  ])
  assert.equal(decision(result, 'Garant, D.').status, 'likely')
  assert.deepEqual(result.links, [{ employer: 'bci', key: 'garant|daniel', name: 'Garant, Daniel', aliases: [{ key: 'garant|d', name: 'Garant, D.', status: 'likely', reason: decision(result, 'Garant, D.').reason }] }])
})

test('the records verify a join: an extraction split, or a position few others hold', () => {
  const split = run([['Nevill, T homas', null, 1, 0, 0, 0, 's'], ['Nevill, Thomas', null, 1, 0, 0, 3, 's']])
  assert.equal(decision(split, 'Nevill, T homas').status, 'verified')
  const title = run([['Fyfe, G.', 'CEO/CIO · CIO', 2955239, 0, 0, 0, 's'], ['Fyfe, Gordon', 'Ceo/Cio', 5391800, 0, 0, 4, 's']])
  assert.equal(decision(title, 'Fyfe, G.').status, 'verified')
  assert.match(decision(title, 'Fyfe, G.').reason, /Same position/)
})

test('a shortened first name joins its full form: Jeff and Jeffrey', () => {
  assert.equal(compatibleNames('Morley, Jeff', 'Morley, Jeffrey'), true)
  assert.equal(compatibleNames('Morley, Jo', 'Morley, Joanne'), false, 'two letters say too little')
  assert.equal(compatibleNames('Morley, Jeff', 'Morley, Geoffrey'), false)
  const result = run([['Morley,Jeff', 'Mgr Banking', 75392, 0, 0, 0, 's'], ['Morley,Jeffrey', 'Mgr Banking', 86150, 0, 0, 2, 's']])
  assert.equal(decision(result, 'Morley,Jeff').status, 'verified')
})

test('several fitting names, one period, a long gap or a jump between neighbouring years keep names apart', () => {
  const several = run([['Jones, D', null, 1, 0, 0, 0, 's'], ['Jones, David', null, 1, 0, 0, 3, 's'], ['Jones, Donna', null, 1, 0, 0, 4, 's']])
  assert.equal(decision(several, 'Jones, D').status, 'apart')
  assert.equal(several.links.length, 0)
  const together = run([['Canning, S', null, 202979, 0, 0, 0, 's'], ['Canning, SE', null, 140117, 0, 0, 0, 's']])
  assert.equal(decision(together, 'Canning, S').status, 'apart')
  const gap = run([['Smith, B', null, 1, 0, 0, 0, 's'], ['Smith, Brian', null, 1, 0, 0, 5, 's']])
  assert.match(decision(gap, 'Smith, B').reason, /13 years/)
  const jump = run([['Pallan, P', null, 10000, 0, 0, 0, 's'], ['Pallan, Paul', null, 90000, 0, 0, 1, 's']])
  assert.match(decision(jump, 'Pallan, P').reason, /Pay changes/)
  const promotion = run([['Rayes, R.', null, 406722, 0, 0, 0, 's'], ['Rayes, Ramy', null, 2607639, 0, 0, 4, 's']])
  assert.equal(decision(promotion, 'Rayes, R.').status, 'likely', 'a rise over years is not weighed')
})

test('a position written into the name is set aside, and joins the plain name', () => {
  assert.equal(nameOnly('Glickman, Eva                Director, HR Payroll Services'), 'Glickman, Eva')
  const result = run([['Glickman, Eva', null, 1, 0, 0, 0, 's'], ['Glickman, Eva                Director, HR', null, 1, 0, 0, 1, 's']])
  assert.equal(result.links.length, 1)
  assert.equal(result.links[0].name, 'Glickman, Eva')
  assert.equal(result.links[0].aliases[0].status, 'verified')
})

test('reviewed decisions override the rules either way', () => {
  const rows = [['Wong, Jason Lany', null, 1, 0, 0, 0, 's'], ['Wong, Jason Larry', null, 1, 0, 0, 3, 's']]
  assert.equal(run(rows).links.length, 0)
  const joined = run(rows, [{ employer: 'bci', names: ['Wong, Jason Lany', 'Wong, Jason Larry'], decision: 'verified', note: 'misread' }])
  assert.equal(joined.links.length, 1)
  assert.equal(joined.links[0].aliases[0].status, 'verified')
  const garant = [['Garant, D.', null, 1, 0, 0, 0, 's'], ['Garant, Daniel', null, 1, 0, 0, 4, 's']]
  const rejected = run(garant, [{ employer: 'bci', names: ['Garant, D.', 'Garant, Daniel'], decision: 'reject', note: 'two people' }])
  assert.equal(rejected.links.length, 0)
})

test('the published links read back as a lookup by employer index and name key', () => {
  const lookup = linkLookup({ links: [['other', 'garant|daniel', 'Garant, Daniel', [['garant|d', 'Garant, D.', 'likely', 'why']]]] }, employers)
  assert.deepEqual(lookup.get('1|garant|d'), { key: 'garant|daniel', name: 'Garant, Daniel', aliasName: 'Garant, D.', status: 'likely', reason: 'why' })
  assert.equal(lookup.get('0|garant|d'), undefined, 'never across employers')
})
