// Pass certificate-font-analysis/certificate-1961-modulated-fonts.svg from the supplied
// 1961-certificate-font-overlap-package. The specimen is already registered at 722 × 550.
import { readFileSync, writeFileSync } from 'node:fs'
import { DOMParser, XMLSerializer } from '@xmldom/xmldom'
import { generateBorder } from '../src/certificates/bc-guilloche-generator.mjs'

const [sourcePath] = process.argv.slice(2)
if (!sourcePath) throw new Error('Provide the path to certificate-1961-modulated-fonts.svg')

const parse = (svg) => new DOMParser().parseFromString(svg, 'image/svg+xml')
const source = parse(readFileSync(sourcePath, 'utf8')).documentElement
const drawing = parse(generateBorder()).documentElement

if (source.getAttribute('viewBox') !== drawing.getAttribute('viewBox')) {
  throw new Error('The lettering and border must share the 722 × 550 specimen coordinates')
}

const paper = Array.from(source.childNodes).find((node) => node.localName === 'rect')
const groups = ['printed-lettering', 'historic-recipient-and-date', 'facsimile-label']
  .map((id) => source.ownerDocument.getElementById(id))
if (paper?.parentNode !== source || groups.some((group) => group?.parentNode !== source)) {
  throw new Error('Expected the original paper and all three lettering groups')
}

const doc = drawing.ownerDocument
drawing.getElementsByTagName('title')[0].textContent = '1961 Certificate of Training · Historical reconstruction'
drawing.getElementsByTagName('desc')[0].textContent = 'The bc-guilloche frame surrounds the supplied QT Linoscroll and Lato Bold outlines and the historic recipient and date. The reconstruction label is retained. The seal and signature are omitted.'
drawing.insertBefore(doc.importNode(paper, true), drawing.getElementsByTagName('defs')[0])
for (const group of groups) drawing.appendChild(doc.importNode(group, true))

const svg = new XMLSerializer().serializeToString(drawing)
writeFileSync(new URL('../public/certificates/certificate-of-training-1961-reconstruction.svg', import.meta.url), `${svg}\n`)
