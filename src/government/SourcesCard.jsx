// What the atlas is drawn from and how far to trust it: a short note that is always shown, and
// everything long (every source, how much the data covers, the historical rosters, the compiler's
// accounting) behind the one fold, built only when it is first opened. The history's sources alone
// are some 1,250 links that almost no visit reads.

import { Disclosure } from '../site/Disclosure.jsx'
import { Coverage, HistoricalRosters, ImportAccounting } from './AtlasCards.jsx'
import { AMR_ATTRIBUTION, AMR_COLLECTION, AMR_LICENCE } from './amrLicence.js'
import { BODY_CHECKED, CURRENT_AS_OF, CURRENT_SOURCES } from './currentData.js'
import { EVENT_SOURCES } from './events.js'
import { HISTORY_SOURCES } from './historyData.js'
import { HISTORICAL_CENSUSES } from './researchData.js'
import { TIMELINE_SOURCES } from './timelineData.js'

const MAIN_SOURCES = [...TIMELINE_SOURCES, ...CURRENT_SOURCES]
const ROSTERS = HISTORICAL_CENSUSES.reduce((sum, census) => sum + census.rosters.length, 0)

const External = ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>

export const SourcesCard = () => (
  <section className="gov-card gov-sources" aria-labelledby="gov-sources-title">
    <h2 id="gov-sources-title" className="gov-card__heading">Sources and caveats</h2>
    <ul className="gov-sources__points">
      <li><strong>Ministries and their lineage:</strong> the BC Archives’ ministry history diagram (to December 2024), corrected where it leaves ends open and extended since.</li>
      <li><strong>Ministers:</strong> the Legislative Library’s Executive Council Appointments 1871–1986 and its cabinet lists since. Cabinet appointments and portfolio transfers checked on {CURRENT_AS_OF}.</li>
      <li><strong>Other bodies and office-holders:</strong> former Crown corporations and agencies, and past Speakers, officers and chief justices, from BC Archives, the Library, Orders in Council and Wikipedia. Other agency leadership checked on {BODY_CHECKED}.</li>
      <li><strong>Staff:</strong> 2025/26 full-time equivalents from the Public Accounts.</li>
      <li><strong>Events</strong> (origins, name and logo changes, appointments, the 2026 election’s schedule): the BC government atlas research package of 25 September 2026 and the research that followed it ({EVENT_SOURCES.length.toLocaleString('en-CA')} sources).</li>
    </ul>
    <p className="gov-muted gov-sources__caveats">
      Which ministry answered for a body is shown where a source states it, and otherwise inferred and marked so. The dates of
      the four identities are estimates, most of all the crest’s. A date is shown only as precisely as its source gives it; an
      unknown start is not treated as proof a body did not exist.
    </p>
    <p className="gov-muted gov-sources__licence">
      Ministers’ responsibilities for Acts: <External href={AMR_COLLECTION.url}>{AMR_COLLECTION.title}</External>,
      under the <External href={AMR_LICENCE.url}>{AMR_LICENCE.name}</External>. {AMR_ATTRIBUTION}
    </p>
    <Disclosure
      className="gov-sources__more"
      summary="All sources, coverage and historical rosters"
      hint={`${MAIN_SOURCES.length} main sources · ${HISTORY_SOURCES.length.toLocaleString('en-CA')} behind the history · ${ROSTERS} rosters`}
    >
      {() => (
        <>
          <h3 className="gov-card__subheading">Main sources <span className="gov-muted">{MAIN_SOURCES.length}</span></h3>
          <ul className="gov-sources__list">
            {MAIN_SOURCES.map((source) => <li key={source.id}><External href={source.url}>{source.title}</External></li>)}
          </ul>

          <h3 className="gov-card__subheading">Coverage</h3>
          <Coverage />

          <h3 className="gov-card__subheading">Historical source rosters <span className="gov-muted">{ROSTERS}</span></h3>
          <HistoricalRosters />

          <h3 className="gov-card__subheading">Import accounting</h3>
          <ImportAccounting />

          <h3 className="gov-card__subheading">Sources behind the history <span className="gov-muted">{HISTORY_SOURCES.length.toLocaleString('en-CA')}</span></h3>
          <ul className="gov-sources__list gov-sources__list--scroll" tabIndex={0} aria-label="Sources behind the history">
            {HISTORY_SOURCES.map((url) => <li key={url}><External href={url}>{url.replace(/^https?:\/\/(www\.)?/, '')}</External></li>)}
          </ul>
        </>
      )}
    </Disclosure>
  </section>
)
