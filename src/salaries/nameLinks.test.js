import test from 'node:test'
import assert from 'node:assert/strict'
import { compatibleNames, findNameLinks, linkLookup, nameOnly, personRecordShards } from './nameLinks.js'

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

test('only an explicit source review can connect different surnames, with its evidence', () => {
  const rows = [
    ['Ionescu, Diana', null, 480016, 6085, 0, 4, 'official', 113],
    ['lonescu, Diana', null, 480016, 6085, 0, 4, 'compiled'],
    ['lonescu, Diana', null, 480016, 6085, 1, 4, 'compiled']
  ]
  assert.equal(run(rows).links.length, 0)
  const evidence = [{ sourceId: 'official', pdfPage: 113 }]
  const result = run(rows, [{ employer: 'bci', names: ['lonescu, Diana', 'Ionescu, Diana'],
    preferredName: 'Ionescu, Diana', decision: 'verified', note: 'Source spelling and complete row reviewed', evidence }])
  assert.equal(result.links.length, 1)
  assert.equal(result.links[0].key, 'ionescu|diana')
  assert.equal(result.links[0].aliases[0].key, 'lonescu|diana')
  assert.deepEqual(result.links[0].aliases[0].evidence, evidence)
  assert.deepEqual(rows[1], ['lonescu, Diana', null, 480016, 6085, 0, 4, 'compiled'])
})

test('reviewed surname links do not obstruct existing compatible given-name variants', () => {
  const rows = [
    ['Germain, Francois F', null, 334706, 9658, 0, 0, 'official'],
    ['Getmain, Francois F', null, 334706, 9658, 0, 0, 'compiled'],
    ['Germain, Francois', null, 462234, 11048, 0, 4, 'official']
  ]
  const result = run(rows, [{ employer: 'bci', names: ['Getmain, Francois F', 'Germain, Francois F'],
    preferredName: 'Germain, Francois F', decision: 'verified', note: 'Original row' }])
  assert.equal(result.links.length, 1)
  assert.equal(result.links[0].aliases.length, 2)
  assert.equal(result.links[0].aliases.find((entry) => entry.key === 'germain|francois').status, 'likely')
  const fuller = run([
    ['Lavely, W illiam', null, 100, 10, 0, 0, 'compiled'],
    ['Lavery, William', null, 100, 10, 0, 0, 'official'],
    ['Lavery, William John', null, 200, 20, 0, 4, 'official']
  ], [{ employer: 'bci', names: ['Lavely, W illiam', 'Lavery, William'],
    preferredName: 'Lavery, William', decision: 'verified', note: 'Original row' }])
  assert.equal(fuller.links.length, 1)
  assert.equal(fuller.links[0].aliases.find((entry) => entry.key === 'lavery|william john').status, 'likely', 'The fuller name keeps its existing uncertainty')
})

test('the disclosed preferred spelling must belong to the reviewed pair', () => {
  assert.throws(() => run([
    ['Ionescu, Diana', null, 100, 0, 0, 0, 's'], ['lonescu, Diana', null, 100, 0, 0, 0, 's']
  ], [{ employer: 'bci', names: ['Ionescu, Diana', 'lonescu, Diana'],
    preferredName: 'Ionescu, Diane', decision: 'verified', note: 'wrong preferred name' }]), /disclosed spellings/)
})

test('a reviewed punctuation correction preserves an older extraction-split connection', () => {
  const rows = [['Alden, C olin MC', null, 99432, 4824, 0, 0, 'compiled'],
    ['Alden,Colin MC', null, 80000, null, 0, 1, 'older'], ['Alden,Colin M.C.', null, 99432, 4824, 0, 0, 'official']]
  const reviewed = [{ employer: employers[0][3], names: [rows[0][0], rows[2][0]], preferredName: rows[2][0], decision: 'verified', note: 'Original row reviewed' }]
  const result = run(rows, reviewed)
  assert.equal(result.links.length, 1)
  assert.equal(result.links[0].name, rows[2][0])
  assert.deepEqual(new Set(result.links[0].aliases.map((a) => a.name)), new Set(rows.slice(0, 2).map((r) => r[0])))
  assert.ok(result.links[0].aliases.every((a) => a.status === 'verified'))
  const conflicting = rows.map((r) => [...r]); conflicting[1][5] = 0
  assert.equal(run(conflicting, reviewed).links[0].aliases.length, 1)
  assert.equal(run(rows, [...reviewed, { employer: employers[0][3], names: rows.slice(0, 2).map((r) => r[0]), decision: 'reject', note: 'Explicitly kept apart' }]).links[0].aliases.length, 1)
})

