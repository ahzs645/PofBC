// Coats of arms: the Province's, with its dated specimens, and the arms of the public bodies,
// universities and local governments around it.
//
// The place is in the address (`?view=arms&holder=british-columbia`), so a holder can be linked to.

import { useEffect, useRef, useState } from 'react'
import { ARMS } from '../assets/crestMark.js'
import { SiteLink } from '../site/navigation.jsx'
import { writeHistory } from '../site/browserHistory.js'
import {
  CATALOGUE_DIR, GROUPS, MUNICIPALITIES, PROVINCE, holderById, holdersInGroup, provinceSections
} from './armsData.js'
import './arms.css'

const SPECIMEN_IMAGES = import.meta.glob('../../research/identity/arms-variants-2026-11-14/reference/*', { eager: true, query: '?url', import: 'default' })
const HOLDER_IMAGES = import.meta.glob('./images/*', { eager: true, query: '?url', import: 'default' })
const specimenUrl = (file) => SPECIMEN_IMAGES[`../../research/identity/arms-variants-2026-11-14/reference/${file}`] ?? null
const holderImageUrl = (file) => HOLDER_IMAGES[`./images/${file}`] ?? null

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
  const url = holder.image?.file ? holderImageUrl(holder.image.file) : null
  if (!url) return <Shield />
  return <img src={url} alt={label && holder.image.alt ? `${holder.image.alt} of ${holder.name}` : (label ?? '')} loading="lazy" decoding="async" />
}

const External = ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>

const SourceList = ({ sources }) => (sources?.length
  ? (
    <ul className="arms__sources">
      {sources.map((source) => <li key={source.url}><External href={source.url}>{source.title}</External></li>)}
    </ul>
    )
  : null)

const PROVINCE_SPECIMEN_COUNT = provinceSections().reduce((sum, section) => sum + section.specimens.length, 0)

const yearOf = (holder) => holder.year ?? holder.granted?.match(/\b(1[89]\d\d|20\d\d)\b/)?.[1] ?? null

