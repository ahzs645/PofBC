// A reviewed design's colour choices use one original SVG. Preview and download share the
// resulting bytes; source files and their provenance remain separately available below.
import { useEffect, useMemo, useState } from 'react'
import { assetUrl } from './collectedCollections.js'
import { paletteFor, renderCollectedPalette } from './collectedPalettes.js'

const paletteFromLocation = (group) => {
  const params = new URLSearchParams(globalThis.location?.search ?? '')
  return paletteFor(group, { paletteId: params.get('colour'), sourceId: params.get('mark') }).id
}

export const CollectedPaletteView = ({ entry }) => {
  const group = entry.paletteGroup
  const master = entry.asset
  const [paletteId, setPaletteId] = useState(() => paletteFromLocation(group))
  const [loaded, setLoaded] = useState(null)
  const [attempt, setAttempt] = useState(0)
  const palette = paletteFor(group, { paletteId })

  useEffect(() => {
    const controller = new AbortController()
    let active = true
    setLoaded(null)
    fetch(assetUrl(master.file), { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`SVG request failed (${response.status})`)
        return response.text()
      })
      .then((text) => { if (active) setLoaded({ file: master.file, text }) })
      .catch((error) => {
        if (active && error.name !== 'AbortError') setLoaded({ file: master.file, error: true })
      })
    return () => { active = false; controller.abort() }
  }, [master.file, attempt])

  useEffect(() => {
    const restore = () => setPaletteId(paletteFromLocation(group))
    globalThis.addEventListener?.('popstate', restore)
    return () => globalThis.removeEventListener?.('popstate', restore)
  }, [group])

  const rendered = useMemo(() => {
    if (loaded?.file !== master.file || !loaded.text) return null
    try {
      const svg = renderCollectedPalette(loaded.text, palette)
      return { url: `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}` }
    } catch {
      return { error: true }
    }
  }, [loaded, master.file, palette])
  const failed = loaded?.file === master.file && loaded.error || rendered?.error
  const sourceFiles = [...new Map((entry.versions ?? [master]).map((source) => [source.file, source])).values()]
  const choose = (id) => {
    setPaletteId(id)
    if (globalThis.history?.replaceState && globalThis.location?.href) {
      const url = new URL(globalThis.location.href)
      url.searchParams.set('mark', entry.id)
      url.searchParams.set('colour', id)
      globalThis.history.replaceState(null, '', url)
    }
  }
  const fileName = `${master.file.split('/').at(-1).replace(/\.svg$/i, '')}-${palette.id}.svg`

  return (
    <section className="gallery__recovered">
      <header className="gallery__head">
        <div>
          <h2>{entry.label}</h2>
          <p className="gallery__note">{entry.years}</p>
        </div>
        <span className="gallery__asset-format">SVG · Vector artwork</span>
      </header>
      <div className="segmented gallery__palette-choices" role="group" aria-label="Colour version">
        {group.palettes.map((choice) => (
          <button key={choice.id} type="button" aria-pressed={choice.id === palette.id}
            onClick={() => choose(choice.id)}>{choice.label}</button>
        ))}
      </div>
      <div className="gallery__recovered-preview" data-dark={palette.darkBackground || undefined}
        aria-busy={!loaded}>
        {rendered?.url
          ? <img src={rendered.url} alt={`${entry.label} — ${palette.label}`} />
          : failed
            ? <p role="alert">The vector preview could not be loaded. <button type="button" className="button button--ghost"
                onClick={() => setAttempt((value) => value + 1)}>Try again</button></p>
            : <p role="status">Loading vector artwork…</p>}
      </div>
      <p className="gallery__note">The SVG download uses the colour version shown.</p>
      <div className="row gallery__asset-downloads">
        {rendered?.url
          ? <a className="button" href={rendered.url} download={fileName}>Download SVG</a>
          : <button className="button" type="button" disabled>Download SVG</button>}
        {failed && <a className="button button--ghost" href={assetUrl(master.file)} download>Download source SVG</a>}
      </div>
      <p>{group.note}</p>
      <dl className="gallery__asset-source">
        <div><dt>Source</dt><dd>{master.publisher}{master.sourceFile ? ` · ${master.sourceFile}` : ''}</dd></div>
        <div><dt>Collected</dt><dd>{master.observedDate}</dd></div>
        {palette.sourceUrl && <div><dt>Colour reference</dt><dd><a href={palette.sourceUrl} target="_blank" rel="noreferrer">
          {palette.sourceLabel || 'Published colour version'}</a></dd></div>}
        {master.sourcePage && <div><dt>Publication</dt><dd><a href={master.sourcePage} target="_blank" rel="noreferrer">
          View source publication or page</a>{master.sourceLocator ? ` · ${master.sourceLocator}` : ''}</dd></div>}
      </dl>
      <details className="gallery__palette-sources">
        <summary>Original source files</summary>
        <p>The original files are kept as published. Colour choices above reuse the source SVG’s shapes; downloads reflect the selected palette.</p>
        <ul>
          {sourceFiles.map((source) => (
            <li key={source.file}>
              <a href={assetUrl(source.file)} download>{source.versionLabel || source.label} · {source.format.toUpperCase()}</a>
              {source.sourceUrl && <> · <a href={source.sourceUrl} target="_blank" rel="noreferrer">Publisher’s file</a></>}
            </li>
          ))}
        </ul>
      </details>
    </section>
  )
}
