// Coats of arms: the Province's, with its dated specimens, and the arms of the public bodies,
// universities and local governments around it, each with the artwork acquired for it.
//
// The place is in the address (`?view=arms&holder=british-columbia`), so a holder can be linked to.

import { Breadcrumbs } from '../site/Breadcrumbs.jsx'
import { useEffect, useRef, useState } from 'react'
import { ARMS } from '../assets/crestMark.js'
import { SiteLink } from '../site/navigation.jsx'
import { writeHistory } from '../site/browserHistory.js'
import {
  ACQUISITION_DIR, CATALOGUE_DIR, GROUPS, PROVINCE, PROVINCE_STORY, holderById, holdersInGroup
} from './armsData.js'
import './arms.css'
import { SourceList } from '../site/SourceList.jsx'

const SPECIMEN_IMAGES = import.meta.glob('../../research/identity/arms-variants-2026-11-14/reference/*', { eager: true, query: '?url', import: 'default' })
const HOLDER_IMAGES = import.meta.glob('./images/*', { eager: true, query: '?url', import: 'default' })
const ARTWORK_IMAGES = import.meta.glob('./artwork/*.webp', { eager: true, query: '?url', import: 'default' })
// The originals of artwork that is an SVG (build-arms-artwork.py copies them beside their WebPs).
// A rendering is shown as the vector it is; the lighter WebP stays the thumbnail in lists of holders.
const ARTWORK_VECTORS = import.meta.glob('./artwork/*.svg', { eager: true, query: '?url', import: 'default' })
const specimenUrl = (file) => SPECIMEN_IMAGES[`../../research/identity/arms-variants-2026-11-14/reference/${file}`] ?? null
const holderImageUrl = (file) => HOLDER_IMAGES[`./images/${file}`] ?? null
const artworkUrl = (id) => ARTWORK_IMAGES[`./artwork/${id}.webp`] ?? null
/** An artwork record's display copy: the acquisition's, or a file kept in ./images/. */
const artworkVectorUrl = (item) => (item.vectorImage ? ARTWORK_VECTORS[`./artwork/${item.vectorImage}`] ?? null : null)
const artworkImageUrl = (item) => (item.file ? holderImageUrl(item.file) : artworkVectorUrl(item) ?? artworkUrl(item.id))

const REPOSITORY = 'https://github.com/ahzs645/PofBC/blob/main'

const readHolder = () => {
  const id = new URLSearchParams(globalThis.location?.search ?? '').get('holder')
  return holderById(id) ? id : null
}

const writeHolder = (id) => {
  if (!globalThis.location) return
  const url = new URL(globalThis.location.href)
  url.searchParams.set('view', 'arms')
  if (id) url.searchParams.set('holder', id)
  else url.searchParams.delete('holder')
  writeHistory(url)
}

/** The Province's arms, drawn from the same vector as the Arms lockup, in the page's ink. */
const ProvinceArms = ({ label }) => (
  <svg className="arms__vector" viewBox={`0 0 ${ARMS.width} ${ARMS.height}`} role={label ? 'img' : undefined} aria-label={label} aria-hidden={label ? undefined : true} focusable="false">
    {ARMS.shapes.map((shape, index) => <path key={index} d={shape.d} fill="currentColor" />)}
  </svg>
)

const Shield = () => (
  <svg className="arms__placeholder" viewBox="0 0 40 48" aria-hidden="true" focusable="false">
    <path d="M4 4h32v18c0 12-8 19-16 22C12 41 4 34 4 22Z" fill="none" stroke="currentColor" strokeWidth="1.5" />
  </svg>
)

const HolderImage = ({ holder, label }) => {
  if (holder.image?.kind === 'vector') return <ProvinceArms label={label} />
  const url = holder.image?.artwork ? artworkUrl(holder.image.artwork) : holder.image?.file ? holderImageUrl(holder.image.file) : null
  if (!url) return <Shield />
  return <img src={url} alt={label && holder.image.alt ? `${holder.image.alt} of ${holder.name}` : (label ?? '')} loading="lazy" decoding="async" />
}

const External = ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>

// A specimen's or stage's own sources, compact, inside its card.
const CardSources = ({ sources }) => (sources?.length
  ? (
    <ul className="arms__sources">
      {sources.map((source) => <li key={source.url}><External href={source.url}>{source.title}</External></li>)}
    </ul>
    )
  : null)

