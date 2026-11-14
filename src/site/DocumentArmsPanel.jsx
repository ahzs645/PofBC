import { DOCUMENT_ARMS_LAYOUT_ORDER, DOCUMENT_ARMS_LAYOUTS } from '../documentArms/layouts.js'
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
        <summary>Evidence and related examples</summary>
        <p>The earlier arms continued in use before the 1987 grant added the helmet, mantling and dogwood details. Different documents used different engravings and lettering.</p>
        <ul>
          <li><a href="https://www2.gov.bc.ca/gov/content/governments/celebrating-british-columbia/symbols-of-bc/coat-of-arms" target="_blank" rel="noreferrer">Province’s history of the arms</a></li>
          <li><a href="https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0832_1978" target="_blank" rel="noreferrer">Original government heading: OIC 832, 6 April 1978</a></li>
          <li><SiteLink to={{ view: 'plates', plate: '1919-cardboard' }}>1919 cardboard plate — the same arms study</SiteLink></li>
          <li><SiteLink to={{ view: 'guides' }}>1977 identity manuals and 1982 memo</SiteLink> — later programme, not specifications for these headings</li>
          <li><a href="https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/celebrating-british-columbia/symbols-of-bc/bc-emblems-set.pdf" target="_blank" rel="noreferrer">The Emblems of British Columbia</a> — current arms guidance</li>
        </ul>
        <p>No period standard for these exact headings has been verified. The source images establish examples of use, not a single government-wide template.</p>
        <a href="https://github.com/ahzs645/PofBC/blob/main/research/identity/document-arms-2026-11-13/README.md" target="_blank" rel="noreferrer">Research, artwork provenance and archival leads</a>
      </details>
    </section>
  )
}
