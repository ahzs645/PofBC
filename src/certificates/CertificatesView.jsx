import { useEffect, useState } from 'react'
import { Segmented } from '../site/Segmented.jsx'
import { SiteLink } from '../site/navigation.jsx'
import { Slider } from '../site/ui/Slider.jsx'
import { TabList } from '../site/ui/TabList.jsx'
import { generateBorder } from './bc-guilloche-generator.mjs'
import './certificates.css'

const asset = (file) => `${import.meta.env.BASE_URL}certificates/${file}`
const specimen = asset('certificate-of-training-1961.png')
const reconstructedCertificate = asset('certificate-of-training-1961-reconstruction.svg')
const borderPdf = asset('bc-training-border.pdf')

const TABS = [
  { id: 'reconstruction', label: 'Reconstruction' },
  { id: 'specimen', label: 'Specimen' },
  { id: 'lettering', label: 'Lettering' },
  { id: 'border', label: 'Border' }
]

const SHAPES = [
  { value: 'frame', label: 'Full frame' },
  { value: 'corner', label: 'Corner' },
  { value: 'repeat', label: 'Straight repeat' }
]

const CORNERS = [
  { value: 'certificate', label: 'Certificate' },
  { value: 'long-leaf', label: 'Long leaf' }
]

const DEFAULT_BORDER = { shape: 'frame', corner: 'certificate', ink: '#056a43', density: 100 }

const CertificateArtwork = ({ reconstruction = false }) => (
  <div className="certificates__layout">
    <figure className="panel certificates__figure">
      <div className="certificates__plate">
        <img src={reconstruction ? reconstructedCertificate : specimen} width="722" height="550" alt={reconstruction
          ? 'Reconstructed Certificate of Training with fitted lettering and a green guilloché border'
          : 'Certificate of Training with a green guilloché border and the department’s oval dogwood seal'} />
      </div>
      <figcaption>{reconstruction
        ? 'The rebuilt guilloché frame surrounds the fitted lettering. The seal and ministerial signature appear in the specimen.'
        : 'Supplied reference image of the 1961 certificate.'}</figcaption>
    </figure>
    <section className="panel certificates__details" aria-labelledby="certificate-details">
      <h3 id="certificate-details">Certificate details</h3>
      <dl>
        <dt>Issued</dt>
        <dd><time dateTime="1961-05-18">May 18, 1961</time> · Victoria, B.C.</dd>
        <dt>Recipient</dt>
        <dd>J. P. Gibault</dd>
        <dt>Course</dt>
        <dd>In-Service Training Course in Fish and Game Branch Administration</dd>
      </dl>
      <div className="certificates__actions">
        {reconstruction
          ? <a href={reconstructedCertificate} download className="button button--primary">Download reconstruction SVG</a>
          : <a href={specimen} download className="button">Download specimen PNG</a>}
        <SiteLink to={{ view: 'gallery', logos: 'recreation-conservation' }}>Recreation and Conservation logos</SiteLink>
      </div>
    </section>
  </div>
)

const studyAsset = (file) => asset(`lettering-study/${file}`)

const LetteringStudy = () => (
  <div className="certificates__layout">
    <figure className="panel certificates__figure certificates__study">
      <img src={studyAsset('blackletter-detail.png')} width="910" height="1126"
        alt="Blackletter comparison showing the two headings in the specimen, the fitted QT Linoscroll outlines, and the overlap between them" />
      <figcaption>Detail from the supplied font-overlap study.</figcaption>
    </figure>
    <section className="panel certificates__details" aria-labelledby="certificate-lettering-details">
      <h3 id="certificate-lettering-details">Lettering study</h3>
      <p className="panel__hint">The study fitted nine printed lines to the specimen. QT Linoscroll had the closest fit for the blackletter headings, and Lato Bold for the sans-serif lines. The historical typefaces remain unidentified.</p>
      <div className="certificates__actions">
        <a href={studyAsset('modulated-lettering.svg')} download className="button button--primary">Download fitted lettering SVG</a>
        <a href={studyAsset('blackletter-overlap.png')} target="_blank" rel="noreferrer" className="button">Open blackletter comparison</a>
        <a href={studyAsset('sans-overlap.png')} target="_blank" rel="noreferrer" className="button">Open sans-serif comparison</a>
        <a href={studyAsset('export-validation.png')} target="_blank" rel="noreferrer" className="button">Open vector export comparison</a>
        <a href={studyAsset('font-rankings.csv')} download>Download font rankings CSV</a>
      </div>
    </section>
  </div>
)

