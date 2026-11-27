// Forests, in Departmental Logos: a department's page and its marks' pages, as every department has
// them (DepartmentCollection.jsx), for designs that are this section's own reconstructions rather
// than the gallery's records.
//
// The department's page has the trail, the head, what the designs are, the designs as tiles and an
// account of them; a design's page has the trail, the design in the gallery's editor layout — the
// preview, its versions and the download — then where it is seen, and its account. Forests has no
// timeline: the designs' order is not a verified sequence of adoption, so it has no eras to show.
// Each version is a page of its own (internalPlaces.js), so Back returns to the one before.

import { useEffect, useRef, useState } from 'react'
import { FOREST_LOGOS, variantsFor } from './forestLogos.js'
import { ForestLogo, standaloneSvg } from './ForestArtwork.jsx'
import { FORESTS_PLACE, forestPlace, forestVersions } from './internalPlaces.js'
import { DEPARTMENTAL_ROOT } from '../gallery/movedGalleryPlaces.js'
import { PreviewBackground } from '../gallery/PreviewBackground.jsx'
import { HydroDownload, saveText } from '../hydro/HydroDownload.jsx'
import { downloadBlob } from '../export/exportLogo.js'
import { objectsForLogo } from '../posters/connections.js'
import { Breadcrumbs } from '../site/Breadcrumbs.jsx'
import { SiteLink, useNavigate } from '../site/navigation.jsx'
import { Segmented } from '../site/Segmented.jsx'

const FOREST_OVAL = { title: 'Forest Oval reference collection', url: 'https://projects.ahmadjalil.com/forestoval/' }

/** How a design is drawn here: its Forest Oval recipe, or a separate drawing from a supplied image. */
const drawingOf = (logo) => logo.kind === 'drawing'
  ? 'A vector reconstruction from a supplied image, recoloured here for each version.'
  : <>Reconstructed in <a href={FOREST_OVAL.url} target="_blank" rel="noreferrer">Forest Oval</a> from supplied references, and drawn here by its engine for each version.</>

/** Forests' page: what the designs are, and each as a tile that opens its page. */
const ForestsPage = ({ headingRef }) => (
  <section className="internal-logos gallery" aria-label="Departmental Logos">
    <Breadcrumbs label="Departmental Logos" steps={[DEPARTMENTAL_ROOT, { label: 'Forests' }]} />
    <div className="gallery__collection-head">
      <div>
        <h2 className="gallery__collection-heading" ref={headingRef} tabIndex={-1}>Forests</h2>
        <p className="gallery__note">The Forest Service and the forests ministries · order of adoption unverified</p>
      </div>
    </div>
    <p className="gallery__intro">
      All are reconstructions. Three of the ovals are reconstructed in Forest Oval from supplied references; the Lands
      Department seal, the evergreen emblem and the yellow-sky, one-ink and green-and-gold Forest Service ovals are
      separate vector reconstructions from supplied images. Each design’s history, dating and sources are on its own page.
    </p>
    <div className="gallery__tiles">
      {FOREST_LOGOS.map((logo) => (
        <SiteLink key={logo.id} to={forestPlace(logo.id)} className="gallery__pick gallery__pick--tile" aria-label={`Open ${logo.name}`}>
          <span className="gallery__art" data-ground="page"><ForestLogo item={logo} name={logo.name} decorative /></span>
          <span className="gallery__label">{logo.name}</span>
          <span className="gallery__note">{logo.description}</span>
        </SiteLink>
      ))}
    </div>
    <section className="panel gallery__about" aria-labelledby="forests-about-title">
      <h2 id="forests-about-title">About these marks</h2>
      <dl className="gallery__facts">
        <div><dt>Provenance</dt><dd>Reconstructions, not original artwork. The three Forest Oval designs are drawn by its engine from supplied references; the others are separate vector reconstructions from supplied images.</dd></div>
        <div><dt>Fidelity</dt><dd>Each is a reconstruction: its colours are flat approximations of the references, not verified ink specifications, and small details are interpreted.</dd></div>
        <div><dt>Dates</dt><dd>The designs are grouped by family. Apart from the seal and the emblem coming before the ovals, their order does not imply a verified sequence of adoption; each design’s dating is on its page.</dd></div>
        <div><dt>Versions</dt><dd>The colourways and studies offered on each design’s page are display variations. They do not establish historical adoption or official approval.</dd></div>
      </dl>
    </section>
  </section>
)

