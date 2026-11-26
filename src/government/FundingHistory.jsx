import { Fragment, useId } from 'react'
import { SiteLink } from '../site/navigation.jsx'
import { ruralConnectionsOf } from './ruralHealth.js'
import { supportProvidedBy } from './forrex.js'
import './fundingHistory.css'

export const FundingHistory = ({ rows, heading = 'Funding and government connections', onChooseCollection }) => {
  const headingId = useId()
  return (
    <section className="funding-history" aria-labelledby={headingId}>
      <h2 id={headingId}>{heading}</h2>
      <dl>
        {rows.map(({ period, organizations, role, note, source }) => <Fragment key={period + role + organizations.map(({ label }) => label).join('|')}>
          <dt><span>{period}</span> {organizations.map(({ label, to }, index) => <Fragment key={label}>
            {index > 0 && ' · '}
            {to ? <SiteLink to={to} onClick={(event) => {
              if (!onChooseCollection || !to.logos || event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return
              event.preventDefault()
              onChooseCollection(to.logos)
            }}>{label}</SiteLink> : label}
          </Fragment>)} · {role}</dt>
          <dd>{note} <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a></dd>
        </Fragment>)}
      </dl>
    </section>
  )
}

export const SupportProvided = ({ id, onChooseCollection }) => {
  const rows = supportProvidedBy(id)
  return rows ? <FundingHistory rows={rows} heading="Historical funding and partnerships" onChooseCollection={onChooseCollection} /> : null
}

export const RuralHealthConnections = ({ id }) => {
  const rows = ruralConnectionsOf(id).map(({ id: node, label, period, role, description, source }) => ({
    period, role, note: description, source, organizations: [{ label, to: { view: 'government', node } }]
  }))
  return rows.length ? <FundingHistory rows={rows} heading="Rural health connections" /> : null
}
