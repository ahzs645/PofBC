import { programMarkVersion } from './programMarkVersions.js'

export const fireSmartGuide = 'https://firesmartbc.ca/wp-content/uploads/2023/04/07.22.25_FSBC_BrandGuidelines.pdf'

export const fireSmartDesigns = [
  { key: 'signature', title: 'British Columbia FireSmart signature', page: 5,
    notes: 'The flame encloses the silhouette of a house. British Columbia sits above the FireSmart lettering. The guide shows a full-colour treatment for each background.' },
  { key: 'wildfire-mitigation', title: 'Wildfire Mitigation Program', page: 17,
    notes: 'A diagonal roofline separates a red flame above from a house below. The three lines of lettering include the provincial abbreviation BC.' },
  { key: 'local-collective', title: 'Local FireSmart Collective Program', page: 19,
    notes: 'Small houses in two shades of blue form a circle beside the two-line program name.' },
  { key: 'plant-program', title: 'FireSmart Plant Program', page: 20,
    notes: 'One flame sits inside another in a green shield. The program name sits in two lines beside it.' },
  { key: 'training-summit', title: 'Wildfire Resiliency and Training Summit', page: 22,
    notes: 'A conifer stands inside a flame framed by a roof. The summit name appears beside it in two lines of capitals.' },
  { key: 'ember-front', title: 'Ember the FireSmart Fox', page: 13,
    poses: { 'ember-front': 'Front profile', 'ember-side': 'Side profile', 'ember-sitting': 'Sitting', 'ember-standing': 'Standing' },
    notes: 'Ember wears the FireSmart flame on her neckerchief. The guide shows her in two profile portraits and two full-body poses.' }
]

// Checksums are for the downloadable SVGs. The PDF page and named example locate each placed graphic.
const checksums = {
  'ember-front': 'bbc3cda6d5ad43a11e6d270b02676d464253a1e287da17dffab9890fae053a7b',
  'ember-side': 'b8db687c1dcf4f034c13e16b040aa4ce153921e7db965b8e96183c3871ae816b',
  'ember-sitting': 'a41b49d56acd7b050fc84af6a4207ca0458b8b5e7f35293979e299bc153b5995',
  'ember-standing': 'cb289de85144bbbe2f7fa3791b545bebaea6150838a8c6aba44c2f43ee59cb61',
  'local-collective-positive': 'b7f1e7d98170137f59b57874c737dadad51f45f613ae8ded908352cd2e89be23',
  'local-collective-reverse': 'eb76f3965b26b58c80cfcd73b20102cff8b95627fae4c191a4f683855070ea22',
  'plant-program-positive': '03175eb1d49c5b5b61027a53d8b23a4d7592a0c7ce5dad0ffc5b720a21bb9d35',
  'plant-program-reverse': 'e8a070d7fddbe69b3ef4c409c64174b272a618f4ee7e6d8d9911318d4e7ad9da',
  'signature-positive': 'fcc4dfa513535a8b46263b9ed05fe53635306600646ef5b1b9a6b05f2ae90aaa',
  'signature-reverse': 'ce94a5e8f82c68fd6187d43a5e480c04da426dd4494d4a16e6d8b77d2e1da662',
  'training-summit-positive': '885fe2d47f92afadab99ebba633cdff5f9b0b6df052a89a39e80d9d09cd483dd',
  'training-summit-reverse': 'e0a120cf5e779a5f2067a5053394820edf90d7708c310b1ffcd4023d6811ebfa',
  'wildfire-mitigation-positive': 'f13e89671a8b93583dc6febd9adf3df07ba0a3a447b82ae8439a5a59d6d98110',
  'wildfire-mitigation-reverse': 'a53736703335c5a7473db8eb69e49af94c96782890820b6572a16f3bdd7d7f79',
}

export const fireSmartSpecimens = {
  program: 'firesmart-bc',
  assets: fireSmartDesigns.flatMap(({ key, title, page, notes, poses }) => {
    const designId = 'firesmart-bc-' + key
    const versions = poses
      ? Object.entries(poses).map(([slug, label]) => ({
        slug, version: { id: 'firesmart-bc-' + slug, versionLabel: label, pose: label, sourceGround: 'light',
          ...(slug === key ? {} : { variantOf: designId }) }
      }))
      : ['positive', 'reverse'].map((treatment) => ({
        slug: key + '-' + treatment,
        version: programMarkVersion(treatment === 'positive' ? designId : designId + '-reverse', designId, treatment, designId + '-reverse')
      }))
    return versions.map(({ slug, version }) => ({
      ...version, label: title, designLabel: title, notes, publisher: 'FireSmart BC',
      file: 'identity-collected/firesmart-bc/' + slug + '.svg', sha256: checksums[slug],
      format: 'svg', isVector: true, evidenceType: 'native-pdf-vector-extraction',
      sourceDate: '2025-07', dateNote: 'July 2025 edition of the guide.', observedDate: '2026-11-25',
      sourceUrl: fireSmartGuide, sourcePage: fireSmartGuide + '#page=' + page,
      sourceLocator: `FireSmart BC Brand Guidelines, version two, PDF page ${page}, ${title}, ${version.versionLabel}.`,
      extraction: { page, method: 'Isolated the placed PDF graphic on transparency and converted with pdftocairo -svg, retaining paths, outlined lettering and gradient fills.' },
      fidelity: 'source compared', fidelityNote: 'Published artwork isolated from its example panel. The SVG contains vector geometry throughout.'
    }))
  })
}