// The historical entries, each design, object or treatment once; the modern renderings are not counted.
const PROVINCE_ENTRY_COUNT = PROVINCE_STORY.filter(({ renderings }) => !renderings)
  .reduce((sum, section) => sum + section.groups.reduce((count, { entries }) => count + entries.length, 0), 0)

const yearOf = (holder) => holder.year ?? holder.granted?.match(/\b(1[89]\d\d|20\d\d)\b/)?.[1] ?? null

const HolderCard = ({ holder, onOpen, feature = false }) => (
  <li className={`arms__card${feature ? ' arms__card--feature' : ''}`}>
    <button type="button" className="arms__open" data-holder={holder.id} onClick={() => onOpen(holder.id)}>
      <span className="arms__art"><HolderImage holder={holder} /></span>
      <span className="arms__card-text">
        <span className="arms__card-name">{holder.name}</span>
        {holder.motto?.text && <span className="arms__card-motto">{holder.motto.text}</span>}
        <span className="arms__card-meta">
          {feature ? `${PROVINCE_ENTRY_COUNT} dated specimens, 1850 to 2023` : [yearOf(holder), holder.registered?.join(', ')].filter(Boolean).join(' · ')}
        </span>
      </span>
    </button>
  </li>
)

const Index = ({ onOpen }) => (
  <>
    <div className="arms__intro">
      <h2>Coats of Arms</h2>
      <p>
        The Province’s arms and their dated drawings, and the registered arms of B.C.’s public
        bodies, each linked to its record in the Canadian Heraldic Authority’s register or another
        primary source.
      </p>
    </div>
    <ul className="arms__grid arms__grid--feature">
      <HolderCard holder={PROVINCE} onOpen={onOpen} feature />
    </ul>
    {GROUPS.filter(({ id }) => id !== 'province').map((group) => {
      const holders = holdersInGroup(group.id)
      if (!holders.length) return null
      return (
        <section key={group.id} className="arms__group" aria-labelledby={`arms-group-${group.id}`}>
          <h3 id={`arms-group-${group.id}`}>{group.title}</h3>
          <p className="arms__group-description">{group.description}</p>
          <ul className="arms__grid">
            {holders.map((holder) => <HolderCard key={holder.id} holder={holder} onOpen={onOpen} />)}
          </ul>
        </section>
      )
    })}
  </>
)

const ELEMENTS = [['arms', 'Arms'], ['crest', 'Crest'], ['supporters', 'Supporters'], ['compartment', 'Compartment'], ['motto', 'Motto'], ['badge', 'Badge'], ['flag', 'Flag']]

const Elements = ({ record, summary }) => {
  const rows = ELEMENTS.map(([key, term]) => [term, record?.[key]]).filter(([, text]) => text)
  if (!rows.length) return null
  return (
    <details className="arms__blazon">
      <summary>{summary}</summary>
      <dl>
        {rows.map(([term, text]) => (
          <div key={term}><dt>{term}</dt><dd>{text}</dd></div>
        ))}
      </dl>
    </details>
  )
}

/**
 * Whether a picture is dark ink on a transparent ground, which the dark theme's tile would swallow.
 * Such a picture is given a soft light well; one that draws its own opaque ground needs none, and
 * nothing is recoloured. A picture that cannot be read (another origin) is left as it is.
 */
const needsLightGround = (image) => {
  try {
    const size = 48
    const canvas = document.createElement('canvas')
    canvas.width = size
    canvas.height = size
    const context = canvas.getContext('2d', { willReadFrequently: true })
    context.drawImage(image, 0, 0, size, size)
    const { data } = context.getImageData(0, 0, size, size)
    let clear = 0
    let inked = 0
    let light = 0
    for (let at = 0; at < data.length; at += 4) {
      if (data[at + 3] < 16) { clear += 1; continue }
      inked += 1
      light += (0.2126 * data[at] + 0.7152 * data[at + 1] + 0.0722 * data[at + 2]) / 255
    }
    return clear > size * size * 0.05 && inked > 0 && light / inked < 0.35
  } catch {
    return false
  }
}
const groundFor = (event) => {
  const frame = event.currentTarget.parentElement
  if (frame && needsLightGround(event.currentTarget)) frame.dataset.ground = 'light'
}

const KINDS = {
  arms: 'Arms',
  shield: 'Shield',
  'partial-achievement': 'Partial achievement',
  flag: 'Flag',
  badge: 'Badge',
  seal: 'Seal',
  lockup: 'Lockup',
  'historical-emblem': 'Historical emblem',
  'letters-patent': 'Letters patent'
}

