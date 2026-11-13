import { useState } from 'react'
import { assetUrl, parseSpecimenDate } from './collectedCollections.js'
import { collectedDisplay } from './tileArt.js'
import { useSiteTheme } from '../site/useTheme.js'
import { CollectedPaletteView } from './CollectedPaletteView.jsx'
import { collectedPreviewFile } from './collectedPalettes.js'

/** A recovered mark is displayed in its source format; raster files stay raster. */
export const CollectedMarkView = ({ entry }) => entry.paletteGroup
  ? <CollectedPaletteView entry={entry} />
  : <SourceMarkView entry={entry} />

const SourceMarkView = ({ entry }) => {
  const [version, setVersion] = useState(() => {
    const requested = new URLSearchParams(globalThis.location?.search ?? '').get('mark')
    return entry.versions?.find((each) => each.id === requested)?.id ?? entry.asset.id
  })
  const asset = entry.versions?.find((each) => each.id === version) ?? entry.asset
  const specimenDate = parseSpecimenDate(asset.specimenDate ?? asset.sourceDate)
  const dateLabel = specimenDate
    ? asset.sourceReproduction && asset.historicalDateLabel
      ? `${asset.historicalDateLabel} · reproduced ${specimenDate.label}`
      : `Seen ${specimenDate.label}`
    : 'Logo dates unestablished'
  const { name: theme } = useSiteTheme()
  // A version chosen by its colour is shown in that colour: one whose page copy would be redrawn
  // (a white version on the light page) is shown as published, on its own plate.
  const copy = collectedDisplay(asset, theme)
  const display = entry.versions && copy?.recoloured ? null : copy
  return (
    <section className="gallery__recovered">
      <header className="gallery__head">
        <div>
          <h2>{entry.label}</h2>
          <p className="gallery__note">{dateLabel}</p>
        </div>
        <span className="gallery__asset-format">{asset.format.toUpperCase()} · {asset.isVector ? 'Vector artwork' : asset.format === 'svg' ? 'Contains bitmap artwork' : 'Image'}</span>
      </header>
      {entry.versions && (
        <div className="segmented" role="group" aria-label="Version">
          {entry.versions.map((each) => (
            <button
              key={each.id}
              type="button"
              aria-pressed={each.id === asset.id}
              onClick={() => setVersion(each.id)}
            >
              {each.versionLabel}
            </button>
          ))}
        </div>
      )}
      {display ? (
        <div className="gallery__recovered-preview gallery__recovered-preview--clean">
          <img src={assetUrl(display.file)} alt={entry.label} data-plate={display.plate || undefined} />
        </div>
      ) : (
        <div className="gallery__recovered-preview" data-dark={asset.darkBackground || undefined}>
          <img src={assetUrl(collectedPreviewFile(asset))} alt={entry.label} />
        </div>
      )}
      <p>{asset.notes}</p>
      <div className="row gallery__asset-downloads">
        <a className="button" href={assetUrl(asset.file)} download>Download {asset.format.toUpperCase()}</a>
        {(asset.downloads ?? []).map((extra) => (
          <a key={extra.file} className="button button--ghost" href={assetUrl(extra.file)} download>{extra.label}</a>
        ))}
        {!asset.isVector && asset.preview && asset.preview !== asset.file && (
          <a className="button button--ghost" href={assetUrl(asset.preview)} download>Download PNG preview</a>
        )}
      </div>
      <dl className="gallery__asset-source">
        <div><dt>Source</dt><dd>{asset.publisher}{asset.sourceFile ? ` · ${asset.sourceFile}` : ''}</dd></div>
        <div><dt>Collected</dt><dd>{asset.observedDate}</dd></div>
        {!specimenDate && asset.sourceDate && <div><dt>Source-date context</dt><dd>{asset.sourceDate}</dd></div>}
        {/* How a redrawn file was made stays in its record, not on the page. */}
        {!asset.reconstruction && <div><dt>Artwork</dt><dd>{asset.fidelityNote}</dd></div>}
        {asset.creator && <div><dt>Credit</dt><dd>{asset.creator}</dd></div>}
        {asset.license && <div><dt>Source licence</dt><dd>{asset.license_url ? <a href={asset.license_url} target="_blank" rel="noreferrer">{asset.license}</a> : asset.license}</dd></div>}
        {asset.previewNote && <div><dt>Preview</dt><dd>{asset.previewNote}</dd></div>}
        {display && (
          <div><dt>Shown</dt><dd>{display.recoloured
            ? `Trimmed to the logo and, for the ${theme === 'dark' ? 'dark' : 'light'} page, with ink that would disappear into it reversed or ${theme === 'dark' ? 'lightened' : 'darkened'}. The download is the file as published.`
            : display.plate
              ? 'Trimmed to the logo and shown in its own colours on a plate, as its overlapping parts cannot be recoloured apart. The download is the file as published.'
              : 'Trimmed to the logo, in its own colours. The download is the file as published.'}</dd></div>
        )}
        {asset.sourcePage && <div><dt>Publication</dt><dd><a href={asset.sourcePage} target="_blank" rel="noreferrer">View source publication or page</a>{asset.sourceLocator ? ` · ${asset.sourceLocator}` : ''}</dd></div>}
        {asset.sourceUrl && asset.sourceUrl !== asset.sourcePage && <div><dt>Original file</dt><dd><a href={asset.sourceUrl} target="_blank" rel="noreferrer">View the source file</a></dd></div>}
      </dl>
    </section>
  )
}
