import { DOCUMENT_ARMS_LAYOUT_ORDER, DOCUMENT_ARMS_LAYOUTS } from '../documentArms/layouts.js'
import { DOCUMENT_ARMS_RESEARCH_URL } from '../documentArms/evidence.js'
import { SiteLink } from './navigation.jsx'
import { Segmented } from './Segmented.jsx'

const OPTIONS = DOCUMENT_ARMS_LAYOUT_ORDER.map((value) => ({
  value, label: DOCUMENT_ARMS_LAYOUTS[value].label,
  title: DOCUMENT_ARMS_LAYOUTS[value].description
}))

export function DocumentArmsPanel({ state, update, clearSpaceOptions }) {
  return (
    <section className="panel document-arms-panel">
      <h2>Historical document layouts</h2>
      <Segmented
        label="Heading"
        options={OPTIONS}
        value={state.documentLayout}
        onChange={(documentLayout) => update({ documentLayout })}
        hint={DOCUMENT_ARMS_LAYOUTS[state.documentLayout]?.hint}
      />
      <Segmented
        label="Clear space"
        options={clearSpaceOptions}
        value={state.clearSpace}
        onChange={(clearSpace) => update({ clearSpace })}
        hint="An adjustable export margin, not a recovered historical rule."
      />
      <details className="document-arms-evidence">
        <summary>Evidence and visual guides</summary>
        <p>Earlier arms appear on the 1954 mining booklet and 1978 orders shown beside the study. The 1987 grant added the helmet, mantling and dogwood details.</p>
        <ul>
          <li><a href="https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms" target="_blank" rel="noreferrer">Province’s history of the arms</a></li>
          <li><a href="https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978" target="_blank" rel="noreferrer">OIC 1121, 4 May 1978</a> — government heading on page 1; the supplied Crown-grant map heading on page 4</li>
          <li><SiteLink to={{ view: 'plates', plate: '1919-cardboard' }}>1919 cardboard plate — the same arms study</SiteLink></li>
          <li><SiteLink to={{ view: 'guides' }}>1977 identity manuals and 1982 memo</SiteLink> — later programme, not specifications for these headings</li>
          <li><a href="https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/bc-emblems-set.pdf" target="_blank" rel="noreferrer">The Emblems of British Columbia</a> — current arms guidance</li>
        </ul>
        <p>The 1954 cover and title page use different engravings. No period standard for these exact headings has been verified; the specimens document individual examples.</p>
        <a href={DOCUMENT_ARMS_RESEARCH_URL} target="_blank" rel="noreferrer">Research, retained originals and archival leads</a>
      </details>
    </section>
  )
}
