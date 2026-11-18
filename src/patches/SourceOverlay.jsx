import { useState } from 'react'

const media = { photo: 'Photograph', vector: 'Vector reference', scan: 'Scan' }

export function SourceOverlay ({ record, drawing, title }) {
  const [selected, setSelected] = useState(0)
  const [opacity, setOpacity] = useState(45)
  const [failedCrop, setFailedCrop] = useState(null)
  const source = record.sources[selected]
  const [width, height] = source.size
  const failed = source.id === failedCrop
  const fit = source.fit
  const transform = fit && `translate(${fit.x}%, ${fit.y}%) rotate(${fit.angle}deg) scale(${fit.scale})`

  return (
    <figure className="patch__stage patch__stage--overlay">
      <figcaption>Source overlay</figcaption>
      {record.sources.length > 1 && <label className="source-overlay__control">Source
        <select aria-label="Source reference" value={selected} onChange={(event) => setSelected(Number(event.target.value))}>
          {record.sources.map((item, i) => <option value={i} key={item.id}>{item.id} · {item.medium}</option>)}
        </select>
      </label>}
      {failed ? <p role="alert">The reference crop could not load.</p> :
        <div className="source-overlay__frame" style={{ '--crop-aspect': width / height }}>
          <img src={`${import.meta.env.BASE_URL}${source.crop}`} alt={`${source.id}, ${source.medium}`} onError={() => setFailedCrop(source.id)} />
          {drawing?.url && <img className="source-overlay__art" src={drawing.url} alt={`Drawing of ${title}`} style={{ opacity: opacity / 100, transform }} />}
        </div>}
      <label className="source-overlay__control">Drawing opacity
        <input aria-label="Drawing opacity" aria-valuetext={`${opacity} percent`} type="range" min="0" max="100" value={opacity} disabled={failed || !drawing?.url} onChange={(event) => setOpacity(Number(event.target.value))} />
        <output>{opacity}%</output>
      </label>
      <p>{media[source.kind] ?? 'Reference'} · {source.medium} · {source.url ? <a href={source.url} target="_blank" rel="noreferrer">{source.id}</a> : source.id}</p>
      <p>{fit ? 'The drawing is aligned to this specimen’s angle and position.' : 'The drawing is centred in the source crop.'} Tilt, overlap and perspective can shift the edges.</p>
      {record.unavailable?.length > 0 && <p>No crop is available for {record.unavailable.join(', ')}.</p>}
    </figure>
  )
}
