// What the salary records are, where they come from, how personal information is handled and how to
// ask for a correction. Linked from every salary section's introduction.

import { CompanionShell } from './CompanionShell.jsx'

const ISSUES = 'https://github.com/ahzs645/PofBC/issues/new'
const correctionUrl = `${ISSUES}?${new URLSearchParams({
  title: 'Salary record correction',
  body: 'Page or record (copy the link from your address bar):\n\nWhat is wrong:\n\nSource that shows the correct value (link and page number):\n'
})}`

const privateUrl = `${ISSUES}?${new URLSearchParams({
  title: 'Private contact request',
  body: 'Please contact me privately about a salary record. (Do not include names or details here: this page is public.)\n'
})}`

export default function AboutView({ onBrowse }) {
  return (
    <CompanionShell browse="about" onBrowse={onBrowse} heading="About these records"
      intro={<p>How the salary pages are built, what the figures can and cannot tell you, how personal information is handled, and how to report an error.</p>}>
      <div className="salaries-about">
        <section aria-labelledby="about-what">
          <h3 id="about-what" className="salaries__title">What the records are</h3>
          <p>Public bodies in British Columbia publish the names and pay of employees paid more than $75,000 a year, with their expenses, in a Statement of Financial Information under the <a href="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96140_01" target="_blank" rel="noreferrer">Financial Information Act</a> (<a href="https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/371_93" target="_blank" rel="noreferrer">Financial Information Regulation</a>). The provincial government publishes the same for its own employees in the Public Accounts. These pages gather those schedules, with a link to the source page for every record.</p>
          <p>Some older years come from a third-party compilation. Those records are labelled as compiled and are replaced by the employer’s own report wherever it has been found.</p>
          <ul>
            <li><strong>Remuneration is not a salary rate.</strong> It is what was paid in the year: overtime, retroactive pay, vacation payouts, severance and part-year work all change it.</li>
            <li><strong>The $75,000 threshold has not changed since 2002</strong> and is not indexed to inflation. As pay rises, more people cross it each year, so the number of records grows even when the workforce does not. Employer pages lead with the typical raise of people on consecutive lists for that reason.</li>
            <li><strong>A name is not an identity.</strong> Records are grouped by the name as published. Two records with one name can be different people; joins between spellings are reviewed and say how sure they are.</li>
            <li><strong>A missing record is not evidence of anything.</strong> Many employers and years have not been added yet, and pay at or below the threshold is not listed.</li>
            <li>Amounts shown in another year’s dollars use the B.C. consumer price index from Statistics Canada.</li>
          </ul>
        </section>

        <section aria-labelledby="about-privacy">
          <h3 id="about-privacy" className="salaries__title">Privacy</h3>
          <p>Everything here was published by the employer or the government. Nothing is added about anyone beyond what those reports say. B.C.’s Information and Privacy Commissioner has found that disclosing a public employee’s remuneration is not an unreasonable invasion of privacy (<a href="https://www.oipc.bc.ca/orders/1036" target="_blank" rel="noreferrer">Order F10-32</a>).</p>
          <ul>
            <li>Pages about a named person ask search engines not to index them, so a search for someone’s name does not lead here.</li>
            <li>The site does not use analytics, advertising or tracking cookies. Your browser may keep a few display preferences, such as the colour theme, on your own device.</li>
          </ul>
        </section>

        <section aria-labelledby="about-corrections">
          <h3 id="about-corrections" className="salaries__title">Corrections and requests</h3>
          <p>If a record does not match its source, or a name, period or amount was read wrongly, please <a href={correctionUrl} target="_blank" rel="noreferrer">report it</a> with the page link and, if you can, the source page that shows the correct value. Records are corrected against the published report; amounts are never changed to anything the source does not say.</p>
          <p>If you are named in a record and have a concern about it being shown, including for your safety, reports are public, so do not describe it there: <a href={privateUrl} target="_blank" rel="noreferrer">ask to be contacted privately</a>, without your name or details, and the site’s owner will reply. Each request is reviewed individually.</p>
        </section>
      </div>
    </CompanionShell>
  )
}
