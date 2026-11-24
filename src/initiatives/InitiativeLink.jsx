import { SiteLink } from '../site/navigation.jsx'
import { initiativeById } from './initiatives.js'
import './initiatives.css'

/** A reciprocal link from an organization's artwork to the initiative it helped deliver. */
export const InitiativeLink = ({ id }) => {
  const initiative = initiativeById(id)
  if (!initiative) return null
  return <SiteLink className="initiatives__teaser" to={{ view: 'initiatives', initiative: id }}>
    <span>Initiatives / {initiative.title}</span>
    <strong>{initiative.exploreLabel ?? 'Explore websites, campaigns and the wider history'}
      <svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M3 10h13m-5-5 5 5-5 5" stroke="currentColor" strokeWidth="1.4" /></svg>
    </strong>
  </SiteLink>
}
