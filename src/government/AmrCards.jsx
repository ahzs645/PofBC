// Which minister administered an Act, from BC Laws' Acts and Ministers' Responsibilities listings
// (December 2015 onward). A date is shown only when the order in council that made the change dates
// it; otherwise the two listings it fell between, or "listed by December 2015" for what the first
// listing already held. A listing's own period is never shown as a date.

import { useState } from 'react'
import { formatEventDate } from './events.js'
import { INSTRUMENTS } from './instruments.js'
import { FIRST_YEAR, lifeOf, PRESENT_YEAR } from './snapshot.js'
import { SourceLink } from './AtlasCards.jsx'
import { useAmr } from './useAmr.js'

const dateOf = (value) => formatEventDate({ start: String(value) })
const month = (value) => (value === 'current' ? 'now' : dateOf(value))

/** A boundary as the evidence allows: a dated order, two listings it fell between, or before coverage. */
const Boundary = ({ boundary, isDated, start }) => {
  if (!boundary) return null
  if (isDated(boundary)) {
    return <>{dateOf(boundary.date)}{boundary.dateKind === 'approved' ? ' (order approved)' : ''} · <SourceLink source={{ url: boundary.source, title: `OIC ${boundary.oic}` }} /></>
  }
  if (boundary.basis === 'bounded') return <>between the {month(boundary.between[0])} and {month(boundary.between[1])} listings</>
  if (boundary.basis === 'before-coverage') return <>{start ? 'listed by December 2015' : ''}</>
  return null
}

/** One run of an Act under one minister title: its scope and its start and end as far as they are known. */
const Run = ({ run, amr, ministry }) => (
  <span className="gov-events__sources">
    {ministry}{run.ministerTitle}
    {run.scope === 'partial' && <span className="gov-muted"> · part of the Act</span>}
    <span className="gov-muted"> · from <Boundary boundary={run.effectiveFrom} isDated={amr.isDated} start /></span>
    <span className="gov-muted"> · {amr.isCurrent(run) ? 'to now' : <>to <Boundary boundary={run.effectiveTo} isDated={amr.isDated} />{!run.effectiveTo && ` the ${month(run.seenIn.last)} listing`}</>}</span>
    {run.scope === 'partial' && run.detailsRaw && <span className="gov-events__note">{run.detailsRaw}</span>}
  </span>
)

const Attribution = ({ amr }) => (
  <p className="gov-muted">
    From <SourceLink source={{ url: amr.AMR_SOURCE.url, title: 'BC Laws: Acts and Ministers’ Responsibilities' }} />, listings from December 2015.
    Derived under the <SourceLink source={{ url: amr.AMR_SOURCE.licenceUrl, title: 'King’s Printer Licence' }} />; not an official version.
  </p>
)

// A catalogue page for an Act, by its short title, where one exists.
const instrumentByAct = (amr) => {
  const map = new Map()
  for (const entry of INSTRUMENTS) if (entry.type === 'act' && !/, \d{4}$/.test(entry.title)) map.set(amr.actKey(entry.title), entry.id)
  return map
}

/** On a ministry's panel: the Acts it was listed as administering. */
export const ActsAdministeredCard = ({ node, onOpenInstrument }) => {
  const amr = useAmr()
  const [open, setOpen] = useState(false)
  if (!amr) return null
  const acts = amr.actsOfEpisode(node.id)
  if (!acts.length) return null
  const pages = instrumentByAct(amr)
  const current = acts.filter((act) => act.current)
  const shown = open ? acts : (current.length ? current : acts).slice(0, 12)
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">Acts administered <span className="gov-muted">{acts.length}</span></h2>
      <Attribution amr={amr} />
      {current.length > 0 && current.length < acts.length && !open && <p className="gov-muted">{current.length} in the current listing; {acts.length - current.length} listed earlier.</p>}
      <ul className="gov-events">
        {shown.map((act) => {
          const page = pages.get(amr.actKey(act.title))
          const title = `${act.title} Act`.replace(/ Act Act$/, ' Act')
          return (
            <li key={act.key} className="gov-events__item">
              <span className="gov-events__date">{act.current ? 'Now' : 'Earlier'}</span>
              <span className="gov-events__body">
                <span className="gov-events__title">
                  {page && onOpenInstrument
                    ? <button type="button" className="gov-link-button" onClick={() => onOpenInstrument(page)}>{title}</button>
                    : act.statregId ? <SourceLink source={{ url: amr.statregUrl(act.statregId), title }} /> : title}
                  {act.partial && <span className="gov-muted"> · part of the Act</span>}
                </span>
                {act.runs.map((run, index) => <Run key={index} run={run} amr={amr} ministry="" />)}
              </span>
            </li>
          )
        })}
      </ul>
      {shown.length < acts.length && <button type="button" className="gov-link-button" onClick={() => setOpen(true)}>Show all {acts.length}</button>}
    </section>
  )
}

const yearOf = (run) => Math.min(PRESENT_YEAR, Math.max(FIRST_YEAR, Number(String(run.effectiveFrom?.date ?? run.effectiveFrom?.between?.[1] ?? run.seenIn.first).slice(0, 4))))

/** On an Act's page: the ministers BC Laws lists as administering it. */
export const AdministeredByCard = ({ instrument, onGo }) => {
  const amr = useAmr()
  if (!amr || instrument.type !== 'act' || /, \d{4}$/.test(instrument.title)) return null
  const found = amr.assignmentsOfActTitle(instrument.title)
  if (found.ambiguous) {
    return (
      <section className="gov-card">
        <h2 className="gov-card__heading">Administered by</h2>
        <p className="gov-muted">BC Laws lists more than one Act with this short title, so which one this is has not been matched.</p>
      </section>
    )
  }
  if (!found.assignments.length) return null
  return (
    <section className="gov-card">
      <h2 className="gov-card__heading">Administered by <span className="gov-muted">{found.assignments.length}</span></h2>
      <Attribution amr={amr} />
      {found.statregId && <p className="gov-muted"><SourceLink source={{ url: amr.statregUrl(found.statregId), title: 'The Act on BC Laws' }} /></p>}
      <ul className="gov-events">
        {found.assignments.map((run, index) => {
          const ministry = run.episodeId ? lifeOf(run.episodeId)?.name : null
          return (
            <li key={index} className="gov-events__item">
              <span className="gov-events__date">{amr.isCurrent(run) ? 'Now' : 'Earlier'}</span>
              <span className="gov-events__body">
                <span className="gov-events__title">
                  {ministry && onGo
                    ? <button type="button" className="gov-link-button" onClick={() => onGo(yearOf(run), run.episodeId)}>{ministry}</button>
                    : <span>{ministry ?? 'No ministry matched for this title'}</span>}
                </span>
                <Run run={run} amr={amr} ministry="" />
              </span>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
