// Export: one SVG string in, a downloadable file out, in any of the generator's formats.
//
// SVG is the string itself. Rasters go through an <img> and a canvas. PDF goes through jsPDF and
// svg2pdf.js, loaded on demand since most visits never export.

export const FORMATS = {
  svg: { label: 'SVG', ext: 'svg', mime: 'image/svg+xml', vector: true, note: 'Vector. Self-contained; the photo is embedded.' },
  pdf: { label: 'PDF', ext: 'pdf', mime: 'application/pdf', vector: true, note: 'Vector, page sized to the artwork.' },
  png: { label: 'PNG', ext: 'png', mime: 'image/png', alpha: true, note: 'Lossless raster.' },
  webp: { label: 'WebP', ext: 'webp', mime: 'image/webp', alpha: true, note: 'Small raster, transparency kept.' },
  jpeg: { label: 'JPEG', ext: 'jpg', mime: 'image/jpeg', alpha: false, note: 'No transparency; composited onto a background.' }
}
export const FORMAT_ORDER = ['svg', 'pdf', 'png', 'webp', 'jpeg']

/** Whether this browser can encode the format. Vector formats always can. */
export const isFormatSupported = (format) => {
  const spec = FORMATS[format]
  if (spec.vector) return true
  try {
    const canvas = document.createElement('canvas')
    canvas.width = canvas.height = 1
    return canvas.toDataURL(spec.mime).startsWith(`data:${spec.mime}`)
  } catch {
    return false
  }
}

const blobToDataUrl = (blob) => new Promise((resolve, reject) => {
  const reader = new FileReader()
  reader.onload = () => resolve(reader.result)
  reader.onerror = reject
  reader.readAsDataURL(blob)
})

const dataUrlCache = new Map()

/** Replaces every external <image> reference in the element with a data URI, so the file stands alone. */
const inlineImages = async (root) => {
  for (const image of root.querySelectorAll('image')) {
    const href = image.getAttribute('href') || image.getAttribute('xlink:href')
    if (!href || href.startsWith('data:')) continue
    if (!dataUrlCache.has(href)) {
      const blob = await (await fetch(href)).blob()
      dataUrlCache.set(href, await blobToDataUrl(blob))
    }
    image.setAttribute('href', dataUrlCache.get(href))
    image.removeAttribute('xlink:href')
  }
}

/**
 * The poster as a complete SVG document, from the live drawing on the stage: hotspots removed,
 * highlighting and dimming cleared, the full page restored, any photo embedded. `view` is the
 * drawing's own viewBox and `page` its size in inches.
 */
export const posterSvgString = async (svgEl, { view, page }) => {
  const clone = svgEl.cloneNode(true)
  clone.querySelector('#hotspots')?.remove()
  for (const el of clone.querySelectorAll('[style]')) el.removeAttribute('style')
  for (const el of clone.querySelectorAll('[class]')) {
    el.classList.remove('pv-active')
    if (!el.classList.length) el.removeAttribute('class')
  }
  clone.setAttribute('viewBox', `${view.x} ${view.y} ${view.w} ${view.h}`)
  clone.setAttribute('width', `${page.w}in`)
  clone.setAttribute('height', `${page.h}in`)
  clone.removeAttribute('preserveAspectRatio')
  await inlineImages(clone)
  return new XMLSerializer().serializeToString(clone)
}

const viewBoxOf = (svg) => {
  const m = /viewBox="([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)[ ,]+([-\d.]+)"/.exec(svg)
  return m ? { x: +m[1], y: +m[2], w: +m[3], h: +m[4] } : { x: 0, y: 0, w: 1, h: 1 }
}

const loadImage = (svg) => new Promise((resolve, reject) => {
  const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }))
  const img = new Image()
  img.onload = () => { URL.revokeObjectURL(url); resolve(img) }
  img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('The drawing could not be rasterised. Try a smaller width or the SVG.')) }
  img.src = url
})

/** Draws the SVG string at `width` pixels wide and encodes it. `background` is required for JPEG. */
export const rasterize = async (svg, { width, format, quality = 0.92, background = null }) => {
  const spec = FORMATS[format]
  const vb = viewBoxOf(svg)
  const height = Math.round(width * vb.h / vb.w)
  // Width/height attributes make the <img> decode at the requested size rather than the SVG's own.
  const doc = new DOMParser().parseFromString(svg, 'image/svg+xml')
  if (doc.querySelector('parsererror')) throw new Error('The drawing is not well-formed SVG.')
  doc.documentElement.setAttribute('width', String(width))
  doc.documentElement.setAttribute('height', String(height))
  const img = await loadImage(new XMLSerializer().serializeToString(doc))
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  if (!ctx) throw new Error('This browser refused a canvas that large. Try a smaller width.')
  if (background || !spec.alpha) {
    ctx.fillStyle = background || '#ffffff'
    ctx.fillRect(0, 0, width, height)
  }
  ctx.drawImage(img, 0, 0, width, height)
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, spec.mime, quality))
  if (!blob) throw new Error('The image could not be encoded. Try a smaller width.')
  return blob
}

/** Vector PDF, page sized in inches. */
export const toPdf = async (svg, { widthIn, heightIn }) => {
  const [{ jsPDF }, { svg2pdf }] = await Promise.all([import('jspdf'), import('svg2pdf.js')])
  const doc = new jsPDF({ orientation: widthIn > heightIn ? 'landscape' : 'portrait', unit: 'in', format: [widthIn, heightIn] })
  const el = new DOMParser().parseFromString(svg, 'image/svg+xml').documentElement
  // svg2pdf measures through the DOM, so the element is attached, off-screen, while it works.
  const holder = document.createElement('div')
  holder.style.cssText = 'position:fixed;left:-100000px;top:0;width:0;height:0;overflow:hidden'
  holder.appendChild(el)
  document.body.appendChild(holder)
  try {
    await svg2pdf(el, doc, { x: 0, y: 0, width: widthIn, height: heightIn })
  } finally {
    holder.remove()
  }
  return doc.output('blob')
}

/**
 * One call for every format. `inches` is the page size for PDF; rasters take `width` in pixels.
 */
export const exportSvg = async (svg, { format, width, inches, quality, background }) => {
  const spec = FORMATS[format]
  if (format === 'svg') return new Blob([svg], { type: spec.mime })
  if (format === 'pdf') return toPdf(svg, { widthIn: inches.w, heightIn: inches.h })
  return rasterize(svg, { width, format, quality, background })
}

export const downloadBlob = (blob, fileName) => {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = fileName
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 10000)
}

export const formatBytes = (n) => (n > 1e6 ? `${(n / 1e6).toFixed(1)} MB` : `${Math.round(n / 1e3)} KB`)