const HolderCard = ({ holder, onOpen, feature = false }) => (
  <li className={`arms__card${feature ? ' arms__card--feature' : ''}`}>
    <button type="button" className="arms__open" data-holder={holder.id} onClick={() => onOpen(holder.id)}>
      <span className="arms__art"><HolderImage holder={holder} /></span>
      <span className="arms__card-text">
        <span className="arms__card-name">{holder.name}</span>
        {holder.motto?.text && <span className="arms__card-motto">{holder.motto.text}</span>}
        <span className="arms__card-meta">
          {feature ? `${PROVINCE_SPECIMEN_COUNT} dated specimens, 1850 to 2023` : [yearOf(holder), holder.registered?.join(', ')].filter(Boolean).join(' · ')}
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
        The Province’s arms and their dated drawings, and the registered arms of the Crown’s offices,
        universities, public bodies and local governments in British Columbia. Each entry links to its
        record in the Canadian Heraldic Authority’s public register or another primary source.
      </p>
    </div>
    <ul className="arms__grid arms__grid--feature">
      <HolderCard holder={PROVINCE} onOpen={onOpen} feature />
    </ul>
    {GROUPS.filter(({ id }) => id !== 'province' && id !== 'municipal').map((group) => {
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
    {MUNICIPALITIES.length > 0 && <Municipalities />}
  </>
)

const Municipalities = () => {
  const group = GROUPS.find(({ id }) => id === 'municipal')
  return (
    <section className="arms__group" aria-labelledby="arms-group-municipal">
      <h3 id="arms-group-municipal">{group.title}</h3>
      <p className="arms__group-description">{group.description} Each name opens its register entry; a place with two dates has two registrations.</p>
      <ul className="arms__municipal">
        {MUNICIPALITIES.map((place) => (
          <li key={place.url} title={place.motto ?? undefined}>
            <External href={place.url}>{place.name}</External>
            {place.date && <span className="arms__municipal-date" title={place.kind}>{place.date}</span>}
          </li>
        ))}
      </ul>
    </section>
  )
}

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

const Stages = ({ stages }) => (
  <section className="arms__section" aria-labelledby="arms-stages">
    <h3 id="arms-stages">Three designs</h3>
    <ol className="arms__stages">
      {stages.map((stage) => (
        <li key={stage.year}>
          <span className="arms__stage-year">{stage.year}</span>
          <strong>{stage.title}</strong>
          <p>{stage.text}</p>
          <SourceList sources={stage.sources} />
        </li>
      ))}
    </ol>
  </section>
)

const Specimen = ({ item }) => {
  const url = specimenUrl(item.image)
  return (
    <li className="arms__specimen">
      <figure>
        <a className="arms__specimen-art" href={url ?? undefined} target="_blank" rel="noreferrer" aria-label={`${item.title}, full image`}>
          {url && <img src={url} alt="" loading="lazy" decoding="async" />}
        </a>
        <figcaption>
          <span className="arms__specimen-number">{item.number}</span>
          <strong>{item.title}</strong>
          <span className="arms__specimen-date">{item.date}</span>
          <span className="arms__specimen-class">{item.classification}</span>
          <p>{item.description}</p>
          {item.credit && <p className="arms__credit">{item.credit}</p>}
          <SourceList sources={item.sources} />
        </figcaption>
      </figure>
    </li>
  )
}

const Specimens = () => (
  <section className="arms__section" aria-labelledby="arms-specimens">
    <h3 id="arms-specimens">Dated specimens</h3>
    <p className="arms__group-description">
      Drawings, prints, objects and reproductions, numbered as in the{' '}
      <External href={`${REPOSITORY}/${PROVINCE.catalogue.readme}`}>arms catalogue</External>{' '}
      (<External href={`${REPOSITORY}/${PROVINCE.catalogue.pdf}`}>PDF</External>). A specimen’s date shows when it
      was in use, not when its drawing was made. Images are unretouched source scans and photographs.
    </p>
    {provinceSections().map((section) => (
      <div key={section.title} className="arms__specimen-section">
        <h4>{section.title}</h4>
        <ul className="arms__specimens">
          {section.specimens.map((item) => <Specimen key={item.id} item={item} />)}
        </ul>
      </div>
    ))}
  </section>
)

const Detail = ({ holder, onBack, titleRef }) => (
  <article className="arms__detail" aria-labelledby="arms-holder-name">
    <button type="button" className="arms__back" onClick={onBack}>← Coats of Arms</button>
    <header className="arms__header">
      <div className="arms__art arms__art--large"><HolderImage holder={holder} label={`Arms of ${holder.name}`} /></div>
      <div className="arms__header-text">
        <h2 id="arms-holder-name" ref={titleRef} tabIndex={-1}>{holder.name}</h2>
        {holder.motto?.text && (
          <p className="arms__motto">
            <em>{holder.motto.text}</em>
            {holder.motto.translation && <> — {holder.motto.translation}</>}
          </p>
        )}
        <dl className="arms__facts">
          {holder.granted && <div><dt>Granted</dt><dd>{holder.granted}</dd></div>}
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
    {holder.stages && <Stages stages={holder.stages} />}
    {holder.id === PROVINCE.id && <Specimens />}
    {(holder.links?.length > 0 || holder.sources?.length > 0 || holder.register?.url || holder.related?.length > 0) && (
      <section className="arms__section" aria-labelledby="arms-elsewhere">
        <h3 id="arms-elsewhere">Sources and related pages</h3>
        <ul className="arms__sources">
          {holder.register?.url && <li><External href={holder.register.url}>Canadian Heraldic Authority: public register entry</External></li>}
          {holder.related?.map((related) => (
            <li key={related.url}><External href={related.url}>{related.title}</External>{related.relation && <> — {related.relation}</>}</li>
          ))}
          {holder.sources?.filter((source) => source.url !== holder.register?.url).map((source) => (
            <li key={source.url}><External href={source.url}>{source.title}</External></li>
          ))}
          {holder.links?.map((link) => <li key={link.label}><SiteLink to={link.to}>{link.label} <span aria-hidden="true">→</span></SiteLink></li>)}
        </ul>
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
