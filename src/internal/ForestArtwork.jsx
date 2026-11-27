// The Forests designs' artwork: Forest Oval's recipes, rendered live, and the supplied drawings,
// recoloured. One component draws either, wherever a design is shown — the index's cover, the
// department's tiles, a design's own page — and hands its finished SVG to the page's download.

import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { loadLetteringRuntime } from '../../vendor/forestoval/shared-primitives/live-lettering/src/runtime.ts'
import mountainRidge from '../../vendor/forestoval/shared-primitives/bc-ministry-v5/scenes/tree-parts/mountain-ridge.svg?raw'
import mountainBase from '../../vendor/forestoval/shared-primitives/bc-ministry-v5/scenes/tree-parts/mountain-base.svg?raw'

// Forest Oval's single-colour recreation retains both mountain edges as lines.
// Its engine recolours the filled mountain to paper; restore the same supplied
// line primitives behind the tree, in the source scene's own coordinate system.
const addMountainLines = (svg, artwork, ink) => {
  const parser = new DOMParser()
  const source = parser.parseFromString(`<svg xmlns="http://www.w3.org/2000/svg">${artwork}</svg>`, 'image/svg+xml')
  const mountain = source.querySelector('path[fill="#0091c4"]')
  const paths = svg.querySelectorAll('[data-layer="scene"] path, defs [data-primitive="scene-tree"] path')
  const target = [...paths].find((path) => path.getAttribute('d') === mountain?.getAttribute('d'))
  if (!target) return
  const lines = [mountainRidge, mountainBase].map((primitive) => {
    const path = document.importNode(parser.parseFromString(primitive, 'image/svg+xml').querySelector('path'), true)
    path.removeAttribute('id')
    path.setAttribute('stroke', ink)
    path.setAttribute('data-primitive', 'mountain-line')
    return path
  })
  target.after(...lines)
}

