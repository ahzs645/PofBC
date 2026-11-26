import { Fragment } from 'react'

const former = 'collected-bc-safety-authority'
const successor = 'collected-technical-safety-bc'
const source = (label, href) => ({ label, href })
const gallery = (label, collection, mark) => ({ label, collection, mark })

const history = [
  ['2003–2004 · From the ministry to an independent regulator',
    'The Safety Authority Act received royal assent on May 29, 2003. It established the British Columbia Safety Authority as a not-for-profit corporation. On April 1, 2004, the Ministry of Community, Aboriginal and Women’s Services transferred its Safety Engineering Services Division to the authority.',
    [source('Safety Authority Act, section 3', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/03038_01'), source('Ministry’s transfer record', 'https://www.bcbudget.gov.bc.ca/annual_reports/2003_2004/caws/caws_performance_link4.htm')]],
  ['The two-brushstroke wordmark',
    'The interim board’s 2004 business plan shows the green serif word “Safety,” the small “British Columbia” inscription and two brushstrokes. The 2008 safety report prints the mark in colour on the front and white on the back. A March 2010 bulletin still uses the colour design.',
    [gallery('Brushstroke wordmark and colourways', former, 'bcsa-2010-brushstrokes'), source('2004 business plan, cover', 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/c0fc255d-a199-4916-98f1-543a808bb828/content#page=2'), source('2008 safety report, cover', 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/f8fb494a-a5a5-4064-9b17-866241bcc819/content#page=2')]],
  ['2010–2016 · One sweep, with and without a tagline',
    'The summer 2010 issue of BCSA Today shows the sans-serif wordmark and single green sweep. BC OnLine posted a version with “Do it right. Stay safe.” on May 31, 2011. An October notice and the authority’s 2013 elevating devices program outline carry the same arrangement. A February 2016 inspection bulletin uses the wordmark alone.',
    [gallery('Wordmark with tagline', former, 'bcsa-2011-tagline'), gallery('Standalone wordmark', former, 'source-recovered-bc-safety-authority-2016'), source('BCSA Today, summer 2010', 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/bb936d09-290c-49a2-9eb6-b68e74ce6fe7/content#page=2'), source('BC OnLine notice archive', 'https://www.bconline.gov.bc.ca/news/BCSA-news.html'), source('October 2011 notice', 'https://www.bconline.gov.bc.ca/pdf/BCSA-System-Changes.pdf')]],
  ['September 20, 2017 · Technical Safety BC',
    'After consulting clients and industry, the authority adopted a new operating name and visual identity to clarify its technical role. British Columbia Safety Authority remains its statutory name.',
    [gallery('Technical Safety BC wordmark', successor, 'source-expanded-technical-safety-bc-website-logo'), source('Authority’s announcement', 'https://www.newswire.ca/news-releases/bc-safety-authority-is-now-technical-safety-bc-646053913.html')]]
]

const connections = [
  ['Province and municipalities',
    'The Province sets legislation and policy. The authority licenses contractors, inspects equipment and investigates incidents across sectors including gas, electrical systems, elevators and railways. A 2022 provincial audit identified ten local governments with delegated gas or electrical permitting and inspection duties.',
    [source('Provincial performance audit, executive summary', 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/construction-industry/building-codes-and-standards/reports/performance_audit_of_technical_safety_bc.pdf')]],
  ['WorkSafeBC and railway safety',
    'On April 1, 2004, WorkSafeBC took on occupational health and safety for workers on provincially regulated railways. BC Safety Authority took on the delegated railway safety duties governing the operation of those systems.',
    [gallery('WorkSafeBC gallery', 'worksafebc'), source('WorkSafeBC jurisdiction guidelines', 'https://www.worksafebc.com/en/law-policy/occupational-health-safety/searchable-ohs-regulation/ohs-guidelines/guidelines-for-workers-compensation-act'), source('Railway delegation order', 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0346_2004')]],
  ['BC OnLine and contractor permits',
    'Electrical and gas contractors could buy permits through BC OnLine. The authority’s 2011 postal-strike notice describes that service and preserves the tagline version of its logo.',
    [gallery('BC OnLine gallery', 'collected-sub-bc-online'), source('Authority’s permit-payment notice', 'https://www.bconline.gov.bc.ca/pdf/PUBLIC_NOTICE_POSTAL_STRIKE.pdf')]]
]

export function SafetyAuthorityHistory({ onChooseCollection }) {
  const link = ({ label, href, collection, mark }) => {
    if (href) return <a href={href} target="_blank" rel="noreferrer">{label}</a>
    const query = new URLSearchParams({ view: 'gallery', logos: collection })
    if (mark) query.set('mark', mark)
    return <a href={`?${query}`} onClick={event => {
      if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
      event.preventDefault()
      onChooseCollection(collection, undefined, mark)
    }}>{label}</a>
  }
  return <>{[['Safety Authority history', history], ['Regulatory and service connections', connections]].map(([title, rows]) =>
    <section className="gallery__shelf" key={title} aria-label={title}>
      <h2 className="gallery__shelf-title">{title}</h2>
      <ul className="gallery__history-records">{rows.map(([heading, note, links]) =>
        <li key={heading}><strong>{heading}</strong><p>{note}</p>
          <p className="gallery__sources">{links.map((item, i) => <Fragment key={item.label}>{i > 0 && ' · '}{link(item)}</Fragment>)}</p>
        </li>
      )}</ul>
    </section>
  )}</>
}
