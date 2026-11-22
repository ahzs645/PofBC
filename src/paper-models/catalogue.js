// Paper models: fold-up models made in PackCAD (vendor/packcad), each a printable sheet whose PDF
// also carries the editable project, so the same file prints and reopens in PackCAD.
//
// The files are in public/paper-models/, as exported: the .packcad.pdf to print (and to reopen in
// PackCAD), and the .packcad.json the viewer opens, which is the same project the PDF carries,
// extracted, so the page need not parse a PDF to show it. paperModels.test.js holds the numbers
// below to the files.

/** PackCAD as published, for opening a downloaded project in the full editor. */
export const PACKCAD_EDITOR_URL = 'https://projects.ahmadjalil.com/packcad/'

export const PAPER_MODEL_SERIES = [
  {
    id: 'gallery-in-transit',
    label: 'Gallery In Transit',
    summary: 'Two fold-up buses: the BC Transit livery in red and white, and the original Gallery In Transit bus in green, orange, blue and yellow.',
    // As the export that brought the two in says of both.
    note: 'Geometry and the folding motion were checked numerically; no physical paper prototype has been tested. Dry-fit before gluing.',
    models: [
      {
        id: 'bc-transit',
        title: 'BC Transit bus',
        livery: 'Red and white',
        dir: 'gallery-in-transit',
        file: 'bc-transit-foldable',
        sheetMm: [297, 199.837],
        panels: 31,
        stages: 7,
        board: 'Chipboard, 0.1 mm',
        instructions: [
          'Print at 100% (actual size) so the sheet keeps its dimensions.',
          'Continuous outer lines are the cut; dotted lines are folds.',
          'Keep the wheels attached to the side walls.'
        ],
        // The roof logo is in Logos as its own entry, cut from this model's printable PDF.
        related: [
          { label: 'Its roof logo in Logos', to: { view: 'gallery', logos: 'bc-transit', mark: 'bct-double-arrow-paper-model' } },
          { label: 'BC Transit in Logos', to: { view: 'gallery', subject: 'bc-transit' } }
        ],
        sha256: {
          json: '364cb28e429f121875d54b2e84de9d5f1cb5ed21139a7698277ec6a2c8b9cbfd',
          pdf: 'eb361167ce55aa5952a24fd2a4f3880a61181b62ff09184fe59d4987f95872be'
        }
      },
      {
        id: 'gallery-in-transit-original',
        title: 'Gallery In Transit bus',
        livery: 'Green, orange, blue and yellow',
        dir: 'gallery-in-transit',
        file: 'gallery-in-transit-original-foldable',
        sheetMm: [279.4, 175.26],
        panels: 27,
        stages: 5,
        board: 'Chipboard, 0.1 mm',
        instructions: [
          'Print at 100% (actual size) so the sheet keeps its dimensions.',
          'Continuous outer lines are the cut; dotted lines are folds.',
          'Keep the wheels attached to the side walls.',
          'The bottom is left open on purpose.'
        ],
        related: [{ label: 'BC Transit in Logos', to: { view: 'gallery', subject: 'bc-transit' } }],
        sha256: {
          json: 'ad78bbaa83a28958b240fa7a385bf2fa259f39d9d22bce5fb7dc6856edf8a63e',
          pdf: '33c7ce48f58e350af813ad0fd5d1e5037ac6e3079e9e1e5b547203bedcd85de1'
        }
      }
    ]
  }
]

export const PAPER_MODELS = PAPER_MODEL_SERIES.flatMap((series) => series.models.map((model) => ({ ...model, series })))

/** A model's files, as paths under public/ (and so under the site's base URL). */
export const filesOf = (model) => ({
  json: `paper-models/${model.dir}/${model.file}.packcad.json`,
  pdf: `paper-models/${model.dir}/${model.file}.packcad.pdf`
})

const mm = (value) => (Math.round(value * 10) / 10).toLocaleString('en-CA')
/** "297 × 199.8 mm" */
export const sheetWords = ([width, height]) => `${mm(width)} × ${mm(height)} mm`