/**
 * Terms that several renderings on a page share are said once for the page: each rendering keeps the
 * short name of its terms (before the first semicolon), and the page says what that name means.
 */
const sharedTerms = (items) => {
  const counts = new Map()
  for (const { licence } of items) if (licence?.includes('; ')) counts.set(licence, (counts.get(licence) ?? 0) + 1)
  return [...counts].filter(([, count]) => count > 1).map(([licence]) => {
    const at = licence.indexOf('; ')
    return { licence, head: licence.slice(0, at), tail: licence.slice(at + 2) }
  })
}

const ArtworkItem = ({ item, shared = [] }) => {
  const url = artworkImageUrl(item)
  const short = shared.find(({ licence }) => licence === item.licence)?.head
  return (
    <li className="arms__specimen">
      <figure>
        <a className="arms__specimen-art" href={url ?? undefined} target="_blank" rel="noreferrer" aria-label={`${item.title}, full image`}>
          {url && <img src={url} alt="" loading="lazy" decoding="async" onLoad={groundFor} />}
        </a>
        <figcaption>
          <span className="arms__specimen-class">{[KINDS[item.kind] ?? item.kind, item.historical && 'historical', item.vector && 'vector'].filter(Boolean).join(' · ')}</span>
          <strong>{item.title}</strong>
          {item.date && <span className="arms__specimen-date">{item.date}</span>}
          <p className="arms__credit">
            {item.author}
            {item.licence && <> · {item.licenceUrl ? <External href={item.licenceUrl}>{short ?? item.licence}</External> : short ?? item.licence}</>}
          </p>
          <ul className="arms__sources">
            {item.page && <li><External href={item.page}>Source</External></li>}
            {item.original && <li><External href={`${REPOSITORY}/${ACQUISITION_DIR}/assets/${item.original}`}>Original file ({item.format})</External></li>}
            {item.alternates?.map((file) => <li key={file}><External href={`${REPOSITORY}/${ACQUISITION_DIR}/assets/${file}`}>Also as {file.split('.').at(-1).toUpperCase()}</External></li>)}
          </ul>
        </figcaption>
      </figure>
    </li>
  )
}

const Artwork = ({ items }) => {
  const pictures = items.filter(({ kind }) => kind !== 'letters-patent')
  const letters = items.filter(({ kind }) => kind === 'letters-patent')
  const shared = sharedTerms(items)
  return (
    <section className="arms__section" aria-labelledby="arms-artwork">
      <h3 id="arms-artwork">Artwork</h3>
      <p className="arms__group-description">
        Every rendering acquired for this page, unretouched; a rendering’s date is not always the design’s.
      </p>
      {shared.map(({ licence, head, tail }) => (
        <p key={licence} className="arms__credit arms__terms"><strong>{head}</strong>: {tail}</p>
      ))}
      {pictures.length > 0 && (
        <ul className="arms__specimens">
          {pictures.map((item) => <ArtworkItem key={item.id} item={item} shared={shared} />)}
        </ul>
      )}
      {letters.length > 0 && (
        <details className="arms__letters">
          <summary>Letters patent and register pages ({letters.length})</summary>
          <ul className="arms__specimens">
            {letters.map((item) => <ArtworkItem key={item.id} item={item} shared={shared} />)}
          </ul>
        </details>
      )}
    </section>
  )
}

// The Province's account, oldest first (armsData.js PROVINCE_STORY). Each entry shows its best
// file and lists every other copy of the same drawing or object, so nothing appears twice and no
// copy, credit or source is lost.

const fileImageUrl = (file) => (file.from === 'catalogue' ? specimenUrl(file.image) : artworkImageUrl(file.item))
const repositoryFile = (path) => `${REPOSITORY}/${path}`

/** A file's own links: its image or original in the repository, its other formats, its source page. */
const FileLinks = ({ file }) => (
  <>
    {file.from === 'catalogue'
      ? <li><External href={repositoryFile(`${CATALOGUE_DIR}/reference/${file.image}`)}>Catalogue image ({file.format})</External></li>
      : (
        <>
          {file.page && <li><External href={file.page}>Source</External></li>}
          {file.original && <li><External href={repositoryFile(`${ACQUISITION_DIR}/assets/${file.original}`)}>Original file ({file.format})</External></li>}
          {file.alternates.map((path) => <li key={path}><External href={repositoryFile(`${ACQUISITION_DIR}/assets/${path}`)}>Also as {path.split('.').at(-1).toUpperCase()}</External></li>)}
        </>
        )}
  </>
)

