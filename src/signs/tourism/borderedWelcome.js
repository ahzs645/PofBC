import { SIGNS } from '../catalogue.js'
import metrics from './super-natural-bordered.metrics.json' with { type: 'json' }

const id = 'super-natural-bordered'
const rows = [
  { key: 'slogan', label: 'Super, Natural', box: { x: 79, y: 35, w: 662, h: 125 },
    lede: 'The comma hangs below the first word. A wide gap separates it from the capital N in “Natural”.' },
  { key: 'province', label: 'British Columbia', box: { x: 32, y: 178, w: 757, h: 103 },
    lede: 'The province’s name forms the widest line on the board.' },
  { key: 'greeting', label: 'welcomes you', box: { x: 121, y: 289, w: 573, h: 113 },
    lede: 'The greeting sits close to the lower border. The y drops below the other letters in the last word.' }
]
const regions = rows.map(({ key }) => key)
const percent = (value) => value.toFixed(1) + '%'

export const BORDERED_WELCOME = {
  id, regions, order: ['overview', ...regions], spotlight: { keep: ['bordered-board', 'bordered-rule'] },
  parts: {
    overview: {
      label: 'Whole sign', box: SIGNS[id].view, pad: 0.06,
      panel: {
        eyebrow: 'Welcome signs · photographic reconstruction',
        heading: 'Super, Natural British Columbia welcomes you',
        lede: 'Three lines of blue serif lettering fill a pale, rounded roadside panel. The photograph shows bicycle gear across its lower-left corner. The date and location are unknown.',
        blocks: [
          { figure: 'overlap', basePhoto: 'photo',
            alt: 'The blue-bordered welcome sign at the angle it appears in the supplied roadside photograph.',
            caption: 'Pink shows the reconstructed lettering projected onto the original photograph. Move the slider to zero to see the photographed letters alone.' },
          { h: 'Lettering overlap with the photograph' },
          { facts: ['All lettering', ...rows.map(({ label }) => label)].map((label) => [label, percent(metrics.iouPercent[label])]) },
          'Four corners register the entire board to the camera image. The percentages give the area of letter ink shared by the drawing and photograph divided by the area covered by either, measured in the original 297 × 224 pixels. Only the three readable lines are scored.',
          `Across ${metrics.spacing.pairs} adjacent pairs, the centre-to-centre spacing in the projected drawing differs from the photograph by an average of ${metrics.spacing.meanAbsoluteErrorPixels} source pixels. The comparison follows each line at its photographed angle.`,
          `The board spans about 160 pixels in the photograph. Changing the ink cutoff gives overall overlap scores of ${percent(metrics.thresholdSensitivity[80])} and ${percent(metrics.thresholdSensitivity[92])}.`,
          { note: 'Each line is centred and typeset in TeX Gyre Termes Bold at the same size. The font supplies the letter widths, kerning and word spaces. The photograph leaves the original typeface, board proportions and paint colours uncertain.' },
          { links: [{ label: 'Flag-topped welcome sign', note: 'The same greeting beneath the Spirit of BC flag and stripes.',
            to: { view: 'signs', sign: 'super-natural' } }] }
        ]
      }
    },
    ...Object.fromEntries(rows.map(({ key, label, box, lede }) => [key, {
      label, box, layer: '#bordered-' + key, pad: 0.1,
      panel: { eyebrow: 'Lettering', heading: label, lede,
        blocks: [{ facts: [['Ink overlap with photograph', percent(metrics.iouPercent[label])]] }] }
    }]))
  }
}
