import { SIGNS } from '../catalogue.js'

const id = 'cheakamus-notice-to-anglers'
const regions = ['heading', 'closure', 'dates', 'credit', 'emblem']

export const FISH_WILDLIFE_SIGNS = {
  [id]: {
    id,
    order: ['overview', ...regions],
    regions,
    spotlight: { keep: ['ck-board'] },
    parts: {
      overview: {
        label: 'Whole sign',
        box: SIGNS[id].view,
        pad: 0.06,
        panel: {
          eyebrow: 'Fish & Wildlife Branch · historical sign',
          heading: SIGNS[id].title,
          lede: 'The branch posted this seasonal closure on the Cheakamus River. Anglers reading the board could locate the closed stretch by following the river upstream to the railway bridge.',
          blocks: [
            { facts: [
              ['Date of sign', 'Unknown'],
              ['Source', 'Supplied photograph and vector reconstruction'],
              ['Drawing', '1060 × 720 units. The physical dimensions are unknown.']
            ] },
            { note: 'This is an archival reconstruction. The photograph obscures parts of the wording, and the lettering and colours are approximate.' }
          ]
        }
      },
      heading: {
        label: 'Heading and river name',
        box: { x: 174, y: 70, w: 818, h: 257 },
        layer: '#ck-red-header, #ck-notice-heading, #ck-river-name',
        hit: 'shape',
        panel: {
          eyebrow: 'Headline',
          heading: 'Notice to Anglers',
          lede: 'Rounded white serifs carry the headline across the vermilion band. The river name is centred on the board below it, in dark sans-serif capitals.'
        }
      },
      closure: {
        label: 'River boundary',
        box: { x: 68, y: 345, w: 905, h: 153 },
        layer: '#ck-closed-line, #ck-upstream-line, #ck-railway-line, #ck-mile-number, #ck-from-line',
        panel: {
          eyebrow: 'River boundary',
          heading: 'From this point to the railway bridge',
          lede: 'The notice describes the closed stretch as running upstream from the board to the British Columbia Railway bridge. The reconstruction reads the mile marker as “(MILE 56.6)”.',
          blocks: [{ note: 'Parts of “FROM THIS POINT” and “BRITISH COLUMBIA” are hidden. The punctuation of the mile marker is also uncertain.' }]
        }
      },
      dates: {
        label: 'Closure dates',
        box: { x: 68, y: 506, w: 555, h: 41 },
        layer: '#ck-start-date, #ck-end-date',
        panel: {
          eyebrow: 'Season',
          heading: 'April 1 to June 30',
          lede: 'The two dates share a baseline. The heavier June lettering has a distinctive J with a bar across the top, drawn from the visible shape in the photograph.'
        }
      },
      credit: {
        label: 'Branch credit',
        box: { x: 98, y: 586, w: 864, h: 24 },
        layer: '#ck-branch-credit',
        panel: {
          eyebrow: 'Issuer',
          heading: 'British Columbia Fish & Wildlife Branch',
          lede: 'A single line of small serif capitals names the issuing branch. The last part of the credit is inferred where the photograph obscures it.'
        }
      },
      emblem: {
        label: 'F&W emblem',
        box: { x: 69, y: 69, w: 101, h: 177 },
        layer: '#ck-fw-emblem',
        panel: {
          eyebrow: 'Branch emblem',
          heading: 'The F&W oval',
          lede: 'At the left of the headline, the gold-and-dark emblem pairs the oval symbol with the F&W initials. The sign uses the gallery’s reconstructed emblem in the sign’s own colours.',
          blocks: [{ links: [{
            label: 'Fish and Wildlife emblem',
            note: 'Gallery · Recreation and Conservation',
            to: { view: 'gallery', logos: 'recreation-conservation', mark: 'drc-fw-oval-1973' }
          }] }]
        }
      }
    }
  }
}
