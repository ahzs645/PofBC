import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { loadLetteringRuntime } from '../../vendor/forestoval/shared-primitives/live-lettering/src/runtime.ts'
import mountainRidge from '../../vendor/forestoval/shared-primitives/bc-ministry-v5/scenes/tree-parts/mountain-ridge.svg?raw'
import mountainBase from '../../vendor/forestoval/shared-primitives/bc-ministry-v5/scenes/tree-parts/mountain-base.svg?raw'
import { FOREST_LOGOS, variantsFor } from './forestLogos.js'
import { SiteLink } from '../site/navigation.jsx'
import './internal.css'

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

// Render the reference presets directly, without the editor, its options or browser drafts.
const OvalLogo = ({ preset, name, decorative = false, theme, colours, composition, background = '#fff' }) => {
  const host = useRef(null)
  const [status, setStatus] = useState('loading')
  const [attempt, setAttempt] = useState(0)
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
      setStatus('ready')
    }
    render().catch(() => { if (!disposed) setStatus('error') })
    return () => { disposed = true }
  }, [preset, name, attempt, theme, colours, composition])

  return (
    <div className="internal-logos__artwork" style={{ background }} aria-hidden={decorative || undefined}>
      <div className="internal-logos__svg" ref={host} />
      {status === 'loading' && <span role="status">Loading logo…</span>}
      {status === 'error' && (decorative ? <span>Logo unavailable</span> : <div role="alert">Could not load this logo. <button type="button" onClick={() => setAttempt((value) => value + 1)}>Retry</button></div>)}
    </div>
  )
}

// Some designs are supplied drawings rather than Forest Oval recipes: recoloured by mapping their own
// colours to new ones, with every id prefixed per copy so a clip path still finds its own shape
// when several copies share a page. They are fetched when first shown, since the engraved seal
// alone is larger than the rest of this view.
const DRAWINGS = {
  'forest-service-lands-department.svg': () => import('./forest-service-lands-department.svg?raw'),
  'forest-service-emblem.svg': () => import('./forest-service-emblem.svg?raw'),
  'forest-service-emblem-two-islands.svg': () => import('./forest-service-emblem-two-islands.svg?raw'),
  'forest-service-green-gold.svg': () => import('./forest-service-green-gold.svg?raw'),
  'forest-service-yellow-sky.svg': () => import('./forest-service-yellow-sky.svg?raw')
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

const DrawingLogo = ({ artwork, recolour, padding, name, decorative = false, background = '#fff' }) => {
  const prefix = `drawing${useId().replace(/[^a-zA-Z0-9]/g, '')}`
  const [attempt, setAttempt] = useState(0)
  const { svg, failed } = useDrawing(artwork, attempt)
  const markup = useMemo(() => svg && drawingMarkup({ svg, recolour, name, prefix }), [svg, recolour, name, prefix])
  return (
    <div className="internal-logos__artwork" style={{ background }} aria-hidden={decorative || undefined}>
      {markup && <div className="internal-logos__svg" style={{ padding }} dangerouslySetInnerHTML={{ __html: markup }} />}
      {!markup && !failed && <span role="status">Loading logo…</span>}
      {failed && (decorative ? <span>Logo unavailable</span> : <div role="alert">Could not load this logo. <button type="button" onClick={() => setAttempt((value) => value + 1)}>Retry</button></div>)}
    </div>
  )
}

const PosterLinks = ({ logo }) => (
  <ul className="internal-logos__posters">
    {logo.seenOn.map((entry) => (
      <li key={entry.to.poster}>
        <SiteLink to={entry.to}><b>{entry.title} <span aria-hidden="true">→</span></b><span>{entry.note}</span></SiteLink>
      </li>
    ))}
  </ul>
)

const LogoSources = ({ logo }) => logo.sources.length > 0 && (
  <details className="internal-logos__sources">
    <summary>Sources</summary>
    <ul>{logo.sources.map((source) => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></li>)}</ul>
  </details>
)

const LogoComments = ({ logo }) => (
  <>
    {logo.comments.map((comment) => <p key={comment}>{comment}</p>)}
    {logo.seenOn && (
      <>
        <h4>On the posters</h4>
        <PosterLinks logo={logo} />
      </>
    )}
  </>
)

// On a logo's own page its history is shown whole; on the family's page, each card carries only
// what dates it, with the comments and sources folded beneath.
const LogoHistory = ({ logo, folded = false }) => folded
  ? (
    <>
      <p className="internal-logos__evidence">{logo.evidence}</p>
      <details className="internal-logos__history">
        <summary>History &amp; comments</summary>
        <div className="internal-logos__comments" aria-label={`${logo.name} historical comments`}>
          <LogoComments logo={logo} />
        </div>
        <LogoSources logo={logo} />
      </details>
    </>
    )
  : (
    <>
      <div className="internal-logos__comments" aria-label={`${logo.name} historical comments`}>
        <h4>History &amp; comments</h4>
        <p className="internal-logos__evidence">{logo.evidence}</p>
        <LogoComments logo={logo} />
      </div>
      <LogoSources logo={logo} />
    </>
    )

const VariantCard = ({ variant }) => (
  <article className="internal-logos__variant" aria-labelledby={`variant-${variant.id}`}>
    {variant.artwork
      ? <DrawingLogo artwork={variant.artwork} recolour={variant.recolour} padding={variant.padding} name={variant.name} background={variant.background} />
      : <OvalLogo preset={variant.recipe} name={variant.name} theme={variant.theme} colours={variant.colours} composition={variant.composition} background={variant.background} />}
    <div className="internal-logos__notes">
      <h3 id={`variant-${variant.id}`}>{variant.name}</h3>
      <p className="internal-logos__description">{variant.note}</p>
      {variant.source && <p className="internal-logos__variant-source"><a href={variant.source.url} target="_blank" rel="noreferrer">{variant.source.title}</a></p>}
    </div>
  </article>
)

const initialSelection = () => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  const logoId = params.get('internal-logo')
  const logo = FOREST_LOGOS.find((entry) => entry.id === logoId)
  return { family: params.get('internal') === 'forests' || !!logo, logoId: logo?.id ?? null }
}

