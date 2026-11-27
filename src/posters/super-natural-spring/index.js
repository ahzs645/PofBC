import svgRaw from './spring-visitors.svg?raw'
import reference from './reference.png'
import { SPRING_POSTER } from './poster.js'

export const load = () => ({
  ...SPRING_POSTER,
  svgRaw,
  reference: {
    src: reference,
    box: SPRING_POSTER.parts.overview.box,
    caption: 'The supplied 1462 × 1021 pixel reference crop of the 1984 advertisement. The image clips some edge content and does not establish the original page dimensions; the reconstruction restores the complete headline within a small inset.'
  },
  variations: {
    label: 'Reconstruction photograph',
    options: [
      {
        id: 'vintage', label: 'Vintage scene', show: '#spring-photo-vintage',
        note: 'The supplied “Vintage Orcas in British Columbia Waters” scene, fitted to the reference. This is a modern reconstruction image.'
      },
      {
        id: 'gemini', label: 'Alternate scene', show: '#spring-photo-gemini',
        changed: 'with the alternate supplied scene',
        note: 'The supplied Gemini-generated scene, cropped to the same picture area. This is an alternate reconstruction, not an original print variant.'
      }
    ]
  }
})