test('person pages request every surname shard behind a canonical name, without unrelated rows', () => {
  const published = { links: [
    ['bci', 'ionescu|diana', 'Ionescu, Diana', [['lonescu|diana', 'lonescu, Diana', 'verified', 'source']]],
    ['bci', 'smith|jane', 'Smith, Jane', [['smyth|jane', 'Smyth, Jane', 'verified', 'source']]]
  ] }
  assert.deepEqual(personRecordShards(published, 'ionescu|diana'), ['io', 'lo'])
  assert.deepEqual(personRecordShards(published, 'lonescu|diana'), ['lo'])
  assert.deepEqual(personRecordShards(null, 'ionescu|diana'), ['io'])
  const lookup = linkLookup(published, employers)
  assert.equal(lookup.get('0|lonescu|diana').key, 'ionescu|diana')
  assert.equal(lookup.get('1|lonescu|diana'), undefined)
})

test('a likely surname bridge never promotes a locally verified spelling into a verified global identity', () => {
  const rows = [['Murtby, Srinivasa', null, 100, 0, 0, 0, 's'], ['Murthy, Srinivasa', null, 100, 0, 0, 0, 's'], ['Murthy, Srinivasa Kumar', null, 110, 0, 0, 1, 's']]
  const result = run(rows, [
    { employer: 'bci', names: [rows[0][0], rows[1][0]], decision: 'verified', preferredName: rows[1][0], note: 'Printed row' },
    { employer: 'bci', names: [rows[1][0], rows[2][0]], decision: 'likely', note: 'Professional continuity assumption' }
  ])
  assert.equal(result.links.length, 1)
  assert.equal(result.links[0].name, rows[1][0])
  assert.equal(result.links[0].aliases.find((a) => a.key === 'murtby|srinivasa').status, 'verified')
  assert.equal(result.links[0].aliases.find((a) => a.key === 'murthy|srinivasa kumar').status, 'likely')
})

test('a professional reviewed full name is separate metadata; every original disclosed spelling remains an alias', () => {
  const rows = [['Pittman, J.', 'SVP Private Equity', 1512762, 19531, 0, 0, 's'], ['Pittmsn, Jim', 'EVP', 3902330, 0, 0, 4, 's']]
  const result = run(rows, [{ employer: 'bci', names: rows.map((r) => r[0]), decision: 'verified', preferredName: rows[0][0], canonicalName: 'Pittman, Jim', note: 'Primary executive disclosure and currency reviewed', evidence: [{ url: 'https://example.test/bci.pdf', pdfPage: 67 }] }])
  const [group] = result.links
  assert.equal(group.key, 'pittman|jim')
  assert.equal(group.reviewedName, true)
  assert.deepEqual(new Set(group.aliases.map((a) => a.name)), new Set(rows.map((r) => r[0])))
  const published = { links: [[group.employer, group.key, group.name, group.aliases.map((a) => [a.key, a.name, a.status, a.reason])]], reviewedNames: ['bci|pittman|jim'] }
  assert.equal(linkLookup(published, employers).get('0|pittmsn|jim').reviewedName, true)
  assert.deepEqual(personRecordShards(published, 'pittman|jim'), ['pi'])
  assert.equal(rows[1][0], 'Pittmsn, Jim')
})

test('unseparated initial spellings are only connected by explicit reviewed formatting', () => {
  const rows = [['LEONG P.', null, 100, 0, 0, 0, 's'], ['Leong, P.', null, 100, 0, 0, 0, 's']]
  assert.equal(run(rows).links.length, 0)
  const result = run(rows, [{ employer: 'bci', names: rows.map((r) => r[0]), decision: 'verified', preferredName: rows[1][0], note: 'Same ordered letters; separator reviewed' }])
  assert.equal(result.links.length, 1)
  assert.equal(result.links[0].name, 'Leong, P.')
})

test('a verified local typo remains a likely alias when its path to the fuller canonical name crosses an inference', () => {
  const rows = [['Murtby, Srinivasa', null, 100, 0, 0, 0, 's'], ['Murthy, Srinivasa', null, 100, 0, 0, 0, 's'], ['Murthyy, Srinivasa Kumar', null, 110, 0, 0, 1, 's']]
  const result = run(rows, [
    { employer: 'bci', names: rows.slice(0, 2).map((r) => r[0]), decision: 'verified', note: 'Local printed spelling' },
    { employer: 'bci', names: [rows[1][0], rows[2][0]], decision: 'likely', note: 'Qualified professional assumption' }
  ])
  assert.equal(result.links[0].name, 'Murthyy, Srinivasa Kumar')
  assert.equal(result.links[0].aliases.find((a) => a.key === 'murtby|srinivasa').status, 'likely')
  assert.match(result.links[0].aliases.find((a) => a.key === 'murtby|srinivasa').reason, /includes an unverified surname inference/)
  assert.equal(result.decisions.find((d) => d.status === 'verified').status, 'verified', 'the original local evidence survives independently')
})