const BorderGenerator = ({ settings, setSettings }) => {
  const [svgUrl, setSvgUrl] = useState(null)
  const { shape, corner, ink, density } = settings
  const shapeLabel = SHAPES.find(({ value }) => value === shape).label
  const filename = shape === 'frame' ? 'bc-training-border.svg' : `bc-training-border-${shape}.svg`

  useEffect(() => {
    const svg = generateBorder({ view: shape, corner, ink, density: density / 100 })
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }))
    setSvgUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [shape, corner, ink, density])

  const change = (field) => (value) => setSettings((previous) => ({ ...previous, [field]: value }))

  return (
    <div className="certificates__layout">
      <figure className="panel certificates__figure">
        <div className="certificates__plate certificates__plate--border" data-shape={shape}>
          {svgUrl && <img src={svgUrl} alt={`${shapeLabel} of the reconstructed guilloché border`} />}
        </div>
        <figcaption>The reconstruction follows the visible border and mirrors the pattern beneath the dogwood seal.</figcaption>
      </figure>
      <section className="panel certificates__details" aria-labelledby="certificate-border-controls">
        <h3 id="certificate-border-controls">Guilloché border reconstruction</h3>
        <Segmented label="Pattern" options={SHAPES} value={shape} onChange={change('shape')} />
        {shape !== 'repeat' && (
          <Segmented label="Corner style" options={CORNERS} value={corner} onChange={change('corner')} />
        )}
        <div className="field certificates__density">
          <label htmlFor="certificate-border-density">Strand density</label>
          <output htmlFor="certificate-border-density">{density}%</output>
          <Slider id="certificate-border-density" value={density} min={60} max={150} aria-valuetext={`${density}%`} onChange={change('density')} />
        </div>
        <div className="field certificates__ink">
          <label htmlFor="certificate-border-ink">Ink colour</label>
          <input id="certificate-border-ink" type="color" value={ink} onChange={(event) => change('ink')(event.target.value)} />
        </div>
        <div className="certificates__actions">
          {svgUrl && <a href={svgUrl} download={filename} className="button button--primary">Download SVG</a>}
          <a href={borderPdf} download className="button">Download default border PDF</a>
          <button type="button" className="button button--ghost" onClick={() => setSettings(DEFAULT_BORDER)}>Reset settings</button>
        </div>
      </section>
    </div>
  )
}

export const CertificatesView = () => {
  const [view, setView] = useState('reconstruction')
  const [settings, setSettings] = useState(DEFAULT_BORDER)
  const panels = {
    reconstruction: <CertificateArtwork reconstruction />,
    specimen: <CertificateArtwork />,
    lettering: <LetteringStudy />,
    border: <BorderGenerator settings={settings} setSettings={setSettings} />
  }

  return (
    <main className="certificates" aria-labelledby="certificate-heading">
      <header className="certificates__header">
        <h2 id="certificate-heading">Certificate of Training</h2>
        <p>Fish and Game Branch · Department of Recreation and Conservation</p>
      </header>
      <TabList idPrefix="certificate" label="Certificate sections" tabs={TABS} selected={view} onChange={setView} />
      {TABS.map(({ id }) => (
        <div key={id} className="certificates__panel" role="tabpanel" id={`certificate-panel-${id}`}
          aria-labelledby={`certificate-tab-${id}`} tabIndex={0} hidden={view !== id}>
          {view === id && panels[id]}
        </div>
      ))}
    </main>
  )
}