const FileCredit = ({ file }) => (file.from === 'catalogue'
  ? file.credit
  : (
    <>
      {file.author}
      {file.licence && <> · {file.licenceUrl ? <External href={file.licenceUrl}>{file.licence}</External> : file.licence}</>}
    </>
    ))

/** Every copy of one entry, the one shown first. */
const Copies = ({ entry }) => (
  <div className="arms__copies">
    <span className="arms__copies-title">Held in {entry.files.length} copies</span>
    <ol>
      {entry.files.map((file, index) => (
        <li key={file.id}>
          <span className="arms__copy-name">
            {index === 0 && <span className="arms__copy-shown">Shown · </span>}
            {file.number ? `No. ${file.number}: ${file.title}` : file.title}
            {file.vector && ' · vector'}
          </span>
          <span className="arms__copy-meta">
            {file.date}
            {(file.credit || file.author) && <> · <FileCredit file={file} /></>}
          </span>
          <ul className="arms__copy-links"><FileLinks file={file} /></ul>
        </li>
      ))}
    </ol>
  </div>
)

const StoryEntry = ({ entry }) => {
  const url = fileImageUrl(entry.lead)
  const single = entry.files.length === 1 ? entry.lead : null
  const kind = [KINDS[entry.kind] ?? entry.kind, entry.historical && 'historical'].filter(Boolean).join(' · ')
  return (
    <li className="arms__specimen" data-entry={entry.id}>
      <figure>
        <a className="arms__specimen-art" href={url ?? undefined} target="_blank" rel="noreferrer" aria-label={`${entry.title}, full image`}>
          {url && <img src={url} alt="" loading="lazy" decoding="async" onLoad={groundFor} />}
        </a>
        <figcaption>
          {entry.number && <span className="arms__specimen-number">No. {entry.number}</span>}
          <strong>{entry.title}</strong>
          <span className="arms__specimen-date">{entry.date}</span>
          <span className="arms__specimen-class">{[entry.classification ?? kind, entry.lead.vector && 'vector'].filter(Boolean).join(' · ')}</span>
          {entry.description && <p>{entry.description}</p>}
          {entry.follows && <p className="arms__credit">Redrawn from no. {entry.follows}; a reconstruction, not original artwork.</p>}
          {/* The entry's credit is its own file's; when another copy is shown, the copies list credits each. */}
          {entry.credit && entry.lead.id === entry.id && <p className="arms__credit">{entry.credit}</p>}
          {single?.from === 'artwork' && (
            <>
              <p className="arms__credit"><FileCredit file={single} /></p>
              <ul className="arms__sources"><FileLinks file={single} /></ul>
            </>
          )}
          {!single && <Copies entry={entry} />}
          <CardSources sources={entry.sources} />
        </figcaption>
      </figure>
    </li>
  )
}

const Story = () => (
  <>
    <p className="arms__story-note">
      Each design, object or treatment appears once, oldest first; where several copies of one drawing are held, the
      best is shown and the rest are listed with it. Numbers are the{' '}
      <External href={`${REPOSITORY}/${PROVINCE.catalogue.readme}`}>arms catalogue</External>’s{' '}
      (<External href={`${REPOSITORY}/${PROVINCE.catalogue.pdf}`}>PDF</External>). A specimen’s date shows when it
      was printed or seen, not when its drawing was made.
    </p>
    {PROVINCE_STORY.map((section) => (
      <section key={section.id} className={`arms__section arms__era${section.renderings ? ' arms__era--renderings' : ''}`} aria-labelledby={`arms-era-${section.id}`}>
        <h3 id={`arms-era-${section.id}`}>
          {section.title}
          <span className="arms__era-period">{section.period}</span>
        </h3>
        {section.stage && <p className="arms__era-text"><strong>{section.stage.title}.</strong> {section.stage.text}</p>}
        {section.text && <p className="arms__era-text">{section.text}</p>}
        <CardSources sources={section.sources} />
        {section.groups.map((group, index) => (
          <div key={group.title ?? index} className="arms__specimen-section">
            {group.title && <h4>{group.title}</h4>}
            <ul className="arms__specimens">
              {group.entries.map((entry) => <StoryEntry key={entry.id} entry={entry} />)}
            </ul>
          </div>
        ))}
        {section.letters.length > 0 && (
          <details className="arms__letters">
            <summary>Letters patent ({section.letters.length})</summary>
            <ul className="arms__specimens">
              {section.letters.map((entry) => <StoryEntry key={entry.id} entry={entry} />)}
            </ul>
          </details>
        )}
      </section>
    ))}
  </>
)

