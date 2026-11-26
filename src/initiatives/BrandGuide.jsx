import { useEffect, useState } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import './brandGuide.css'

const PageText = ({ base, page }) => {
  const [pages, setPages] = useState(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    fetch(base + '/text.json', { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('Page text unavailable')
        return response.json()
      })
      .then(setPages)
      .catch(() => { if (!controller.signal.aborted) setFailed(true) })
    return () => controller.abort()
  }, [base])
  if (failed) return <p role="status">Page text could not load. The publisher’s PDF is linked above.</p>
  if (!pages) return <p role="status">Loading page text…</p>
  return pages[page - 1]?.map((line, i) => <p key={i}>{line}</p>)
}

export const BrandGuide = ({ guide, source, requestedPage, onPage }) => {
  const [showText, setShowText] = useState(false)
  const [zoom, setZoom] = useState(false)
  const [colourFormat, setColourFormat] = useState('screen')
  const pages = guide.chapters.flatMap((chapter) => chapter.pages.map((title) => ({ title, chapter })))
  const number = Number(requestedPage)
  const page = Number.isInteger(number) && number >= 1 && number <= pages.length ? number : 1
  const { title, chapter } = pages[page - 1]
  const base = import.meta.env.BASE_URL + 'tourism/guides/' + guide.folder
  const firstPage = (group) => pages.findIndex((p) => p.chapter === group) + 1
  const showPalette = chapter === pages[guide.palettePage - 1].chapter
  const related = guide.related?.[chapter.title] ?? []
  const select = (next) => { setZoom(false); onPage(next) }

  return <div className="brand-guide">
    <nav className="brand-guide__contents" aria-label="Guide chapters">
      <h4>Contents</h4>
      {guide.chapters.map((group) => {
        const start = firstPage(group)
        const last = start + group.pages.length - 1
        return <button key={group.title} type="button" aria-current={group === chapter ? 'true' : undefined}
          onClick={() => select(start)}><span>{group.title}</span><small>{start === last ? start : start + '–' + last}</small></button>
      })}
    </nav>
    <div className="brand-guide__reader">
      <header><h4>{chapter.title}</h4><p>{chapter.description}</p></header>
      <div className="brand-guide__controls">
        <label>Page <select value={page} onChange={(event) => select(Number(event.target.value))} aria-label="Guide page">
          {guide.chapters.map((group) => <optgroup key={group.title} label={group.title}>{group.pages.map((name, i) => {
            const n = firstPage(group) + i
            return <option key={n} value={n}>{n}. {name}</option>
          })}</optgroup>)}
        </select></label>
        <div><button type="button" aria-label="Previous guide page" disabled={page === 1} onClick={() => select(page - 1)}>←</button>
          <button type="button" aria-label="Next guide page" disabled={page === pages.length} onClick={() => select(page + 1)}>→</button></div>
      </div>
      <div className={'brand-guide__sheet' + (zoom ? ' brand-guide__sheet--zoom' : '')} tabIndex={zoom ? 0 : undefined}
        role="region" aria-label="Original guide page">
        <img key={page} src={base + '/' + page + '.webp'} alt={source.title + ', page ' + page + ', ' + title}
          width="1680" height={guide.pageHeight} />
      </div>
      <div className="brand-guide__caption"><span aria-live="polite">Page {page} of {pages.length} · {title}</span>
        <button type="button" aria-pressed={zoom} onClick={() => setZoom(!zoom)}>{zoom ? 'Fit page' : 'Enlarge page'}</button>
        <a href={source.url + '#page=' + page} target="_blank" rel="noreferrer">Original PDF ↗</a>
      </div>
      <details className="brand-guide__text" onToggle={(event) => setShowText(event.currentTarget.open)}>
        <summary>Read page text</summary>{showText && <PageText base={base} page={page} />}
      </details>
      {showPalette && <section className="brand-guide__palette"><h4>Colour specifications</h4>
        <label className="brand-guide__format">Colour values <select value={colourFormat} onChange={(event) => setColourFormat(event.target.value)}>
          <option value="screen">Screen (hex)</option><option value="process">CMYK</option><option value="spot">Pantone</option>
        </select></label>
        <ul>{guide.colours.map(([role, name, colour, process, spot]) => {
          const screen = guide.printOnly?.includes(name) ? 'Print only in guide' : colour
          const values = { screen, process, spot }
          return <li key={name}><i style={{ backgroundColor: colour }} aria-hidden="true" />
            <div><strong>{name}</strong><small>{role} · {values[colourFormat] ?? 'Unspecified'}</small></div>
          </li>
        })}</ul>
      </section>}
      {related.length > 0 && <nav aria-label="Related brand material" className="initiative__related">
        {related.map(({ label, to }) => <SiteLink key={label} to={to}>{label} →</SiteLink>)}
      </nav>}
    </div>
  </div>
}