export const InternalLogosView = () => {
  const [selection, setSelection] = useState(initialSelection)
  const title = useRef(null)
  const forestButton = useRef(null)
  const logoButtons = useRef({})
  const current = FOREST_LOGOS.find((logo) => logo.id === selection.logoId)
  const variants = current ? variantsFor(current) : null
  const navigate = (family, logoId = null) => {
    const url = new URL(globalThis.location.href)
    if (family) url.searchParams.set('internal', 'forests')
    else url.searchParams.delete('internal')
    if (logoId) url.searchParams.set('internal-logo', logoId)
    else url.searchParams.delete('internal-logo')
    globalThis.history?.replaceState(null, '', url)
    setSelection({ family, logoId })
  }
  const backToFamily = () => {
    const id = selection.logoId
    navigate(true)
    requestAnimationFrame(() => logoButtons.current[id]?.focus())
  }
  useEffect(() => {
    if (selection.family) title.current?.focus()
  }, [selection.family, selection.logoId])

  return (
    <section className="internal-logos" aria-label="Internal Logos">
      {current ? (
        <>
          <div className="internal-logos__intro">
            <button className="internal-logos__back" type="button" onClick={backToFamily}>← Forests</button>
            <h2 ref={title} tabIndex={-1}>{current.name}</h2>
            <p>{current.description}</p>
          </div>
          <h3 className="internal-logos__section-title">Colour variants</h3>
          <div className="internal-logos__variants">
            {variants.colours.map((variant) => <VariantCard key={variant.id} variant={variant} />)}
          </div>
          <p className="internal-logos__footnote">The colourways are display variations; they do not establish historical adoption or official approval.</p>
          {variants.related.length > 0 && (
            <>
              <h3 className="internal-logos__section-title">Service variants</h3>
              <div className="internal-logos__variants">
                {variants.related.map((variant) => <VariantCard key={variant.id} variant={variant} />)}
              </div>
            </>
          )}
          {current.seenOn && (
            <>
              <h3 className="internal-logos__section-title">On the posters</h3>
              <p className="internal-logos__footnote">Open a poster at its emblem; every other part of the poster is clickable too.</p>
              <PosterLinks logo={current} />
            </>
          )}
          <div className="internal-logos__history-panel"><LogoHistory logo={current} /></div>
        </>
      ) : selection.family ? (
        <>
          <div className="internal-logos__intro">
            <button className="internal-logos__back" type="button" onClick={() => { navigate(false); requestAnimationFrame(() => forestButton.current?.focus()) }}>← Internal Logos</button>
            <h2 ref={title} tabIndex={-1}>Forests</h2>
          </div>
          <div className="internal-logos__designs">
            {FOREST_LOGOS.map((logo) => (
              <article key={logo.id} className="internal-logos__design" aria-labelledby={`internal-${logo.id}`}>
                {/* The artwork opens the logo too, for a pointer; the title is the one way in for a
                    keyboard or a screen reader, so the artwork stays out of both. */}
                <button type="button" className="internal-logos__open" tabIndex={-1} aria-hidden="true" onClick={() => navigate(true, logo.id)}>
                  {logo.kind === 'drawing' ? <DrawingLogo artwork={logo.artwork} padding={logo.padding} name={logo.name} decorative /> : <OvalLogo preset={logo.id} name={logo.name} decorative />}
                </button>
                <div className="internal-logos__notes">
                  <h3 id={`internal-${logo.id}`}>
                    <button type="button" className="internal-logos__title" aria-label={`${logo.name}: view variants`} ref={(element) => { logoButtons.current[logo.id] = element }} onClick={() => navigate(true, logo.id)}>
                      {logo.name} <span aria-hidden="true">→</span>
                    </button>
                  </h3>
                  <p className="internal-logos__description">{logo.description}</p>
                  <LogoHistory logo={logo} folded />
                </div>
              </article>
            ))}
          </div>
          <details className="internal-logos__footnote">
            <summary>All are reconstructions, and their order is not a verified sequence of adoption.</summary>
            <p>Three of the ovals are reconstructed in Forest Oval from supplied references; the Lands Department seal, the evergreen emblem and the yellow-sky and green-and-gold Forest Service ovals are separate vector reconstructions from supplied images. The designs are grouped by family; apart from the seal and the emblem coming before the ovals, their order does not imply a verified sequence of adoption.</p>
          </details>
        </>
      ) : (
        <>
          <div className="internal-logos__intro">
            <h2>Internal Logos</h2>
          </div>
          <button ref={forestButton} type="button" className="internal-logos__family" onClick={() => navigate(true)}>
            <OvalLogo preset="forests" name="Forests" decorative />
            <span className="internal-logos__family-text">
              <span className="internal-logos__family-title">Forests <span aria-hidden="true">→</span></span>
              <span>Two early marks and five oval designs</span>
              <span className="internal-logos__family-description">The Forest Service’s engraved Lands Department seal and its evergreen emblem from before about 1973, then the Forests and long ministry name ovals and three Forest Service ovals. View the logos and their history.</span>
            </span>
          </button>
        </>
      )}
    </section>
  )
}
