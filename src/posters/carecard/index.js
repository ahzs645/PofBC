import svgRaw from './new-carecard.svg?raw'
import reference from './reference.webp'
import proof from './overlap.png'
import paints from './paints.json'
import { CARECARD_POSTER } from './poster.js'
import sepiaPdf from '../../../artwork/posters/carecard/carecard-sepia.pdf?url'
import colourPdf from '../../../artwork/posters/carecard/carecard-colour.pdf?url'
import grayPdf from '../../../artwork/posters/carecard/carecard-grayscale.pdf?url'

export const load = () => ({
  ...CARECARD_POSTER,
  svgRaw,
  figures: { overlap: proof },
  reference: {
    src: reference, box: CARECARD_POSTER.parts.overview.box,
    caption: 'The supplied 891 × 1215 pixel screenshot in its original position.'
  },
  variations: {
    label: 'Print edition', toolbar: true,
    options: [
      { id: 'sepia', label: 'Sepia', printPdf: sepiaPdf, note: 'Warm paper and dark ink from the Forest Service newspaper reconstruction.' },
      { id: 'colour', label: 'Colour', printPdf: colourPdf, swap: paints.colour, changed: 'in colour', note: 'Catalogue card colours and the generator’s three-colour flag on white stock. An interpretive edition of the newspaper ad.' },
      { id: 'grayscale', label: 'Black ink', printPdf: grayPdf, swap: paints.grayscale, changed: 'in black ink', note: 'Single-channel grayscale for printing on white or tinted paper.' }
    ]
  }
})
