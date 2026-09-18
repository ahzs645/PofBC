// Exporting a whole set at once.
//
// Handing someone "the logo" usually means handing them every lockup they might need, in the
// formats their tools want, at the sizes their layouts call for. Doing that one download at a time
// is the tedious part of the job, so this renders the cross-product in one pass and zips it.
//
// Every file goes through the same renderLogoBlob() as a single download, so a bundled asset is
// byte-for-byte the asset someone would have got on their own.

import { EXPORT_FORMATS, buildFileName, downloadBlob, renderLogoBlob } from './exportLogo.js'
import { LAYOUTS, LAYOUT_ORDER } from '../logo/layouts.js'

/** What a bundle contains unless told otherwise: all three lockups, vector plus a couple of PNGs. */
export const BUNDLE_DEFAULTS = {
  layouts: [...LAYOUT_ORDER],
  formats: ['svg', 'pdf', 'png'],
  sizes: [1024, 2048]
}

const slugify = (value) => String(value ?? '')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '')
  .slice(0, 60)

/**
 * Every file a bundle will contain, in the order it will be rendered.
 *
 * Separated from the rendering so the UI can show the count and the file list before committing to
 * the work — a careless tick of every box is 60 renders, and it is better to see that first.
 *
 * @returns {Array<{layout: string, format: string, pixelWidth?: number, path: string}>}
 */
export const planBundle = ({
  layouts = BUNDLE_DEFAULTS.layouts,
  formats = BUNDLE_DEFAULTS.formats,
  sizes = BUNDLE_DEFAULTS.sizes,
  ...lockup
} = {}) => {
  const entries = []
  const folder = bundleName(lockup)

  // The current era has one mark per ministry, not a choice of lockups, so it bundles formats and
  // sizes only and everything lands in one folder.
  const chosen = lockup.era === 'current'
    ? [null]
    : LAYOUT_ORDER.filter((id) => layouts.includes(id))

  for (const layout of chosen) {
    for (const format of Object.keys(EXPORT_FORMATS).filter((id) => formats.includes(id))) {
      const spec = EXPORT_FORMATS[format]
      // A vector file has no size; a raster one is rendered once per requested width.
      const widths = spec.vector ? [undefined] : (sizes.length ? sizes : BUNDLE_DEFAULTS.sizes)

      for (const pixelWidth of widths) {
        const name = buildFileName({ ...lockup, layout, format })
        const sized = pixelWidth
          ? name.replace(/\.(\w+)$/, `-${pixelWidth}.$1`)
          : name

        const where = layout ? `${folder}/${layout}/${sized}` : `${folder}/${sized}`
        entries.push({ layout, format, pixelWidth, path: where })
      }
    }
  }

  return entries
}

/** The folder everything sits under, so unzipping leaves one thing behind rather than three. */
export const bundleName = (lockup = {}) => (
  lockup.era === 'current'
    ? ['bc', slugify(lockup.currentMinistry), lockup.language].filter(Boolean).join('-')
    : ['bc', slugify(lockup.ministry) || 'wordmark'].filter(Boolean).join('-')
)

const FORMAT_NOTES = {
  svg: 'Vector. Best for the web and for anything that will be resized.',
  pdf: 'Vector, print-ready, page sized to the artwork.',
  png: 'Raster with transparency, at the pixel width in the filename.',
  webp: 'Raster with transparency, smaller than PNG, for the web.',
  jpeg: 'Raster without transparency; composited onto white.'
}

// A plain-text note travels with the bundle. Someone opening this a year from now should not have
// to guess what the folders are, or which file to hand a printer.
const readme = (lockup, entries) => {
  const layouts = [...new Set(entries.map((entry) => entry.layout))]
  // Only what is actually in the box: a legend describing files that are not there is worse than
  // no legend at all.
  const formats = [...new Set(entries.map((entry) => entry.format))]

  return [
    'Province of British Columbia — logo bundle',
    '='.repeat(42),
    '',
    `Ministry:    ${lockup.ministry || '(wordmark only)'}`,
    lockup.program ? `Second line: ${lockup.program}` : null,
    `Mark:        ${lockup.markColor}`,
    `Text:        ${lockup.textColor}`,
    `Background:  ${lockup.background === 'none' ? 'transparent' : lockup.background}`,
    lockup.outlineText ? 'Type:        converted to outlines' : 'Type:        live text, font embedded',
    '',
    ...(layouts.filter(Boolean).length
      ? ['Lockups', '-------', ...layouts.filter(Boolean).map((id) => `  ${id.padEnd(12)} ${LAYOUTS[id].description}`), '']
      : ['This is the Province\'s official ministry mark, used exactly as published.', '']),
    'Formats',
    '-------',
    ...formats.map((id) => `  .${EXPORT_FORMATS[id].extension.padEnd(5)} ${FORMAT_NOTES[id]}`),
    '',
    `${entries.length} files.`,
    '',
    'The mark is a provincial symbol; its use is governed by the Government of British Columbia.',
    ''
  ].filter((line) => line !== null).join('\n')
}

/**
 * Renders a bundle and returns it as a zip Blob.
 *
 * @param {object} options            Everything renderLogoBlob() accepts, plus layouts/formats/sizes.
 * @param {(progress: {completed: number, total: number, path: string}) => void} [onProgress]
 * @param {AbortSignal} [options.signal]  Abandons the run between files.
 */
export const renderBundle = async ({ signal, ...options } = {}, onProgress) => {
  const { zip } = await import('fflate')

  const entries = planBundle(options)
  if (!entries.length) throw new Error('Nothing selected to export.')

  const files = {}
  let completed = 0

  for (const entry of entries) {
    if (signal?.aborted) throw new DOMException('Export cancelled', 'AbortError')

    const blob = await renderLogoBlob({
      ...options,
      ...(entry.layout ? { layout: entry.layout } : {}),
      format: entry.format,
      pixelWidth: entry.pixelWidth
    })

    // Already-compressed formats are stored rather than deflated: it saves the time and achieves
    // essentially nothing, since PNG, WebP and JPEG are compressed streams already.
    const level = EXPORT_FORMATS[entry.format].vector ? 6 : 0
    files[entry.path] = [new Uint8Array(await blob.arrayBuffer()), { level }]

    completed += 1
    onProgress?.({ completed, total: entries.length, path: entry.path })
  }

  files[`${bundleName(options)}/README.txt`] = [
    new TextEncoder().encode(readme(options, entries)),
    { level: 6 }
  ]

  const zipped = await new Promise((resolve, reject) => {
    zip(files, { level: 6 }, (error, data) => (error ? reject(error) : resolve(data)))
  })

  // A fresh copy of the bytes: fflate may hand back a view onto a larger pooled buffer, and Blob
  // would otherwise capture the whole thing.
  return new Blob([zipped.slice()], { type: 'application/zip' })
}

/** Renders a bundle and downloads it. Returns the filename it saved. */
export const exportBundle = async (options = {}, onProgress) => {
  const blob = await renderBundle(options, onProgress)
  const fileName = `${bundleName(options)}-logos.zip`
  downloadBlob(blob, fileName)
  return fileName
}
