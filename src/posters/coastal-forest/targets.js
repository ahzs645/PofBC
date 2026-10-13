// The coastal poster's second export: the logo from its studio.

import { POSTER_BLACK } from './logo/renderLogo.js'

export const logoTarget = ({ getSvg, tag }) => ({
  id: 'logo',
  label: 'The logo as configured',
  getSvg,
  inches: (aspect) => ({ w: 8, h: 8 * aspect }),
  widths: [512, 1024, 2048, 4096],
  backgrounds: [
    { name: 'Transparent', value: null },
    { name: 'Poster black', value: POSTER_BLACK },
    { name: 'White', value: '#ffffff' }
  ],
  vectorNote: (format) => (format === 'pdf' ? 'An 8 inch wide page, vector, type already outlined.' : 'Type outlined; nothing in the file refers to a font.'),
  fileName: (spec, width) => `bc-logo-${tag}${width ? `-${width}` : ''}.${spec.ext}`
})
