import svgRaw from './spring-visitors.svg?raw'
import reference from './reference.png'
import { SPRING_POSTER } from './poster.js'

export const load = () => ({
  ...SPRING_POSTER,
  svgRaw,
  reference: {
    src: reference,
    box: SPRING_POSTER.parts.overview.box,
    caption: 'The supplied 620 × 418 pixel reference of the 1984 advertisement, also reproduced by Concordia University in 2021.'
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
