import { assetUrl } from './collectedCollections.js'
import { collectedDisplay } from './tileArt.js'
import { useSiteTheme } from '../site/useTheme.js'

/** Source files retain their format; documented redraws are identified as reconstructions. */
export const CollectedMarkView = ({ entry }) => {
  const { asset } = entry
  const { name: theme } = useSiteTheme()
  const display = collectedDisplay(asset, theme)
  const downloadDescription = asset.reconstruction
    ? 'The download is the documented reconstruction.'
    : 'The download is the file as published.'
  return (
    <section className="gallery__recovered">
      <header className="gallery__head">
        <div>
          <h2>{entry.label}</h2>
          <p className="gallery__note">{entry.years}</p>
        </div>
        <span className="gallery__asset-format">{asset.format.toUpperCase()} · {asset.isVector ? asset.reconstruction ? 'Vector reconstruction' : 'Vector artwork' : asset.format === 'svg' ? 'Contains bitmap artwork' : 'Image'}</span>
      </header>
      {display ? (
        <div className="gallery__recovered-preview gallery__recovered-preview--clean">
          <img src={assetUrl(display.file)} alt={entry.label} data-plate={display.plate || undefined} />
        </div>
      ) : (
        <div className="gallery__recovered-preview" data-dark={asset.darkBackground || undefined}>
          <img src={assetUrl(asset.preview || asset.file)} alt={entry.label} />
        </div>
      )}
      <p>{asset.notes}</p>
      <div className="row gallery__asset-downloads">
        <a className="button" href={assetUrl(asset.file)} download>Download {asset.format.toUpperCase()}</a>
        {asset.preview && asset.preview !== asset.file && (
          <a className="button button--ghost" href={assetUrl(asset.preview)} download>Download PNG preview</a>
        )}
      </div>
      <dl className="gallery__asset-source">
        <div><dt>Source</dt><dd>{asset.publisher}{asset.sourceFile ? ` · ${asset.sourceFile}` : ''}</dd></div>
        <div><dt>{asset.reconstructionBy === 'project' ? 'Reconstructed' : 'Collected'}</dt><dd>{asset.observedDate}</dd></div>
        <div><dt>Artwork</dt><dd>{asset.fidelityNote}</dd></div>
        {asset.creator && <div><dt>Credit</dt><dd>{asset.creator}</dd></div>}
        {asset.license && <div><dt>Source licence</dt><dd>{asset.license_url ? <a href={asset.license_url} target="_blank" rel="noreferrer">{asset.license}</a> : asset.license}</dd></div>}
        {asset.previewNote && <div><dt>Preview</dt><dd>{asset.previewNote}</dd></div>}
        {display && (
          <div><dt>Shown</dt><dd>{display.recoloured
            ? `Trimmed to the logo and, for the ${theme === 'dark' ? 'dark' : 'light'} page, with ink that would disappear into it reversed or ${theme === 'dark' ? 'lightened' : 'darkened'}. ${downloadDescription}`
            : display.plate
              ? `Trimmed to the logo and shown in its own colours on a plate, as its overlapping parts cannot be recoloured apart. ${downloadDescription}`
              : `Trimmed to the logo, in its own colours. ${downloadDescription}`}</dd></div>
        )}
        {asset.sourcePage && <div><dt>Publication</dt><dd><a href={asset.sourcePage} target="_blank" rel="noreferrer">View source publication or page</a>{asset.sourceLocator ? ` · ${asset.sourceLocator}` : ''}</dd></div>}
        {asset.sourceUrl && asset.sourceUrl !== asset.sourcePage && <div><dt>{asset.reconstruction ? 'Reference file' : 'Original file'}</dt><dd><a href={asset.sourceUrl} target="_blank" rel="noreferrer">View the source file</a></dd></div>}
        {asset.references?.map((reference) => (
          <div key={reference.url}><dt>Reference</dt><dd><a href={reference.url} target="_blank" rel="noreferrer">{reference.title}</a>{reference.locator ? ` · ${reference.locator}` : ''}</dd></div>
        ))}
        {asset.researchUrl && <div><dt>Research</dt><dd><a href={asset.researchUrl} target="_blank" rel="noreferrer">Read the reconstruction research and checks</a></dd></div>}
      </dl>
    </section>
  )
}
