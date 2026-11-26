import { createHash, randomUUID } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import outlines from '../artwork/cleanbc/outlines.json' with { type: 'json' }
import placements from '../artwork/cleanbc/placements.json' with { type: 'json' }
import sources from '../src/gallery/cleanbcSources.json' with { type: 'json' }

const artwork = new URL('../artwork/cleanbc/', import.meta.url)
const publicArtwork = fileURLToPath(new URL('../public/identity-collected/cleanbc/', import.meta.url))
const inks = {
  white: '#fff', black: '#231f20', clear: 'none',
  leafGreen: '#8bc043', firGreen: '#5fa544', skyBlue: '#008fb4', gold: '#e3a82b',
  provincialBlue: '#234075', provincialReverseBlue: '#7b8cac', descriptorBlue: '#043673'
}

// Keep publisher class numbers and rule order so that the archival file can be reproduced.
const fillRule = (classNumber, ink) => `      .cls-${classNumber} {\n        fill: ${ink};\n      }\n`
const recipes = {
  'base-wordmark': {
    white: { template: 'white' }
  },
  'better-buildings-endorsed': {
    black: { template: 'black' },
    positive: {
      template: 'colour', leafClass: 1, backgroundClass: 2, mountainsClass: 3,
      firstFill: inks.leafGreen, secondFill: inks.white, thirdFill: inks.provincialBlue
    },
    reverse: {
      template: 'colour', leafClass: 2, backgroundClass: 3, mountainsClass: 1,
      firstFill: inks.provincialReverseBlue, secondFill: inks.leafGreen, thirdFill: inks.white
    },
    white: { template: 'white', archivalSpacer: '  ' }
  },
  'better-buildings-wordmark': {
    black: { template: 'mono', canvasClass: 1, inkClass: 2, firstFill: inks.clear, secondFill: inks.black },
    positive: {
      template: 'colour', firClass: 2, shadePathClass: 3, isolationClass: 4, shadeGroupClass: 5,
      descriptorClass: 6, reverseWhiteRule: '', positiveBlueRule: '\n' + fillRule(6, inks.descriptorBlue)
    },
    reverse: {
      template: 'colour', firClass: 3, shadePathClass: 4, isolationClass: 5, shadeGroupClass: 6,
      descriptorClass: 2, reverseWhiteRule: fillRule(2, inks.white) + '\n', positiveBlueRule: ''
    },
    white: { template: 'mono', canvasClass: 2, inkClass: 1, firstFill: inks.white, secondFill: inks.clear }
  }
}

function placedOutline(path, file) {
  const [outline, coordinates = []] = typeof path === 'string' ? [path] : path
  if (!Object.hasOwn(outlines, outline)) throw new Error(`${file}: unknown CleanBC outline ${outline}`)
  return outlines[outline].replace(/\{(\d+)\}/g, (_, index) => {
    if (coordinates[index] === undefined) throw new Error(`${file}: missing coordinate ${index} for ${outline}`)
    return coordinates[index]
  })
}

function renderArtwork() {
  const outputs = new Map()
  for (const [layout, treatments] of Object.entries(recipes)) {
    const { paths, ...canvas } = placements[layout]
    const source = sources.find(({ id }) => id === layout)
    for (const [treatment, { template, ...paint }] of Object.entries(treatments)) {
      const file = `${layout}-${treatment}.svg`
      const values = { ...canvas, ...inks, ...paint }
      const xml = readFileSync(new URL(`${layout}-${template}.svg.in`, artwork), 'utf8')
        .replaceAll('\r\n', '\n').trimEnd()
        .replace(/\{\{([\w-]+)\}\}/g, (_, key) => {
          if (Object.hasOwn(paths, key)) return placedOutline(paths[key], file)
          if (Object.hasOwn(values, key)) return values[key]
          throw new Error(`${file}: unknown CleanBC template value ${key}`)
        })
      const expected = source?.versions.find((version) => version.treatment === treatment)?.sha256
      if (createHash('sha256').update(xml).digest('hex') !== expected) {
        throw new Error(`${file}: generated SVG differs from the CleanBC source register`)
      }
      outputs.set(file, xml)
    }
  }
  return outputs
}

export function buildCleanbcArtwork(destination = publicArtwork) {
  // Validate every rendition before touching the public copies.
  const outputs = renderArtwork()
  mkdirSync(destination, { recursive: true })
  for (const [file, xml] of outputs) {
    const output = join(destination, file)
    if (existsSync(output) && readFileSync(output, 'utf8') === xml) continue
    const temporary = join(destination, `.${file}.${randomUUID()}.tmp`)
    try {
      writeFileSync(temporary, xml)
      renameSync(temporary, output)
    } finally {
      rmSync(temporary, { force: true })
    }
  }
  return outputs.size
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(`Built ${buildCleanbcArtwork()} CleanBC SVGs from shared artwork`)
}
