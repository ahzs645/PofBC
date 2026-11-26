import { useState } from 'react'
import { assetUrl, parseSpecimenDate } from './collectedCollections.js'
import { collectedDetailPreview, defaultCollectedAsset } from './tileArt.js'
import { PreviewBackground } from './PreviewBackground.jsx'
import { ProgramPlacement } from './ProgramPlacement.jsx'
import { useSiteTheme } from '../site/useTheme.js'
import { CollectedPaletteView } from './CollectedPaletteView.jsx'
import { holdScrollFrom } from '../site/holdScroll.js'

/** A recovered mark is displayed in its source format; raster files stay raster. */
export const CollectedMarkView = ({ entry }) => entry.paletteGroup
  ? <CollectedPaletteView entry={entry} />
  : <SourceMarkView entry={entry} />

const SourceMarkView = ({ entry }) => {
  const [version, setVersion] = useState(() => {
    const requested = new URLSearchParams(globalThis.location?.search ?? '').get('mark')
    // A design link opens its default artwork. Individual alternate versions remain selectable.
    if (requested === entry.id || (requested && requested === entry.asset.reconstructionOf)) return null
    return entry.versions?.find((each) => each.id === requested)?.id ?? null
  })
  const { name: siteTheme } = useSiteTheme()
  const [white, setWhite] = useState(false)
  const theme = white ? 'light' : siteTheme
  const asset = entry.versions?.find((each) => each.id === version) ?? defaultCollectedAsset(entry, theme)
  const specimenDate = parseSpecimenDate(asset.specimenDate ?? asset.sourceDate)
  const dateLabel = !specimenDate ? 'Logo dates unestablished'
    : asset.reconstructionDate ? `Reconstructed ${asset.reconstructionDate} · specimen dated ${specimenDate.label}`
    : asset.sourceReproduction && asset.historicalDateLabel ? `${asset.historicalDateLabel} · reproduced ${specimenDate.label}`
    : `Seen ${specimenDate.label}`
  const { display, file, ground, themed } = collectedDetailPreview(asset, theme, Boolean(version))
  const artworkType = asset.isVector ? 'Vector artwork' : asset.format === 'svg' ? 'Contains bitmap artwork' : 'Image'
  const vectorAdaptation = asset.evidenceType === 'adaptation-of-source-vector'
  const extractedArtwork = Boolean(asset.extraction?.pdfBounds || asset.extraction?.method)
  const colourSource = {
    'website-colours-on-source-vector': 'website',
    'publication-colours-on-source-vector': 'publication'
  }[asset.evidenceType]
  const downloadLabel = colourSource ? `Download ${colourSource}-colour` : asset.reconstruction ? 'Download reconstruction'
    : vectorAdaptation ? 'Download' : extractedArtwork ? 'Download source artwork' : 'Download original'
  const downloadNote = colourSource ? `The SVG download uses the ${colourSource} colours.` : asset.reconstruction
    ? 'The download is the reconstruction, not original artwork.'
    : vectorAdaptation ? 'The SVG download uses this version’s inks on a transparent canvas.'
    : extractedArtwork ? `The source artwork is available to download as ${asset.format.toUpperCase()}.` : 'The original file is available to download as published.'
  const preview = (
    <PreviewBackground white={white} onToggle={() => setWhite(!white)}>
      <div className={`gallery__recovered-preview${themed ? ' gallery__recovered-preview--clean' : ''}`}
        data-transparent={asset.previewBackground === 'transparent' || undefined}
        data-dark={!themed && asset.darkBackground || undefined}>
        <img src={assetUrl(file)} alt={asset.pose ? `${entry.label}, ${asset.pose}` : entry.label} data-preview-ground={ground ?? (white && !themed && asset.darkBackground ? 'dark' : undefined)} />
      </div>
    </PreviewBackground>
  )
  return (
    <section className="gallery__recovered">
      <header className="gallery__head">
        <div>
          <h2>{entry.label}</h2>
          <p className="gallery__note">{dateLabel}</p>
        </div>
        <span className="gallery__asset-format">{asset.format.toUpperCase()} · {asset.reconstruction ? 'Reconstruction · ' : ''}{artworkType}</span>
      </header>
      {entry.versions && (
        <div className="segmented" role="group" aria-label="Version">
          {entry.versions.map((each) => (
            <button
              key={each.id}
              type="button"
              aria-pressed={each.id === asset.id}
              onClick={(event) => {
                if (each.id !== asset.id) holdScrollFrom(event)
                setVersion(each.id)
              }}
            >
              {each.versionLabel}
            </button>
          ))}
        </div>
      )}
      {asset.referenceDetail ? (
        <div className="gallery__reference-pair">
          <figure>
            <figcaption>Reconstruction</figcaption>
            {preview}
          </figure>
          <figure>
            <figcaption>Published detail</figcaption>
            <a className="gallery__recovered-preview" href={asset.sourceUrl} target="_blank" rel="noreferrer" aria-label={`Open published source for ${entry.label}`}>
              <img src={asset.referenceDetail.url ?? assetUrl(asset.referenceDetail.file)} alt={`Published reference for ${entry.label}`} />
            </a>
          </figure>
        </div>
      ) : preview}
      <p>{asset.notes}</p>
      <div className="row gallery__asset-downloads">
        <a className="button" href={assetUrl(asset.file)} download>{downloadLabel} {asset.format.toUpperCase()}</a>
        {display && !display.plate && (
          <a className="button button--ghost" href={assetUrl(display.file)} download>Download displayed SVG</a>
        )}
        {(asset.downloads ?? []).map((extra) => (
          <a key={extra.file} className="button button--ghost" href={assetUrl(extra.file)} download>{extra.label}</a>
        ))}
        {!asset.isVector && asset.preview && asset.preview !== asset.file && (
          <a className="button button--ghost" href={assetUrl(asset.preview)} download>Download PNG preview</a>
        )}
      </div>
      <ProgramPlacement asset={asset} />
      <dl className="gallery__asset-source">
        <div><dt>Source</dt><dd>{asset.publisher}{asset.sourceFile ? ` · ${asset.sourceFile}` : ''}</dd></div>
        <div><dt>Collected</dt><dd>{asset.observedDate}</dd></div>
        {!specimenDate && asset.sourceDate && <div><dt>Source-date context</dt><dd>{asset.sourceDate}</dd></div>}
        <div><dt>Artwork</dt><dd>{asset.reconstruction && 'Reconstruction. '}{asset.fidelityNote}</dd></div>
        {asset.creator && <div><dt>Credit</dt><dd>{asset.creator}</dd></div>}
        {asset.license && <div><dt>Source licence</dt><dd>{asset.license_url ? <a href={asset.license_url} target="_blank" rel="noreferrer">{asset.license}</a> : asset.license}</dd></div>}
        {asset.previewNote && <div><dt>Preview</dt><dd>{asset.previewNote}</dd></div>}
        {display && (
          <div><dt>Shown</dt><dd>{display.preserveCanvas
            ? 'The full artwork is shown with its original margins.'
            : asset.pose && display.palette
            ? 'The dark preview keeps the original colours and adds a fine edge around the darkest shapes.'
            : display.palette
            ? `Trimmed to the logo and, for the ${theme === 'dark' ? 'dark' : 'light'} preview, redrawn in colours that keep the parts distinct.`
            : display.recoloured
            ? `Trimmed to the logo and, for the ${theme === 'dark' ? 'dark' : 'light'} preview, with ink that would disappear into it reversed or ${theme === 'dark' ? 'lightened' : 'darkened'}.`
            : display.plate
              ? 'Trimmed to the logo and shown in its own colours on a plate, as its overlapping parts cannot be recoloured apart.'
              : 'Trimmed to the logo, in its own colours.'} {downloadNote}</dd></div>
        )}
        {asset.sourcePage && <div><dt>Publication</dt><dd><a href={asset.sourcePage} target="_blank" rel="noreferrer">View source publication or page</a>{asset.sourceLocator ? ` · ${asset.sourceLocator}` : ''}</dd></div>}
        {(asset.alsoSeen ?? []).filter((seen) => seen.label && seen.source).map((seen) => (
          <div key={seen.source}><dt>Also published in</dt><dd><a href={seen.source} target="_blank" rel="noreferrer">{seen.label}</a></dd></div>
        ))}
        {asset.sourceUrl && asset.sourceUrl !== asset.sourcePage && <div><dt>{asset.reconstruction ? 'Source reference' : 'Original file'}</dt><dd><a href={asset.sourceUrl} target="_blank" rel="noreferrer">View the source file</a></dd></div>}
      </dl>
    </section>
  )
}