const Detail = ({ holder, onBack, titleRef }) => (
  <article className="arms__detail" aria-labelledby="arms-holder-name">
    <Breadcrumbs label="Coats of Arms" steps={[{ label: 'All coats of arms', onClick: onBack }, { label: holder.name }]} />
    <header className="arms__header">
      <div className="arms__art arms__art--large"><HolderImage holder={holder} label={`Arms of ${holder.name}`} /></div>
      <div className="arms__header-text">
        <div className="arms__title-row">
          <h2 id="arms-holder-name" ref={titleRef} tabIndex={-1}>{holder.name}</h2>
        </div>
        {holder.motto?.text && (
          <p className="arms__motto">
            <em>{holder.motto.text}</em>
            {holder.motto.translation && <> ({holder.motto.translation})</>}
          </p>
        )}
        {holder.motto?.note && <p className="arms__note">{holder.motto.note}</p>}
        <dl className="arms__facts">
          {holder.granted && <div><dt>{holder.grantedLabel ?? 'Granted'}</dt><dd>{holder.granted}</dd></div>}
          {holder.registeredInCanada && <div><dt>In Canada</dt><dd>{holder.registeredInCanada}</dd></div>}
          {holder.registered?.length > 0 && <div><dt>Registered</dt><dd>{holder.registered.join(', ')}</dd></div>}
          {holder.register?.volume && <div><dt>Register</dt><dd>{holder.register.volume}</dd></div>}
        </dl>
        {holder.description && <p className="arms__description">{holder.description}</p>}
        {holder.note && <p className="arms__note">{holder.note}</p>}
        <Elements record={holder.symbolism} summary="Symbolism, from the register" />
        <Elements record={holder.blazon} summary="Blazon" />
        {holder.image?.credit && (
          <p className="arms__credit">
            {holder.image.alt ? `${holder.image.alt}: ` : 'Image: '}
            {holder.image.page ? <External href={holder.image.page}>{holder.image.credit}</External> : holder.image.credit}
          </p>
        )}
      </div>
    </header>
    {holder.id === PROVINCE.id
      ? <Story />
      : holder.artwork?.length > 0 && <Artwork items={holder.artwork} />}
    {(holder.links?.length > 0 || holder.sources?.length > 0 || holder.register?.url || holder.related?.length > 0) && (
      <section className="arms__section" aria-labelledby="arms-elsewhere">
        <h3 id="arms-elsewhere">Sources</h3>
        <SourceList sources={[
          ...(holder.register?.url ? [{ url: holder.register.url, title: 'Canadian Heraldic Authority: public register entry' }] : []),
          ...(holder.related ?? []).map((related) => ({ url: related.url, title: related.title, note: related.relation })),
          ...(holder.sources ?? []).filter((source) => source.url !== holder.register?.url).map((source) => ({ url: source.url, title: source.title }))
        ]} />
        {holder.links?.length > 0 && (
          <p className="arms__links">
            {holder.links.map((link) => <SiteLink key={link.label} to={link.to}>{link.label} <span aria-hidden="true">→</span></SiteLink>)}
          </p>
        )}
      </section>
    )}
  </article>
)

export const ArmsView = () => {
  const [holderId, setHolderId] = useState(readHolder)
  const title = useRef(null)
  const last = useRef(null)
  const holder = holderById(holderId)

  useEffect(() => {
    if (holder) {
      globalThis.scrollTo?.({ top: 0 })
      title.current?.focus({ preventScroll: true })
    }
  }, [holder])

  const open = (id) => {
    last.current = id
    writeHolder(id)
    setHolderId(id)
  }
  const back = () => {
    writeHolder(null)
    setHolderId(null)
    requestAnimationFrame(() => {
      const button = last.current && document.querySelector(`[data-holder="${last.current}"]`)
      button?.focus()
    })
  }

  return (
    <section className="arms" aria-label="Coats of Arms">
      {holder ? <Detail holder={holder} onBack={back} titleRef={title} /> : <Index onOpen={open} />}
    </section>
  )
}
