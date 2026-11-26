import { assetUrl } from './collectedCollections.js'
import { foundationSources as sources } from './bcParksFoundation.js'
import { baselClassicSpecimen, baselGroteskSpecimen } from './foundationDesignStudies.js'
import './parksFoundation.css'

const files = (name) => assetUrl('identity-collected/bc-parks-foundation/' + name)
const images = 'https://cdn.sanity.io/images/p3hjnjl0/production/'
const references = [
  ['Brand playbook', '136100d9d4083a0cbd50a1a9e195e4f74e13b0c0-3300x2550.jpg', 'The playbook pairs Basel Classic Black with Basel Grotesk Regular and Medium. Its pages also specify colour pairings and the space around the logo.'],
  ['Campaign and stationery', '35e19662170538b93da26155419b9754574225b7-3300x2550.jpg', 'Business cards and campaign layouts show how the signature and headline sit against solid colour and photography.'],
  ['Landscape photography', '316790053ad6883866cf135177f05221c132ee06-1640x924.png', 'A small illuminated tent gives a sense of scale beneath the northern lights.'],
  ['Wildlife infographic', 'e9d17957cde330fcbd70dbe28f10b6ee013b800f-1640x924.png', 'Four translucent panels place mammal statistics around a bear. A fine polygon connects the composition.']
]
const programs = [
  ['Discover Parks', 'discover-parks'], ['PaRx', 'parx'], ['Healthy By Nature', 'healthy-by-nature'],
  ['BC Conservation Fund', 'bc-conservation-fund'], ['Parks Bank', 'parks-bank'], ['30×30', '30x30']
]

const Source = ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>

export const ParksFoundationHistory = () => <div className="foundation-history">
  <section aria-labelledby="foundation-identity">
    <h2 id="foundation-identity">The 2025 visual identity</h2>
    <p>The Foundation published its refreshed identity on September 18, 2025. Burnkit kept the existing logo and built a system of type, colour, photography and infographics around it. The logo lettering is preserved as outlines in the downloadable SVGs. <Source href={sources.launch}>Foundation announcement</Source> · <Source href={sources.designer}>Burnkit case study</Source></p>
    <div className="foundation-figures">
      <figure>
        <img src={files('signature-clear-space.svg')} alt="A band around the signature measures one BC letter-pair wide on all four sides."/>
        <figcaption><h3>Signature clear space</h3><p>The width of “BC” in the signature sets the minimum margin on each side. The two dimension lines compare that width with the left margin.</p>
          <a href={files('signature-clear-space.svg')} download>Download clear-space diagram (SVG)</a></figcaption>
      </figure>
      <figure>
        <img src={files('colour-proportions.svg')} alt="Charcoal and Moss occupy half the chart. Umber and Sunset occupy one quarter, and Midnight and Mist the other quarter."/>
        <figcaption><h3>Colour proportions</h3><p>The playbook gives the three pairs approximate shares of 50%, 25% and 25%. This diagram uses the screen colours from the Foundation’s RGB logo files.</p>
          <a href={files('colour-proportions.svg')} download>Download palette diagram (SVG)</a></figcaption>
      </figure>
    </div>
    <p className="gallery__note">PofBC drew both diagrams from the Foundation’s published playbook.</p>
    <h3>Typeface and downloads</h3>
    <p>Chi-Long Trieu designed Basel for Optimo. The Foundation uses Classic Black for headings and Grotesk Regular and Medium for supporting text. <Source href="https://optimo.ch/typefaces/basel">Try or license Basel</Source> · <Source href={baselClassicSpecimen}>Classic specimen (PDF)</Source> · <Source href={baselGroteskSpecimen}>Grotesk specimen (PDF)</Source></p>
    <div className="row gallery__asset-downloads">
      <a className="button" href={files('design-studies.zip')} download>Download all 15 SVGs and source notes (ZIP)</a>
      <a className="button button--ghost" href={files('playbook/SOURCES.md')} download>Download source notes</a>
    </div>
    <h3>Examples from the launch</h3>
    <div className="foundation-figures">
      {references.map(([title, file, caption]) => <figure key={file}>
        <a href={images + file} target="_blank" rel="noreferrer" aria-label={'Open full-size ' + title.toLowerCase()}>
          <img loading="lazy" src={images + file + '?w=680&auto=format'} alt={title}/>
        </a>
        <figcaption><h4>{title}</h4><p>{caption}</p></figcaption>
      </figure>)}
    </div>
  </section>
  <section aria-labelledby="foundation-partnership">
    <h2 id="foundation-partnership">The partnership with BC Parks</h2>
    <dl>
      <dt>2017 · Establishment</dt><dd>The Province provided an initial $10 million and announced the Foundation’s ten-member board on March 28. Karla Rockwell was its first chair. <Source href={sources.board}>Provincial announcement</Source></dd>
      <dt>2018 · Operations and agreement</dt><dd>The Foundation dates its start to 2018. In May it signed a collaborative agreement with the Province. <Source href={sources.faq}>Foundation FAQ</Source> · <Source href={sources.agreement}>Ministry estimates notes</Source></dd>
      <dt>2019 · Early artwork</dt><dd>The activity book <i>Connecting with Place</i> shows the white Foundation signature beside four illustrated park patches. The 2019 version is selectable on the signature page. <Source href={sources.earlier}>Activity book, page 10</Source> · <Source href={sources.loki}>Loki Creative’s identity project</Source></dd>
      <dt>2022 · The two signatures together</dt><dd>The January BC Parks brand guide shows a partner layout pairing the provincial BC Parks signature with the Foundation’s mark. <Source href="https://cdn.prod.website-files.com/60d2303d770c7e4f4545cdd3/654a7cd469d3db15c96b0b1e_Fullwidth-Image-1-.jpg">Becoming’s published guide pages</Source></dd>
      <dt>2023 · Endowment and conservation funding</dt><dd>On June 1 the Province announced a further $10 million for the Foundation. In October the two partners announced conservation financing to support First Nations-led projects. <Source href={sources.endowment}>Endowment announcement</Source> · <Source href={sources.conservation}>Conservation financing announcement</Source></dd>
    </dl>
    <h3>Foundation initiatives</h3>
    <p>Discover Parks is one place the partnership reaches visitors. The Foundation developed the program, and sales of BC Parks licence plates help fund it. <Source href="https://bcparks.ca/plan-your-trip/discover-parks/">BC Parks program description</Source></p>
    <ul className="foundation-programs">{programs.map(([name, slug]) => <li key={slug}><Source href={'https://bcparksfoundation.ca/initiatives/' + slug + '/'}>{name}</Source></li>)}</ul>
  </section>
</div>
