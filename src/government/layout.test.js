import { test } from 'node:test'
import assert from 'node:assert/strict'
import {
  allocateSectors, arcPath, bandPath, layoutGovernment, lerpAngle, normaliseAngle, RIM, rimAt, territoryPath,
  rotationToBottom, SECTOR_GAP, SECTORS, spreadAngles
} from './layout.js'

const TAU = Math.PI * 2
const close = (actual, expected, message) => assert.ok(Math.abs(actual - expected) < 1e-9, message ?? `${actual} ≉ ${expected}`)

test('the sectors fill the disc exactly, gaps included', () => {
  const sectors = allocateSectors({ legislative: 12, executive: 90, judicial: 3 })
  const covered = sectors.reduce((sum, { start, end }) => sum + (end - start), 0)
  close(covered + SECTOR_GAP * SECTORS.length, TAU)
})

test('the legislature is centred at twelve o’clock and the branches run clockwise', () => {
  const [legislative, executive, judicial] = allocateSectors({ legislative: 12, executive: 90, judicial: 3 })
  close((legislative.start + legislative.end) / 2, -Math.PI / 2)
  close(executive.start, legislative.end + SECTOR_GAP)
  close(judicial.start, executive.end + SECTOR_GAP)
})

test('a branch with three bodies still gets a readable sector', () => {
  const judicial = allocateSectors({ legislative: 12, executive: 200, judicial: 3 })[2]
  assert.ok(judicial.end - judicial.start > (30 * Math.PI) / 180)
})

test('a few nodes gather in the middle of a wide sector', () => {
  const angles = spreadAngles(3, 0, Math.PI)
  close(angles[1], Math.PI / 2)
  close(angles[2] - angles[1], 0.35)
})

test('a crowded sector spreads its nodes to fit inside it', () => {
  const angles = spreadAngles(40, 0, 1)
  assert.ok(angles[0] >= 0.06 - 1e-9 && angles.at(-1) <= 1 - 0.06 + 1e-9)
})

test('outer bodies sit beyond the ministry they answer to, and each family is one tooth', () => {
  const nodes = [
    { id: 'health', kind: 'ministry', branch: 'executive', ring: 'cabinet' },
    { id: 'finance', kind: 'ministry', branch: 'executive', ring: 'cabinet' },
    { id: 'bclc', kind: 'crown-corporation', branch: 'executive', ring: 'outer', group: 'finance' },
    { id: 'vch', kind: 'health-authority', branch: 'executive', ring: 'outer', group: 'health' },
    { id: 'bca', kind: 'crown-corporation', branch: 'executive', ring: 'outer', group: 'finance' }
  ]
  const { positions, teeth } = layoutGovernment(nodes)
  assert.ok(positions.health.angle < positions.finance.angle)
  // Health's authority comes first, then Finance's two corporations, stacked outwards.
  assert.ok(positions.vch.angle < positions.bclc.angle)
  close(positions.bclc.angle, positions.bca.angle)
  assert.ok(positions.bca.radius > positions.bclc.radius)
  assert.deepEqual(teeth.map((tooth) => tooth.group), ['health', 'finance'])
  // Only the family that needs a second row raises a tooth above the rim.
  const [health, finance] = teeth
  assert.ok(health.top <= RIM && finance.top > RIM)
})

test('the rim rises smoothly to a tooth and back', () => {
  const tooth = { start: 1, end: 1.2, top: RIM + 40 }
  assert.equal(rimAt(0.5, [tooth]), RIM)
  close(rimAt(1.1, [tooth]), RIM + 40)
  const shoulder = rimAt(1 - 0.02, [tooth])
  assert.ok(shoulder > RIM && shoulder < RIM + 40)
})

test('a branch territory is one closed path', () => {
  assert.match(territoryPath({ start: 0, end: 1 }, [{ start: 0.3, end: 0.5, top: RIM + 30 }]), /^M[\d.,-]+(L[\d.,-]+)+A.+Z$/)
})

test('the rotation to six o’clock takes the short way round', () => {
  close(rotationToBottom(Math.PI / 2), 0)
  close(rotationToBottom(-Math.PI / 2), Math.PI)
  close(rotationToBottom(0), Math.PI / 2)
  assert.ok(Math.abs(rotationToBottom(3)) <= Math.PI)
})

test('angles interpolate across the seam rather than the long way', () => {
  close(lerpAngle(3, -3, 0.5), normaliseAngle(3 + (TAU - 6) / 2) + TAU * 0 + (3 + (TAU - 6) / 2 - normaliseAngle(3 + (TAU - 6) / 2)))
  assert.ok(Math.abs(lerpAngle(3, -3, 0.5) - Math.PI) < 1e-9)
})

test('paths are well formed', () => {
  assert.match(bandPath(0, 1, 100, 200), /^M[\d.,-]+A.+L.+A.+Z$/)
  assert.match(arcPath(-2, -1, 150), /^M[\d.,-]+A150,150 0 0 1 /)
  // An arc across the bottom is reversed, so text along it reads left to right.
  assert.match(arcPath(1, 2, 150), /^M[\d.,-]+A150,150 0 0 0 /)
})

test('a parent’s sub-agencies sit beyond it as dots, and a Crown’s raise its tooth', () => {
  const nodes = [
    { id: 'forests', kind: 'ministry', branch: 'executive', ring: 'cabinet' },
    { id: 'wildfire', kind: 'sub', branch: 'executive', ring: 'sub', parent: 'forests' },
    { id: 'timber', kind: 'sub', branch: 'executive', ring: 'sub', parent: 'forests' },
    { id: 'hydro', kind: 'crown-corporation', branch: 'executive', ring: 'outer', group: 'forests' },
    ...['a', 'b', 'c', 'd', 'e', 'f', 'g'].map((id) => ({ id: `hydro-${id}`, kind: 'sub', branch: 'executive', ring: 'sub', parent: 'hydro' }))
  ]
  const { positions, teeth } = layoutGovernment(nodes)
  assert.ok(positions.wildfire.radius > positions.forests.radius)
  assert.ok(Math.abs(positions.wildfire.angle - positions.forests.angle) < 0.05)
  assert.ok(positions['hydro-g'].radius > positions.hydro.radius)
  assert.ok(teeth[0].top > positions['hydro-g'].radius)
})