/** The version groups a design's page offers, each with what it is. */
const versionGroups = (logo) => {
  const { colours, studies = [], related = [] } = variantsFor(logo)
  return [
    { label: 'Colourway', versions: colours, hint: 'The colourways are display variations; they do not establish historical adoption or official approval.' },
    { label: 'Reconstructed studies', versions: studies, hint: 'Modern construction and reversal experiments based on the reference specimens, not verified historical logo versions.' },
    { label: 'Service variants', versions: related }
  ].filter(({ versions }) => versions.length > 0)
}

/** Where a design is seen: the posters that carry it, and the patches and badges made of it. */
const SeenOn = ({ logo }) => {
  const rows = [
    ...(logo.seenOn ?? []).map((entry) => ({ key: entry.to.poster ?? entry.to.card ?? entry.title, to: entry.to, title: entry.title, note: entry.note })),
    ...objectsForLogo(logo.id).map((entry) => ({ key: entry.to.patch, to: entry.to, title: entry.label, note: entry.note }))
  ]
  return rows.length > 0 && (
    <section className="gallery__history" aria-labelledby="forest-seen-on">
      <h2 id="forest-seen-on" className="gallery__shelf-title">On the posters, and as an object</h2>
      <ul className="gallery__history-records">
        {rows.map(({ key, to, title, note }) => (
          <li key={key}>
            <SiteLink to={to}>{title} <span aria-hidden="true">→</span></SiteLink>
            <p className="gallery__note">{note}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}

/** A design's account, as the gallery gives a mark's: its dating, history, drawing and sources. */
const AboutForestMark = ({ logo }) => (
  <section className="panel gallery__about" aria-labelledby="about-mark">
    <h2 id="about-mark">About this mark</h2>
    <dl className="gallery__facts">
      <div><dt>Dates</dt><dd>{logo.evidence}</dd></div>
      <div><dt>History</dt><dd>{logo.comments.map((comment) => <p key={comment}>{comment}</p>)}</dd></div>
      {logo.article && (
        <div>
          <dt>Newspaper comparison</dt>
          <dd>
            <p><b>{logo.article.title}</b></p>
            <blockquote className="internal-logos__quote">“{logo.article.excerpt}”</blockquote>
            <p>{logo.article.context}</p>
            <p>{logo.article.qualification}</p>
            <p>{logo.article.citation}</p>
          </dd>
        </div>
      )}
      <div><dt>Drawing</dt><dd>{drawingOf(logo)}</dd></div>
      {logo.measurements?.length > 0 && <div><dt>Fit</dt><dd>{logo.measurements.map((line) => <p key={line}>{line}</p>)}</dd></div>}
      {logo.sources.length > 0 && (
        <div>
          <dt>Sources</dt>
          <dd><ul className="internal-logos__sources">{logo.sources.map((source) => <li key={source.url}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></li>)}</ul></dd>
        </div>
      )}
    </dl>
  </section>
)

const LIVE_FORMATS = [
  { value: 'svg', label: 'SVG', note: 'Vector, with the lettering as live text naming its typefaces, which are not included: it shows as drawn only where they are installed.' },
  { value: 'png', label: 'PNG', note: 'Pixels, 2048 wide, drawn with the typefaces this page loaded.' }
]

/**
 * The download for a Forest Oval design. Its lettering is live text in licensed typefaces, which
 * Forest Oval does not redistribute, so it offers what its engine exports: an SVG naming the faces,
 * and a PNG drawn with them. (A supplied drawing is all paths, and has the gallery's every format.)
 */
const LiveDownload = ({ drawn, fileName }) => {
  const [format, setFormat] = useState('svg')
  const [status, setStatus] = useState({ message: '', tone: 'info' })
  const spec = LIVE_FORMATS.find(({ value }) => value === format)
  const download = async () => {
    const live = drawn.current?.live
    if (!live) return setStatus({ message: 'The logo is still being drawn.', tone: 'error' })
    try {
      if (format === 'svg') saveText(live.svg(), fileName('svg'), 'image/svg+xml')
      else downloadBlob(await live.png(2048), fileName('png'))
      setStatus({ message: `Saved ${fileName(format)}`, tone: 'info' })
    } catch (error) {
      setStatus({ message: error.message || 'The export failed.', tone: 'error' })
    }
  }
  return (
    <section className="panel">
      <h2>Download</h2>
      <Segmented label="Format" options={LIVE_FORMATS} value={format} onChange={setFormat} />
      <p className="field__note">{spec.note}</p>
      <div className="field">
        <button type="button" className="button button--primary" onClick={download}>Download {spec.label}</button>
        <p className="field__note" style={{ wordBreak: 'break-all' }}>{fileName(format)}</p>
      </div>
      <p className="export__status" data-tone={status.tone} role="status" aria-live="polite">{status.message}</p>
    </section>
  )
}

/** A design's page, at one of its versions. */
const ForestMark = ({ logo, variantId, currentRef, versionsRef }) => {
  const navigate = useNavigate()
  const [white, setWhite] = useState(false)
  const drawn = useRef(null)
  const versions = forestVersions(logo)
  const version = versions.find(({ id }) => id === variantId) ?? versions[0]
  const draw = ({ width }) => {
    if (!drawn.current) throw new Error('The logo is still being drawn.')
    return standaloneSvg(drawn.current.svg, width)
  }
  const fileName = (extension) => `${logo.id}-${version.id}.${extension}`
  return (
    <section className="internal-logos gallery" aria-label="Departmental Logos">
      <Breadcrumbs label="Departmental Logos" currentRef={currentRef}
        steps={[DEPARTMENTAL_ROOT, { label: 'Forests', to: FORESTS_PLACE }, { label: logo.name }]} />
      <div className="hydro">
        <div className="gallery__head hydro__head">
          <div>
            <h2>{logo.name} <span className="gallery__years">{logo.evidence}</span></h2>
            <p className="gallery__note">{logo.description}</p>
          </div>
        </div>
        <div className="layout">
          <section className="stage" aria-label="Preview">
            <PreviewBackground white={white} onToggle={() => setWhite(!white)}>
              <div className="stage__frame internal-logos__stage">
                <ForestLogo key={version.id} item={version} name={`${logo.name}, ${version.name}`} white={white}
                  onReady={(ready) => { drawn.current = ready }} />
              </div>
            </PreviewBackground>
            <div className="contrast-list hydro__rules">
              <p className="contrast" data-level="pass">
                <span className="contrast__surface">Reconstruction · {version.name}</span>
                <span className="contrast__message">
                  {version.note}
                  {version.source && <> <a href={version.source.url} target="_blank" rel="noreferrer">{version.source.title}</a></>}
                </span>
              </p>
            </div>
          </section>
          <div className="controls">
            <section className="panel" ref={versionsRef}>
              <h2>Version</h2>
              {versionGroups(logo).map((group) => (
                <Segmented key={group.label} label={group.label} hint={group.hint}
                  options={group.versions.map(({ id, name }) => ({ value: id, label: name }))}
                  value={group.versions.some(({ id }) => id === version.id) ? version.id : ''}
                  onChange={(id) => id !== version.id && navigate(forestPlace(logo.id, id))} />
              ))}
            </section>
            {version.artwork
              ? <HydroDownload fileName={fileName} draw={draw} />
              : <LiveDownload key={version.id} drawn={drawn} fileName={fileName} />}
          </div>
        </div>
      </div>
      <SeenOn logo={logo} />
      <AboutForestMark logo={logo} />
    </section>
  )
}

/**
 * @param {object} props
 * @param {string|null} props.logoId The design open, if any.
 * @param {string|null} props.variantId Its version, if not its default.
 */
export default function ForestsCollection({ logoId, variantId }) {
  const heading = useRef(null)
  const versions = useRef(null)
  const logo = FOREST_LOGOS.find(({ id }) => id === logoId)
  // A page opens at its name, so a screen reader starts there; a version chosen on a design's page
  // opens with its own button focused, where the choice was made.
  useEffect(() => {
    const chosen = variantId && versions.current?.querySelector('[aria-pressed="true"]')
    if (chosen) chosen.focus()
    else heading.current?.focus({ preventScroll: true })
  }, [logoId, variantId])
  return logo
    ? <ForestMark logo={logo} variantId={variantId} currentRef={heading} versionsRef={versions} />
    : <ForestsPage headingRef={heading} />
}
