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
const markPath = new URL('../public/identity-recreation-conservation/drc-dogwood-oval-1970.svg', import.meta.url)
const mark = parse(readFileSync(markPath, 'utf8')).documentElement

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
drawing.getElementsByTagName('desc')[0].textContent = 'Historical reconstruction with the bc-guilloche frame, fitted QT Linoscroll and Lato Bold lettering, and the gallery’s dogwood oval fitted to the 1961 specimen. The ministerial signature is blank.'
drawing.insertBefore(doc.importNode(paper, true), drawing.getElementsByTagName('defs')[0])
for (const group of groups) drawing.appendChild(doc.importNode(group, true))

// Fit the gallery vector to the printed oval's outer edge in the 722 × 550 specimen.
const [radiusX, radiusY] = [60.3, 77.5]
const seal = doc.createElementNS(drawing.namespaceURI, 'g')
seal.setAttribute('id', 'certificate-dogwood-seal')
seal.setAttribute('aria-label', 'British Columbia Department of Recreation and Conservation dogwood oval')
seal.setAttribute('transform', 'translate(86.7 449.7) rotate(-1.1)')

// The specimen leaves a narrow paper edge between the seal and the guilloché.
const knockout = doc.createElementNS(drawing.namespaceURI, 'ellipse')
knockout.setAttribute('rx', String(radiusX + 1.5))
knockout.setAttribute('ry', String(radiusY + 1.5))
knockout.setAttribute('fill', paper.getAttribute('fill'))
seal.appendChild(knockout)

const oval = mark.getElementsByTagName('ellipse')[0]
const placedMark = doc.createElementNS(drawing.namespaceURI, 'g')
const scaleX = (radiusX / Number(oval.getAttribute('rx'))).toFixed(6)
const scaleY = (radiusY / Number(oval.getAttribute('ry'))).toFixed(6)
placedMark.setAttribute('transform', `scale(${scaleX} ${scaleY}) translate(-${oval.getAttribute('cx')} -${oval.getAttribute('cy')})`)
for (const layer of Array.from(mark.childNodes)) {
  if (layer.nodeType === 1 && !['title', 'desc'].includes(layer.localName)) placedMark.appendChild(doc.importNode(layer, true))
}

const specimenInks = { '#1b5032': '#00532b', '#f1f1e6': '#ebf0d4' }
for (const element of Array.from(placedMark.getElementsByTagName('*'))) {
  for (const attribute of ['fill', 'stroke']) {
    const ink = specimenInks[element.getAttribute(attribute)?.toLowerCase()]
    if (ink) element.setAttribute(attribute, ink)
  }
}
seal.appendChild(placedMark)
drawing.appendChild(seal)

const svg = new XMLSerializer().serializeToString(drawing)
writeFileSync(new URL('../public/certificates/certificate-of-training-1961-reconstruction.svg', import.meta.url), `${svg}\n`)
