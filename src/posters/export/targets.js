// What a poster can export, described for ExportDialog.

const DPI = [50, 100, 150, 200, 300]
const round = (value) => Math.round(value / 100) * 100

/**
 * The poster itself, at its own page size. `meta` is its catalogue card; `tag` names a change made
 * on the stage (a swapped logo, say), which goes into the label and the file name.
 */
export const posterTarget = ({ meta, getSvg, tag, noun = 'poster', changed = 'with the swapped logo' }) => {
  const { page } = meta
  const widths = [...new Set(DPI.map((dpi) => round(page.w * dpi)))]
  const photo = meta.id === 'coastal-forest'
  return {
    id: 'poster',
    label: tag ? `The ${noun}, ${changed}` : `The ${noun}`,
    getSvg,
    inches: page,
    dpiBase: page.w,
    widths,
    backgrounds: meta.background
      ? [{ name: 'Its own paper', value: meta.background }]
      : [{ name: 'Transparent', value: null }, { name: 'White', value: '#ffffff' }],
    largeNote: { from: 4800, text: `Large canvases can fail in Safari. Chrome and Firefox handle ${widths.at(-1)} px (300 dpi at ${page.w} × ${page.h} in).` },
    vectorNote: (format) => (format === 'pdf'
      ? `A ${page.w} × ${page.h} inch page, no bleed or crop marks. ${photo ? 'The photograph is embedded; the lettering and logo stay vector.' : 'Everything stays vector; the lettering is already outlined.'}`
      : photo ? 'The outlined master with the photograph embedded as a data URI, so the file stands alone.' : 'The outlined master; nothing in the file refers to a font or an image.'),
    fileName: (spec, width) => `${meta.id}${tag ? `-${tag}` : ''}${width ? `-${width}` : ''}.${spec.ext}`
  }
}
