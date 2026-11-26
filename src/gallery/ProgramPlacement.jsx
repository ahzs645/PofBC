import { useState } from 'react'
import { assetUrl } from './collectedCollections.js'
import { collectedDisplay } from './tileArt.js'
import { checkPlacement } from './programPlacement.js'
import './programPlacement.css'

export function ProgramPlacement({ asset }) {
  const rule = asset?.placement
  if (!rule) return null
  return (
    <details className="program-placement" id="placement" open={globalThis.location?.hash === '#placement' || undefined}>
      <summary>Check placement</summary>
      <PlacementControls key={asset.variantOf ?? asset.id} asset={asset} rule={rule} />
    </details>
  )
}

function PlacementControls({ asset, rule }) {
  const [medium, setMedium] = useState('screen')
  const [height, setHeight] = useState({ screen: String(rule.px ?? 50), print: String(rule.print ?? (rule.printUnit === 'mm' ? 10 : .5)) })
  const [manual, setManual] = useState(false)
  const [margins, setMargins] = useState({ screen: '', print: '' })
  const [ground, setGround] = useState(null)
  const [companion, setCompanion] = useState('')
  const [location, setLocation] = useState('')
  const [downloadError, setDownloadError] = useState(false)
  const unit = medium === 'screen' ? 'px' : rule.printUnit
  const proof = checkPlacement(rule, medium, height[medium], manual ? margins[medium] : null)
  const inkGround = asset.sourceGround ?? 'light'
  const background = ground ?? (inkGround === 'dark' ? '#252525' : '#ffffff')
  const copy = collectedDisplay(asset, inkGround)
  const placed = proof.height > 0 && proof.available != null && copy
  const trim = copy?.inkInset ?? 0
  const imageHeight = 100 / (1 - 2 * trim)
  const imageWidth = imageHeight * (copy?.aspect ?? 1)
  const bleed = imageHeight * trim
  const artWidth = imageWidth - 2 * bleed
  const inset = placed ? 100 * proof.available / proof.height : 0
  const frameWidth = artWidth + 2 * inset
  const frameHeight = 100 + 2 * inset
  const drawable = Number.isFinite(frameWidth) && Number.isFinite(frameHeight) && frameWidth > 0 && frameHeight > 0
  async function download() {
    setDownloadError(false)
    try {
      const { exportProgramPlacement } = await import('./exportProgramPlacement.js')
      await exportProgramPlacement({ asset, copy, height: proof.height, margin: proof.available, unit, background })
    } catch {
      setDownloadError(true)
    }
  }
  return (
    <div className="program-placement__body">
      <div className="program-placement__fields">
        <label>Medium
          <select value={medium} onChange={(e) => setMedium(e.target.value)}>
            <option value="screen">Screen</option><option value="print">Print</option>
          </select>
        </label>
        <label>Visible artwork height ({unit})
          <input type="number" min="0" step="any" value={height[medium]}
            onChange={(e) => setHeight({ ...height, [medium]: e.target.value })} />
        </label>
        {rule.spacing != null && <label>Clear space
          <select value={manual ? 'measured' : 'guide'} onChange={(e) => setManual(e.target.value === 'measured')}>
            <option value="guide">Use guide margin</option><option value="measured">Check measured margin</option>
          </select>
        </label>}
        {manual && <label>Smallest margin on any side ({unit})
          <input type="number" min="0" step="any" value={margins[medium]}
            onChange={(e) => setMargins({ ...margins, [medium]: e.target.value })} />
        </label>}
        <label>Placement background
          <input type="color" value={background} onChange={(e) => setGround(e.target.value)} />
        </label>
      </div>
      {copy && drawable &&
        <svg className="program-placement__diagram" role="img" aria-label="Proportional placement preview"
          viewBox={`0 0 ${frameWidth} ${frameHeight}`} style={{ backgroundColor: background }}>
          <image href={assetUrl(copy.file)} x={inset - bleed} y={inset - bleed} width={imageWidth} height={imageHeight} />
          {placed && <rect x={inset} y={inset} width={artWidth} height="100" fill="none" stroke="#888"
            strokeDasharray="3 3" vectorEffect="non-scaling-stroke" />}
        </svg>}
      <div aria-live="polite" className="program-placement__results">
        {!proof.height ? <p>Enter an artwork height greater than zero.</p> : <>
          <p>{proof.minimum == null ? 'The guide gives no minimum height for this layout.' :
            `${proof.sizeOK ? 'Meets' : 'Below'} the minimum height of ${proof.minimum} ${unit}. Placed artwork is ${proof.height} ${unit} high.`}</p>
          {proof.target != null ? <p>Guide margin of <strong>{proof.target} {unit}</strong> per side (rounded up). {rule.reference}.
            {manual && (' ' + (proof.spacingOK == null ? 'Enter the smallest available margin.' :
              proof.spacingOK ? 'Measured margin meets the guide.' : 'Measured margin is too small.'))}</p> :
            <p>The guide gives no clear-space measurement for this layout.</p>}
        </>}
      </div>
      {rule.companion && <label>Provincial mark elsewhere in this communication
        <select value={companion} onChange={(e) => setCompanion(e.target.value)}>
          <option value="">Check placement</option><option value="visible">Visible elsewhere</option>
          <option value="missing">Missing</option>
        </select>
        {companion === 'missing' && <span role="status">Place the provincial mark elsewhere or use the endorsed layout.</span>}
      </label>}
      {rule.companion && companion === 'visible' && <label>Location of the provincial mark
        <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. back cover" />
      </label>}
      {placed && drawable && <div>
        <button type="button" className="button button--ghost" onClick={download}>Download placed SVG</button>
        {downloadError && <p role="alert">Couldn’t load the artwork. Try the download again.</p>}
      </div>}
      {medium === 'print' && asset.printMember && <p className="gallery__note">
        <a href={asset.sourceUrl}>Download provincial print kit (ZIP)</a><br />
        CMYK EPS · <span className="program-placement__member">{asset.printMember}</span>
      </p>}
      <p className="gallery__note">Inspect the lettering and symbol against the intended background. Measurements use visible artwork before padding. <a href={rule.guide} target="_blank" rel="noreferrer">{rule.citation}</a></p>
    </div>
  )
}
