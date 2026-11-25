import { CollectedMarkView } from '../gallery/CollectedMarkView.jsx'
import { specimenEntriesOf } from '../gallery/collectedCollections.js'
import { SiteLink } from '../site/navigation.jsx'

const [specimen] = specimenEntriesOf('travel-industry')

export default function TravelIndustryLogo() {
  return <section className="internal-logos" aria-label="Departmental Logos">
    <SiteLink className="internal-logos__back" to={{ view: 'internal' }}>← Departmental Logos</SiteLink>
    <CollectedMarkView entry={specimen} />
    <p>{specimen.asset.dateNote}</p>
    <SiteLink to={{ view: 'gallery', subject: 'department-of-travel-industry' }}>Department of Travel Industry in the register →</SiteLink>
  </section>
}