// In dark mode a logo on the default white paper moves onto a dark tile. Artwork drawn only in black
// and white is inverted there (exactly: black becomes white); artwork in dark inks alone sits in a
// light well; colour artwork keeps its colours, with a light edge so its black outlines still read
// (internal.css). A version with a background of its own keeps it, and so does every version on the
// preview's white background.
const PAPER = new Set(['#fff', '#ffffff', 'white'])
const PLAIN = new Set(['#000', '#000000', 'black', '#fff', '#ffffff', 'white', 'none', 'transparent', 'currentcolor'])
// A one-ink study drawn in a near-black or deep green would vanish on the dark tile, and inverting a
// colour would change the artwork, so that ink is given a light well to sit in instead.
const isDark = (colour) => {
  const hex = colour.toLowerCase().match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/)?.[1]
  if (!hex) return false
  const full = hex.length === 3 ? [...hex].map((digit) => digit + digit).join('') : hex
  const [r, g, b] = [0, 2, 4].map((at) => parseInt(full.slice(at, at + 2), 16) / 255)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.35
}
const inkOf = (colours) => {
  const all = [...colours].map((colour) => colour.toLowerCase())
  if (all.every((colour) => PLAIN.has(colour))) return 'mono'
  // White beside the dark ink means the drawing carries its own dark ground (a reversed study).
  const white = all.some((colour) => ['#fff', '#ffffff', 'white'].includes(colour))
  const inks = all.filter((colour) => !PLAIN.has(colour))
  return !white && inks.every(isDark) ? 'dark' : 'colour'
}
const coloursOfMarkup = (markup) => new Set([...markup.matchAll(/(?:fill|stroke)(?:="|:\s*)(#[0-9a-fA-F]{3,6}|[a-z]+)/g)].map((match) => match[1]))
const coloursOfElement = (root) => {
  const colours = new Set()
  for (const element of root.querySelectorAll('*')) {
    for (const attribute of ['fill', 'stroke']) if (element.getAttribute(attribute)) colours.add(element.getAttribute(attribute))
    for (const match of (element.getAttribute('style') ?? '').matchAll(/(?:fill|stroke)\s*:\s*([^;]+)/g)) colours.add(match[1].trim())
  }
  return colours
}
const tile = (background, ink, white) => ({
  style: { '--tile': background },
  'data-paper': (!white && PAPER.has(String(background).toLowerCase())) || undefined,
  'data-ink': ink ?? undefined
})

const Failure = ({ decorative, retry }) => decorative
  ? <span>Logo unavailable</span>
  : <span role="alert">Could not load this logo. <button type="button" onClick={retry}>Retry</button></span>

// Render the reference presets directly, without the editor, its options or browser drafts.
const OvalLogo = ({ preset, name, decorative, theme, colours, composition, background = '#fff', white, onReady }) => {
  const host = useRef(null)
  const [status, setStatus] = useState('loading')
  const [attempt, setAttempt] = useState(0)
  const [ink, setInk] = useState(null)
  useEffect(() => {
    let disposed = false
    setStatus('loading')
    const render = async () => {
      const runtime = await loadLetteringRuntime()
      const { P, E } = runtime
      const [kabel] = await E.ensureFonts(['kabel-black'], false)
      const state = E.recipeState(preset, {
        textFit: 'reference-calibrated',
        treeLettering: kabel?.status === 'ready' ? 'kabel-black' : 'reference-v2',
        autoProfile: true,
        separatorPlacement: 'follow-text',
        fanOut: true,
        centreInRing: true
      })
      let result = await E.render({
        ...state,
        ...(theme ? { theme } : {}),
        ...(colours ? { colours } : {})
      })
      if (composition === 'airtanker-package') {
        const { AIRTANKER } = await import('../../vendor/forestoval/shared-primitives/live-lettering/src/badges/airtanker.ts')
        result = await AIRTANKER.compose(result, runtime, null)
      }
      if (disposed) return
      const { svg } = result
      // The composition repeats its diamond source twice. Its duplicate IDs
      // are unnecessary on the instances; keep one target for each source ID.
      if (composition) {
        const ids = new Set()
        for (const element of svg.querySelectorAll('[id]')) {
          if (ids.has(element.id)) element.removeAttribute('id')
          else ids.add(element.id)
        }
      }
      if (preset === 'forest-service' && theme === 'mono') {
        addMountainLines(svg, E.ART.treeInner, result.state.colours.ink ?? P.THEMES[result.state.theme].ink)
      }
      // These are catalogue specimens, not clickable text fields.
      svg.querySelectorAll('[data-live-text]').forEach((run) => {
        run.removeAttribute('tabindex')
        run.removeAttribute('role')
      })
      svg.setAttribute('role', 'img')
      svg.removeAttribute('aria-labelledby')
      svg.setAttribute('aria-label', `${name} oval logo`)
      svg.setAttribute('focusable', 'false')
      host.current.replaceChildren(svg)
      setInk(inkOf(coloursOfElement(svg)))
      setStatus('ready')
      // Forest Oval's own exports: an SVG whose lettering stays live text naming local fonts (the
      // font files are not redistributed), and a PNG drawn with the fonts this page loaded.
      onReady?.({
        svg,
        live: {
          svg: () => E.serialise(result).replace(/<svg\b[^>]*>/, (tag) => tag.replace(/ (?:role|aria-label|focusable)="[^"]*"/g, '')),
          png: (width) => E.png(result, width)
        }
      })
    }
    render().catch(() => { if (!disposed) setStatus('error') })
    return () => { disposed = true }
  }, [preset, name, attempt, theme, colours, composition])

  return (
    <span className="internal-logos__artwork" {...tile(background, ink, white)} aria-hidden={decorative || undefined}>
      <span className="internal-logos__svg" ref={host} />
      {status === 'loading' && <span role="status">Loading logo…</span>}
      {status === 'error' && <Failure decorative={decorative} retry={() => setAttempt((value) => value + 1)} />}
    </span>
  )
}

// Some designs are supplied drawings rather than Forest Oval recipes: recoloured by mapping their own
// colours to new ones, with every id prefixed per copy so a clip path still finds its own shape
// when several copies share a page. They are fetched when first shown, since the engraved seal
// alone is larger than the rest of this view.
const DRAWINGS = {
  'forest-service-lands-department.svg': () => import('./forest-service-lands-department.svg?raw'),
  'forest-service-emblem.svg': () => import('./forest-service-emblem.svg?raw'),
  'forest-service-emblem-lettered.svg': () => import('./forest-service-emblem-lettered.svg?raw'),
  'forest-service-emblem-one-ink.svg': () => import('./forest-service-emblem-one-ink.svg?raw'),
  'forest-service-emblem-three-islands-separated.svg': () => import('./forest-service-emblem-three-islands-separated.svg?raw'),
  'forest-service-emblem-three-islands-green.svg': () => import('./forest-service-emblem-three-islands-green.svg?raw'),
  'forest-service-emblem-reverse.svg': () => import('./forest-service-emblem-reverse.svg?raw'),
  'forest-service-green-gold.svg': () => import('./forest-service-green-gold.svg?raw'),
  'forest-service-yellow-sky.svg': () => import('./forest-service-yellow-sky.svg?raw'),
  'forest-service-one-ink-oval.svg': () => import('./forest-service-one-ink-oval.svg?raw')
}
const fetched = new Map()

const useDrawing = (artwork, attempt) => {
  const [state, setState] = useState(() => ({ svg: fetched.get(artwork) ?? null, failed: false }))
  useEffect(() => {
    if (fetched.has(artwork)) { setState({ svg: fetched.get(artwork), failed: false }); return undefined }
    let gone = false
    setState({ svg: null, failed: false })
    DRAWINGS[artwork]()
      .then(({ default: svg }) => { fetched.set(artwork, svg); if (!gone) setState({ svg, failed: false }) })
      .catch(() => { if (!gone) setState({ svg: null, failed: true }) })
    return () => { gone = true }
  }, [artwork, attempt])
  return state
}

const drawingMarkup = ({ svg, recolour = {}, name, prefix }) => svg
  .replace(/<\?xml[^>]*>\s*/, '')
  .replace(/<title[\s\S]*?<\/title>\s*/, '')
  .replace(/<desc[\s\S]*?<\/desc>\s*/, '')
  .replace(/<svg[^>]*>/, (tag) => tag.replace(/ (?:width|height|aria-labelledby|role)="[^"]*"/g, '').replace('<svg', `<svg role="img" aria-label="${name}" focusable="false"`))
  .replace(/ id="([^"]+)"/g, (_, id) => ` id="${prefix}-${id}"`)
  .replace(/url\(#([^)]+)\)/g, (_, id) => `url(#${prefix}-${id})`)
  .replace(/(fill|stroke)="(#[0-9a-fA-F]{6})"/g, (_, attribute, hex) => `${attribute}="${recolour[hex.toUpperCase()] ?? hex}"`)

const DrawingLogo = ({ artwork, recolour, padding, name, decorative, background = '#fff', white, onReady }) => {
  const prefix = `drawing${useId().replace(/[^a-zA-Z0-9]/g, '')}`
  const [attempt, setAttempt] = useState(0)
  const host = useRef(null)
  const { svg, failed } = useDrawing(artwork, attempt)
  const markup = useMemo(() => svg && drawingMarkup({ svg, recolour, name, prefix }), [svg, recolour, name, prefix])
  const ink = useMemo(() => (markup ? inkOf(coloursOfMarkup(markup)) : null), [markup])
  useEffect(() => {
    const drawn = markup && host.current?.querySelector('svg')
    if (drawn) onReady?.({ svg: drawn })
  }, [markup])
  return (
    <span className="internal-logos__artwork" {...tile(background, ink, white)} aria-hidden={decorative || undefined}>
      {markup && <span ref={host} className="internal-logos__svg" style={{ padding }} dangerouslySetInnerHTML={{ __html: markup }} />}
      {!markup && !failed && <span role="status">Loading logo…</span>}
      {failed && <Failure decorative={decorative} retry={() => setAttempt((value) => value + 1)} />}
    </span>
  )
}

/**
 * A Forests design, or one version of it: a supplied drawing when it names one, else its Forest
 * Oval recipe (a design's own id is its recipe).
 *
 * @param {object} props
 * @param {object} props.item A design from FOREST_LOGOS, or a version from variantsFor().
 * @param {string} props.name What the artwork is called for a screen reader.
 * @param {boolean} [props.decorative] Hidden from a screen reader: its card names it.
 * @param {boolean} [props.white] On the preview's white background, whatever the theme.
 * @param {(drawn: { svg: SVGSVGElement, live?: { svg: () => string, png: (width: number) => Promise<Blob> } }) => void} [props.onReady]
 *   Given the drawn SVG, for a download; a Forest Oval recipe also gives its engine's own exports
 *   (`live`), since its lettering is live text.
 */
export const ForestLogo = ({ item, name, decorative = false, white = false, onReady }) => item.artwork
  ? <DrawingLogo artwork={item.artwork} recolour={item.recolour} padding={item.padding} name={name} decorative={decorative}
      background={item.background} white={white} onReady={onReady} />
  : <OvalLogo preset={item.recipe ?? item.id} name={name} decorative={decorative} theme={item.theme} colours={item.colours}
      composition={item.composition} background={item.background} white={white} onReady={onReady} />

/**
 * The drawn SVG as a standalone file at a given pixel width: its own namespace, its size from its
 * view box, and none of the page's accessibility hooks.
 */
export const standaloneSvg = (svg, width) => {
  const copy = svg.cloneNode(true)
  for (const attribute of ['role', 'aria-label', 'aria-labelledby', 'focusable', 'class', 'style']) copy.removeAttribute(attribute)
  copy.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  const [, , boxWidth, boxHeight] = (copy.getAttribute('viewBox') ?? '').split(/[\s,]+/).map(Number)
  const view = { width: boxWidth || width, height: boxHeight || width }
  copy.setAttribute('width', String(width))
  copy.setAttribute('height', String(Math.round((width * view.height) / view.width)))
  return { svg: new XMLSerializer().serializeToString(copy), view }
}
